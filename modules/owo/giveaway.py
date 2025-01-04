import discord

class Giveaway:
	def __init__(self, client):
		self.client = client

	async def join_owo_giveaway(self, message):
		if message.channel.id not in self.client.data.config.join_owo_giveaway['server_id_blacklist'] and message.id not in self.client.data.discord.ga_joined and self.client.others.message(message, True, False, [], []) and message.embeds and "New Giveaway" in str(message.embeds[0].author.name) and len(message.components) > 0:
			try:
				button = message.components[0].children[0]
				await button.click()
				self.client.data.discord.ga_joined.append(message.id)
				await self.client.webhook.send(
					title = "🎁 JOINED GIVEAWAY 🎁",
					description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
					color = discord.Colour.random()
				)
				self.client.logger.info(f"Joined A New Giveaway ({message.id})")
			except Exception as e:
				if "COMPONENT_VALIDATION_FAILED" in str(e):
					self.client.data.discord.ga_joined.append(message.id)
				pass