import re
import random
import asyncio

class Gamble:
	def __init__(self, client):
		self.client = client

	async def check_slot(self, message):
		if self.client.data.available.selfbot and self.client.others.message(message, True, True, [str(self.client.data.discord.nickname)], []):
			if "won nothing" in message.content:
				self.client.logger.info(f"Slot turn lost {self.client.data.current_gamble_bet.slot} cowoncy")
				self.client.data.stat.gambled_cowoncy -= self.client.data.current_gamble_bet.slot
				self.client.data.current_gamble_bet.slot *= int(self.client.data.config.gamble['slot']['rate'])
			if "<:eggplant:417475705719226369> <:eggplant:417475705719226369> <:eggplant:417475705719226369>" in message.content:
				self.client.logger.info(f"Slot turn draw {self.client.data.current_gamble_bet.slot} cowoncy")
			if "<:heart:417475705899712522> <:heart:417475705899712522> <:heart:417475705899712522>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot} cowoncy (x2)")
				self.client.data.stat.gambled_cowoncy += self.client.data.current_gamble_bet.slot
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			if "<:cherry:417475705178161162> <:cherry:417475705178161162> <:cherry:417475705178161162>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot * 2} cowoncy (x3)")
				self.client.data.stat.gambled_cowoncy += self.client.data.current_gamble_bet.slot * 2
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			if "<:cowoncy:417475705912426496> <:cowoncy:417475705912426496> <:cowoncy:417475705912426496>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot * 3} cowoncy (x4)")
				self.client.data.stat.gambled_cowoncy += self.client.data.current_gamble_bet.slot * 3
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			if "<:o_:417475705899843604> <:w_:417475705920684053> <:o_:417475705899843604>" in message.content:
				self.client.logger.info(f"Slot turn won {self.client.data.current_gamble_bet.slot * 9} cowoncy (x10)")
				self.client.data.stat.gambled_cowoncy += self.client.data.current_gamble_bet.slot * 9
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])

	async def check_coinflip(self, message):
		if self.client.data.available.selfbot and self.client.others.message(message, True, True, [str(self.client.data.discord.nickname)], []):
				if "you lost" in message.content:
					self.client.logger.info(f"Coinflip turn lost {self.client.data.current_gamble_bet.coinflip} cowoncy")
					self.client.data.stat.gambled_cowoncy -= self.client.data.current_gamble_bet.coinflip
					self.client.data.current_gamble_bet.coinflip *= int(self.client.data.config.gamble['coinflip']['rate'])
				if "you won" in message.content:
					self.client.logger.info(f"Coinflip turn won {self.client.data.current_gamble_bet.coinflip} cowoncy")
					self.client.data.stat.gambled_cowoncy += self.client.data.current_gamble_bet.coinflip
					self.client.data.current_gamble_bet.coinflip = int(self.client.data.config.gamble['coinflip']['bet'])

	async def play_slot(self):
		if self.client.data.available.selfbot:
			if self.client.data.current_gamble_bet.slot >= int(self.client.data.config.gamble['slot']['max']):
				self.client.data.current_gamble_bet.slot = int(self.client.data.config.gamble['slot']['bet'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}s {self.client.data.current_gamble_bet.slot}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}s {self.client.data.current_gamble_bet.slot}")
			self.client.data.stat.sent_message += 1

	async def play_coinflip(self):
		if self.client.data.available.selfbot:
			if self.client.data.current_gamble_bet.coinflip >= int(self.client.data.config.gamble['coinflip']['max']):
				self.client.data.current_gamble_bet.coinflip = int(self.client.data.config.gamble['coinflip']['bet'])
			side = random.choice(['h', 't'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}cf {self.client.data.current_gamble_bet.coinflip} {side}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}cf {self.client.data.current_gamble_bet.coinflip} {side}")
			self.client.data.stat.sent_message += 1

	async def play_blackjack(self):
		if self.client.data.available.selfbot:
			if self.client.data.current_gamble_bet.blackjack >= int(self.client.data.config.gamble['blackjack']['max']):
				self.client.data.current_gamble_bet.blackjack = int(self.client.data.config.gamble['blackjack']['bet'])
			await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}bj {self.client.data.current_gamble_bet.blackjack}")
			self.client.logger.info(f"Sent {self.client.data.discord.prefix}bj {self.client.data.current_gamble_bet.blackjack}")
			self.client.data.stat.sent_message += 1
			self.client.data.available.blackjack = False
			while not self.client.data.available.blackjack:
				blackjack_message = None
				await asyncio.sleep(random.randint(2, 3))
				async for message in self.client.data.discord.channel.history(limit = 10):
					if self.client.others.message(message, True, True, [], []) and message.embeds and str(self.client.user.name) in message.embeds[0].author.name and "play blackjack" in message.embeds[0].author.name:
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
						self.client.data.stat.gambled_cowoncy += self.client.data.current_gamble_bet.blackjack
						self.client.data.current_gamble_bet.blackjack = int(self.client.data.config.gamble['blackjack']['bet'])
						self.client.data.available.blackjack = True
					elif "You lost" in blackjack_message.embeds[0].footer.text:
						self.client.logger.info(f"Blackjack turn lost {self.client.data.current_gamble_bet.blackjack} cowoncy")
						self.client.data.stat.gambled_cowoncy -= self.client.data.current_gamble_bet.blackjack
						self.client.data.current_gamble_bet.blackjack *= int(self.client.data.config.gamble['blackjack']['rate'])
						self.client.data.available.blackjack = True
					elif "You tied" in blackjack_message.embeds[0].footer.text or "You both bust" in blackjack_message.embeds[0].footer.text:
						self.client.logger.info(f"Blackjack turn draw {self.client.data.current_gamble_bet.blackjack} cowoncy")
						self.client.data.available.blackjack = True
				else:
					break