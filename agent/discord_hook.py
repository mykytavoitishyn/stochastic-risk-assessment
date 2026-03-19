"""Discord hook: receive messages in a channel and reply via the market agent."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from dotenv import load_dotenv
from agent import run, load_skills

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

# Per-channel conversation history
histories: dict[int, list] = {}
skills = {}


@bot.event
async def on_ready():
    global skills
    skills = load_skills()
    print(f"Logged in as {bot.user}. Skills: {list(skills)}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    text = message.content.strip()
    if not text:
        return

    # Resolve skill shortcut
    if text.startswith("/"):
        name = text[1:].lower()
        if name not in skills:
            await message.channel.send(f"Unknown skill. Available: {', '.join('/' + k for k in skills)}")
            return
        text = skills[name]

    history = histories.setdefault(message.channel.id, [])

    async with message.channel.typing():
        response, histories[message.channel.id] = run(text, history)

    # Discord has a 2000-char limit per message
    for chunk in [response[i:i+2000] for i in range(0, len(response), 2000)]:
        await message.channel.send(chunk)


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_BOT_TOKEN not set in .env")
    bot.run(TOKEN)
