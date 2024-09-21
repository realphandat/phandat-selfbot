import asyncio
from playsound3 import playsound

class Notification:
    def __init__(self, client):
        self.client = client

    async def notify(self):
        if self.client.data.config.music_notification:
            await self.play_music()

    async def play_music(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, playsound, 'assets/music.mp3')
