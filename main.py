import discord
import os
import IB

#connection to discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('The Important Boi is now running.'.format(client))

@client.event
async def on_message(message):
    # If the message was sent by the bot, ignore it.
    if message.author == client.user:
        return

    # Otherwise, check to see if it starts with $
    if message.content.startswith('$'):
        # Test message.
        #await message.channel.send("I'm thinking about it...")

        # Split the message's content into an array of arguments
        arg = message.content.split()
        
        # Then, call the IB function that deciphers the arguments and responds.
        await IB.readArgs(arg, message.channel, message.author.mention)

token = open('auth.txt').read()
client.run(token)
