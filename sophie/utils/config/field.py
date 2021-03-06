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
#

import os
from typing import Any

from pydantic.fields import FieldInfo, Undefined


def Field(default: Any = Undefined, *, env: Any, **extra: Any) -> Any:
    """A hack method to include out of box env variable support in pydantic BaseModels"""

    if env := os.environ.get(env):
        return FieldInfo(env, **extra)

    return FieldInfo(default, **extra)


__all__ = [
    "Field"
]
