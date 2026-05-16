import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Intents are required in discord.py 2.0+
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True          # Required for on_member events and unban

bot_prefix = '^'
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)

sad_msgs = ["Anger", "Emptiness", "Frustration", "Inadequacy", "Helplessness", "Fear", "Guilt", "Loneliness",
            "Depression", "Overwhelmed", "Resentment", "Failure", "Sadness", "Jealousy"]


@bot.command()
async def quote(ctx):
    """Sends a random motivational quote."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://zenquotes.io/api/random") as response:
            if response.status == 200:
                json_data = await response.json()
                random_quote = f"{json_data[0]['q']} -{json_data[0]['a']}"
                await ctx.send(random_quote)
            else:
                await ctx.send("Could not fetch a quote at the moment.")


@bot.event
async def on_ready():
    print(f"Successfully logged in as {bot.user}")


@bot.event
async def on_member_join(member):
    print(f'Hello {member}, have fun!')


@bot.event
async def on_member_remove(member):
    print(f'Nothing lasts forever, goodbye {member}!')


@bot.command()
async def add(ctx, a: int, b: int):
    """Adds two numbers."""
    await ctx.send(a + b)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower().startswith("who is the goat?"):
        await message.channel.send("me😈")

    # This is required to allow commands to work when on_message is defined
    await bot.process_commands(message)


@bot.command()
async def help_me(ctx):
    """Shows available commands."""
    help_text = (
        "**Available Commands:**\n"
        "`^quote` - Send a random motivational quote\n"
        "`^add <n1> <n2>` - Add two numbers\n"
        "`^square <n>` - Square a number\n"
        "`^ping` - Check bot latency\n"
        "`^clear <amount>` - Purge messages\n"
        "`^kick <member>` - Kick a user\n"
        "`^ban <member>` - Ban a user\n"
        "`^unban <user>` - Unban a user"
    )
    await ctx.send(help_text)


@bot.command()
async def clear(ctx, amount: int = 1):
    """Purges a specified number of messages."""
    await ctx.channel.purge(limit=amount + 1)  # +1 to include the command itself


@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kicks a member."""
    await member.kick(reason=reason)
    await ctx.send(f'Kicked {member.mention}')


@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    """Bans a member."""
    await member.ban(reason=reason)
    await ctx.send(f'Banned {member.mention}')


@bot.command()
async def unban(ctx, *, member):
    """Unbans a user by name or handle."""
    banned_users = [entry async for entry in ctx.guild.bans()]
    
    for ban_entry in banned_users:
        user = ban_entry.user
        # Check if input matches username#discriminator or just username
        if member == str(user) or member == user.name:
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.name}')
            return
    
    await ctx.send(f"Could not find user '{member}' in the ban list.")


@bot.command()
async def ping(ctx):
    """Checks the bot's latency."""
    await ctx.send(f"Ping is equal to {round(bot.latency * 1000)}ms")


@bot.command()
async def square(ctx, arg: int):
    """Squares a number."""
    await ctx.send(arg ** 2)


# Start the bot using the token from .env
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("Error: No DISCORD_TOKEN found in .env file.")
