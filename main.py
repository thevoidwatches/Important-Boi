import discord
import os
import IB
#from keep_alive import keep_alive

#connection to discord
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

#registers an event
@client.event
async def on_ready():
    print('Now running.'.format(client))

async def on_error():
    print('An unknown error has occured.'.format(client))

@client.event
async def on_message(message):
    # If the message was sent by the bot, ignore it.
    if message.author == client.user:
        return

    # Otherwise, check to see if it starts with $
    if message.content.startswith('$'):
        #Test message.
        #await message.channel.send("I'm thinking about it...")

        #Split the message.content into a set of arguments
        arg = message.content.split()
        
        #call a function that deciphers the arguments
        await IB.readArgs(arg, message.channel, message.author.mention)

#keep_alive()
token ='OTAzNDg3Mzg2MjIxMTUwMjA4.YXtsMg.zzS8AtLWj0vF1qXu2UqqTAXUxOA'
client.run(token)
