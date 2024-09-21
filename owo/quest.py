import random
import asyncio
import aiohttp

class Quest:
    def __init__(self, client):
        self.client = client
    """
    I have made use of aiohttp instead of requests, this way it should prevent blocking of code
    """
    async def send_message(self, token, channel_id, content):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"https://discord.com/api/v9/channels/{channel_id}/messages",
                    headers={"Authorization": token},
                    json={"content": content},
                    timeout=10
                ) as res:
                    if res.status != 200:
                        self.client.logger.error(f"Couldn't send message ({res.status}) | {token} | {channel_id}")
            except asyncio.TimeoutError:
                self.client.logger.error(f"Couldn't send message (Timeout)")
            except aiohttp.ClientConnectionError:
                self.client.logger.error(f"Couldn't send message (ConnectionError)")

    async def action_someone(self):
        if self.client.data.available.selfbot:
            action = random.choice(self.client.data.cmd.action)
            await self.client.data.discord.channel.send(f"{self.client.data.discord.prefix}{action} <@{self.client.data.bot.id}>")
            self.client.logger.info(f"Sent {self.client.data.discord.prefix}{action} <@{self.client.data.bot.id}>")
            self.client.data.stat.command += 1

    async def battle_friend(self, client):
        if client.data.available.selfbot:
            channel = random.choice(self.client.data.config.quest['channel_id'])
            content = f"owob <@{self.client.user.id}>"
            member = await self.client.get_channel(channel).guild.fetch_member(client.user.id)
            nickname = member.nick if member.nick else member.display_name
            await self.send_message(client.data.config.token, channel, content)
            client.logger.info(f"Sent {content}")
            client.data.stat.command += 1
            try:
                battle_message = await self.client.wait_for("message", check=lambda message: message.channel.id == channel and (
                    (self.client.conditions.message(message, True, False, [f'<@{self.client.user.id}>'], []) and message.embeds and "owo ab" in message.embeds[0].description) or
                     self.client.conditions.message(message, True, False, ['🚫', 'There is already a pending battle!', str(nickname)], [])
                ), timeout=10)
                if self.client.conditions.message(battle_message, True, False, ['🚫', 'There is already a pending battle!', str(nickname)], []):
                    self.client.logger.warning(f"There is already a pending battle, retry after 10 minutes")
                    await asyncio.sleep(600)
            except asyncio.TimeoutError:
                self.client.logger.error(f"Couldn't get battle message from {client.user.name}")

    async def cookie(self, client):
        if client.data.available.selfbot:
            channel = random.choice(self.client.data.config.quest['channel_id'])
            content = f"owocookie {self.client.user.id}"
            await self.send_message(client.data.config.token, channel, content)
            client.logger.info(f"Sent {content}")
            client.data.stat.command += 1

    async def pray(self, client):
        if client.data.available.selfbot:
            channel = random.choice(self.client.data.config.quest['channel_id'])
            content = f"owopray {self.client.user.id}"
            await self.send_message(client.data.config.token, channel, content)
            client.logger.info(f"Sent {content}")
            client.data.stat.command += 1

    async def curse(self, client):
        if client.data.available.selfbot:
            channel = random.choice(self.client.data.config.quest['channel_id'])
            content = f"owocurse {self.client.user.id}"
            await self.send_message(client.data.config.token, channel, content)
            client.logger.info(f"Sent {content}")
            client.data.stat.command += 1

    async def action_you(self, client):
        if client.data.available.selfbot:
            action = random.choice(client.data.cmd.action)
            channel = random.choice(self.client.data.config.quest['channel_id'])
            content = f"owo{action} <@{self.client.user.id}>"
            await self.send_message(client.data.config.token, channel, content)
            client.logger.info(f"Sent {content}")
            client.data.stat.command += 1
