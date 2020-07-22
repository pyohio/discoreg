import asyncio
import os
import discord

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

from discoreg.registrations.models import EmailRole

class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))

    async def my_background_task(self):
        await self.wait_until_ready()
        counter = 0
        channel = self.get_channel(734788395024515153) # channel ID goes here
        while not self.is_closed():
            counter += 1
            await channel.send(counter)
            await asyncio.sleep(5) # task runs every 60 seconds


client = MyClient()
client.run(DISCORD_BOT_TOKEN)
