import time
import random
import json

class Data:
	def __init__(self, token):
		self.config = Config(token)

		self.stat = Stat()
		self.quest = Quest()
		self.discord = Discord()
		self.selfbot = Selfbot(self.config)
		self.cooldown = Cooldown()
		self.checking = Checking()
		self.available = Available()
		self.current_task_loop = Current_Task_Loop()
		self.current_gamble_bet = Current_Gamble_Bet(self)

class Config:
	def __init__(self, token):
		with open("setting/config.json") as file:
			self.directory = json.load(file)['directory']['owo']
		with open(self.directory) as file:
			data = json.load(file)
			self.token = token
			self.error_retry_times = data[token]['error_retry_times']
			self.emoji = data[token]['emoji']
			self.notification = data[token]['notification']
			self.history = data[token]['history']
			self.command = data[token]['command']
			self.sleep_after_certain_time = data[token]['sleep_after_certain_time']
			self.captcha = data[token]['captcha']
			self.get_owo_prefix = data[token]['get_owo_prefix']
			self.check_owo_status = data[token]['check_owo_status']
			self.join_owo_giveaway = data[token]['join_owo_giveaway']
			self.channel = data[token]['channel']
			self.vote_topgg = data[token]['vote_topgg']
			self.claim_daily = data[token]['claim_daily']
			self.do_quest = data[token]['do_quest']
			self.grind = data[token]['grind']
			self.huntbot = data[token]['huntbot']
			self.use_gem = data[token]['use_gem']
			self.sell_sac_animal = data[token]['sell_sac_animal']
			self.notify_caught_animal = data[token]['notify_caught_animal']
			self.gamble = data[token]['gamble']
			self.minigame = data[token]['minigame']

class Stat:
	def __init__(self):
		self.sent_message = 0
		self.slept = 0
		self.solved_captcha = 0
		self.changed_channel = 0
		self.done_quest = 0
		self.claimed_huntbot = 0
		self.used_gem = 0
		self.gambled_cowoncy = 0

class Quest:
	def __init__(self):
		self.owo = False
		self.hunt = False
		self.battle = False
		self.gamble = False
		self.action_someone = False
		self.battle_friend = False
		self.cookie = False
		self.pray = False
		self.curse = False
		self.action_you = False

class Discord:
	def __init__(self):
		self.mention = ""
		self.prefix = "owo"
		self.nickname = ""
		self.channel = ""
		self.channel_id = ""
		self.quest = ""
		self.inventory = "gem1 gem3 gem4 star"
		self.ga_joined = []

class Selfbot:
	def __init__(self, config):
		self.on_ready = True
		self.turn_on_time = time.time()
		self.work_time = random.randint(int(config.sleep_after_certain_time['work']['min']), int(config.sleep_after_certain_time['work']['max']))

class Cooldown:
	def __init__(self):
		self.daily = 0
		self.quest = 0
		self.huntbot = 0
		self.glitch = 0
		self.others_minigame = 0

class Checking:
	def __init__(self):
		self.captcha_attempt = 0
		self.pause = False
		self.no_gem = False
		self.run_limit = False
		self.pup_limit = False
		self.piku_limit = False
		self.doing_quest = False
		self.block_battle = False
		self.block_pray_curse = False

class Available:
	def __init__(self):
		self.selfbot = True
		self.captcha = False
		self.quest = True
		self.special_pet = True
		self.blackjack = False

class Current_Task_Loop:
	def __init__(self):
		self.sleep_after_certain_time = 0
		self.check_twocaptcha_balance = 0
		self.check_owo_status = 0
		self.change_channel = 0
		self.vote_topgg = 0
		self.claim_daily = 0
		self.do_quest = 0
		self.grind = 0
		self.claim_submit_huntbot = 0
		self.check_glitch = 0
		self.sell_sac_animal = 0
		self.gamble = 0
		self.pray_curse = 0
		self.others_minigame = 0

class Current_Gamble_Bet:
	def __init__(self, client):
		self.client = client
		self.slot = int(self.client.config.gamble['slot']['bet'])
		self.coinflip = int(self.client.config.gamble['coinflip']['bet'])
		self.blackjack = int(self.client.config.gamble['blackjack']['bet'])