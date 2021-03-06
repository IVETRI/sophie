# Copyright (C) 2018 - 2020 MrYacha.
# Copyright (C) 2020 Jeepeo.
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
from functools import cached_property

from importlib import import_module
from pathlib import Path, PosixPath, WindowsPath
from typing import Any, ClassVar, Dict, List, Optional, TYPE_CHECKING, Tuple, Type, Union, cast

from sophie.utils.bases import Base, BaseModule
from sophie.utils.config import cfg, real_config
from sophie.utils.logging import log

from .requirements import check_requirements

if TYPE_CHECKING:
    from aiogram import Router


class Package:

    def __init__(self, type: str, name: str, path: Path):  # noqa: A002
        self.type = type
        self.name = name
        self.path = path

        # vars
        self.data: Dict[Any, Any] = {}
        self.version: Optional[str] = None

        if not path.exists():
            raise FileNotFoundError

        log.debug(f"Loading {self.name} package, {self.type=}...")

        if (requirements_file_path := self.path / 'requirements.txt').exists():
            log.debug(f"Checking requirements for {self.name} {self.type}...")
            with open(requirements_file_path) as f:
                check_requirements(f)
                log.debug("...Done!")

        log.debug(f"Importing {self.name} package...")
        self.p_object: Any = import_module(self.python_path)  # contains the module

        version_file = self.path / 'version.txt'
        if version_file.exists():
            with open(version_file) as f:
                self.version = f.read()

        if hasattr(self.base, 'configurations'):
            self.__load_config()

        if hasattr(self.base, '__pre_init__'):
            self.__trigger_pre_init()

        log.debug(f"Successfully loaded package {self.name}")

    @cached_property
    def python_path(self) -> str:
        if isinstance(self.path, WindowsPath):
            return str(self.path).replace('\\', '.')
        elif isinstance(self.path, PosixPath):
            return str(self.path).replace('/', '.')
        else:
            return str(self.path)

    def __load_config(self) -> bool:
        log.debug(f"Loading configurations for {self.name} package")
        setattr(
            getattr(
                cfg,
                self.type
            ),
            self.name,
            self.base.configurations.parse_obj(
                real_config.get(self.type, {}).get(self.name, {})
            )
        )
        return True

    def __trigger_pre_init(self) -> Any:
        log.debug(f"Running __pre_init__ of {self.name} package...")
        self.base.__pre_init__(self.p_object)
        log.debug("...Done")

    @cached_property
    def base(self) -> Type[Base]:
        for cls in inspect.getmembers(self.p_object, self.__istarget):
            return cls[1]
        raise RuntimeError(f"{self.type} {self.name} should implement base!")

    @staticmethod
    def __istarget(member: Any) -> bool:
        if inspect.isclass(member) and issubclass(member, Base):
            if member.__name__ not in {'BaseModule', 'BaseComponent'}:
                return True
        return False

    def __repr__(self) -> str:
        # debugging
        attrs = ", ".join(repr(v) if k is None else f'{k}={v!r}' for k, v in self.__dict__.items())
        cls = self.__class__.__name__
        return f"{cls}({attrs})"


class Module(Package):
    routers: ClassVar[List[Tuple[Router, Union[int, float]]]] = []

    def __init__(self, name: str, path: Path):
        super().__init__('module', name, path)
        self._load_module(self, cast(BaseModule, self.base))

    @classmethod
    def _load_module(cls, package: Package, module: BaseModule) -> None:
        # Load routers
        if module.router:
            log.debug(f"Loading router(s) for {package.name} {package.type}...")
            routers: List[Router] = [module.router] if not isinstance(module.router, list) else module.router

            for router in routers:
                cls.routers.append((router, module.level))

    @classmethod
    def register_routers(cls) -> None:
        from sophie.services.aiogram import modules_router

        # sort the routers according to level
        cls.routers.sort(key=lambda x: x[1])

        for router, _ in cls.routers:
            modules_router.include_router(router)

        log.debug(f"Registered {len(cls.routers)} routers!")
