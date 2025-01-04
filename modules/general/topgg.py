
import discord
import asyncio

from aiohttp import ClientSession
from selenium_driverless import webdriver
from selenium.webdriver.common.by import By

class Topgg:
	def __init__(self, client):
		self.client = client

	async def get_oauth(self, oauth, oauth_req):
		retry_times = 0
		while retry_times < int(self.client.data.config.error_retry_times):
			async with ClientSession() as session:
				payload = {"permissions": "0", "authorize": True}
				headers = {
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
					"Accept": "*/*",
					"Accept-Language": "en-US,en;q=0.5",
					"Accept-Encoding": "gzip, deflate, br",
					"Content-Type": "application/json",
					"Authorization": self.client.data.config.token,
					"X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEwOS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzExMS4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTExLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTg3NTk5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
					"X-Debug-Options": "bugReporterEnabled",
					"Origin": "https://discord.com",
					"Connection": "keep-alive",
					"Referer": oauth,
					"Sec-Fetch-Dest": "empty",
					"Sec-Fetch-Mode": "cors",
					"Sec-Fetch-Site": "same-origin",
					"TE": "trailers",
				}
				async with session.post(oauth_req, headers = headers, json = payload) as res:
					if res.status == 200:
						response = await res.json()
						result_session = response.get("location")
						return result_session
					else:
						self.client.logger.error(f"Getting top.gg oauth has the problem | {await res.text()}")
						await self.client.webhook.send(
							content = self.client.data.discord.mention,
							title = "⚙️ TOP.GG OAUTH ⚙️",
							description = f"**{self.client.data.emoji.arrow}Error: {await res.text()}**",
							color = discord.Colour.random()
						)
			retry_times += 1
			await asyncio.sleep(20)
		else:
			await self.client.notification.notify()

	async def vote_topgg(self):
		options = webdriver.ChromeOptions()
		if not self.client.data.config.vote_topgg['display']:
			options.headless = True
		options.add_argument("--start-maximized")
		oauth = "https://discord.com/oauth2/authorize?scope=identify%20guilds%20email&redirect_uri=https%3A%2F%2Ftop.gg%2Flogin%2Fcallback&response_type=code&client_id=422087909634736160&state=Lw=="
		oauth_req = (oauth.split("/oauth2")[0] + "/api/v9/oauth2" + oauth.split("/oauth2")[1])
		topgg = await self.get_oauth(oauth, oauth_req)
		async with webdriver.Chrome(options = options) as driver:
			await driver.get(topgg, wait_load = True, timeout = 5)
			self.client.logger.info(f"Loaded top.gg homepage")
			await asyncio.sleep(20)
			button = await driver.find_element(by = By.XPATH, value = f'//a[@href="/bot/{self.client.bot.id}/vote"]')
			await button.click()
			self.client.logger.info(f"Loaded {self.client.bot.display_name} vote page on top.gg")
			await asyncio.sleep(20)
			button = await driver.find_element(by=By.XPATH, value=".//button[contains(text(),'Vote')]")
			await button.click()
			self.client.logger.info(f"Voted {self.client.bot.display_name} on top.gg")
			await asyncio.sleep(20)