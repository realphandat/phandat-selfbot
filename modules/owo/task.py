import asyncio
import random
import discord
import time

from discord.ext import tasks

class Task:
	def __init__(self, client):
		self.client = client
		self.tasks = [
			self.sleep_after_certain_time,
			self.check_twocaptcha_balance,
			self.check_owo_status,
			self.change_channel,
			self.vote_topgg,
			self.claim_daily,
			self.do_quest,
			self.grind,
			self.claim_submit_huntbot,
			self.check_glitch,
			self.sell_sac_animal,
			self.gamble,
			self.pray_curse,
			self.others_minigame,
		]

	async def start(self, skip = None):
		self.client.data.available.selfbot = True
		for task in self.tasks:
			if skip:
				if task in skip:
					continue
			try:
				task.start()
				await asyncio.sleep(random.randint(5, 10))
			except RuntimeError:
				pass

	async def stop(self, skip = None):
		self.client.data.available.selfbot = False
		for task in self.tasks:
			if skip:
				if task in skip:
					continue
			task.cancel()

	@tasks.loop(minutes = 1)
	async def sleep_after_certain_time(self):
		if self.client.data.config.sleep_after_certain_time['mode']:
			await self.client.sleep.sleep_after_certain_time()
		self.client.data.current_task_loop.sleep_after_certain_time += 1

	@tasks.loop(minutes = 1)
	async def check_twocaptcha_balance(self):
		if self.client.data.config.captcha['pause_if_twocaptcha_balance_is_low']['mode']:
			if self.client.data.config.captcha['solve_image_captcha']['mode']:
				await self.client.captcha.check_twocaptcha_balance(self.client.data.config.captcha['solve_image_captcha']['twocaptcha'])
			if self.client.data.config.captcha['solve_hcaptcha']['mode']:
				await self.client.captcha.check_twocaptcha_balance(self.client.data.config.captcha['solve_hcaptcha']['twocaptcha'])
		self.client.data.current_task_loop.check_twocaptcha_balance += 1

	@tasks.loop(minutes = 1)
	async def check_owo_status(self):
		if self.client.data.config.check_owo_status['mode'] and self.client.data.current_task_loop.check_owo_status > 0:
			await self.client.others.check_owo_status()
		self.client.data.current_task_loop.check_owo_status += 1

	@tasks.loop(seconds = random.randint(600, 1200))
	async def change_channel(self):
		if self.client.data.current_task_loop.change_channel > 0:
			await self.client.channel.change_channel()
		self.client.data.current_task_loop.change_channel += 1

	@tasks.loop(hours = 12)
	async def vote_topgg(self):
		if self.client.data.config.vote_topgg['mode']:
			await self.client.topgg.vote_topgg()
		self.client.data.current_task_loop.vote_topgg += 1

	@tasks.loop(minutes = 1)
	async def claim_daily(self):
		if self.client.data.config.claim_daily['mode']:
			await self.client.daily.claim_daily()
		self.client.data.current_task_loop.claim_daily += 1

	@tasks.loop(minutes = 1)
	async def do_quest(self):
		if int(self.client.data.cooldown.quest) - time.time() <= 0:
			self.client.data.available.quest = True
		if self.client.data.config.do_quest['mode'] and self.client.data.available.quest and not self.client.data.checking.doing_quest:
			await self.client.quest.do_quest()
		self.client.data.current_task_loop.do_quest += 1

	@tasks.loop(seconds = random.randint(18, 25))
	async def grind(self):
		try:
			if self.client.data.config.grind['owo']['mode'] or self.client.data.quest.owo:
				await self.client.grind.send_owo()
			await asyncio.sleep(random.randint(5, 10))
			if self.client.data.config.grind['hunt']['mode'] or self.client.data.quest.hunt:
				await self.client.grind.send_hunt()
			await asyncio.sleep(random.randint(5, 10))
			if (self.client.data.config.grind['battle']['mode'] or self.client.data.quest.battle) and not self.client.data.checking.block_battle:
				await self.client.grind.send_battle()
			await asyncio.sleep(random.randint(5, 10))
			if self.client.data.config.grind['quote']['mode']:
				await self.client.grind.send_quote()
		except Exception as e:
			self.client.logger.error(f"Grind Has The Error | {str(e)}")
			await self.client.webhook.send(
				title = "⚙️ GRIND ⚙️",
				description = f"**{self.client.data.config.emoji['arrow']}Error: {str(e)}**",
				color = discord.Colour.random()
			)
		self.client.data.current_task_loop.grind += 1

	@tasks.loop(minutes = 1)
	async def claim_submit_huntbot(self):
		if self.client.data.config.huntbot['claim_submit']:
			await self.client.huntbot.claim_submit_huntbot()
		self.client.data.current_task_loop.claim_submit_huntbot += 1

	@tasks.loop(seconds = random.randint(600, 1200))
	async def check_glitch(self):
		if self.client.data.config.use_gem['use_gem_when_glitch_available']:
			await self.client.gem.check_glitch()
		self.client.data.current_task_loop.check_glitch += 1

	@tasks.loop(seconds = random.randint(1200, 3600))
	async def sell_sac_animal(self):
		if self.client.data.config.sell_sac_animal['mode']:
			await self.client.animal.sell_sac_animal()
		self.client.data.current_task_loop.sell_sac_animal += 1

	@tasks.loop(seconds = random.randint(60, 120))
	async def gamble(self):
		if self.client.data.config.gamble['slot']['mode'] or self.client.data.quest.gamble:
			await self.client.gamble.play_slot()
			await asyncio.sleep(random.randint(5, 10))
		if self.client.data.config.gamble['coinflip']['mode'] or self.client.data.quest.gamble:
			await self.client.gamble.play_coinflip()
			await asyncio.sleep(random.randint(5, 10))
		if self.client.data.config.gamble['blackjack']['mode'] or self.client.data.quest.gamble:
			await self.client.gamble.play_blackjack()
		self.client.data.current_task_loop.gamble += 1

	@tasks.loop(seconds = random.randint(300, 600))
	async def pray_curse(self):
		if self.client.data.config.minigame['pray_curse']['mode'] and (not self.client.data.quest.pray or not self.client.data.quest.curse) and not self.client.data.checking.block_pray_curse:
			if self.client.data.config.minigame['pray_curse']['type'].lower() == "pray":
				await self.client.minigame.pray(self.client.data.config.minigame['pray_curse']['target'])
			else:
				await self.client.minigame.curse(self.client.data.config.minigame['pray_curse']['target'])
		self.client.data.current_task_loop.pray_curse += 1

	@tasks.loop(seconds = random.randint(60, 120))
	async def others_minigame(self):
		if int(self.client.data.cooldown.others_minigame) - time.time() <= 0:
			self.client.data.checking.run_limit = False
			self.client.data.checking.pup_limit = False
			self.client.data.checking.piku_limit = False
		if self.client.data.config.minigame['others']['run'] and not self.client.data.checking.run_limit:
			await self.client.minigame.send_run()
		if self.client.data.config.minigame['others']['pup'] and not self.client.data.checking.pup_limit:
			await self.client.minigame.send_pup()
		if self.client.data.config.minigame['others']['piku'] and not self.client.data.checking.piku_limit:
			await self.client.minigame.send_piku()
		if self.client.data.config.minigame['others']['common_ring']:
			await self.client.minigame.buy_common_ring()
		self.client.data.current_task_loop.others_minigame += 1