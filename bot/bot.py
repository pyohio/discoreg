import os
import discord

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]


class MyClient(discord.Client):
    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))


client = MyClient()
client.run(DISCORD_BOT_TOKEN)
