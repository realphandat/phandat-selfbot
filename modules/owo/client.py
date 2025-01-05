import discord

from modules.owo.data import Data
from modules.owo.command import Command
from modules.owo.sleep import Sleep
from modules.owo.captcha import Captcha
from modules.owo.giveaway import Giveaway
from modules.owo.channel import Channel
from modules.owo.daily import Daily
from modules.owo.quest import Quest
from modules.owo.grind import Grind
from modules.owo.huntbot import Huntbot
from modules.owo.gem import Gem
from modules.owo.animal import Animal
from modules.owo.gamble import Gamble
from modules.owo.minigame import Minigame
from modules.owo.task import Task
from modules.owo.others import Others

from modules.general.notification import Notification
from modules.general.log import Log
from modules.general.webhook import Webhook
from modules.general.topgg import Topgg

class OwOSelfbot(discord.Client):
	def __init__(self, Clients, token, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.Clients = Clients
		self.data = Data(token)
		self.command = Command(self)
		self.sleep = Sleep(self)
		self.captcha = Captcha(self)
		self.giveaway = Giveaway(self)
		self.channel = Channel(self)
		self.daily = Daily(self)
		self.quest = Quest(self)
		self.grind = Grind(self)
		self.huntbot = Huntbot(self)
		self.gem = Gem(self)
		self.animal = Animal(self)
		self.gamble = Gamble(self)
		self.minigame = Minigame(self)
		self.task = Task(self)
		self.others = Others(self)
		self.notification = Notification(self)
		self.log = Log(self)
		self.webhook = Webhook(self)
		self.topgg = Topgg(self)
	
	async def on_ready(self):
		if self.data.selfbot.on_ready:
			self.data.selfbot.on_ready = False
			self.bot = self.get_user(408785106942164992)
			self.logger = await self.log.create("owo", self.data.config.history['file']['mode'], self.data.config.history['file']['directory'])
			await self.others.startup()
			await self.others.intro()
			await self.task.start()

	async def on_message(self, message):
		if self.data.config.command['mode']:
			await self.command.command(message)
		await self.captcha.detect_image_captcha(message)
		await self.captcha.detect_hcaptcha(message)
		await self.captcha.detect_unknown_captcha(message)
		await self.captcha.detect_problems(message)
		if self.data.config.channel['change_when_be_mentioned']:
			await self.channel.change_when_be_mentioned(message)
		if self.data.config.channel['change_when_be_challenged'] or self.data.quest.battle_friend:
			await self.channel.change_when_be_challenged(message)
		if self.data.config.do_quest['mode']:
			await self.quest.quest_progress(message)
		if (self.data.config.use_gem['mode'] or self.gem.glitch_available()) and not self.data.checking.no_gem:
			empty_gem = await self.gem.check_empty_gem(message)
			if empty_gem:
				await self.gem.use_gem(empty_gem)
		if self.data.config.notify_caught_animal['mode']:
			await self.animal.check_caught_animal(message)

	async def on_message_edit(self, before, after):
		if self.data.config.join_owo_giveaway['mode']:
			await self.giveaway.join_owo_giveaway(after)
		if self.data.config.gamble['slot']['mode']:
			await self.gamble.check_slot(after)
		if self.data.config.gamble['coinflip']['mode']:
			await self.gamble.check_coinflip(after)