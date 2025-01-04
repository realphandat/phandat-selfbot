import os

class Notification:
	def __init__(self, client):
		self.client = client
	
	async def notify(self):
		if self.client.data.config.notification['play_music']['mode']:
			await self.play_music()

	async def play_music(self):
		try:
			os.startfile(os.path.dirname(__file__) + self.client.data.config.notification['play_music']['directory'])
			self.client.logger.info(f"Played music")
		except:
			self.client.logger.error(f"Couldn't play music")
			pass