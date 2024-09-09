import discord
from discord.ext import commands
import re
from collections import defaultdict
import time

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = discord.Bot(intents=intents)

phone_number_pattern = re.compile(r'\+?[0-9]{7,}')
email_pattern = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
ip_address_pattern = re.compile(r'\b\d{1,3}(?:\.\d{1,3}){3}\b')
credit_card_pattern = re.compile(r'\b(?:\d[ -]*?){13,19}\b')

LOG_CHANNEL_ID = 123456787890 # Log Channel For Sensitive Data

user_message_count = defaultdict(lambda: {'count': 0, 'last_message': '', 'last_time': 0})

SPAM_RESET_TIME = 60
SPAM_LIMIT = 10

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author.guild_permissions.administrator or message.author.id == message.guild.owner_id:

        return

    print(f"Received message: {message.content}")

    user_data = user_message_count[message.author.id]
    current_time = time.time()

    if message.content == user_data['last_message']:
        if current_time - user_data['last_time'] < SPAM_RESET_TIME:
            user_data['count'] += 1
        else:
            user_data['count'] = 1
    else:
        user_data['count'] = 1

    user_data['last_message'] = message.content
    user_data['last_time'] = current_time

    if user_data['count'] > SPAM_LIMIT:
        print(f"{message.author} is spamming. Banning...")
        await message.channel.send(f"{message.author.mention} has been banned for spamming.")
        await message.guild.ban(message.author, reason="Spamming")

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"Banned {message.author} for spamming: {message.content}")

        

    if (phone_number_pattern.search(message.content) or
        email_pattern.search(message.content) or
        ip_address_pattern.search(message.content) or
        credit_card_pattern.search(message.content)):

        print(f"Sensitive data detected in message: {message.content}")
        await message.delete()

        await message.channel.send(f"{message.author.mention}, Stop Sharing Sensitive Information!")
          
           
          
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"Deleted message from {message.author}: {message.content}")
        else:
            print(f"Log channel not found: {LOG_CHANNEL_ID}")


# bot token

bot.run('')
