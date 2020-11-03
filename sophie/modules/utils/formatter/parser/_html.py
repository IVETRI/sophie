# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of Sophie.

from collections import deque
from html.parser import HTMLParser
from typing import Deque, Dict, List, Optional, Tuple

from aiogram.api.types import MessageEntity

from .utils import MessageEntityType, _MutableMessageEntity, _co_entities, _escape_html, add_surrogate, del_surrogate, \
    strip_text

BOLD = {'b', 'strong'}
ITALICS = {'i', 'em'}
UNDERLINE = {'u'}
STRIKETHROUGH = {'s', 'del', 'strike'}
CODE = {'code', 'pre'}
LINK = {'a'}


class _HTMLToTelegramParser(HTMLParser):
    def __init__(self) -> None:
        super(_HTMLToTelegramParser, self).__init__(convert_charrefs=False)

        self.text = ''

        self.entities: List[_MutableMessageEntity] = []
        self._building_entities: Dict[str, _MutableMessageEntity] = {}

        self._open_tags: Deque[str] = deque()
        self._open_tags_meta: Deque[Optional[str]] = deque()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        self._open_tags.appendleft(tag)
        self._open_tags_meta.appendleft(None)

        dict_attrs = dict(attrs)
        entity_type = None
        args = {}
        if tag in BOLD:
            entity_type = MessageEntityType.BOLD
        elif tag in ITALICS:
            entity_type = MessageEntityType.ITALIC
        elif tag in UNDERLINE:
            entity_type = MessageEntityType.UNDERLINE
        elif tag in STRIKETHROUGH:
            entity_type = MessageEntityType.STRIKETHROUGH
        elif tag == 'code':
            try:
                pre = self._building_entities['pre']
                try:
                    if (cls := dict_attrs['class']) is not None:
                        pre.language = cls[len('language-'):]
                except KeyError:
                    pass
            except KeyError:
                entity_type = MessageEntityType.CODE
        elif tag == 'pre':
            entity_type = MessageEntityType.PRE
            args['language'] = ''
        elif tag in LINK:
            try:
                if (url := dict_attrs['href']) is None:
                    return
            except KeyError:
                return
            if url.startswith('mailto:'):
                url = url[len('mailto:'):]
                entity_type = MessageEntityType.EMAIL
            else:
                if self.get_starttag_text() == url:
                    entity_type = MessageEntityType.URL
                else:
                    entity_type = MessageEntityType.TEXT_LINK
                    args['url'] = url
                    url = None
            self._open_tags_meta.popleft()
            self._open_tags_meta.appendleft(url)

        if entity_type and tag not in self._building_entities:
            self._building_entities[tag] = _MutableMessageEntity(
                type=entity_type,
                offset=len(self.text),
                length=0,
                **args,)

    def handle_data(self, text: str) -> None:
        previous_tag = self._open_tags[0] if len(self._open_tags) > 0 else ''
        if previous_tag == 'a':
            url = self._open_tags_meta[0]
            if url:
                text = url

        for _, entity in self._building_entities.items():
            entity.length += len(text)

        self.text += text

    def handle_endtag(self, tag: str) -> None:
        try:
            self._open_tags.popleft()
            self._open_tags_meta.popleft()
        except IndexError:
            pass
        entity = self._building_entities.pop(tag, None)
        if entity:
            self.entities.append(entity)

    def error(self, message: str) -> None:
        raise ValueError(message)


def parse_html(html: str) -> Tuple[str, List[MessageEntity]]:
    parser = _HTMLToTelegramParser()
    parser.feed(add_surrogate(html))
    text = strip_text(parser.text, parser.entities)
    return _escape_html(del_surrogate(text)), _co_entities(parser.entities)
