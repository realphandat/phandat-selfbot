import discord
import asyncio
import random
import time
import re

class Others:
	def __init__(self, client):
		self.client = client

	def message(self, message, is_owo, in_channel, all_content, any_content):
		if not is_owo or message.author.id == self.client.bot.id:
			if not in_channel or message.channel.id == self.client.data.discord.channel_id:
				if not all_content or all(text in message.content for text in all_content):
					if not any_content or any(text in message.content for text in any_content):
						return True

	async def startup(self):
		try:
			await self.client.bot.create_dm()
			self.client.logger.info(f"Created OwO dm")
		except:
			self.client.logger.error(f"Couldn't create OwO dm")
			pass
		mentioner_id = set(self.client.data.config.history['discord']['target'])
		mentioner_id.add(self.client.user.id)
		self.client.data.discord.mention = ''.join(f"<@{x}>" for x in mentioner_id)
		await self.client.channel.get_channel()
		await self.client.channel.get_nickname()
		if self.client.data.config.get_owo_prefix['mode']:
			await self.get_owo_prefix()
		else:
			self.client.data.discord.prefix = self.client.data.config.get_owo_prefix['default']

	async def intro(self):
		console = f"Start at channel {self.client.data.discord.channel} ({self.client.data.discord.channel_id})"
		webhook = f"{self.client.data.config.emoji['arrow']}<#{self.client.data.discord.channel_id}>"
		if self.client.data.config.sleep_after_certain_time['mode']:
			console = console + f" for {self.client.data.selfbot.work_time} seconds"
			webhook = f"**{self.client.data.config.emoji['arrow']}Work for __{self.client.data.selfbot.work_time}__ seconds**\n" + webhook
		if self.client.data.config.command['mode']:
			webhook = f"**{self.client.data.config.emoji['arrow']}Send `help` or `<@{self.client.user.id}> help`**\n" + webhook
		self.client.logger.info(console)
		await self.client.webhook.send(
			title = f"🚀 STARTED <t:{int(self.client.data.selfbot.turn_on_time)}:R> 🚀",
			description = webhook,
			color = discord.Colour.random()
		)
		self.client.data.selfbot.work_time += time.time()

	async def get_owo_prefix(self):
		await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}prefix")
		self.client.logger.info(f"Sent {self.client.data.discord.prefix}prefix")
		self.client.data.stat.sent_message += 1
		try:
			owo_prefix_message = await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [], ['the current prefix', 'no prefix']), timeout = 10)
			if 'the current prefix' in owo_prefix_message.content:
				self.client.data.discord.prefix = re.findall(r"`(.*?)`", owo_prefix_message.content)[0]
			if "no prefix" in owo_prefix_message.content:
				self.client.logger.info(f"Server has no prefix")
			self.client.logger.info(f"OwO prefix is currently {self.client.data.discord.prefix}")
		except asyncio.TimeoutError:
			self.client.logger.error(f"Couldn't get OwO prefix ({self.client.data.discord.prefix})")

	async def check_owo_status(self):
		if self.client.data.available.selfbot:
			async for message in self.client.data.discord.channel.history(limit = 10):
				if self.client.others.message(message, True, True, [], []):
					break
			else:
				command = random.choice(self.client.data.config.check_owo_status['message'])
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{command}")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}{command}")
				self.client.data.stat.sent_message += 1
				try:
					await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [], []), timeout = 10)
				except asyncio.TimeoutError:
					self.client.logger.warning(f"!!! OwO doesn't respond !!!")
					self.client.logger.info(f"Wait for {self.client.data.config.check_owo_status['wait_time']} seconds")
					await self.client.webhook.send(
						content = self.client.data.discord.mention,
						title = "**💀 OWO'S OFFLINE 💀**",
						description = f"**{self.client.data.config.emoji['arrow']}Wait for {self.client.data.config.check_owo_status['wait_time']} seconds**",
						color = discord.Colour.random()
					)
					self.client.data.available.selfbot = False
					await asyncio.sleep(int(self.client.data.config.check_owo_status['wait_time']))
					self.client.data.available.selfbot = True