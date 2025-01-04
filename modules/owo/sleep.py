import discord
import asyncio
import random
import time

class Sleep:
	def __init__(self, client):
		self.client = client

	async def sleep_after_certain_time(self, skip = False):
		if self.client.data.available.selfbot and ((self.client.data.selfbot.work_time - time.time() <= 0) or skip):
			sleep = random.randint(int(self.client.data.config.sleep_after_certain_time['sleep']['min']), int(self.client.data.config.sleep_after_certain_time['sleep']['max']))
			self.client.logger.info(f"Sleep for {sleep} Seconds")
			await self.client.webhook.send(
				title = "🛌 SLEEP 🛌",
				description = f"**{self.client.data.config.emoji['arrow']}Sleep for __{sleep}__ seconds**",
				color = discord.Colour.random()
			)
			self.client.data.available.selfbot = False
			await asyncio.sleep(sleep)
			if not self.client.data.checking.pause:
				work = random.randint(int(self.client.data.config.sleep_after_certain_time['work']['min']), int(self.client.data.config.sleep_after_certain_time['work']['max']))
				self.client.data.selfbot.work_time = work + time.time()
				self.client.logger.info(f"Done! Work for {work} seconds")
				await self.client.webhook.send(
					title = "🌄 CONTINUE 🌄",
					description = f"**{self.client.data.config.emoji['arrow']}Work for __{work}__ seconds**",
					color = discord.Colour.random()
				)
				self.client.data.available.captcha = False
				self.client.data.available.selfbot = True
				self.client.data.stat.slept += 1