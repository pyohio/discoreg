import asyncio
import os
from datetime import timedelta

import discord
import pytz
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from nextupbot.models import SessionNotification

DISCORD_BOT_TOKEN = settings.DISCORD_BOT_TOKEN
DISCORD_BOT_CHANNEL = settings.DISCORD_BOT_CHANNEL
DISCORD_BOT_OFFSET_SECONDS = settings.DISCORD_BOT_OFFSET_SECONDS


class BotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())
        self.embed = None
        self.notification = None

    async def build_embed(self):
        if self.notification is None:
            return
        sn = self.notification
        embed_kwargs = {}
        # if sn.color_hex_string:
        #     embed_kwargs["color"] = hex(int(sn.color_hex_string, 16))
        if sn.url:
            embed_kwargs["url"] = sn.url
        if sn.description:
            embed_kwargs["description"] = sn.description
        embed = discord.Embed(title=sn.title, **embed_kwargs)
        if sn.author_name:
            embed.set_author(name=sn.author_name)
        if sn.field_1_name:
            embed.add_field(name=sn.field_1_name, value=sn.field_1_value)
        self.embed = embed

    @sync_to_async
    def get_current_notification(self):
        # window = timedelta(seconds=5)
        # offset = timedelta(seconds=DISCORD_BOT_OFFSET_SECONDS)

        # now = timezone.now()
        sessions = SessionNotification.objects.all()
        self.notification = sessions[0]

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        print("Message from {0.author}: {0.content}".format(message))

    async def my_background_task(self):
        await self.wait_until_ready()
        counter = 0
        channel = self.get_channel(DISCORD_BOT_CHANNEL)
        while not self.is_closed():
            counter += 1
            await channel.send(timezone.now())
            # await self.get_current_notification()
            # if self.notification:
            #     await self.build_embed()
            #     await channel.send(embed=self.embed)
            # else:
            #     await channel.send("Nothin'")
            await asyncio.sleep(3)


class Command(BaseCommand):
    help = "Start a Discord bot to post notifications about upcoming events."

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        bot = BotClient()
        bot.run(DISCORD_BOT_TOKEN)

        # self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
