import aiohttp
import datetime
import discord

class Webhook:
	def __init__(self, client):
		self.client = client
		
	async def send(self, content = None, title = None, description = None, color = None, image = None, thumnail = None):
		if self.client.data.config.history['discord']['mode']:
			try:
				async with aiohttp.ClientSession() as session:
					webhook = discord.Webhook.from_url(self.client.data.config.history['discord']['webhook_url'], session = session)
					if title:
						embed = discord.Embed(title = title, description = description, color = color)
						embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar)
						if image:
							embed.set_image(url = image)
						if thumnail:
							embed.set_thumbnail(url = thumnail)
						embed.timestamp = datetime.datetime.now()
						embed.set_footer(text = self.client.bot, icon_url = self.client.bot.avatar)
						await webhook.send(content = content, embed = embed)
					else:
						await webhook.send(content = content)
			except discord.errors.HTTPException:
				self.client.logger.error(f"Invalid webhook url")
				pass