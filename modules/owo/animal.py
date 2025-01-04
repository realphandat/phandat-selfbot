import discord
import re

class Animal:
	def __init__(self, client):
		self.client = client

	async def check_caught_animal(self, message):
		if self.client.data.available.selfbot and self.client.others.message(message, True, True, [str(self.client.data.discord.nickname), '🌱', 'gained'], []):
			animals = message.content.split("**|**")[0]
			for tier in self.client.data.config.notify_caught_animal['tier']:
				x = self.client.data.config.notify_caught_animal['tier'][tier]
				if x['mode'] and any(animal in animals for animal in x['name']):
						await self.notify_caught_animal(message, x['emoji'])

	async def notify_caught_animal(self, message, emoji):
		tier = re.findall(r":(.*?):", emoji)[0]
		self.client.logger.info(f"Found {tier.capitalize()} pet")
		await self.client.webhook.send(
			title = f"{emoji} {tier.upper()} PET {emoji}",
			description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
			color = discord.Colour.random()
		)

	async def sell_sac_animal(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{self.client.data.config.sell_sac_animal['type']} {self.client.data.config.sell_sac_animal['rank']}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}{self.client.data.config.sell_sac_animal['type']} {self.client.data.config.sell_sac_animal['rank']}")
			self.client.data.stat.sent_message += 1