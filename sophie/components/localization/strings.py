# Copyright (C) 2018 - 2020 MrYacha.
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

from typing import Optional, Union, TypeVar, Any, Dict, cast, Callable

from aiogram.dispatcher.handler import MessageHandler
from babel.core import Locale

from .lanuages import get_babel, get_language_emoji
from .locale import get_chat_locale
from .loader import GLOBAL_TRANSLATIONS


class GetStrings:
    def __init__(self, module: Optional[str] = None):
        from sophie.utils.loader import LOADED_MODULES

        self.modules = LOADED_MODULES
        self.module = module

    def get_by_locale_name(self, locale_code: str) -> Dict[str, str]:
        if not self.module:
            translations = GLOBAL_TRANSLATIONS
        else:
            translations = self.modules[self.module].data['translations']

        if locale_code not in translations:
            locale_code = 'en-US'

        return translations[locale_code]

    async def get_by_chat_id(self, chat_id: int) -> Dict[str, str]:
        locale_name = await get_chat_locale(chat_id)
        return self.get_by_locale_name(locale_name)

    def __getitem__(self, locale_name: str) -> Dict[str, str]:
        return self.get_by_locale_name(locale_name)


class GetString:
    def __init__(self, module: Optional[str] = None, *, key: str):
        self.module = module
        self.key = key

    def get_by_locale_name(self, locale_code: str) -> Dict[str, str]:
        strings = GetStrings(self.module)[locale_code]  # type: ignore
        return strings

    async def get_by_chat_id(self, chat_id: int) -> str:
        locale_code = await get_chat_locale(chat_id)
        return self.get_by_locale_name(locale_code)[self.key]


class Strings:
    """
    Replacement of strings dict
    """

    def __init__(self, locale_code: str, module: str):
        self.locale_code = locale_code
        self.strings = GetStrings(module).get_by_locale_name(locale_code)

    def _get_string(self, key: str) -> str:
        return self.strings[key]

    def get(self, key: str, **kwargs: Any) -> str:
        string = self._get_string(key)
        string = string.format(**kwargs)
        return string

    @property
    def code(self) -> str:
        return self.locale_code

    @property
    def babel(self) -> Locale:
        return get_babel(self.locale_code)

    @property
    def emoji(self) -> str:
        return get_language_emoji(self.locale_code)

    def __getitem__(self, key: str) -> Union[str, dict]:
        return self._get_string(key)


T = TypeVar("T", bound=Callable[..., Any])


def get_strings_dec(func: T) -> T:
    async def decorated(event: MessageHandler, *args: Any, **kwargs: Any) -> Any:
        module_name = func.__module__.split('.')[2]

        chat_id = event.chat.id
        strings = Strings(await get_chat_locale(chat_id), module_name)

        return await func(event, *args, strings=strings, **kwargs)

    return cast(T, decorated)
