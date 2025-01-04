import discord
import asyncio
import aiohttp
import re
import os
import io
import glob
import numpy
import time
import datetime
from PIL import Image

class Huntbot:
	def __init__(self, client):
		self.client = client

	async def solve_huntbot_captcha(self, captcha):
		checks = []
		check_images = glob.glob(self.client.data.config.huntbot['directory'])
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
			self.client.data.stat.sent_message += 1
			try:
				huntbot_message = await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [], ['Please include your password', 'Here is your password!', 'BACK IN', 'BACK WITH']), timeout = 10)
				if self.client.others.message(huntbot_message, True, True, [str(self.client.data.discord.nickname), 'Please include your password'], []):
					retry_huntbot = re.findall(r"(?<=Password will reset in )(\d+)", huntbot_message.content)
					retry_huntbot = int(int(retry_huntbot[0]) * 60)
					self.client.data.cooldown.huntbot = retry_huntbot + time.time()
					self.client.logger.info(f"Lost huntbot message, retry after {datetime.timedelta(seconds = retry_huntbot)}")
				elif self.client.data.available.selfbot and self.client.others.message(huntbot_message, True, True, [str(self.client.data.discord.nickname), 'Here is your password!'], []):
					await self.client.webhook.send(
						title = "🤖 HUNTBOT CAPTCHA 🤖",
						description = f"{self.client.data.config.emoji['arrow']}{huntbot_message.jump_url}",
						color = discord.Colour.random(),
						image = huntbot_message.attachments[0]
					)
					answer = await self.solve_huntbot_captcha(huntbot_message.attachments[0].url)
					await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}hb 1d {answer}")
					self.client.logger.info(f"Sent {self.client.data.discord.prefix}hb 1d {answer}")
					self.client.data.stat.sent_message += 1
					try:
						huntbot_verification_message = await self.client.wait_for("message", check = lambda message: self.client.others.message(message, True, True, [str(self.client.data.discord.nickname)], ['YOU SPENT', 'Wrong password']), timeout = 10)
						if "YOU SPENT" in huntbot_verification_message.content:
							self.client.logger.info(f"Submitted huntbot successfully")
							await self.client.webhook.send(
								title = "🎉 CORRECT SOLUTION 🎉",
								description = f"**{self.client.data.config.emoji['arrow']}Answer: {answer}**",
								color = discord.Colour.random(),
								thumnail = huntbot_message.attachments[0]
							)
						if "Wrong password" in huntbot_verification_message.content:
							self.client.logger.info(f"Submitted huntbot failed")
							await self.client.webhook.send(
								title = "🚫 INCORRECT SOLUTION 🚫",
								description = f"**{self.client.data.config.emoji['arrow']}Answer: {answer}**",
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
					await self.client.webhook.send(
						title = "📌 SUBMITTED HUNTBOT 📌",
						description = huntbot_message.content,
						color = discord.Colour.random()
					)
				elif "BACK WITH" in huntbot_message.content:
					self.client.logger.info(f"Claimed huntbot")
					await self.client.webhook.send(
						title = "📦 CLAIMED HUNTBOT 📦",
						description = huntbot_message.content,
						color = discord.Colour.random()
					)
					self.client.data.stat.claimed_huntbot += 1
					if self.client.data.available.selfbot and self.client.data.config.huntbot['upgrade']['mode']:
						await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}upgrade {self.client.data.config.huntbot['upgrade']['type']} all")
						self.client.logger.info(f"Sent {self.client.data.discord.prefix}upgrade {self.client.data.config.huntbot['upgrade']['type']} all")
						self.client.data.stat.sent_message += 1
			except asyncio.TimeoutError:
				self.client.logger.error(f"Couldn't get huntbot message")