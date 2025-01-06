import discord
import asyncio
import base64
import re
from aiohttp import ClientSession, CookieJar
from twocaptcha import TwoCaptcha

class Captcha:
	def __init__(self, client):
		self.client = client

	async def detect_image_captcha(self, message):
		if not self.client.data.available.captcha and self.client.others.message(message, True, False, ['⚠️'], []) and (message.channel.id == self.client.bot.dm_channel.id or str(self.client.user.name) in message.content) and message.attachments:
			real_message = re.sub(r"[^0-9a-zA-Z]", "", message.content)
			if "letter" not in real_message:
				return
			self.client.data.available.captcha = True
			self.client.data.available.selfbot = False
			self.client.logger.warning(f"!!! Image Captcha appears !!!")
			await self.client.webhook.send(
				content = self.client.data.discord.mention,
				title = "🚨 IMAGE CAPTCHA APPEARS 🚨",
				description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
				color = discord.Colour.random(),
				image = message.attachments[0]
			)
			if self.client.data.config.captcha['solve_image_captcha']['mode']:
				captcha = base64.b64encode(await message.attachments[0].read()).decode("utf-8")
				lenghth = real_message[real_message.find("letter") - 1]
				await self.solve_image_captcha(message.attachments[0], captcha, lenghth, [])
			else:
				await self.client.notification.notify()

	async def detect_hcaptcha(self, message):
		if not self.client.data.available.captcha and self.client.others.message(message, True, False, ['⚠️', f'<@{self.client.user.id}>'], []):
			real_message = re.sub(r"[^a-zA-Z]", "", message.content)
			if "link" not in real_message:
				return
			self.client.data.available.captcha = True
			self.client.data.available.selfbot = False
			self.client.logger.warning(f"!!! HCaptcha appears !!!")
			await self.client.webhook.send(
				content = self.client.data.discord.mention,
				title = "🚨 HCAPTCHA APPEARS 🚨",
				description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
				color = discord.Colour.random()
			)
			if self.client.data.config.captcha['solve_hcaptcha']['mode']:
				await self.solve_hcaptcha()
			else:
				await self.client.notification.notify()

	async def detect_unknown_captcha(self, message):
		if not self.client.data.available.captcha and self.client.others.message(message, True, False, ['⚠️', f'<@{self.client.user.id}>'], []) and not message.attachments:
			real_message = re.sub(r"[^a-zA-Z]", "", message.content)
			if "verify" not in real_message:
				return
			if any(text in message.content for text in ['letter', 'link']):
				return
			await self.client.notification.notify()
			self.client.data.available.captcha = True
			self.client.data.available.selfbot = False
			self.client.logger.warning(f"!!! Unknown Captcha !!!")
			await self.client.webhook.send(
				content = self.client.data.discord.mention,
				title = "🔒 UNKNOWN CAPTCHA 🔒",
				description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
				color = discord.Colour.random()
			)

	async def detect_problems(self, message):
		if self.client.others.message(message, True, False, ['You have been banned'], []) and (str(self.client.user.name) in message.content or message.channel.id == self.client.bot.dm_channel.id):
			await self.client.notification.notify()
			self.client.logger.warning(f"!!! You have been banned !!!")
			await self.client.webhook.send(
				content = self.client.data.discord.mention,
				title = "🔨 YOU HAVE BEEN BANNED 🔨",
				description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
				color = discord.Colour.random()
			)
			self.client.data.available.selfbot = False
		if self.client.others.message(message, True, False, [str(self.client.data.discord.nickname), 'don\'t have enough cowoncy!'], []) and not "you silly hooman" in message.content:
			await self.client.notification.notify()
			self.client.logger.warning(f"!!! Ran out of cowoncy !!!")
			await self.client.webhook.send(
				content = self.client.data.discord.mention,
				title = "💸 RAN OUT OF COWONCY 💸",
				description = f"{self.client.data.config.emoji['arrow']}{message.jump_url}",
				color = discord.Colour.random()
			)
			self.client.data.available.selfbot = False

	async def solve_image_captcha(self, image, captcha, lenghth, wrong_answer):
		result = None
		for api_key in self.client.data.config.captcha['solve_image_captcha']['twocaptcha']:
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
					await self.client.webhook.send(
						content = self.client.data.discord.mention,
						title = "⚙️ TWOCAPTCHA API ⚙️",
						description = f"**{self.client.data.config.emoji['arrow']}Error: {str(e)}**",
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
			await self.client.bot.send(result['code'])
			self.client.logger.info(f"Sent {result['code']}")
			self.client.data.stat.sent_message += 1
			try:
				captcha_verification = await self.client.wait_for("message", check = lambda message: message.channel.id == self.client.bot.dm_channel.id and any(text in message.content for text in ['👍', '🚫']), timeout = 10)
				if "👍" in captcha_verification.content:
					self.client.logger.info(f"Solved Image Captcha successfully")
					await self.client.webhook.send(
						title = "👍 CORRECT SOLUTION 👍",
						description = f"**{self.client.data.config.emoji['arrow']}Answer: {result['code']}**",
						color = discord.Colour.random(),
						thumnail = image
					)
					twocaptcha.report(result['captchaId'], True)
					self.client.data.stat.solved_captcha += 1
					self.client.data.available.captcha = False
					self.client.data.available.selfbot = True
					self.client.data.checking.captcha_attempt = 0
					if self.client.data.config.captcha['solve_image_captcha']['sleep_after_solve']:
						await self.client.sleep.sleep_after_certain_time(True)
				elif "🚫" in captcha_verification.content:
					self.client.logger.info(f"Solved Image Captcha failed")
					await self.client.webhook.send(
						content = self.client.data.discord.mention,
						title = "🚫 INCORRECT SOLUTION 🚫",
						description = f"**{self.client.data.config.emoji['arrow']}Answer: {result['code']}**",
						color = discord.Colour.random(),
						thumnail = image
					)
					twocaptcha.report(result['captchaId'], False)
					self.client.data.checking.captcha_attempt += 1
					if self.client.data.checking.captcha_attempt < int(self.client.data.config.captcha['solve_image_captcha']['attempt']):
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
					await self.client.webhook.send(
						content = self.client.data.discord.mention,
						title = "⚙️ SUMBIT HCAPTCHA OAUTH ⚙️",
						description = f"**{self.client.data.config.emoji['arrow']}Error: {res2.status}**",
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
				oauth = f"https://discord.com/api/v9/oauth2/authorize?response_type=code&redirect_uri=https%3A%2F%2Fowobot.com%2Fapi%2Fauth%2Fdiscord%2Fredirect&scope=identify%20guilds%20email%20guilds.members.read&client_id={self.client.bot.id}"
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
					'Referer': f"https://discord.com//oauth2/authorize?response_type=code&redirect_uri=https%3A%2F%2Fowobot.com%2Fapi%2Fauth%2Fdiscord%2Fredirect&scope=identify%20guilds%20email%20guilds.members.read&client_id={self.client.bot.id}",
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
						await self.client.webhook.send(
							content = self.client.data.discord.mention,
							title = "⚙️ GET HCAPTCHA OAUTH ⚙️",
							description = f"**{self.client.data.config.emoji['arrow']}Error: {await res.text()}**",
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
		for api_key in self.client.data.config.captcha['solve_hcaptcha']['twocaptcha']:
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
					await self.client.webhook.send(
						content = self.client.data.discord.mention,
						title = "⚙️ TWOCAPTCHA API ⚙️",
						description = f"**{self.client.data.config.emoji['arrow']}Error: {str(e)}**",
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
							await self.client.webhook.send(
								title = "👍 CORRECT SOLUTION 👍",
								description = f"**{self.client.data.config.emoji['arrow']}Solved successfully**",
								color = discord.Colour.random()
							)
							twocaptcha.report(result['captchaId'], True)
							self.client.data.stat.solved_captcha += 1
							self.client.data.available.captcha = False
							self.client.data.available.selfbot = True
							self.client.data.checking.captcha_attempt = 0
							if self.client.data.config.captcha['solve_hcaptcha']['sleep_after_solve']:
								await self.client.sleep.sleep_after_certain_time(True)
						else:
							self.client.logger.info(f"Solved HCaptcha failed")
							await self.client.webhook.send(
								content = self.client.data.discord.mention,
								title = "🚫 INCORRECT SOLUTION 🚫",
								description = f"**{self.client.data.config.emoji['arrow']}Solved failed**",
								color = discord.Colour.random()
							)
							twocaptcha.report(result['captchaId'], False)
							self.client.data.checking.captcha_attempt += 1
							if self.client.data.checking.captcha_attempt < int(self.client.data.config.captcha['solve_hcaptcha']['attempt']):
								await self.solve_hcaptcha()
							else:
								await self.client.notification.notify()

	async def check_twocaptcha_balance(self, twocaptcha_api_keys):
		if self.client.data.available.selfbot and self.client.data.config.captcha['solve_image_captcha']['mode'] and not self.client.data.available.captcha:
			for api_key in twocaptcha_api_keys:
				twocaptcha = TwoCaptcha(
					server="2captcha.com",
					apiKey=str(api_key),
					defaultTimeout=300,
					pollingInterval=5
				)
				for _ in range(int(self.client.data.config.error_retry_times)):
					try:
						balance = twocaptcha.balance()
						if balance >= self.client.data.config.captcha['pause_if_twocaptcha_balance_is_low']['amount']:
							return
					except Exception as e:
						if str(e) in {"ERROR_KEY_DOES_NOT_EXIST", "ERROR_WRONG_USER_KEY"}:
							break
						await asyncio.sleep(20)
				else:
					continue
				break
			else:
				await self.client.notification.notify()
				self.client.logger.warning(f"TwoCaptcha API is invalid or has under {self.client.data.config.captcha['pause_if_twocaptcha_balance_is_low']['amount']}$")
				await self.client.webhook.send(
					content = self.client.data.discord.mention,
					title = "💸 NOT ENOUGH BALANCE 💸",
					description = f"**{self.client.data.config.emoji['arrow']}TwoCaptcha API is invalid or has under {self.client.data.config.captcha['pause_if_twocaptcha_balance_is_low']['amount']}$**",
					color = discord.Colour.random()
				)
				self.client.data.available.selfbot = False