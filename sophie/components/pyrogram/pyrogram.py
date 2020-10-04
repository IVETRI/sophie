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

import logging

from pyrogram import Client

from sophie.utils.config import cfg

TOKEN = cfg.general.token
session_name = TOKEN.split(':')[0]

API_ID = cfg.component.pyrogram.app_id
API_HASH = cfg.component.pyrogram.app_hash

pbot = Client(
    session_name,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)

# disable logging for pyrogram [not for ERROR logging]
logging.getLogger('pyrogram').setLevel(level=logging.ERROR)
