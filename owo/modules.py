import discord
import asyncio
import aiohttp
import random
import re
import os
import io
import glob
import numpy
import time
import base64
import datetime
import requests

from requests import get
from aiohttp import ClientSession, CookieJar
from PIL import Image
from twocaptcha import TwoCaptcha

class Modules:
	def __init__(self, client):
		self.client = client

	async def startup(self):
		mentioner_id = set(self.client.data.config.webhook['mentioner_id'])
		mentioner_id.add(self.client.user.id)
		self.client.data.discord.mention = ''.join(f"<@{x}>" for x in mentioner_id)
		await self.get_channel()
		await self.get_nickname()
		if self.client.data.config.get_owo_prefix['mode']:
			await self.get_owo_prefix()
		else:
			self.client.data.discord.prefix = self.client.data.config.get_owo_prefix['default']

	async def intro(self):
		console = f"Start at channel {self.client.data.discord.channel} ({self.client.data.discord.channel_id})"
		webhook = f"{self.client.data.emoji.arrow}<#{self.client.data.discord.channel_id}>"
		if self.client.data.config.sleep:
			console = console + f" for {self.client.data.selfbot.work_time} seconds"
			webhook = f"**{self.client.data.emoji.arrow}Work for __{self.client.data.selfbot.work_time}__ seconds**\n" + webhook
		if self.client.data.config.command['mode']:
			webhook = f"**{self.client.data.emoji.arrow}Send `help` or `<@{self.client.user.id}> help`**\n" + webhook
		self.client.logger.info(console)
		await self.client.webhooks.send(
			title = f"🚀 STARTED <t:{int(self.client.data.selfbot.turn_on_time)}:R> 🚀",
			description = webhook,
			color = discord.Colour.random()
		)
		self.client.data.selfbot.work_time += time.time()

	async def get_owo_prefix(self):
		await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}prefix")
		self.client.logger.info(f"Sent {self.client.data.discord.prefix}prefix")
		self.client.data.stat.command += 1
		try:
			owo_prefix_message = await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, ['the current prefix'], []), timeout = 10)
			self.client.data.discord.prefix = re.findall(r"`(.*?)`", owo_prefix_message.content)[0]
			self.client.logger.info(f"OwO prefix is currently {self.client.data.discord.prefix}")
		except asyncio.TimeoutError:
			self.client.logger.error(f"Couldn't get OwO prefix ({self.client.data.discord.prefix})")

	async def get_channel(self):
		self.client.data.discord.channel_id = int(random.choice(self.client.data.config.channel_id))
		self.client.data.discord.channel = self.client.get_channel(self.client.data.discord.channel_id)

	async def get_nickname(self):
		member = await self.client.data.discord.channel.guild.fetch_member(self.client.user.id)
		nickname = member.nick if member.nick else member.display_name
		self.client.data.discord.nickname = nickname

	async def check_owo_status(self):
		if self.client.data.available.selfbot:
			async for message in self.client.data.discord.channel.history(limit = 10):
				if self.client.conditions.message(message, True, True, [], []):
					break
			else:
				command = random.choice(['h', 'hunt', 'b', 'battle'])
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{command}")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}{command}")
				self.client.data.stat.command += 1
				try:
					await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [], []), timeout = 10)
				except asyncio.TimeoutError:
					self.client.logger.warning(f"!!! OwO doesn't respond !!!")
					self.client.logger.info(f"Wait for 30 minutes")
					await self.client.webhooks.send(
						content = self.client.data.discord.mention,
						title = "**💀 OWO'S OFFLINE 💀**",
						description = f"**{self.client.data.emoji.arrow}Wait for 30 minutes**",
						color = discord.Colour.random()
					)
					self.client.data.available.selfbot = False
					await asyncio.sleep(1800)
					self.client.data.available.selfbot = True

	async def change_channel(self):
		if self.client.data.available.selfbot and len(self.client.data.config.channel_id) > 1:
			await self.get_channel()
			await self.get_nickname()
			if self.client.data.config.get_owo_prefix['mode']:
				await self.get_owo_prefix()
			else:
				self.client.data.discord.prefix = self.client.data.config.get_owo_prefix['default']
			self.client.logger.info(f"Changed channel to {self.client.data.discord.channel} ({self.client.data.discord.channel_id})")
			await self.client.webhooks.send(
				title = "🏠 CHANGED CHANNEL 🏠",
				description = f"{self.client.data.emoji.arrow}<#{self.client.data.discord.channel_id}>",
				color = discord.Colour.random()
			)
			self.client.data.stat.change_channel += 1

	async def check_twocaptcha_balance(self, twocaptcha_api_keys):
		if self.client.data.available.selfbot and self.client.data.config.image_captcha['mode']:
			enoguh_balance = False
			for api_key in twocaptcha_api_keys:
				twocaptcha = TwoCaptcha(**{
							"server": "2captcha.com",
							"apiKey": str(api_key),
							"defaultTimeout": 300,
							"pollingInterval": 5
				})
				retry_times = 0
				while retry_times < int(self.client.data.config.error_retry_times):
					try:
						balance = twocaptcha.balance()
						if balance >= self.client.data.config.twocaptcha_balance['amount']:
							enoguh_balance = True
							break
						else:
							break
					except Exception as e:
						if str(e) == "ERROR_KEY_DOES_NOT_EXIST" or str(e) == "ERROR_WRONG_USER_KEY":
							break
						else:
							retry_times += 1
							await asyncio.sleep(20)
				if enoguh_balance:
					break
			else:
				await self.client.notification.notify()
				self.client.logger.warning(f"TwoCaptcha API is invalid or has under {self.client.data.config.twocaptcha_balance['amount']}$")
				await self.client.webhooks.send(
					content = self.client.data.discord.mention,
					title = "💸 NOT ENOUGH BALANCE 💸",
					description = f"**{self.client.data.emoji.arrow}TwoCaptcha API is invalid or has under {self.client.data.config.twocaptcha_balance['amount']}$**",
					color = discord.Colour.random()
				)
				self.client.data.available.selfbot = False

	async def do_quest(self):
		if self.client.data.available.selfbot and self.client.data.config.quest['mode']:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}q")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}q")
			self.client.data.stat.command += 1
			try:
				quest_message = await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [], []) and message.embeds and message.embeds[0].description and f"These quests belong to <@{self.client.user.id}>" in message.embeds[0].description, timeout = 10)
				if "You finished all of your quests" in quest_message.embeds[0].description:
					self.client.data.available.quest = False
					next_quest = self.client.conditions.reset_time()
					self.client.data.cooldown.quest = next_quest + time.time()
					self.client.logger.info(f"Finished all quests ({datetime.timedelta(seconds = next_quest)})")
				else:
					tasks = re.findall(r"\*\*[1-3]. (.*?)\*\*", quest_message.embeds[0].description)
					rewards = re.findall(r"<:blank:427371936482328596>\`‣ Reward:\` (.*?)\n<:blank:427371936482328596>", quest_message.embeds[0].description)
					quests = [list(x) for x in zip(tasks, rewards)]

					if len(self.client.OwOClients) == 1:
						for quest in quests:
							if self.client.conditions.single_quest(quest[0]):
								self.client.data.discord.quest = quest
								break
						else:
							self.client.data.available.quest = False
							retry_quest = self.client.conditions.reset_time()
							self.client.data.cooldown.quest = retry_quest + time.time()
							self.client.logger.warning(f"Don't have multi OwO clients to do couple quest ({datetime.timedelta(seconds = retry_quest)})")
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
						if self.client.data.config.quest['safe']:
							self.client.data.quest.hunt = True
							self.client.data.quest.battle = True
					elif re.findall(r"[0-9]+ xp from hunting and battling!", self.client.data.discord.quest[0]):
						self.client.data.quest.hunt = True
						self.client.data.quest.battle = True
						if self.client.data.config.quest['safe']:
							self.client.data.quest.owo = True
					elif re.findall(r"Hunt [0-9]+ animals that are (.*?) rank!", self.client.data.discord.quest[0]):
						self.client.data.quest.hunt = True
						if self.client.data.config.quest['safe']:
							self.client.data.quest.owo = True
							self.client.data.quest.battle = True
					elif re.findall(r"Manually hunt [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.hunt = True
						if self.client.data.config.quest['safe']:
							self.client.data.quest.owo = True
							self.client.data.quest.battle = True
					elif re.findall(r"Battle [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.battle = True
						if self.client.data.config.quest['safe']:
							self.client.data.quest.owo = True
							self.client.data.quest.hunt = True
					elif re.findall(r"Gamble [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.gamble = True
					elif re.findall(r"Use an action command on someone [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.action_someone = True
						while self.client.data.quest.action_someone:
							await self.client.quest.action_someone()
							await asyncio.sleep(5)

					elif re.findall(r"Battle with a friend [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.battle_friend = True
						while self.client.data.quest.battle_friend:
							for client in self.client.OwOClients:
								if client.user.id == self.client.user.id:
									continue
								client.data.checking.block_battle = True
								await self.client.quest.battle_friend(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.battle_friend:
									break
							await asyncio.sleep(15)
						for client in self.client.OwOClients:
							client.data.checking.block_battle = False

					elif re.findall(r"Receive a cookie from [0-9]+ friends!", self.client.data.discord.quest[0]):
						self.client.data.quest.cookie = True
						while self.client.data.quest.cookie:
							for client in self.client.OwOClients:
								if client.user.id == self.client.user.id:
									continue
								await self.client.quest.cookie(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.cookie:
									break
							cookie_again = self.client.conditions.reset_time()
							self.client.logger.info(f"Give cookie after {datetime.timedelta(seconds = cookie_again)}")
							await asyncio.sleep(cookie_again)

					elif re.findall(r"Have a friend pray to you [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.pray = True
						while self.client.data.quest.pray:
							for client in self.client.OwOClients:
								if client.user.id == self.client.user.id:
									continue
								client.data.checking.block_pray_curse = True
								await self.client.quest.pray(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.pray:
									break
							await asyncio.sleep(300)
						for client in self.client.OwOClients:
							client.data.checking.block_pray_curse = False

					elif re.findall(r"Have a friend curse you [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.curse = True
						while self.client.data.quest.curse:
							for client in self.client.OwOClients:
								if client.user.id == self.client.user.id:
									continue
								client.data.checking.block_pray_curse = True
								await self.client.quest.curse(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.curse:
									break
							await asyncio.sleep(300)
						for client in self.client.OwOClients:
							client.data.checking.block_pray_curse = False

					elif re.findall(r"Have a friend use an action command on you [0-9]+ times!", self.client.data.discord.quest[0]):
						self.client.data.quest.action_you = True
						while self.client.data.quest.action_you:
							for client in self.client.OwOClients:
								if client.user.id == self.client.user.id:
									continue
								await self.client.quest.action_you(client)
								await asyncio.sleep(3)
								if not self.client.data.quest.action_you:
									break
							await asyncio.sleep(5)
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get quest message")

	async def claim_daily(self):
		if self.client.data.available.selfbot and int(self.client.data.cooldown.daily) - time.time() <= 0:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}daily")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}daily")
			self.client.data.stat.command += 1
			try:
				daily_message = await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [str(self.client.data.discord.nickname)], ['next daily', 'Nu']), timeout = 10)
				daily_again = self.client.conditions.reset_time()
				self.client.data.cooldown.daily = daily_again + time.time()
				if "next daily" in daily_message.content:
					self.client.logger.info(f"Claimed daily ({datetime.timedelta(seconds = daily_again)})")
				elif "Nu" in daily_message.content:
					self.client.logger.info(f"Couldn't claim daily ({datetime.timedelta(seconds = daily_again)})")
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get daily message")

	async def sleep(self, skip = False):
		if self.client.data.available.selfbot and ((self.client.data.selfbot.work_time - time.time() <= 0) or skip):
			sleep = random.randint(300, 600)
			self.client.logger.info(f"Sleep for {sleep} Seconds")
			await self.client.webhooks.send(
				title = "🛌 SLEEP 🛌",
				description = f"**{self.client.data.emoji.arrow}Sleep for __{sleep}__ seconds**",
				color = discord.Colour.random()
			)
			self.client.data.available.selfbot = False
			await asyncio.sleep(sleep)
			if not self.client.data.checking.pause:
				work = random.randint(600, 1200)
				self.client.data.selfbot.work_time = work + time.time()
				self.client.logger.info(f"Done! Work for {work} seconds")
				await self.client.webhooks.send(
					title = "🌄 CONTINUE 🌄",
					description = f"**{self.client.data.emoji.arrow}Work for __{work}__ seconds**",
					color = discord.Colour.random()
				)
				self.client.data.available.selfbot = True
				self.client.data.stat.sleep += 1

	async def send_owo(self):
		if self.client.data.available.selfbot:
			say = random.choice(self.client.data.cmd.owo)
			await self.client.data.discord.channel.send(say)
			self.client.logger.info(f"Sent {say}")
			self.client.data.stat.command += 1

	async def send_hunt(self):
		if self.client.data.available.selfbot:
			say = random.choice(self.client.data.cmd.hunt)
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{say}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}{say}")
			self.client.data.stat.command += 1

	async def send_battle(self):
		if self.client.data.available.selfbot:
			say = random.choice(self.client.data.cmd.battle)
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{say}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}{say}")
			self.client.data.stat.command += 1

	async def send_quote(self):
		if self.client.data.available.selfbot:
			try:
				url = "https://zenquotes.io/api/random"
				response = get(url)
				if response.status_code == 200:
					json_data = response.json()
					quote = json_data[0]['q']
					await self.client.data.discord.channel.send(f"`{quote}`")
					self.client.logger.info(f"Sent {quote[0:30]}...")
					self.client.data.stat.command += 1
			except requests.exceptions.ConnectionError:
				self.client.logger.error(f"Couldn't connect {url}")

	async def solve_huntbot_captcha(self, captcha):
		checks = []
		check_images = glob.glob("assets/huntbot/**/*.png")
		for check_image in sorted(check_images):
			img = Image.open(check_image)
			checks.append((img, img.size, check_image.split(".")[0].split(os.sep)[-1]))
		async with aiohttp.ClientSession() as session:
			async with session.get(captcha) as resp:
				large_image = Image.open(io.BytesIO(await resp.read()))
				large_array = numpy.array(large_image)

		matches = []
		for img, (small_w, small_h), letter in checks:
			small_array = numpy.array(img)
			mask = small_array[:, :, 3] > 0
			for y in range(large_array.shape[0] - small_h + 1):
				for x in range(large_array.shape[1] - small_w + 1):
					segment = large_array[y:y + small_h, x:x + small_w]
					if numpy.array_equal(segment[mask], small_array[mask]):
						if not any((m[0] - small_w < x < m[0] + small_w) and (m[1] - small_h < y < m[1] + small_h) for m in matches):
							matches.append((x, y, letter))
		matches = sorted(matches, key = lambda tup: tup[0])
		return("".join([i[2] for i in matches]))

	async def claim_submit_huntbot(self):
		if self.client.data.available.selfbot and int(self.client.data.cooldown.huntbot) - time.time() <= 0:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}hb 1d")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}hb 1d")
			self.client.data.stat.command += 1
			try:
				huntbot_message = await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [], ['Please include your password', 'Here is your password!', 'BACK IN', 'BACK WITH']), timeout = 10)
				if self.client.conditions.message(huntbot_message, True, True, [str(self.client.data.discord.nickname), 'Please include your password'], []):
					retry_huntbot = re.findall(r"(?<=Password will reset in )(\d+)", huntbot_message.content)
					retry_huntbot = int(int(retry_huntbot[0]) * 60)
					self.client.data.cooldown.huntbot = retry_huntbot + time.time()
					self.client.logger.info(f"Lost huntbot message, retry after {datetime.timedelta(seconds = retry_huntbot)}")
				elif self.client.data.available.selfbot and self.client.conditions.message(huntbot_message, True, True, [str(self.client.data.discord.nickname), 'Here is your password!'], []):
					await self.client.webhooks.send(
						title = "🤖 HUNTBOT CAPTCHA 🤖",
						description = f"{self.client.data.emoji.arrow}{huntbot_message.jump_url}",
						color = discord.Colour.random(),
						image = huntbot_message.attachments[0]
					)
					answer = await self.solve_huntbot_captcha(huntbot_message.attachments[0].url)
					await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}hb 1d {answer}")
					self.client.logger.info(f"Sent {self.client.data.discord.prefix}hb 1d {answer}")
					self.client.data.stat.command += 1
					try:
						huntbot_verification_message = await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [str(self.client.data.discord.nickname)], ['YOU SPENT', 'Wrong password']), timeout = 10)
						if "YOU SPENT" in huntbot_verification_message.content:
							self.client.logger.info(f"Submitted huntbot successfully")
							await self.client.webhooks.send(
								title = "🎉 CORRECT SOLUTION 🎉",
								description = f"**{self.client.data.emoji.arrow}Answer: {answer}**",
								color = discord.Colour.random(),
								thumnail = huntbot_message.attachments[0]
							)
						if "Wrong password" in huntbot_verification_message.content:
							self.client.logger.info(f"Submitted huntbot failed")
							await self.client.webhooks.send(
								title = "🚫 INCORRECT SOLUTION 🚫",
								description = f"**{self.client.data.emoji.arrow}Answer: {answer}**",
								color = discord.Colour.random(),
								thumnail = huntbot_message.attachments[0]
							)
					except asyncio.TimeoutError:
						self.client.logger.error(f"Couldn't get huntbot verification message")
				elif "STILL HUNTING" in huntbot_message.content:
					next_huntbot = re.findall("[0-9]+", re.findall("`(.*?)`", huntbot_message.content)[0])
					if len(next_huntbot) == 1:
						next_huntbot = int(int(next_huntbot[0]) * 60)
					else:
						next_huntbot = int(int(next_huntbot[0]) * 3600 + int(next_huntbot[1]) * 60)
					self.client.data.cooldown.huntbot = next_huntbot + time.time()
					self.client.logger.info(f"Huntbot'll be back in {datetime.timedelta(seconds = next_huntbot)}")
					await self.client.webhooks.send(
						title = "📌 SUBMITTED HUNTBOT 📌",
						description = huntbot_message.content,
						color = discord.Colour.random()
					)
				elif "BACK WITH" in huntbot_message.content:
					self.client.logger.info(f"Claimed huntbot")
					await self.client.webhooks.send(
						title = "📦 CLAIMED HUNTBOT 📦",
						description = huntbot_message.content,
						color = discord.Colour.random()
					)
					self.client.data.stat.huntbot += 1
					if self.client.data.available.selfbot and self.client.data.config.huntbot['upgrade']['mode']:
						await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}upgrade {self.client.data.config.huntbot['upgrade']['type']} all")
						self.client.logger.info(f"Sent {self.client.data.discord.prefix}upgrade {self.client.data.config.huntbot['upgrade']['type']} all")
						self.client.data.stat.command += 1
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get huntbot message")

	async def check_glitch(self):
		if self.client.data.available.selfbot and self.client.data.cooldown.glitch - time.time() <= 0:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}dt")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}dt")
			self.client.data.stat.command += 1
			try:
				glitch_message = await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [], ['are available', 'not available']), timeout = 10)
				if "are available" in glitch_message.content:
					glitch_end = re.findall("[0-9]+", re.findall(r"\*\*(.*?)\*\*", glitch_message.content)[2])
					if len(glitch_end) == 1:
						glitch_end = int(glitch_end[0])
					elif len(glitch_end) == 2:
						glitch_end = int(int(glitch_end[0]) * 60 + int(glitch_end[1]))
					elif len(glitch_end) == 3:
						glitch_end = int(int(glitch_end[0]) * 3600 + int(glitch_end[1]) * 60 + int(glitch_end[2]))
					self.client.data.cooldown.glitch = glitch_end + time.time()
					self.client.logger.info(f"Distorted animals are available ({datetime.timedelta(seconds = glitch_end)})")
				elif "not available" in glitch_message.content:
					self.client.logger.info(f"Distorted animals aren't available")
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get distorted animals message")

	async def sell_sac_animals(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{self.client.data.config.animals['type']} {self.client.data.config.animals['rank']}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}{self.client.data.config.animals['type']} {self.client.data.config.animals['rank']}")
			self.client.data.stat.command += 1

	async def play_slot(self):
		if self.client.data.available.selfbot:
			if self.client.data.current_gamble_bet.slot >= int(self.client.data.config.gamble['slot']['max']):
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}s {self.client.data.current_gamble_bet.slot}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}s {self.client.data.current_gamble_bet.slot}")
			self.client.data.stat.command += 1

	async def play_coinflip(self):
		if self.client.data.available.selfbot:
			if self.client.data.current_gamble_bet.coinflip >= int(self.client.data.config.gamble['coinflip']['max']):
				self.client.data.current_gamble_bet.coinflip = int(self.client.data.config.gamble['coinflip']['bet'])
			side = random.choice(['h', 't'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}cf {self.client.data.current_gamble_bet.coinflip} {side}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}cf {self.client.data.current_gamble_bet.coinflip} {side}")
			self.client.data.stat.command += 1

	async def play_blackjack(self):
		if self.client.data.available.selfbot:
			if self.client.data.current_gamble_bet.blackjack >= int(self.client.data.config.gamble['blackjack']['max']):
				self.client.data.current_gamble_bet.blackjack = int(self.client.data.config.gamble['blackjack']['bet'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}bj {self.client.data.current_gamble_bet.blackjack}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}bj {self.client.data.current_gamble_bet.blackjack}")
			self.client.data.stat.command += 1
			self.client.data.available.blackjack = False
			while not self.client.data.available.blackjack:
				blackjack_message = None
				await asyncio.sleep(random.randint(2, 3))
				async for message in self.client.data.discord.channel.history(limit = 10):
					if self.client.conditions.message(message, True, True, [], []) and message.embeds and str(self.client.user.name) in message.embeds[0].author.name and "play blackjack" in message.embeds[0].author.name:
						blackjack_message = message
						break
				if blackjack_message:
					if "in progress" in blackjack_message.embeds[0].footer.text or "resuming previous" in blackjack_message.embeds[0].footer.text:
						my_blackjack_point = int(re.findall(r"\[(.*?)\]", blackjack_message.embeds[0].fields[1].name)[0])
						if my_blackjack_point <= 17:
							try:
								if blackjack_message.reactions[0].emoji == "👊":
									if blackjack_message.reactions[0].me:
										await blackjack_message.remove_reaction('👊', self.client.user)
									else:
										await blackjack_message.add_reaction('👊')
								else:
									if blackjack_message.reactions[1].me:
										await blackjack_message.remove_reaction('👊', self.client.user)
									else:
										await blackjack_message.add_reaction('👊')
								self.client.logger.info(f"Blackjack turn has {my_blackjack_point} points (Hit)")
							except IndexError:
								pass
						else:
							await blackjack_message.add_reaction('🛑')
							self.client.logger.info(f"Blackjack turn has {my_blackjack_point} points (Stand)")
					elif "You won" in blackjack_message.embeds[0].footer.text:
						self.client.logger.info(f"Blackjack turn won {self.client.data.current_gamble_bet.blackjack} cowoncy")
						self.client.data.stat.gamble += self.client.data.current_gamble_bet.blackjack
						self.client.data.current_gamble_bet.blackjack = int(self.client.data.config.gamble['blackjack']['bet'])
						self.client.data.available.blackjack = True
					elif "You lost" in blackjack_message.embeds[0].footer.text:
						self.client.logger.info(f"Blackjack turn lost {self.client.data.current_gamble_bet.blackjack} cowoncy")
						self.client.data.stat.gamble -= self.client.data.current_gamble_bet.blackjack
						self.client.data.current_gamble_bet.blackjack *= int(self.client.data.config.gamble['blackjack']['rate'])
						self.client.data.available.blackjack = True
					elif "You tied" in blackjack_message.embeds[0].footer.text or "You both bust" in blackjack_message.embeds[0].footer.text:
						self.client.logger.info(f"Blackjack turn draw {self.client.data.current_gamble_bet.blackjack} cowoncy")
						self.client.data.available.blackjack = True
				else:
					break

	async def pray(self, user_id):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}pray {user_id}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}pray {user_id}")
			self.client.data.stat.command += 1

	async def curse(self, user_id):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}curse {user_id}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}curse {user_id}")
			self.client.data.stat.command += 1

	async def send_run(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}run")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}run")
			self.client.data.stat.command += 1
			try:
				await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, ['tired to run'], []), timeout = 10)
				run_again = self.client.conditions.reset_time()
				self.client.data.cooldown.entertainment = run_again + time.time()
				self.client.logger.info(f"Run for today is over ({datetime.timedelta(seconds = run_again)})")
				self.client.data.checking.run_limit = True
			except asyncio.TimeoutError:
				pass

	async def send_pup(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}pup")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}pup")
			self.client.data.stat.command += 1
			try:
				await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, ['no puppies'], []), timeout = 10)
				pup_again = self.client.conditions.reset_time()
				self.client.data.cooldown.entertainment = pup_again + time.time()
				self.client.logger.info(f"Pup for today is over ({datetime.timedelta(seconds = pup_again)})")
				self.client.data.checking.pup_limit = True
			except asyncio.TimeoutError:
				pass

	async def send_piku(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}piku")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}piku")
			self.client.data.stat.command += 1
			try:
				await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, ['out of carrots'], []), timeout = 10)
				piku_again = self.client.conditions.reset_time()
				self.client.data.cooldown.entertainment = piku_again + time.time()
				self.client.logger.info(f"Piku for today is over ({datetime.timedelta(seconds = piku_again)})")
				self.client.data.checking.piku_limit = True
			except asyncio.TimeoutError:
				pass

	async def buy_common_ring(self):
		if self.client.data.available.selfbot:
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}buy 1")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}buy 1")
			self.client.data.stat.command += 1

	async def solve_image_captcha(self, image, captcha, lenghth, wrong_answer):
		result = None
		for api_key in self.client.data.config.image_captcha['twocaptcha']:
			twocaptcha = TwoCaptcha(**{
						"server": "2captcha.com",
						"apiKey": str(api_key),
						"defaultTimeout": 300,
						"pollingInterval": 5
			})
			retry_times = 0
			while retry_times < int(self.client.data.config.error_retry_times):
				try:
					balance = twocaptcha.balance()
					self.client.logger.info(f"TwoCaptcha API ({api_key}) currently have {balance}$")
					result = twocaptcha.normal(captcha, numeric = 2, minLen = lenghth, maxLen = lenghth, phrase = 0, caseSensitive = 0, calc = 0, lang = "en")
					if result['code'].lower() in wrong_answer:
						twocaptcha.report(result['captchaId'], False)
						await self.solve_image_captcha(image, captcha, lenghth, wrong_answer)
					break
				except Exception as e:
					await self.client.webhooks.send(
						content = self.client.data.discord.mention,
						title = "⚙️ TWOCAPTCHA API ⚙️",
						description = f"**{self.client.data.emoji.arrow}Error: {str(e)}**",
						color = discord.Colour.random()
					)
					if str(e) == "ERROR_KEY_DOES_NOT_EXIST" or str(e) == "ERROR_WRONG_USER_KEY":
						self.client.logger.error(f"TwoCaptcha API ({api_key}) is invalid")
						break
					elif str(e) == "ERROR_ZERO_BALANCE":
						self.client.logger.error(f"TwoCaptcha API ({api_key}) ran out of money")
						break
					else:
						self.client.logger.error(f"TwoCaptcha API ({api_key}) has the problem | {e}")
						retry_times += 1
						await asyncio.sleep(20)
			if result:
				break
		else:
			await self.client.notification.notify()
		if result:
			await self.client.data.bot.send(result['code'])
			self.client.logger.info(f"Sent {result['code']}")
			self.client.data.stat.command += 1
			try:
				captcha_verification = await self.client.wait_for("message", check = lambda message: message.channel.id == self.client.data.bot.dm_channel.id and any(text in message.content for text in ['👍', '🚫']), timeout = 10)
				if "👍" in captcha_verification.content:
					self.client.logger.info(f"Solved Image Captcha successfully")
					await self.client.webhooks.send(
						title = "👍 CORRECT SOLUTION 👍",
						description = f"**{self.client.data.emoji.arrow}Answer: {result['code']}**",
						color = discord.Colour.random(),
						thumnail = image
					)
					twocaptcha.report(result['captchaId'], True)
					self.client.data.stat.captcha += 1
					self.client.data.available.captcha = False
					self.client.data.available.selfbot = True
					self.client.data.checking.captcha_attempts = 0
					if self.client.data.config.image_captcha['sleep_after_solve']:
						await self.sleep(True)
				elif "🚫" in captcha_verification.content:
					self.client.logger.info(f"Solved Image Captcha failed")
					await self.client.webhooks.send(
						content = self.client.data.discord.mention,
						title = "🚫 INCORRECT SOLUTION 🚫",
						description = f"**{self.client.data.emoji.arrow}Answer: {result['code']}**",
						color = discord.Colour.random(),
						thumnail = image
					)
					twocaptcha.report(result['captchaId'], False)
					self.client.data.checking.captcha_attempts += 1
					if self.client.data.checking.captcha_attempts < int(self.client.data.config.image_captcha['attempts']):
						wrong_answer.append(result['code'].lower())
						await self.solve_image_captcha(image, captcha, lenghth, wrong_answer)
					else:
						await self.client.notification.notify()
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get captcha verification message")
				await self.client.notification.notify()

	async def submit_oauth(self, res):
		retry_times = 0
		while retry_times < int(self.client.data.config.error_retry_times):
			response = await res.json()
			locauri = response.get("location")
			headers = {
				"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.5", "connection": "keep-alive",
				"host": "owobot.com",
				"referer": "https://discord.com/", "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "cross-site", "sec-fetch-user": "?1", "upgrade-insecure-requests": "1", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"
			}
			session = ClientSession(cookie_jar=CookieJar())
			async with session.get(locauri, headers=headers, allow_redirects=False) as res2:
				if res2.status in (302, 307):
					return session
				else:
					self.client.logger.error(f"Failed to add token to HCaptcha oauth | {res2.status}")
					await self.client.webhooks.send(
						content = self.client.data.discord.mention,
						title = "⚙️ SUMBIT HCAPTCHA OAUTH ⚙️",
						description = f"**{self.client.data.emoji.arrow}Error: {res2.status}**",
						color = discord.Colour.random()
					)
			retry_times += 1
			await asyncio.sleep(20)
		else:
			await self.client.notification.notify()

	async def get_oauth(self):
		retry_times = 0
		while retry_times < int(self.client.data.config.error_retry_times):
			async with ClientSession() as session:
				oauth = f"https://discord.com/api/v9/oauth2/authorize?response_type=code&redirect_uri=https%3A%2F%2Fowobot.com%2Fapi%2Fauth%2Fdiscord%2Fredirect&scope=identify%20guilds%20email%20guilds.members.read&client_id={self.client.data.bot.id}"
				payload = {"permissions": "0", "authorize": True}
				headers = {
					'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
					'Accept': '*/*',
					'Accept-Language': 'en-US,en;q=0.5',
					'Accept-Encoding': 'gzip, deflate, br',
					'Content-Type': 'application/json',
					'Authorization': self.client.data.config.token,
					'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEwOS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzExMS4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTExLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTg3NTk5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
					'X-Debug-Options': 'bugReporterEnabled',
					'Origin': 'https://discord.com',
					'Connection': 'keep-alive',
					'Referer': f"https://discord.com//oauth2/authorize?response_type=code&redirect_uri=https%3A%2F%2Fowobot.com%2Fapi%2Fauth%2Fdiscord%2Fredirect&scope=identify%20guilds%20email%20guilds.members.read&client_id={self.client.data.bot.id}",
					'Sec-Fetch-Dest': 'empty',
					'Sec-Fetch-Mode': 'cors',
					'Sec-Fetch-Site': 'same-origin',
					'TE': 'trailers',
				}
				async with session.post(oauth, headers=headers, json=payload) as res:
					if res.status == 200:
						result_session = await self.submit_oauth(res)
						return result_session
					else:
						self.client.logger.error(f"Getting HCaptcha oauth has the problem | {await res.text()}")
						await self.client.webhooks.send(
							content = self.client.data.discord.mention,
							title = "⚙️ GET HCAPTCHA OAUTH ⚙️",
							description = f"**{self.client.data.emoji.arrow}Error: {await res.text()}**",
							color = discord.Colour.random()
						)
			retry_times += 1
			await asyncio.sleep(20)
		else:
			await self.client.notification.notify()

	async def solve_hcaptcha(self):
		headers = {
			"Accept": "application/json, text/plain, */*",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US;en;q=0.8",
			"Content-Type": "application/json;charset=UTF-8",
			"Origin": "https://owobot.com",
			"Referer": "https://owobot.com/captcha",
			"Sec-Fetch-Dest": "empty",
			"Sec-Fetch-Mode": "cors",
			"Sec-Fetch-Site": "same-origin",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"
		}
		result = None
		for api_key in self.client.data.config.hcaptcha['twocaptcha']:
			twocaptcha = TwoCaptcha(**{
						"server": "2captcha.com",
						"apiKey": str(api_key),
						"defaultTimeout": 300,
						"pollingInterval": 5
			})
			retry_times = 0
			while retry_times < int(self.client.data.config.error_retry_times):
				try:
					balance = twocaptcha.balance()
					self.client.logger.info(f"TwoCaptcha API ({api_key}) currently have {balance}$")
					result = twocaptcha.hcaptcha(sitekey = "a6a1d5ce-612d-472d-8e37-7601408fbc09", url = "https://owobot.com/captcha")
					break
				except Exception as e:
					await self.client.webhooks.send(
						content = self.client.data.discord.mention,
						title = "⚙️ TWOCAPTCHA API ⚙️",
						description = f"**{self.client.data.emoji.arrow}Error: {str(e)}**",
						color = discord.Colour.random()
					)
					if str(e) == "ERROR_KEY_DOES_NOT_EXIST" or str(e) == "ERROR_WRONG_USER_KEY":
						self.client.logger.error(f"TwoCaptcha API ({api_key}) is invalid")
						break
					elif str(e) == "ERROR_ZERO_BALANCE":
						self.client.logger.error(f"TwoCaptcha API ({api_key}) run out of money")
						break
					else:
						self.client.logger.error(f"TwoCaptcha API ({api_key}) has the problem | {e}")
						retry_times += 1
						await asyncio.sleep(20)
			if result:
				break
		else:
			await self.client.notification.notify()
		if result:
			result_session = await self.get_oauth()
			if result_session:
				async with result_session as session:
					cookies = {cookie.key: cookie.value for cookie in session.cookie_jar}
					async with session.post("https://owobot.com/api/captcha/verify", headers=headers, json={"token": result['code']}, cookies=cookies) as res:
						if res.status == 200:
							self.client.logger.info(f"Solved HCaptcha successfully")
							await self.client.webhooks.send(
								title = "👍 CORRECT SOLUTION 👍",
								description = f"**{self.client.data.emoji.arrow}Solved successfully**",
								color = discord.Colour.random()
							)
							twocaptcha.report(result['captchaId'], True)
							self.client.data.stat.captcha += 1
							self.client.data.available.captcha = False
							self.client.data.available.selfbot = True
							self.client.data.checking.captcha_attempts = 0
							if self.client.data.config.hcaptcha['sleep_after_solve']:
								await self.sleep(True)
						else:
							self.client.logger.info(f"Solved HCaptcha failed")
							await self.client.webhooks.send(
								content = self.client.data.discord.mention,
								title = "🚫 INCORRECT SOLUTION 🚫",
								description = f"**{self.client.data.emoji.arrow}Solved failed**",
								color = discord.Colour.random()
							)
							twocaptcha.report(result['captchaId'], False)
							self.client.data.checking.captcha_attempts += 1
							if self.client.data.checking.captcha_attempts < int(self.client.data.config.hcaptcha['attempts']):
								await self.solve_hcaptcha()
							else:
								await self.client.notification.notify()

	async def detect_image_captcha(self, message):
		if not self.client.data.available.captcha and self.client.conditions.message(message, True, False, ['⚠️', 'letter word'], []) and (message.channel.id == self.client.data.bot.dm_channel.id or str(self.client.user.name) in message.content) and message.attachments:
			self.client.data.available.captcha = True
			self.client.data.available.selfbot = False
			self.client.logger.warning(f"!!! Image Captcha appears !!!")
			await self.client.webhooks.send(
				content = self.client.data.discord.mention,
				title = "🚨 IMAGE CAPTCHA APPEARS 🚨",
				description = f"{self.client.data.emoji.arrow}{message.jump_url}",
				color = discord.Colour.random(),
				image = message.attachments[0]
			)
			if self.client.data.config.image_captcha['mode']:
				captcha = base64.b64encode(await message.attachments[0].read()).decode("utf-8")
				lenghth = message.content[message.content.find("letter word") - 2]
				await self.solve_image_captcha(message.attachments[0], captcha, lenghth, [])
			else:
				await self.client.notification.notify()

	async def detect_hcaptcha(self, message):
		if not self.client.data.available.captcha and self.client.conditions.message(message, True, False, [f'<@{self.client.user.id}>', '⚠️', 'https://owobot.com/captcha'], []):
			self.client.data.available.captcha = True
			self.client.data.available.selfbot = False
			self.client.logger.warning(f"!!! HCaptcha appears !!!")
			await self.client.webhooks.send(
				content = self.client.data.discord.mention,
				title = "🚨 HCAPTCHA APPEARS 🚨",
				description = f"{self.client.data.emoji.arrow}{message.jump_url}",
				color = discord.Colour.random()
			)
			if self.client.data.config.hcaptcha['mode']:
				await self.solve_hcaptcha()
			else:
				await self.client.notification.notify()

	async def detect_unknown_captcha(self, message):
		if not self.client.data.available.captcha and self.client.conditions.message(message, True, False, [f'<@{self.client.user.id}>', 'verify that you are human!'], []) and not message.attachments and not "https://owobot.com/captcha" in message.content:
			await self.client.notification.notify()
			self.client.data.available.captcha = True
			self.client.data.available.selfbot = False
			self.client.logger.warning(f"!!! Unknown Captcha !!!")
			await self.client.webhooks.send(
				content = self.client.data.discord.mention,
				title = "🔒 UNKNOWN CAPTCHA 🔒",
				description = f"{self.client.data.emoji.arrow}{message.jump_url}",
				color = discord.Colour.random()
			)

	async def detect_problems(self, message):
		if self.client.conditions.message(message, True, False, ['You have been banned'], []) and (str(self.client.user.name) in message.content or message.channel.id == self.client.data.bot.dm_channel.id):
			await self.client.notification.notify()
			self.client.logger.warning(f"!!! Has been banned !!!")
			await self.client.webhooks.send(
				content = self.client.data.discord.mention,
				title = "🔨 HAS BEEN BANNED 🔨",
				description = f"{self.client.data.emoji.arrow}{message.jump_url}",
				color = discord.Colour.random()
			)
			self.client.data.available.selfbot = False
		if self.client.conditions.message(message, True, False, [str(self.client.data.discord.nickname), 'don\'t have enough cowoncy!'], []) and not "you silly hooman" in message.content:
			await self.client.notification.notify()
			self.client.logger.warning(f"!!! Out of cowoncy !!!")
			await self.client.webhooks.send(
				content = self.client.data.discord.mention,
				title = "💸 OUT OF COWONCY 💸",
				description = f"{self.client.data.emoji.arrow}{message.jump_url}",
				color = discord.Colour.random()
			)
			self.client.data.available.selfbot = False

	async def someone_mentions(self, message):
		if self.client.data.available.selfbot and message.mentions and not message.author.bot and self.client.conditions.message(message, False, True, [], []):
			if message.mentions[0].id == self.client.user.id or f"<@{self.client.user.id}>" in message.content:
				self.client.logger.info(f"Someone mentions")
				await self.client.webhooks.send(
					title = "🏷️ SOMEONE MENTIONS 🏷️",
					description = f"{self.client.data.emoji.arrow}{message.jump_url}",
					color = discord.Colour.random()
				)
				await self.change_channel()

	async def someone_challenges(self, message):
		if self.client.data.available.selfbot and self.client.conditions.message(message, True, False, [f'<@{self.client.user.id}>'], []) and message.embeds and "owo ab" in message.embeds[0].description:
			self.client.logger.info(f"Someone challenges")
			await self.client.webhooks.send(
				title = "🥊 SOMEONE CHALLENGES 🥊",
				description = f"{self.client.data.emoji.arrow}{message.jump_url}",
				color = discord.Colour.random()
			)
			choice = random.choice([1, 2])
			if choice == 1:
				if self.client.conditions.message(message, False, True, [], []):
					await message.channel.send(f"{self.client.data.discord.prefix}ab")
					self.client.logger.info(f"Sent {self.client.data.discord.prefix}ab")
				else:
					await message.channel.send(f"owoab")
					self.client.logger.info(f"Sent owoab")
				self.client.data.stat.command += 1
			if choice == 2:
				button = message.components[0].children[0]
				await button.click()
				self.client.logger.info(f"Clicked accept button")

	async def quest_progress(self, message):
		if self.client.data.checking.doing_quest and self.client.conditions.message(message, True, False, [f'You finished a quest and earned: {self.client.data.discord.quest[1]}!'], []):
			self.client.logger.info(f"Finished {self.client.data.discord.quest[0]} and earned {self.client.data.discord.quest[1]}")
			self.client.data.stat.quest += 1
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

	async def check_empty_gem(self, message):
		if self.client.data.available.selfbot and self.client.conditions.message(message, True, True, [str(self.client.data.discord.nickname), '🌱', 'gained'], []):
			empty_gem = []
			if not "gem1" in message.content and "gem1" in self.client.data.discord.inventory:
				empty_gem.append("gem1")
			if not "gem3" in message.content and "gem3" in self.client.data.discord.inventory:
				empty_gem.append("gem3")
			if not "gem4" in message.content and "gem4" in self.client.data.discord.inventory:
				empty_gem.append("gem4")
			if not "star" in message.content and "star" in self.client.data.discord.inventory and self.client.data.config.gem['star'] and self.client.data.available.special_pet:
				empty_gem.append("star")
			return empty_gem

	async def use_gem(self, empty_gem):
		await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}inv")
		self.client.logger.info(f"Sent {self.client.data.discord.prefix}inv")
		self.client.data.stat.command += 1
		try:
			inv = await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [f'{str(self.client.data.discord.nickname)}\'s Inventory'], []), timeout = 10)
			self.client.data.discord.inventory = inv.content
			inv = [int(item) for item in re.findall(r"`(.*?)`", inv.content) if item.isnumeric()]
			if self.client.data.available.selfbot and self.client.data.config.gem['open_box'] and 50 in inv:
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}lb all")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}lb all")
				self.client.data.stat.command += 1
				await asyncio.sleep(random.randint(2, 3))
			if self.client.data.available.selfbot and self.client.data.config.gem['open_crate'] and 100 in inv:
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}wc all")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}wc all")
				self.client.data.stat.command += 1
				await asyncio.sleep(random.randint(2, 3))
			if self.client.data.available.selfbot and self.client.data.config.gem['open_flootbox'] and 49 in inv:
				await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}lb f")
				self.client.logger.info(f"Sent {self.client.data.discord.prefix}lb f")
				self.client.data.stat.command += 1
				await asyncio.sleep(random.randint(2, 3))
			gems_in_inv = None
			if self.client.data.config.gem['sort'].lower() == "min":
				gems_in_inv = [sorted([gem for gem in inv if range[0] < gem < range[1]]) for range in [(50, 58), (64, 72), (71, 79), (78, 86)]]
			else:
				gems_in_inv = [sorted([gem for gem in inv if range[0] < gem < range[1]], reverse = True) for range in [(50, 58), (64, 72), (71, 79), (78, 86)]]
			if gems_in_inv == [[], [], [], []]:
				self.client.logger.info(f"Inventory doesn't have enough gems")
				self.client.data.checking.no_gem = True
				return
			use_gem = ""
			if "gem1" in empty_gem and gems_in_inv[0] != []:
				use_gem = use_gem + str(gems_in_inv[0][0]) + " "
			if "gem3" in empty_gem and gems_in_inv[1] != []:
				use_gem = use_gem + str(gems_in_inv[1][0]) + " "
			if "gem4" in empty_gem and gems_in_inv[2] != []:
				use_gem = use_gem + str(gems_in_inv[2][0]) + " "
			if "star" in empty_gem and gems_in_inv[3] != []:
				use_gem = use_gem + str(gems_in_inv[3][0]) + " "
			if not use_gem:
				return
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}use {use_gem}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}use {use_gem}")
			self.client.data.stat.command += 1
			self.client.data.stat.gem += 1
			self.client.data.checking.no_gem = False
			try:
				await self.client.wait_for("message", check = lambda message: self.client.conditions.message(message, True, True, [str(self.client.data.discord.nickname), 'active Special gem or you do not own'], []), timeout = 10)
				self.client.data.available.special_pet = False
			except asyncio.TimeoutError:
				pass
		except asyncio.TimeoutError:
			self.client.logger.error(f"Couldn't get inventory")

	async def check_caught_animals(self, message):
		if self.client.data.available.selfbot and self.client.conditions.message(message, True, True, [str(self.client.data.discord.nickname), '🌱', 'gained'], []):
			animals = message.content.split("**|**")[0]
			if any(animal in animals for animal in self.client.data.animals_list.legendary):
					await self.notify_caught_animals(message, self.client.data.emoji.legendary)

			if any(animal in animals for animal in self.client.data.animals_list.gem):
					await self.notify_caught_animals(message, self.client.data.emoji.gem)

			if any(animal in animals for animal in self.client.data.animals_list.fabled):
					await self.notify_caught_animals(message, self.client.data.emoji.fabled)

			if any(animal in animals for animal in self.client.data.animals_list.glitch):
					await self.notify_caught_animals(message, self.client.data.emoji.glitch)

			if any(animal in animals for animal in self.client.data.animals_list.hidden):
					await self.notify_caught_animals(message, self.client.data.emoji.hidden)

	async def notify_caught_animals(self, message, emoji):
		tier = re.findall(r":(.*?):", emoji)[0]
		self.client.logger.info(f"Found {tier.capitalize()} pet")
		await self.client.webhooks.send(
			title = f"{emoji} {tier.upper()} PET {emoji}",
			description = f"{self.client.data.emoji.arrow}{message.jump_url}",
			color = discord.Colour.random()
		)

	async def check_slot(self, message):
		if self.client.data.available.selfbot and self.client.conditions.message(message, True, True, [str(self.client.data.discord.nickname)], []):
			if "won nothing" in message.content:
				self.client.logger.info(f"Slot turn lost {self.client.data.current_gamble_bet.slot} cowoncy")
				self.client.data.stat.gamble -= self.client.data.current_gamble_bet.slot
				self.client.data.current_gamble_bet.slot *= int(self.client.data.config.gamble['slot']['rate'])
			if "<:eggplant:417475705719226369> <:eggplant:417475705719226369> <:eggplant:417475705719226369>" in message.content:
				self.client.logger.info(f"Slot turn draw {self.client.data.current_gamble_bet.slot} cowoncy")
			if "<:heart:417475705899712522> <:heart:417475705899712522> <:heart:417475705899712522>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot} cowoncy (x2)")
				self.client.data.stat.gamble += self.client.data.current_gamble_bet.slot
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			if "<:cherry:417475705178161162> <:cherry:417475705178161162> <:cherry:417475705178161162>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot * 2} cowoncy (x3)")
				self.client.data.stat.gamble += self.client.data.current_gamble_bet.slot * 2
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			if "<:cowoncy:417475705912426496> <:cowoncy:417475705912426496> <:cowoncy:417475705912426496>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot * 3} cowoncy (x4)")
				self.client.data.stat.gamble += self.client.data.current_gamble_bet.slot * 3
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			if "<:o_:417475705899843604> <:w_:417475705920684053> <:o_:417475705899843604>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot * 9} cowoncy (x10)")
				self.client.data.stat.gamble += self.client.data.current_gamble_bet.slot * 9
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])

	async def check_coinflip(self, message):
		if self.client.data.available.selfbot and self.client.conditions.message(message, True, True, [str(self.client.data.discord.nickname)], []):
				if "you lost" in message.content:
					self.client.logger.info(f"Coinflip turn lost {self.client.data.current_gamble_bet.coinflip} cowoncy")
					self.client.data.stat.gamble -= self.client.data.current_gamble_bet.coinflip
					self.client.data.current_gamble_bet.coinflip *= int(self.client.data.config.gamble['coinflip']['rate'])
				if "you won" in message.content:
					self.client.logger.info(f"Coinflip turn won {self.client.data.current_gamble_bet.coinflip} cowoncy")
					self.client.data.stat.gamble += self.client.data.current_gamble_bet.coinflip
					self.client.data.current_gamble_bet.coinflip = int(self.client.data.config.gamble['coinflip']['bet'])

	async def join_owo_giveaway(self, message):
		if message.id not in self.client.data.discord.ga_joined and self.client.conditions.message(message, True, False, [], []) and message.embeds and "New Giveaway" in str(message.embeds[0].author.name) and len(message.components) > 0:
			try:
				button = message.components[0].children[0]
				await button.click()
				self.client.data.discord.ga_joined.append(message.id)
				await self.client.webhooks.send(
					title = "🎁 JOINED GIVEAWAY 🎁",
					description = f"{self.client.data.emoji.arrow}{message.jump_url}",
					color = discord.Colour.random()
				)
				self.client.logger.info(f"Joined A New Giveaway ({message.id})")
			except Exception as e:
				if "COMPONENT_VALIDATION_FAILED" in str(e):
					self.client.data.discord.ga_joined.append(message.id)
				pass

	def filter_command(self, message):
			command = message.content
			if message.content.startswith(f"<@{self.client.user.id}>"):
				command = message.content.replace(f"<@{self.client.user.id}>", "", 1)
			command = filter(bool, command.split(" "))
			return(list(command))

	async def command(self, message):
		if message.author.id in self.client.data.config.command['owner_id'] or message.author.id == self.client.user.id:
			command = self.filter_command(message)
			if not command:
				return

			if command[0].lower() == "start":
				await self.client.commands.start_selfbot()
			if command[0].lower() == "pause":
				await self.client.commands.pause_selfbot()

			if command[0].lower() == "help":
				await self.client.commands.help()
			if command[0].lower() == "stat":
				await self.client.commands.stat_selfbot()
			if command[0].lower() == "setting":
				await self.client.commands.show_setting()

			if command[0].lower() == "say" and "-" in message.content and len(command) >= 2:
				await self.client.commands.say_text(message)

			if command[0].lower() == "give" and len(command) >= 3:
				await self.client.commands.give_cowoncy(message, command)

			if command[0].lower() == "do_quest" and len(command) >= 2:
				await self.client.commands.change_do_quest_mode(command)

			if command[0].lower() == "huntbot_upgrade_mode" and len(command) >= 2:
				await self.client.commands.change_huntbot_upgrade_mode(command)
			if command[0].lower() == "huntbot_upgrade_type" and len(command) >= 2:
				await self.client.commands.change_huntbot_upgrade_type(command)

			if command[0].lower() == "use_gem" and len(command) >= 2:
				await self.client.commands.change_use_gem_mode(command)
			if command[0].lower() == "sort_gem" and len(command) >= 2:
				await self.client.commands.change_sort_gem_mode(command)
			if command[0].lower() == "star_gem" and len(command) >= 2:
				await self.client.commands.change_star_gem_mode(command)

			if command[0].lower() == "animals_mode" and len(command) >= 2:
				await self.client.commands.change_animals_mode(command)
			if command[0].lower() == "animals_type" and len(command) >= 2:
				await self.client.commands.change_animals_type(command)
			if command[0].lower() == "animals_rank" and len(command) >= 2:
				await self.client.commands.change_animals_rank(command)
