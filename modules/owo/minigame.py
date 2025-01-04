import asyncio
import time
import datetime

class Minigame:
	def __init__(self, client):
		self.client = client

	async def pray(self, user_id):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}pray {user_id}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}pray {user_id}")
			self.client.data.stat.sent_message += 1

	async def curse(self, user_id):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}curse {user_id}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}curse {user_id}")
			self.client.data.stat.sent_message += 1

	async def send_run(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}run")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}run")
			self.client.data.stat.sent_message += 1
			try:
				await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, ['tired to run'], []), timeout = 10)
				run_again = self.client.daily.reset_time()
				self.client.data.cooldown.others_minigame = run_again + time.time()
				self.client.logger.info(f"Run for today is over ({datetime.timedelta(seconds = run_again)})")
				self.client.data.checking.run_limit = True
			except asyncio.TimeoutError:
				pass

	async def send_pup(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}pup")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}pup")
			self.client.data.stat.sent_message += 1
			try:
				await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, ['no puppies'], []), timeout = 10)
				pup_again = self.client.daily.reset_time()
				self.client.data.cooldown.others_minigame = pup_again + time.time()
				self.client.logger.info(f"Pup for today is over ({datetime.timedelta(seconds = pup_again)})")
				self.client.data.checking.pup_limit = True
			except asyncio.TimeoutError:
				pass

	async def send_piku(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}piku")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}piku")
			self.client.data.stat.sent_message += 1
			try:
				await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, ['out of carrots'], []), timeout = 10)
				piku_again = self.client.daily.reset_time()
				self.client.data.cooldown.others_minigame = piku_again + time.time()
				self.client.logger.info(f"Piku for today is over ({datetime.timedelta(seconds = piku_again)})")
				self.client.data.checking.piku_limit = True
			except asyncio.TimeoutError:
				pass

	async def buy_common_ring(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}buy 1")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}buy 1")
			self.client.data.stat.sent_message += 1