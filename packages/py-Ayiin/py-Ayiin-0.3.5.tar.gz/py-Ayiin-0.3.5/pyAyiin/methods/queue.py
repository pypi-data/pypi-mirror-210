# py - Ayiin
# Copyright (C) 2022-2023 @AyiinXd
#
# This file is a part of < https://github.com/AyiinXd/pyAyiin >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/AyiinXd/pyAyiin/blob/main/LICENSE/>.
#
# FROM py-Ayiin <https://github.com/AyiinXd/pyAyiin>
# t.me/AyiinChat & t.me/AyiinSupport


# ========================×========================
#            Jangan Hapus Credit Ngentod
# ========================×========================

from pycover.types.input_stream import AudioPiped, AudioVideoPiped
from pycover.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)

class Queues(object):
    def __init__(self):
        self.queue = {}

    def add_to_queue(self, chat_id, songname, link, ref, type, quality):
        if chat_id in self.queue:
            chat_queue = self.queue[chat_id]
            chat_queue.append([songname, link, ref, type, quality])
            return int(len(chat_queue) - 1)
        self.queue[chat_id] = [[songname, link, ref, type, quality]]
    
    def get_queue(self, chat_id):
        if chat_id in self.queue:
            return self.queue[chat_id]
        return 0
    
    def pop_an_item(self, chat_id):
        if chat_id in self.queue:
            chat_queue = self.queue[chat_id]
            chat_queue.pop(0)
            return 1
        return 0
    
    def clear_queue(self, chat_id: int):
        if chat_id in self.queue:
            self.queue.pop(chat_id)
            return 1
        return 0
    
    async def skip_song(self, client, chat_id):
        try:
            if chat_id in self.queue:
                chat_queue = self.get_queue(chat_id)
                if len(chat_queue) == 1:
                    await client.leave_group_call(chat_id)
                    self.clear_queue(chat_id)
                    return 1
                else:
                    songname = chat_queue[1][0]
                    url = chat_queue[1][1]
                    link = chat_queue[1][2]
                    type = chat_queue[1][3]
                    RESOLUSI = chat_queue[1][4]
                    if type == "Audio":
                        await client.change_stream(
                            chat_id,
                            AudioPiped(
                                url,
                                HighQualityAudio(),
                            ),
                        )
                    elif type == "Video":
                        if RESOLUSI == 720:
                            hm = HighQualityVideo()
                        elif RESOLUSI == 480:
                            hm = MediumQualityVideo()
                        elif RESOLUSI == 360:
                            hm = LowQualityVideo()
                        await client.change_stream(
                            chat_id, AudioVideoPiped(url, HighQualityAudio(), hm)
                        )
                    self.pop_an_item(chat_id)
                    return [songname, link, type]
            else:
                return 0
        except Exception as e:
            print(e)

    async def skip_item(self, chat_id, h):
        if chat_id in self.queue:
            chat_queue = self.get_queue(chat_id)
            try:
                x = int(h)
                songname = chat_queue[x][0]
                chat_queue.pop(x)
                return songname
            except Exception as e:
                print(e)
                return 0
        else:
            return 0
