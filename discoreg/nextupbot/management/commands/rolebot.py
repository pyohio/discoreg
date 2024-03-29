import asyncio
import logging
import discord
import arrow
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

DISCORD_BOT_TOKEN = settings.DISCORD_BOT_TOKEN
DISCORD_BOT_DEBUG_CHANNEL = settings.DISCORD_BOT_DEBUG_CHANNEL
DISCORD_BOT_EVENT_ROLE = settings.DISCORD_BOT_EVENT_ROLE
DISCORD_BOT_EVENT_START_DATETIME = arrow.get(settings.DISCORD_BOT_EVENT_START_DATETIME)
DISCORD_BOT_EVENT_END_DATETIME = arrow.get(settings.DISCORD_BOT_EVENT_END_DATETIME)


class BotClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        # self.bg_task = self.loop.create_task(self.test_loop())
        self.embed = None
        self.notification = None

    async def on_ready(self):
        print("Logged on as {0}!".format(self.user))

    async def on_message(self, message):
        debug_channel = self.get_channel(DISCORD_BOT_DEBUG_CHANNEL)

        if arrow.utcnow() < DISCORD_BOT_EVENT_START_DATETIME:
            print("Before event start, ignoring")
            return
        if arrow.utcnow() > DISCORD_BOT_EVENT_END_DATETIME:
            print("After event end, ignoring")
            return

        if message.author == self.user:
            return
        print("Message from {0.author}: {0.content}".format(message))
        # await debug_channel.send(
        #     "Saw message from {0.author} in {0.channel}: {0.content}".format(message)
        # )
        await self.assign_role(message.author)

    async def on_raw_reaction_add(self, payload):
        debug_channel = self.get_channel(DISCORD_BOT_DEBUG_CHANNEL)

        if arrow.utcnow() < DISCORD_BOT_EVENT_START_DATETIME:
            print("Before event start, ignoring")
            return
        if arrow.utcnow() > DISCORD_BOT_EVENT_END_DATETIME:
            print("After event end, ignoring")
            return

        print("Raw reaction from {0}: {1}".format(payload, payload))
        # await debug_channel.send(
        #     "Saw raw reaction from {0} on {1}: {2}".format(
        #         payload.user_id, payload.message_id, payload.emoji
        #     )
        # )
        await self.assign_role(payload.member)

    async def assign_role(self, member):
        debug_channel = self.get_channel(DISCORD_BOT_DEBUG_CHANNEL)
        role = member.guild.get_role(DISCORD_BOT_EVENT_ROLE)
        if role not in member.roles:
            await member.add_roles(role)
            await debug_channel.send(
                "Added role <@&{0.id}> to <@{1.id}>".format(role, member)
            )

    async def test_loop(self):
        await self.wait_until_ready()
        counter = 0
        channel = self.get_channel(DISCORD_BOT_DEBUG_CHANNEL)
        while not self.is_closed():
            counter += 1
            # await channel.send(timezone.now())
            await asyncio.sleep(5)


class Command(BaseCommand):
    help = "Start a Discord bot to post notifications about upcoming events."

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        logger.info("creating bot client")
        bot = BotClient()
        bot.run(DISCORD_BOT_TOKEN)
        logger.info("bot client ended")

        # self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
