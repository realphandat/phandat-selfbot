import re
import random
import asyncio
import aiohttp
import time
import datetime

class Quest:
	def __init__(self, client):
		self.client = client

	def single_quest(self, quest):
		if re.findall(r"Say 'owo' [0-9]+ times!", quest):
			return True
		if re.findall(r"[0-9]+ xp from hunting and battling!", quest):
			return True
		if re.findall(r"Manually hunt [0-9]+ times!", quest):
			return True
		if re.findall(r"Hunt [0-9]+ animals that are (.*?) rank!", quest):
			return True
		if re.findall(r"Battle [0-9]+ times!", quest):
			return True
		if re.findall(r"Gamble [0-9]+ times!", quest):
			return True
		if re.findall(r"Use an action command on someone [0-9]+ times!", quest):
			return True

	async def quest_progress(self, message):
		if self.client.data.checking.doing_quest and self.client.others.message(message, True, False, [f'You finished a quest and earned: {self.client.data.discord.quest[1]}!'], []):
			self.client.logger.info(f"Finished {self.client.data.discord.quest[0]} and earned {self.client.data.discord.quest[1]}")
			self.client.data.stat.done_quest += 1
			self.client.data.checking.doing_quest = False
			self.client.data.quest.owo = False
			self.client.data.quest.hunt = False
			self.client.data.quest.battle = False
			self.client.data.quest.gamble = False
			self.client.data.quest.action_someone = False
			self.client.data.quest.battle_friend = False
			self.client.data.quest.cookie = False
			self.client.data.quest.pray = False
			self.client.data.quest.curse = False
			self.client.data.quest.action_you = False

	async def do_quest(self):
		if self.client.data.available.selfbot and self.client.data.config.do_quest['mode']:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}q")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}q")
			self.client.data.stat.sent_message += 1
			try:
				quest_message = await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [], []) and message.embeds and message.embeds[0].description and f"These quests belong to <@{self.client.user.id}>" in message.embeds[0].description, timeout = 10)
				if "You finished all of your quests" in quest_message.embeds[0].description:
					self.client.data.available.quest = False
					next_quest = self.client.daily.reset_time()
					self.client.data.cooldown.quest = next_quest + time.time()
					self.client.logger.info(f"Finished all quests ({datetime.timedelta(seconds = next_quest)})")
				else:
					tasks = re.findall(r"\*\*[1-3]. (.*?)\*\*", quest_message.embeds[0].description)
					rewards = re.findall(r"<:blank:427371936482328596>\`‣ Reward:\` (.*?)\n<:blank:427371936482328596>", quest_message.embeds[0].description)
					quests = [list(x) for x in zip(tasks, rewards)]

					if len(self.client.Clients) == 1:
						for quest in quests:
							if self.single_quest(quest[0]):
								self.client.data.discord.quest = quest
								break
						else:
							self.client.data.available.quest = False
							retry_quest = self.client.daily.reset_time()
							self.client.data.cooldown.quest = retry_quest + time.time()
							self.client.logger.warning(f"Don't have multi clients to do couple quest ({datetime.timedelta(seconds = retry_quest)})")
							return
					else:
						self.client.data.discord.quest = quests[0]

					if "<:weaponshard:655902978712272917>" in self.client.data.discord.quest[1]:
						reward = self.client.data.discord.quest[1].split(" ")
						reward = f"{reward[1]}**x{reward[0]}**"
						self.client.data.discord.quest[1] = reward

					self.client.data.checking.doing_quest = True
					self.client.logger.info(f"{self.client.data.discord.quest[0]} ({self.client.data.discord.quest[1]})")
					if re.findall(r"Say 'owo' [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.owo = True
						if self.client.data.config.do_quest['safe']:
							self.client.data.quest.hunt = True
							self.client.data.quest.battle = True
					elif re.findall(r"[0-9]+ xp from hunting and battling!", self.client.data.discord.quest[0]):
						self.client.data.quest.hunt = True
						self.client.data.quest.battle = True
						if self.client.data.config.do_quest['safe']:
							self.client.data.quest.owo = True
					elif re.findall(r"Hunt [0-9]+ animals that are (.*?) rank!", self.client.data.discord.quest[0]):
						self.client.data.quest.hunt = True
						if self.client.data.config.do_quest['safe']:
							self.client.data.quest.owo = True
							self.client.data.quest.battle = True
					elif re.findall(r"Manually hunt [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.hunt = True
						if self.client.data.config.do_quest['safe']:
							self.client.data.quest.owo = True
							self.client.data.quest.battle = True
					elif re.findall(r"Battle [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.battle = True
						if self.client.data.config.do_quest['safe']:
							self.client.data.quest.owo = True
							self.client.data.quest.hunt = True
					elif re.findall(r"Gamble [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.gamble = True
					elif re.findall(r"Use an action command on someone [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.action_someone = True
						while self.client.data.quest.action_someone:
							await self.action_someone()
							await asyncio.sleep(5)

					elif re.findall(r"Battle with a friend [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.battle_friend = True
						while self.client.data.quest.battle_friend:
							for client in self.client.Clients:
								if client.user.id == self.client.user.id:
									continue
								client.data.checking.block_battle = True
								await self.battle_friend(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.battle_friend:
									break
							await asyncio.sleep(15)
						for client in self.client.Clients:
							client.data.checking.block_battle = False

					elif re.findall(r"Receive a cookie from [0-9]+ friends!", self.client.data.discord.quest[0]):
						self.client.data.quest.cookie = True
						while self.client.data.quest.cookie:
							for client in self.client.Clients:
								if client.user.id == self.client.user.id:
									continue
								await self.cookie(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.cookie:
									break
							cookie_again = self.client.daily.reset_time()
							self.client.logger.info(f"Give cookie after {datetime.timedelta(seconds = cookie_again)}")
							await asyncio.sleep(cookie_again)

					elif re.findall(r"Have a friend pray to you [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.pray = True
						while self.client.data.quest.pray:
							for client in self.client.Clients:
								if client.user.id == self.client.user.id:
									continue
								client.data.checking.block_pray_curse = True
								await self.pray(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.pray:
									break
							await asyncio.sleep(300)
						for client in self.client.Clients:
							client.data.checking.block_pray_curse = False

					elif re.findall(r"Have a friend curse you [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.curse = True
						while self.client.data.quest.curse:
							for client in self.client.Clients:
								if client.user.id == self.client.user.id:
									continue
								client.data.checking.block_pray_curse = True
								await self.curse(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.curse:
									break
							await asyncio.sleep(300)
						for client in self.client.Clients:
							client.data.checking.block_pray_curse = False

					elif re.findall(r"Have a friend use an action command on you [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.action_you = True
						while self.client.data.quest.action_you:
							for client in self.client.Clients:
								if client.user.id == self.client.user.id:
									continue
								await self.action_you(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.action_you:
									break
							await asyncio.sleep(5)
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get quest message")

	async def send_message(self, token, channel_id, content):
		async with aiohttp.ClientSession() as session:
			try:
				async with session.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers = {"Authorization": token}, json = {"content": content}, timeout = 10) as res:
					if res.status != 200:
						self.client.logger.error(f"Couldn't send message ({res.status_code}) | {token} | {channel_id}")
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't send message (TimeoutError)")
			except aiohttp.ClientConnectionError:
				self.client.logger.error(f"Couldn't send message (ClientConnectionError)")

	async def action_someone(self):
		if self.client.data.available.selfbot:
			action = random.choice(self.client.data.config.do_quest['action'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{action} <@{self.client.bot.id}>")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}{action} <@{self.client.bot.id}>")
			self.client.data.stat.sent_message += 1

	async def battle_friend(self, client):
		if client.data.available.selfbot:
			channel = random.choice(self.client.data.config.do_quest['channel_id'])
			content = f"owob <@{self.client.user.id}>"
			member = await self.client.get_channel(channel).guild.fetch_member(client.user.id)
			nickname = member.nick if member.nick else member.display_name
			await self.send_message(client.data.config.token, channel, content)
			client.logger.info(f"Sent {content}")
			client.data.stat.sent_message += 1
			try:
				battle_message = await self.client.wait_for("message", check = lambda message: message.channel.id == channel and ((self.client.others.message(message, True, False, [f'<@{self.client.user.id}>'], []) and message.embeds and "owo ab" in message.embeds[0].description) or self.client.others.message(message, True, False, ['🚫', 'There is already a pending battle!', str(nickname)], [])), timeout = 10)
				if self.client.others.message(battle_message, True, False, ['🚫', 'There is already a pending battle!', str(nickname)], []):
					self.client.logger.warning(f"There is already a pending battle, retry after 10 minutes")
					await asyncio.sleep(600)
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get battle message from {client.user.name}")

	async def cookie(self, client):
		if client.data.available.selfbot:
			channel = random.choice(self.client.data.config.do_quest['channel_id'])
			content = f"owocookie {self.client.user.id}"
			await self.send_message(client.data.config.token, channel, content)
			client.logger.info(f"Sent {content}")
			client.data.stat.sent_message += 1

	async def pray(self, client):
		if client.data.available.selfbot:
			channel = random.choice(self.client.data.config.do_quest['channel_id'])
			content = f"owopray {self.client.user.id}"
			await self.send_message(client.data.config.token, channel, content)
			client.logger.info(f"Sent {content}")
			client.data.stat.sent_message += 1

	async def curse(self, client):
		if client.data.available.selfbot:
			channel = random.choice(self.client.data.config.do_quest['channel_id'])
			content = f"owocurse {self.client.user.id}"
			await self.send_message(client.data.config.token, channel, content)
			client.logger.info(f"Sent {content}")
			client.data.stat.sent_message += 1

	async def action_you(self, client):
		if client.data.available.selfbot:
			action = random.choice(self.client.data.config.do_quest['action'])
			channel = random.choice(self.client.data.config.do_quest['channel_id'])
			content = f"owo{action} <@{self.client.user.id}>"
			await self.send_message(client.data.config.token, channel, content)
			client.logger.info(f"Sent {content}")
			client.data.stat.sent_message += 1