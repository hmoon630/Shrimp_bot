import discord
from discord.ext import commands
import os
import traceback
import aiohttp

from const import Settings
from handlers import CommandFinder, DBManager, get_logger
from utils import Timer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ShrimpBot(commands.Bot):
    def __init__(self, logger=None, **kwargs):
        self.color = 0xFF421A
        self.logger = logger
        self.BASE_DIR = BASE_DIR
        self.command_finder = CommandFinder()
        self.db_manager = DBManager()
        super().__init__(command_prefix="", help_command=None, **kwargs)

    async def on_ready(self):
        activity = discord.Game(name="새우야 도움말")
        await self.change_presence(activity=activity)
        self.logger.info("Bot Started!")

    async def on_error(self, event_method, *args, **kwargs):
        exc_info = traceback.format_exc()
        self.logger.error(exc_info)

        url = Settings.error_webhook

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                url, adapter=discord.AsyncWebhookAdapter(session)
            )

            for i in range(0, len(exc_info), 2000):
                em = discord.Embed(
                    title=f"에러!", description=exc_info[i : i + 2000], colour=self.color,
                )

            await webhook.send(embed=em)

    async def on_message(self, message: discord.Message):
        await self.wait_until_ready()
        contents = message.content.split()
        author = message.author

        if not message.author.bot and contents:
            func = self.command_finder.get_function_by_message(message)

            if func is None:
                if message.guild is None:
                    return

                func = self.command_finder.get_function(None, command="custom_show")
            else:
                self.logger.info(
                    f"{author.name}#{author.discriminator} : {message.content}"
                )

            await func(self, message)
