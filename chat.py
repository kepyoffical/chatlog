import discord
from discord.ext import commands, tasks
import asyncio
import re
import os
from dotenv import load_dotenv

# .env betöltése
load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Chatlog fájl elérési útja
CHATLOG_FILE = 'server.log'

# Eseményekhez regex (csatlakozás, kilépés, halál, chat)
JOIN_REGEX = re.compile(r'(.+) joined the game')
QUIT_REGEX = re.compile(r'(.+) left the game')
DEATH_REGEX = re.compile(r'(.+) died')
CHAT_REGEX = re.compile(r'<(.+)> (.+)')

# Fájlból olvasás pozíciója
last_position = 0

# Beállított chat log csatorna
chatlog_channel_id = None

@bot.event
async def on_ready():
    print(f'Bejelentkezve: {bot.user}')
    read_chatlog.start()  # elindítjuk a figyelést

@tasks.loop(seconds=2)
async def read_chatlog():
    global last_position, chatlog_channel_id
    if chatlog_channel_id is None:
        return  # nincs beállítva csatorna

    if not os.path.exists(CHATLOG_FILE):
        return

    with open(CHATLOG_FILE, 'r', encoding='utf-8') as f:
        f.seek(last_position)
        lines = f.readlines()
        last_position = f.tell()

    channel = bot.get_channel(chatlog_channel_id)
    if not channel:
        return

    for line in lines:
        line = line.strip()
        if match := JOIN_REGEX.search(line):
            await channel.send(f'✅ **{match.group(1)}** csatlakozott a szerverre!')
        elif match := QUIT_REGEX.search(line):
            await channel.send(f'❌ **{match.group(1)}** kilépett a szerverről!')
        elif match := DEATH_REGEX.search(line):
            await channel.send(f'💀 **{match.group(1)}** meghalt!')
        elif match := CHAT_REGEX.search(line):
            await channel.send(f'💬 **{match.group(1)}:** {match.group(2)}')

# Parancs a Discordon a chatlog csatorna beállításához
@bot.command()
async def setchatlog(ctx):
    global chatlog_channel_id
    chatlog_channel_id = ctx.channel.id
    await ctx.send(f'Chat log csatorna beállítva ide: {ctx.channel.mention}')

bot.run(TOKEN)
