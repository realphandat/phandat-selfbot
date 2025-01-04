import asyncio
import re
import random
import time
import datetime

class Gem:
	def __init__(self, client):
		self.client = client
	
	async def check_empty_gem(self, message):
		if self.client.data.available.selfbot and self.client.others.message(message, True, True, [str(self.client.data.discord.nickname), '🌱', 'gained'], []):
			empty_gem = []
			if not "gem1" in message.content and "gem1" in self.client.data.discord.inventory:
				empty_gem.append("gem1")
			if not "gem3" in message.content and "gem3" in self.client.data.discord.inventory:
				empty_gem.append("gem3")
			if not "gem4" in message.content and "gem4" in self.client.data.discord.inventory:
				empty_gem.append("gem4")
			if not "star" in message.content and "star" in self.client.data.discord.inventory and self.client.data.config.use_gem['star'] and self.client.data.available.special_pet:
				empty_gem.append("star")
			return empty_gem

	async def use_gem(self, empty_gem):
		await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}inv")
		self.client.logger.info(f"Sent {self.client.data.discord.prefix}inv")
		self.client.data.stat.sent_message += 1
		try:
			inv = await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [f'{str(self.client.data.discord.nickname)}\'s Inventory'], []), timeout = 10)
			self.client.data.discord.inventory = inv.content
			inv = [int(item) for item in re.findall(r"`(.*?)`", inv.content) if item.isnumeric()]
			if self.client.data.available.selfbot and self.client.data.config.use_gem['open_box'] and 50 in inv:
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}lb all")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}lb all")
				self.client.data.stat.sent_message += 1
				await asyncio.sleep(random.randint(2, 3))
			if self.client.data.available.selfbot and self.client.data.config.use_gem['open_crate'] and 100 in inv:
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}wc all")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}wc all")
				self.client.data.stat.sent_message += 1
				await asyncio.sleep(random.randint(2, 3))
			if self.client.data.available.selfbot and self.client.data.config.use_gem['open_flootbox'] and 49 in inv:
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}lb f")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}lb f")
				self.client.data.stat.sent_message += 1
				await asyncio.sleep(random.randint(2, 3))
			gem_in_inv = None
			if self.client.data.config.use_gem['sort'].lower() == "min":
				gem_in_inv = [sorted([gem for gem in inv if range[0] < gem < range[1]]) for range in [(50, 58), (64, 72), (71, 79), (78, 86)]]
			else:
				gem_in_inv = [sorted([gem for gem in inv if range[0] < gem < range[1]], reverse = True) for range in [(50, 58), (64, 72), (71, 79), (78, 86)]]
			if gem_in_inv == [[], [], [], []]:
				self.client.logger.info(f"Inventory doesn't have enough gem")
				self.client.data.checking.no_gem = True
				return
			use_gem = ""
			if "gem1" in empty_gem and gem_in_inv[0] != []:
				use_gem = use_gem + str(gem_in_inv[0][0]) + " "
			if "gem3" in empty_gem and gem_in_inv[1] != []:
				use_gem = use_gem + str(gem_in_inv[1][0]) + " "
			if "gem4" in empty_gem and gem_in_inv[2] != []:
				use_gem = use_gem + str(gem_in_inv[2][0]) + " "
			if "star" in empty_gem and gem_in_inv[3] != []:
				use_gem = use_gem + str(gem_in_inv[3][0]) + " "
			if not use_gem:
				return
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}use {use_gem}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}use {use_gem}")
			self.client.data.stat.sent_message += 1
			self.client.data.stat.used_gem += 1
			self.client.data.checking.no_gem = False
			try:
				await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [str(self.client.data.discord.nickname), 'active Special gem or you do not own'], []), timeout = 10)
				self.client.data.available.special_pet = False
			except asyncio.TimeoutError:
				pass
		except asyncio.TimeoutError:
			self.client.logger.error(f"Couldn't get inventory")

	async def check_glitch(self):
		if self.client.data.available.selfbot and self.client.data.cooldown.glitch - time.time() <= 0:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}dt")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}dt")
			self.client.data.stat.sent_message += 1
			try:
				glitch_message = await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [], ['are available', 'not available']), timeout = 10)
				if "are available" in glitch_message.content:
					glitch_end = re.findall("[0-9]+", re.findall(r"\*\*(.*?)\*\*", glitch_message.content)[2])
					if len(glitch_end) == 1:
						glitch_end = int(glitch_end[0])
					elif len(glitch_end) == 2:
						glitch_end = int(int(glitch_end[0]) * 60 + int(glitch_end[1]))
					elif len(glitch_end) == 3:
						glitch_end = int(int(glitch_end[0]) * 3600 + int(glitch_end[1]) * 60 + int(glitch_end[2]))
					self.client.data.cooldown.glitch = glitch_end + time.time()
					self.client.logger.info(f"Glitch is available ({datetime.timedelta(seconds = glitch_end)})")
				elif "not available" in glitch_message.content:
					self.client.logger.info(f"Glitch isn't available")
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get glitch message")

	def glitch_available(self):
		return self.client.data.config.use_gem['use_gem_when_glitch_available'] and not (self.client.data.cooldown.glitch - time.time() <= 0) and self.client.data.current_task_loop.check_glitch > 0