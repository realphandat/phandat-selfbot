import random
import requests
import re
from functools import reduce

class Grind:
	def __init__(self, client):
		self.client = client

	async def send_owo(self):
		if self.client.data.available.selfbot:
			say = random.choice(self.client.data.config.grind['owo']['message'])
			await self.client.data.discord.channel.send(say)
			self.client.logger.info(f"Sent {say}")
			self.client.data.stat.sent_message += 1

	async def send_hunt(self):
		if self.client.data.available.selfbot:
			say = random.choice(self.client.data.config.grind['hunt']['message'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{say}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}{say}")
			self.client.data.stat.sent_message += 1

	async def send_battle(self):
		if self.client.data.available.selfbot:
			say = random.choice(self.client.data.config.grind['battle']['message'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{say}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}{say}")
			self.client.data.stat.sent_message += 1

	async def send_quote(self):
		if self.client.data.available.selfbot:
			try:
				response = requests.get(self.client.data.config.grind['quote']['api'])
				if response.status_code == 200:
					json_data = response.json()
					quote = reduce(lambda d, p: d[int(p) if p.isdigit() else p.strip("'")], re.findall(r'\[(.*?)\]', self.client.data.config.grind['quote']['path']), json_data)
					await self.client.data.discord.channel.send(f"`{quote}`")
					self.client.logger.info(f"Sent {quote[0:30]}...")
					self.client.data.stat.sent_message += 1
			except requests.exceptions.ConnectionError:
				self.client.logger.error(f"Couldn't connect {self.client.data.config.grind['quote']['api']}")