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

from typing import Any, Awaitable, Callable, Generator, List, Optional, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from re import Pattern


class BaseFormatPlugin:
    __syntax__: Optional[Pattern] = None

    if TYPE_CHECKING:
        compile_: Callable[..., Awaitable[Any]]
        decompile: Callable[..., Awaitable[Any]]
        validate: Callable[..., Awaitable[Any]]
    else:

        @classmethod
        async def compile_(cls, *args: Any, **kwargs: Any) -> Any:
            pass

        @classmethod
        async def decompile(cls, *args: Any, **kwargs: Any) -> Any:
            pass

        @classmethod
        async def validate(cls, *args: Any, **kwargs: Any) -> Any:
            pass


def get_all_plugins(
        included: Optional[List[str]] = None, excluded: Optional[List[str]] = None
) -> Generator[Type[BaseFormatPlugin], Any, None]:
    for plugin in BaseFormatPlugin.__subclasses__():
        if included is not None:
            if plugin.__name__ not in included:
                continue
        elif excluded is not None:
            if plugin.__name__ in excluded:
                continue
        yield plugin
