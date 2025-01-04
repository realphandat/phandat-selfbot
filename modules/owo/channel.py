import discord
import random

class Channel:
	def __init__(self, client):
		self.client = client

	async def get_nickname(self):
		member = await self.client.data.discord.channel.guild.fetch_member(self.client.user.id)
		nickname = member.nick if member.nick else member.display_name
		self.client.data.discord.nickname = nickname

	async def get_channel(self):
		self.client.data.discord.channel_id = int(random.choice(self.client.data.config.channel['id_list']))
		self.client.data.discord.channel = self.client.get_channel(self.client.data.discord.channel_id)

	async def change_channel(self):
		if self.client.data.available.selfbot and len(self.client.data.config.channel['id_list']) > 1:
			await self.get_channel()
			await self.get_nickname()
			if self.client.data.config.get_owo_prefix['mode']:
				await self.client.others.get_owo_prefix()
			else:
				self.client.data.discord.prefix = self.client.data.config.get_owo_prefix['default']
			self.client.logger.info(f"Changed channel to {self.client.data.discord.channel} ({self.client.data.discord.channel_id})")
			await self.client.webhook.send(
				title = "🏠 CHANGED CHANNEL 🏠",
				description = f"{self.client.data.config.emoji['arrow']}<#{self.client.data.discord.channel_id}>",
				color = discord.Colour.random()
			)
			self.client.data.stat.changed_channel += 1

	async def change_when_be_mentioned(self, message):
		if self.client.data.available.selfbot and message.mentions and not message.author.bot and self.client.others.message(message, False, True, [], []):
			if message.mentions[0].id == self.client.user.id or f"<@{self.client.user.id}>" in message.content:
				self.client.logger.info(f"Someone mentions")
				await self.client.webhook.send(
					title = "🏷️ SOMEONE MENTIONS 🏷️",
					description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
					color = discord.Colour.random()
				)
				await self.change_channel()

	async def change_when_be_challenged(self, message):
		if self.client.data.available.selfbot and self.client.others.message(message, True, False, [f'<@{self.client.user.id}>'], []) and message.embeds and "owo ab" in message.embeds[0].description:
			self.client.logger.info(f"Someone challenges")
			await self.client.webhook.send(
				title = "🥊 SOMEONE CHALLENGES 🥊",
				description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
				color = discord.Colour.random()
			)
			choice = random.choice([1, 2])
			if choice == 1:
				if self.client.others.message(message, False, True, [], []):
					await message.channel.send(f"{self.client.data.discord.prefix}ab")
					self.client.logger.info(f"Sent {self.client.data.discord.prefix}ab")
				else:
					await message.channel.send(f"owoab")
					self.client.logger.info(f"Sent owoab")
				self.client.data.stat.sent_message += 1
			if choice == 2:
				button = message.components[0].children[0]
				await button.click()
				self.client.logger.info(f"Clicked accept button")