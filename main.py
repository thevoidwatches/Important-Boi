import discord
import asyncio
import IB
from discord.ext import commands

#connection to discord
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print('The Important Boi is now running.')

@bot.event
async def setup_hook():
    await bot.tree.sync()

@bot.event
async def on_message(message):
    # If the message was sent by the bot, ignore it.
    if message.author == bot.user:
        return

    # Check to see if it starts with $ for legacy text commands
    if message.content.startswith('$'):
        # Split the message's content into an array of arguments
        arg = message.content.split()

        # Then, call the IB function that deciphers the arguments and responds.
        await IB.readArgs(arg, message.channel, message.author.mention)

    # Process commands so cog-based commands also work
    await bot.process_commands(message)

async def main():
    async with bot:
        await bot.load_extension("commands_dicebot")
        await bot.load_extension("commands_mnm")
        token = open('auth.txt').read().strip()
        await bot.start(token, reconnect=True)

asyncio.run(main())
