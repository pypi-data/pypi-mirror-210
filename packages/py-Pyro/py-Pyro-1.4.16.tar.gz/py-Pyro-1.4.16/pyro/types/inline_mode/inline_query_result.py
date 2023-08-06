#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from uuid import uuid4

import pyro
from pyro import types
from ..object import Object

"""- :obj:`~pyro.types.InlineQueryResultCachedAudio`
    - :obj:`~pyro.types.InlineQueryResultCachedDocument`
    - :obj:`~pyro.types.InlineQueryResultCachedGif`
    - :obj:`~pyro.types.InlineQueryResultCachedMpeg4Gif`
    - :obj:`~pyro.types.InlineQueryResultCachedPhoto`
    - :obj:`~pyro.types.InlineQueryResultCachedSticker`
    - :obj:`~pyro.types.InlineQueryResultCachedVideo`
    - :obj:`~pyro.types.InlineQueryResultCachedVoice`
    - :obj:`~pyro.types.InlineQueryResultAudio`
    - :obj:`~pyro.types.InlineQueryResultContact`
    - :obj:`~pyro.types.InlineQueryResultGame`
    - :obj:`~pyro.types.InlineQueryResultDocument`
    - :obj:`~pyro.types.InlineQueryResultGif`
    - :obj:`~pyro.types.InlineQueryResultLocation`
    - :obj:`~pyro.types.InlineQueryResultMpeg4Gif`
    - :obj:`~pyro.types.InlineQueryResultPhoto`
    - :obj:`~pyro.types.InlineQueryResultVenue`
    - :obj:`~pyro.types.InlineQueryResultVideo`
    - :obj:`~pyro.types.InlineQueryResultVoice`"""


class InlineQueryResult(Object):
    """One result of an inline query.

    Pyrogram currently supports results of the following types:

    - :obj:`~pyro.types.InlineQueryResultArticle`
    - :obj:`~pyro.types.InlineQueryResultPhoto`
    - :obj:`~pyro.types.InlineQueryResultAnimation`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "pyro.Client"):
        pass
