import disnake
from disnake.ext import commands
import os
import asyncio

bot = commands.Bot(
    command_prefix='!',
    help_command=None,
    intents=disnake.Intents.all(),
    test_guilds=[id_guild]
)


async def load():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")


async def main():
    await load()

asyncio.run(main())
bot.run("TOKEN")
