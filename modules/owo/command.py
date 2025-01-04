import discord
import asyncio
import json

class Command:
	def __init__(self, client):
		self.client = client

	def filter_command(self, message):
			command = message.content
			if message.content.startswith(f"<@{self.client.user.id}>"):
				command = message.content.replace(f"<@{self.client.user.id}>", "", 1)
			command = filter(bool, command.split(" "))
			return(list(command))

	async def command(self, message):
		if message.author.id in self.client.data.config.command['target'] or message.author.id == self.client.user.id:
			command = self.filter_command(message)
			if not command:
				return

			if command[0].lower() == "start":
				await self.start_selfbot()
			if command[0].lower() == "pause":
				await self.pause_selfbot()

			if command[0].lower() == "help":
				await self.help()
			if command[0].lower() == "stat":
				await self.stat_selfbot()
			if command[0].lower() == "setting":
				await self.show_setting()

			if command[0].lower() == "say" and "-" in message.content and len(command) >= 2:
				await self.say_text(message)

			if command[0].lower() == "give" and len(command) >= 3:
				await self.give_cowoncy(message, command)

			if command[0].lower() == "do_quest" and len(command) >= 2:
				await self.change_do_quest_mode(command)

			if command[0].lower() == "huntbot_upgrade_mode" and len(command) >= 2:
				await self.change_huntbot_upgrade_mode(command)
			if command[0].lower() == "huntbot_upgrade_type" and len(command) >= 2:
				await self.change_huntbot_upgrade_type(command)

			if command[0].lower() == "use_gem" and len(command) >= 2:
				await self.change_use_gem_mode(command)
			if command[0].lower() == "sort_gem" and len(command) >= 2:
				await self.change_sort_gem_mode(command)
			if command[0].lower() == "star_gem" and len(command) >= 2:
				await self.change_star_gem_mode(command)

			if command[0].lower() == "animal_mode" and len(command) >= 2:
				await self.change_animal_mode(command)
			if command[0].lower() == "animal_type" and len(command) >= 2:
				await self.change_animal_type(command)
			if command[0].lower() == "animal_rank" and len(command) >= 2:
				await self.change_animal_rank(command)

	async def help(self):
		menu = """
**`start`
`pause`

`help`
`stat`
`setting`

`say` + `-text`
`give` + `<@user_id>` + `amount` 
`do_quest` + `on/off`

`huntbot_upgrade_mode` + `on/off`
`huntbot_upgrade_type` + `type`  

`use_gem` + `on/off`
`sort_gem` + `min/max`
`star_gem` + `on/off`

`animal_mode` + `on/off`
`animal_type` + `type`
`animal_rank` + `rank`**
"""
		self.client.logger.info(menu)
		await self.client.webhook.send(
			title = f"📋 COMMAND MENU 📋",
			description = menu,
			color = discord.Colour.random()
		)

	async def start_selfbot(self):
		self.client.data.checking.pause = False
		self.client.data.available.captcha = False
		self.client.data.available.selfbot = True
		self.client.logger.info(f"Start selfbot")
		await self.client.webhook.send(
			title = f"🌤️ START SELFBOT 🌤️",
			color = discord.Colour.random()
		)

	async def pause_selfbot(self):
		self.client.data.checking.pause = True
		self.client.data.available.selfbot = False
		self.client.logger.info(f"Pause selfbot")
		await self.client.webhook.send(
			title = f"🌑 PAUSE SELFBOT 🌑",
			color = discord.Colour.random()
		)

	async def stat_selfbot(self):
		stat = f"""
**Worked <t:{int(self.client.data.selfbot.turn_on_time)}:R> with:
{self.client.data.config.emoji['arrow']}Sent __{self.client.data.stat.sent_message}__ Message
{self.client.data.config.emoji['arrow']}Slept __{self.client.data.stat.slept}__ Times
{self.client.data.config.emoji['arrow']}Solved __{self.client.data.stat.solved_captcha}__ Captcha
{self.client.data.config.emoji['arrow']}Changed Channel __{self.client.data.stat.changed_channel}__ Times
{self.client.data.config.emoji['arrow']}Done __{self.client.data.stat.done_quest}__ Quest
{self.client.data.config.emoji['arrow']}Claimed Huntbot __{self.client.data.stat.claimed_huntbot}__ Times       
{self.client.data.config.emoji['arrow']}Used Gem __{self.client.data.stat.used_gem}__ Times
{self.client.data.config.emoji['arrow']}Gambled __{self.client.data.stat.gambled_cowoncy}__ Cowoncy**
"""
		self.client.logger.info(stat)
		await self.client.webhook.send(
			title = f"📊 STAT 📊",
			description = stat,
			color = discord.Colour.random()
		)

	async def show_setting(self):
		await self.client.webhook.send(
			title = f"🔥 CONFIRM `YES` IN 10S 🔥",
			description = "**Send setting via webhook including __token__, __TwoCaptcha API__, __webhook url__, ...**",
			color = discord.Colour.random()
		)
		try:
			await self.client.wait_for("message", check = lambda message: message.content.lower() in ['yes', 'y'] and message.author.id in self.client.data.config.command['target'], timeout = 10)
		except asyncio.TimeoutError:
			pass
		else:
			with open(self.client.data.config.directory) as file:
				config = json.load(file)
			self.client.logger.info(config[self.client.data.config.token])
			await self.client.webhook.send(
				title = f"💾 SETTING 💾",
				description = config[self.client.data.config.token],
				color = discord.Colour.random()
			)

	async def say_text(self, message):
		text = message.content.split("-")[1]
		await message.channel.send(text)
		self.client.logger.info(f"Sent {text}")

	def give_cowoncy_filter(self, message, nickname):
		if self.message(message, True, False, [f'<@{self.client.user.id}>', '... *but... why?*'], []):
			return True
		if self.message(message, True, False, [nickname, 'you can only send'], []):
			return True
		if self.message(message, True, False, [nickname, 'you silly hooman'], []):
			return True
		if self.message(message, True, False, [], []) and message.embeds and nickname in message.embeds[0].author.name and "you are about to give cowoncy" in message.embeds[0].author.name:
			return True

	async def give_cowoncy(self, message, command):
		if self.client.others.message(message, False, True, [], []):
			await message.channel.send(f"{self.client.data.discord.prefix}give {command[1]} {command[2]}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}give {command[1]} {command[2]}")
		else:
			await message.channel.send(f"owogive {command[1]} {command[2]}")
			self.client.logger.info(f"Sent owogive {command[1]} {command[2]}")
		self.client.data.stat.sent_message += 1
		member = await self.client.get_channel(message.channel.id).guild.fetch_member(self.client.user.id)
		nickname = member.nick if member.nick else member.display_name
		try:
			give_cowoncy_message = await self.client.wait_for("message", check = lambda message: self.give_cowoncy(message, str(nickname)), timeout = 10)
			if self.client.others.message(give_cowoncy_message, True, False, [f'<@{self.client.user.id}>', '... *but... why?*'], []):
				self.client.logger.info(f"Can't give cowoncy to yourself")
			elif self.client.others.message(give_cowoncy_message, True, False, [str(nickname), 'you can only send'], []):
				self.client.logger.info(f"Amount of giving cowoncy for today is over")
			elif self.client.others.message(give_cowoncy_message, True, False, [str(nickname), 'you silly hooman'], []):
				self.client.logger.info(f"Don't have enough cowoncy to give")
			elif self.client.others.message(give_cowoncy_message, True, False, [], []) and give_cowoncy_message.embeds and str(nickname) in give_cowoncy_message.embeds[0].author.name and "you are about to give cowoncy" in give_cowoncy_message.embeds[0].author.name:
				button = give_cowoncy_message.components[0].children[0]
				await button.click()
				self.client.logger.info(f"Gived cowoncy successfully")
		except asyncio.TimeoutError:
			self.client.logger.error(f"Couldn't get send cowoncy message")

	async def change_do_quest_mode(self, command):
		if command[1].lower() == "on" or command[1].lower() == "off":
			setting = command[1].lower() == "on"
			self.client.data.checking.doing_quest = not setting
			self.client.data.available.quest = setting
			self.client.data.config.do_quest['mode'] = setting
			self.client.logger.info(f"Do quest: {command[1].lower()}")
			await self.client.webhook.send(
				title = f"🛸 CHANGED CONFIG 🛸",
				description = f"**{self.client.data.config.emoji['arrow']}Do quest: {command[1].lower()}**",
				color = discord.Colour.random()
			)

	async def change_huntbot_upgrade_mode(self, command):
		if command[1].lower() == "on" or command[1].lower() == "off":
			setting = command[1].lower() == "on"
			self.client.data.config.huntbot['upgrade']['mode'] = setting
			self.client.logger.info(f"Huntbot upgrade mode: {command[1].lower()}")
			await self.client.webhook.send(
				title = f"🛸 CHANGED CONFIG 🛸",
				description = f"**{self.client.data.config.emoji['arrow']}Huntbot upgrade mode: {command[1].lower()}**",
				color = discord.Colour.random()
			)

	async def change_huntbot_upgrade_type(self, command):
		self.client.data.config.huntbot['upgrade']['type'] = command[1].lower()
		self.client.logger.info(f"Huntbot upgrade type: {command[1].lower()}")
		await self.client.webhook.send(
			title = f"🛸 CHANGED CONFIG 🛸",
			description = f"**{self.client.data.config.emoji['arrow']}Huntbot upgrade type: {command[1].lower()}**",
			color = discord.Colour.random()
		)

	async def change_use_gem_mode(self, command):
		if command[1].lower() == "on" or command[1].lower() == "off":
			setting = command[1].lower() == "on"
			self.client.data.checking.no_gem = not setting
			self.client.data.config.gem['mode'] = setting
			self.client.logger.info(f"Use gem: {command[1].lower()}")
			await self.client.webhook.send(
				title = f"🛸 CHANGED CONFIG 🛸",
				description = f"**{self.client.data.config.emoji['arrow']}Use gem: {command[1].lower()}**",
				color = discord.Colour.random()
			)

	async def change_sort_gem_mode(self, command):
		if command[1].lower() == "min" or command[1].lower() == "max":
			self.client.data.config.gem['sort'] = command[1].lower()
			self.client.logger.info(f"Sort gem: {command[1].lower()}")
			await self.client.webhook.send(
				title = f"🛸 CHANGED CONFIG 🛸",
				description = f"**{self.client.data.config.emoji['arrow']}Sort gem: {command[1].lower()}**",
				color = discord.Colour.random()
			)

	async def change_star_gem_mode(self, command):
		if command[1].lower() == "on" or command[1].lower() == "off":
			setting = command[1].lower() == "on"
			self.client.data.available.special_pet = setting
			self.client.data.config.gem['star'] = setting
			self.client.logger.info(f"Star gem: {command[1].lower()}")
			await self.client.webhook.send(
				title = f"🛸 CHANGED CONFIG 🛸",
				description = f"**{self.client.data.config.emoji['arrow']}Star gem: {command[1].lower()}**",
				color = discord.Colour.random()
			)

	async def change_animal_mode(self, command):
		if command[1].lower() == "on" or command[1].lower() == "off":
			setting = command[1].lower() == "on"
			self.client.data.config.sell_sac_animal['mode'] = setting
			self.client.logger.info(f"animal mode: {command[1].lower()}")
			await self.client.webhook.send(
				title = f"🛸 CHANGED CONFIG 🛸",
				description = f"**{self.client.data.config.emoji['arrow']}animal mode: {command[1].lower()}**",
				color = discord.Colour.random()
			)

	async def change_animal_type(self, command):
		self.client.data.config.sell_sac_animal['type'] = command[1].lower()
		self.client.logger.info(f"animal type: {command[1].lower()}")
		await self.client.webhook.send(
			title = f"🛸 CHANGED CONFIG 🛸",
			description = f"**{self.client.data.config.emoji['arrow']}animal type: {command[1].lower()}**",
			color = discord.Colour.random()
		)

	async def change_animal_rank(self, command):
		self.client.data.config.sell_sac_animal['rank'] = command[1].lower()
		self.client.logger.info(f"animal rank: {command[1].lower()}")
		await self.client.webhook.send(
			title = f"🛸 CHANGED CONFIG 🛸",
			description = f"**{self.client.data.config.emoji['arrow']}animal rank: {command[1].lower()}**",
			color = discord.Colour.random()
		)