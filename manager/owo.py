import json
import inquirer

class OwOManager:
	def __init__(self):
		self.mode = ['Yes', 'No']
		self.file = "configs/owo.json"

		with open("assets/template.json") as file:
			self.template = json.load(file)['owo']

		self.features = [
			"Select all",
			"Check OwO status and pause when it is offline",
			"Join OwO giveaway",
			"Get OwO prefix or set it as default",
			"Change channel when someone mentions",
			"Accept challenge from someone",
			"Add channel id",
			"Solve image captcha",
			"Solve hcaptcha",
			"Stop when TwoCaptcha balance is below any number",
			"Do quest",
			"Vote top.gg (Require chorme)",
			"Claim daily",
			"Go to sleep",
			"Grind (Send OwO/UwU, hunt, battle, quote)",
			"Claim and submit huntbot",
			"Use gem (open box/crate/flootbox)",
			"Use gem when distorted animals are available",
			"Sell/Sacrifice animals",
			"Check and notify caught pets",
			"Gamble (Play slot/coinflip/blackjack)",
			"Pray/Curse",
			"Entertainment (Farm run/pup/piku/common ring)",
			"Discord command",
			"Discord webhook",
			"Log file",
			"Music notification",
			"Retry errors"
		]

	def homepage(self):
		with open(self.file) as file:
			config = json.load(file)
		choices = ['Back', 'Add accounts', 'Remove accounts']
		for account in config:
			choices.append(account)
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = choices)
		if select == "Back":
			return
		elif select == "Add accounts":
			self.add_accounts()
		elif select == "Remove accounts":
			self.remove_accounts()
		else:
			self.change_accounts(select)
		self.homepage()

	def add_accounts(self):
		with open(self.file) as file:
			config = json.load(file)
		while True:
				token = input("[!] Enter a discord token: ")
				if not token == "" and not " " in token:
					break
				print("[-] Token mustn't be empty or have spaces")
		account = {token: self.template}
		config.update(account)
		with open(self.file, "w") as file:
			json.dump(config, file, indent = 4)
		print("[+] Added a new account")
		self.change_accounts(token, True)

	def remove_accounts(self):
		with open(self.file) as file:
			config = json.load(file)
		choices = []
		for account in config:
			choices.append(account)
		select = inquirer.checkbox("Move ↑↓ and SPACE to choose, then ENTER to select", choices = choices)
		amount = 0
		for account in select:
			amount += 1
			del config[account]
		with open(self.file, 'w') as file:
			json.dump(config, file, indent = 4)
		if amount > 0:
			print(f"[-] Removed {amount} {'account' if amount == 1 else 'accounts'}")

	def change_accounts(self, token, select_all = False):
		with open(self.file) as file:
			config = json.load(file)

		if not select_all:
			select = inquirer.checkbox("Move ↑↓ and SPACE to choose, then ENTER to select", choices = self.features)
			if "Select all" in select:
				select_all = True

		if select_all or "Check OwO status and pause when it is offline" in select:
			self.check_owo_status(token, config)

		if select_all or "Join OwO giveaway" in select:
			self.join_owo_giveaway(token, config)

		if select_all or "Get OwO prefix or set it as default" in select:
			self.get_owo_prefix(token, config)

		if select_all or "Change channel when someone mentions" in select:
			self.someone_mentions(token, config)

		if select_all or "Accept challenge from someone" in select:
			self.someone_challenges(token, config)

		if select_all or "Add channel id" in select:
			self.channel_id(token, config)

		if select_all or "Solve image captcha" in select:
			self.captcha(config[token]['image_captcha'], "image captcha")

		if select_all or "Solve hcaptcha" in select:
			self.captcha(config[token]['hcaptcha'], "hcaptcha")

		if select_all or "Stop when TwoCaptcha balance is below any number" in select:
			self.twocaptcha_balance(token, config)

		if select_all or "Do quest" in select:
			self.quest(token, config)

		if select_all or "Vote top.gg (Require chorme)" in select:
			self.topgg(token, config)

		if select_all or "Claim daily" in select:
			self.daily(token, config)

		if select_all or "Go to sleep" in select:
			self.sleep(token, config)

		if select_all or "Grind (Send OwO/UwU, hunt, battle, quote)" in select:
			self.grind(token, config)

		if select_all or "Claim and submit huntbot" in select:
			self.huntbot(token, config)

		if select_all or "Use gem (open box/crate/flootbox)" in select:
			self.gem(token, config)

		if select_all or "Use gem when distorted animals are available" in select:
			self.glitch(token, config)

		if select_all or "Sell/Sacrifice animals" in select:
			self.animals(token, config)

		if select_all or "Check and notify caught pets" in select:
			self.caught(token, config)

		if select_all or "Gamble (Play slot/coinflip/blackjack)" in select:
			self.gamble(token, config)

		if select_all or "Pray/Curse" in select:
			self.pray_curse(token, config)

		if select_all or "Entertainment (Farm run/pup/piku/common ring)" in select:
			self.entertainment(token, config)

		if select_all or "Discord command" in select:
			self.command(token, config)

		if select_all or "Discord webhook" in select:
			self.webhook(token, config)

		if select_all or "Log file" in select:
			self.log_file(token, config)

		if select_all or "Music notification" in select:
			self.music_notification(token, config)

		if select_all or "Retry errors" in select:
			self.error_retry_times(token, config)

		with open(self.file, 'w') as file:
			json.dump(config, file, indent = 4)
		print("[+] Saved!")

	def check_owo_status(self, token, config):
		print(f"[!] Check OwO status and pause when it is offline (Recent: {config[token]['check_owo_status']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['check_owo_status'] = select == "Yes"

	def join_owo_giveaway(self, token, config):
		print(f"[!] Join OwO giveaway (Recent: {config[token]['join_owo_giveaway']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['join_owo_giveaway'] = select == "Yes"

	def get_owo_prefix(self, token, config):
		print(f"[!] Get OwO prefix (Recent: {config[token]['get_owo_prefix']['mode']}) or set it as default (Recent: {config[token]['get_owo_prefix']['default']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = ['Get OwO prefix', 'Set as default'])
		if select == "Get OwO prefix":
			config[token]['get_owo_prefix']['mode'] = True
		if select == "Set as default":
			config[token]['get_owo_prefix']['mode'] = False
			default = input("[!] Enter the OwO prefix default (E.g: 'owo'): ")
			config[token]['get_owo_prefix']['default'] = default

	def someone_mentions(self, token, config):
		print(f"[!] Change channel when someone mentions you (Recent: {config[token]['someone_mentions']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['someone_mentions'] = select == "Yes"

	def someone_challenges(self, token, config):
		print(f"[!] Accept challenge from someone (Recent: {config[token]['someone_challenges']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['someone_challenges'] = select == "Yes"

	def channel_id(self, token, config):
		while True:
			try:
				amount = int(input(f"[!] Enter the amount of channel id (E.g: 3) (Recent: {config[token]['channel_id']}): ")) + 1
				break
			except ValueError:
				print("[-] Must be a number")
		channel_id = []
		for num in range(1, amount):
			while True:
				try:
					x = int(input(f"[!] Enter the channel id {num}: "))
					break
				except ValueError:
					print("[-] Must be a number")
			channel_id.append(x)
		config[token]['channel_id'] = channel_id

	def captcha(self, data, name):
		print(f"[!] Solve {name} ({data['mode']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		data['mode'] = select == "Yes"
		if data['mode']:
			while True:
				try:
					attempts = int(input(f"[!] Enter the amount of resolve {name} (E.g: 3) (Recent: {data['attempts']}): "))
					break
				except ValueError:
					print("[-] Must be a number")
			data['attempts'] = attempts
			print(f"[!] Sleep after solve {name}")
			select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
			data['sleep_after_solve'] = select == "Yes"
			while True:
				try:
					amount = int(input(f"[!] Enter the amount of TwoCaptcha API for {name} solving system (E.g: 1) (Recent: {data['twocaptcha']}): ")) + 1
					break
				except ValueError:
					print("[-] Must be a number")
			twocaptcha = []
			for num in range(1, amount):
				x = input(f"[!] Enter the TwoCaptcha API {num}: ")
				twocaptcha.append(x)
			data['twocaptcha'] = twocaptcha

	def twocaptcha_balance(self, token, config):
		print(f"[!] Stop when TwoCaptcha balance is below any number (Recent: {config[token]['twocaptcha_balance']['mode']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['twocaptcha_balance']['mode'] = select == "Yes"
		if config[token]['twocaptcha_balance']['mode']:
			while True:
				try:
					amount = float(input(f"[!] Enter the TwoCaptcha balance wanna stop (E.g: 0.01) (Recent: {config[token]['twocaptcha_balance']['amount']}): "))
					break
				except ValueError:
					print("[-] Must be a number")
			config[token]['twocaptcha_balance']['amount'] = amount

	def quest(self, token, config):
		print(f"[!] Do quest (Recent: {config[token]['quest']['mode']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['quest']['mode'] = select == "Yes"
		if config[token]['quest']['mode']:
			print(f"[!] Do quest safely (Recent: {config[token]['quest']['safe']})")
			select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
			config[token]['quest']['safe'] = select == "Yes"
			while True:
				try:
					amount = int(input(f"[!] Enter the amount of quest channel id (E.g: 3) (Recent: {config[token]['quest']['channel_id']}): ")) + 1
					break
				except ValueError:
					print("[-] Must be a number")
			quest_channel_id = []
			for num in range(1, amount):
				while True:
					try:
						x = int(input(f"[!] Enter the quest channel id {num}: "))
						break
					except ValueError:
						print("[-] Must be a number")
				quest_channel_id.append(x)
			config[token]['quest']['channel_id'] = quest_channel_id

	def topgg(self, token, config):
		print(f"[!] Vote top.gg (Require chorme) (Recent: {config[token]['topgg']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['topgg'] = select == "Yes"

	def daily(self, token, config):
		print(f"[!] Claim daily (Recent: {config[token]['daily']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['daily'] = select == "Yes"

	def sleep(self, token, config):
		print(f"[!] Sleep after a certain time (Recent: {config[token]['sleep']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['sleep'] = select == "Yes"

	def grind(self, token, config):
		print(f"[!] What do you wanna farm")
		print(f"Recent: (OwO/UwU: {config[token]['grind']['owo']}/Hunt: {config[token]['grind']['hunt']}/Battle: {config[token]['grind']['battle']}/Quote: {config[token]['grind']['quote']})")
		select = inquirer.checkbox("Move ↑↓ and SPACE to choose, then ENTER to select", choices = ['OwO/UwU', 'Hunt', 'Battle', 'Quote'])
		config[token]['grind']['owo'] = "OwO/UwU" in select
		config[token]['grind']['hunt'] = "Hunt" in select
		config[token]['grind']['battle'] = "Battle" in select
		config[token]['grind']['quote'] = "Quote" in select

	def huntbot(self, token, config):
		print(f"[!] Claim and submit huntbot (Recent: {config[token]['huntbot']['claim_submit']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['huntbot']['claim_submit'] = select == "Yes"
		if config[token]['huntbot']['claim_submit']:
			print(f"[!] Upgrade huntbot (Recent: {config[token]['huntbot']['upgrade'] ['mode']})")
			select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
			config[token]['huntbot']['upgrade'] ['mode'] = select == "Yes"
			if config[token]['huntbot']['upgrade'] ['mode']:
				print(f"[!] Huntbot upgrade type (Recent: {config[token]['huntbot']['upgrade'] ['type']})")
				select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = ['Efficiency', 'Duration', 'Cost', 'Gain', 'Experience', 'Radar'])
				config[token]['huntbot']['upgrade'] ['type'] = select.lower()

	def gem(self, token, config):
		print(f"[!] Use gem (Recent: {config[token]['gem']['mode']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['gem']['mode'] = select == "Yes"
		if config[token]['gem']['mode']:
			print(f"[!] Sort gem min/max (Recent: {config[token]['gem']['sort']})")
			select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = ['Min', 'Max'])
			config[token]['gem']['sort'] = select.lower()
			print("[!] What do you want")
			print(f"Recent: (Use star gem: {config[token]['gem']['star']}/Open box: {config[token]['gem']['open_box']}/Open crate: {config[token]['gem']['open_crate']}/Open flootbox: {config[token]['gem']['open_flootbox']})")
			select = inquirer.checkbox("Move ↑↓ and SPACE to choose, then ENTER to select", choices = ['Use star gem', 'Open box', 'Open crate', 'Open flootbox'])
			config[token]['gem']['star'] = "Use star gem" in select
			config[token]['gem']['open_box'] = "Open box" in select
			config[token]['gem']['open_crate'] = "Open crate" in select
			config[token]['gem']['open_flootbox'] = "Open flootbox" in select

	def glitch(self, token, config):
		print(f"[!] Use gem when distorted animals are available (Recent: {config[token]['glitch']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['glitch'] = select == "Yes"

	def animals(self, token, config):
		print(f"[!] Sell/Sacrifice animals (Recent: {config[token]['animals']['mode']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['animals']['mode'] = select == "Yes"
		if config[token]['animals']['mode']:
			print(f"[!] Which type do you want (Recent: {config[token]['animals']['type']})")
			select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = ['Sell', 'Sacrifice'])
			config[token]['animals']['type'] = select.lower()
			print(f"[!] Which rank do you want (Recent: {config[token]['animals']['rank']})")
			select = inquirer.checkbox("Move ↑↓ and SPACE to choose, then ENTER to select", choices = ['Common', 'Uncommon', 'Rare', 'Epic', 'Special', 'Mythical', 'Legendary', 'Gem', 'Bot', 'Distorted', 'Fabled', 'Hidden'])
			if select:
				config[token]['animals']['rank'] = "".join(f"{x[0]} " for x in select)

	def caught(self, token, config):
		print(f"[!] Check and notify caught pets (Recent: {config[token]['caught']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['caught'] = select == "Yes"

	def gamble(self, token, config):
		print(f"[!] What do you wanna play")
		print(f"Recent: (Slot: {config[token]['gamble']['slot']['mode']}/Coinflip: {config[token]['gamble']['coinflip']['mode']}/Blackjack: {config[token]['gamble']['blackjack']['mode']})")
		select = inquirer.checkbox("Move ↑↓ and SPACE to choose, then ENTER to select", choices = ['Slot', 'Coinflip', 'Blackjack'])
		config[token]['gamble']['slot']['mode'] = "Slot" in select
		if config[token]['gamble']['slot']['mode']:
			self.slot_coinflip_blackjack(config[token]['gamble']['slot'], "slot")

		config[token]['gamble']['coinflip']['mode'] = "Coinflip" in select
		if config[token]['gamble']['coinflip']['mode']:
			self.slot_coinflip_blackjack(config[token]['gamble']['coinflip'], "coinflip")

		config[token]['gamble']['blackjack']['mode'] = "Blackjack" in select
		if config[token]['gamble']['blackjack']['mode']:
			self.slot_coinflip_blackjack(config[token]['gamble']['blackjack'], "blackjack")

	def slot_coinflip_blackjack(self, data, name):
		while True:
			try:
				bet = int(input(f"[!] Enter the amount of cowoncy to start bet {name} (E.g: 1) (Recent: {data['bet']}): "))
				break
			except ValueError:
				print("[-] Must be a number")
		data['bet'] = bet
		while True:
			try:
				rate = int(input(f"[!] Enter the rate number to multiply when lose on {name} (E.g: 2) (Recent: {data['rate']}): "))
				break
			except ValueError:
				print("[-] Must be a number")
		data['rate'] = rate
		while True:
			try:
				max = int(input(f"[!] Enter the amount of maximum bet {name} (E.g: 250000) (Recent: {data['max']}): "))
				break
			except ValueError:
				print("[-] Must be a number")
		data['max'] = max

	def pray_curse(self, token, config):
		print(f"[!] Pray/Curse (Recent: {config[token]['pray_curse']['mode']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['pray_curse']['mode'] = select == "Yes"
		if config[token]['pray_curse']['mode']:
			print(f"[!] Which type do you want (Recent: {config[token]['pray_curse']['type']})")
			select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = ['Pray', 'Curse'])
			config[token]['pray_curse']['type'] = select.lower()
			print(f"[!] {select} another user")
			select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
			if select == "Yes":
				while True:
					try:
						user_id = int(input(f"[!] Enter a user id to {select.lower()} (E.g: 123456789) (Recent: {config[token]['pray_curse']['user_id']}): "))
						break
					except ValueError:
						print("[-] Must be a number")
				config[token]['pray_curse']['user_id'] = user_id

	def entertainment(self, token, config):
		print("[!] What do you wanna farm")
		print(f"Recent: (Run: {config[token]['entertainment']['run']}/Pup: {config[token]['entertainment']['pup']}/Piku: {config[token]['entertainment']['piku']}/Common ring: {config[token]['entertainment']['common_ring']})")
		select = inquirer.checkbox("Move ↑↓ and SPACE to choose, then ENTER to select", choices = ['Run', 'Pup', 'Piku', 'Common ring'])
		config[token]['entertainment']['run'] = "Run" in select
		config[token]['entertainment']['pup'] = "Pup" in select
		config[token]['entertainment']['piku'] = "Piku" in select
		config[token]['entertainment']['common_ring'] = "Common ring" in select

	def command(self, token, config):
		print("[!] Discord command")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['command']['mode'] = select == "Yes"
		if config[token]['command']['mode']:
			while True:
				try:
					amount = int(input("[!] Enter the amount of owner id (E.g: 3): ")) + 1
					break
				except ValueError:
					print("[-] Must be a number")
			owner_id = []
			for num in range(1, amount):
				while True:
					try:
						x = int(input(f"[!] Enter the owner id {num}: "))
						break
					except ValueError:
						print("[-] Must be a number")
				owner_id.append(x)
			config[token]['command']['owner_id'] = owner_id

	def webhook(self, token, config):
		print(f"[!] Discord webhook (Recent: {config[token]['webhook']['mode']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['webhook']['mode'] = select == "Yes"
		if config[token]['webhook']['mode']:
			while True:
				try:
					amount = int(input(f"[!] Enter the amount of mentioner id (E.g: 3) (Recent: {config[token]['webhook']['mentioner_id']}): ")) + 1
					break
				except ValueError:
					print("[-] Must be a number")
			mentioner_id = []
			for num in range(1, amount):
				while True:
					try:
						x = int(input(f"[!] Enter the mentioner id {num}: "))
						break
					except ValueError:
						print("[-] Must be a number")
				mentioner_id.append(x)
			config[token]['webhook']['mentioner_id'] = mentioner_id
			config[token]['webhook']['url'] = input(f"[!] Enter the webhook url (E.g: discord.com/api/webhooks/123/abc) (Recent: {config[token]['webhook']['url']}): ")

	def log_file(self, token, config):
		print(f"[!] Log file (Recent: {config[token]['log_file']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['log_file'] = select == "Yes"

	def music_notification(self, token, config):
		print(f"[!] Music notification (Recent: {config[token]['music_notification']})")
		select = inquirer.list_input("Move ↑↓ and ENTER to select", choices = self.mode)
		config[token]['music_notification'] = select == "Yes"

	def error_retry_times(self, token, config):
		while True:
			try:
				times = int(input(f"[!] Enter error retry times (E.g: 10) (Recent: {config[token]['error_retry_times']}): "))
				break
			except ValueError:
				print("[-] Must be a number")
		config[token]['error_retry_times'] = times