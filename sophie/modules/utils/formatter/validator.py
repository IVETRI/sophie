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

from __future__ import annotations

import inspect
from typing import Any, Callable, List, Optional, TYPE_CHECKING

from sophie.components.localization import GetString
from .plugins.bases import get_all_plugins

if TYPE_CHECKING:
    from aiogram.api.types import Message
    from .compiler import RawNoteModel


class _Validate:

    async def __call__(
            self, message: Message,
            data: RawNoteModel,
            excluded: Optional[List[str]] = None,
            included: Optional[List[str]] = None
    ) -> bool:

        self.message = message
        self.data = data
        self.excluded = excluded
        self.included = included

        # vars
        self.plugins: List[str] = []

        result = await self.validate()
        if self.plugins:
            self.data.plugins = self.plugins
        return result

    @classmethod
    def generate_kwargs(cls, validator: Callable[..., Any], **kwargs: Any) -> dict:
        spec = inspect.getfullargspec(validator)
        return {key: value for key, value in kwargs.items() if key in spec.args}

    async def validate(self) -> bool:
        for plugin in get_all_plugins(included=self.included, excluded=self.excluded):
            try:
                if plugin.__syntax__:
                    if self.data.text is not None:
                        for match in plugin.__syntax__.finditer(self.data.text):
                            kwargs = self.generate_kwargs(
                                plugin.validate, message=self.message, data=self.data, match=match
                            )
                            await plugin.validate(**kwargs)
                else:
                    kwargs = self.generate_kwargs(
                        plugin.validate, message=self.message, data=self.data
                    )
                    await plugin.validate(**kwargs)
            except (TypeError, ValueError, AssertionError) as err:
                if err.args:
                    await self.message.reply(
                        await GetString(key=err.args[0], chat_id=self.message.chat.id)
                    )
                return False
            self.plugins.append(plugin.__name__)
        return True


validate = _Validate()

__all__ = ["validate"]
