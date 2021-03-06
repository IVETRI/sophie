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

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from aiogram.api.types import Message


def get_args(message: Message) -> str:
    if message.text is not None:
        args = message.text.split(' ', 1)  # TODO: Change to aio's method
        if len(args) == 1:
            return ''
        return args[1]
    return ''


def get_args_list(message: Message, lower: bool = True) -> typing.List[str]:
    args = get_args(message)
    if lower:
        args = args.lower()
    return args.split(' ')
