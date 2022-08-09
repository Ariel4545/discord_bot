import discord
from discord.ext import commands
import requests
import json


bot_prefix = '^'
bot = commands.Bot(command_prefix=bot_prefix)

sad_msgs = ["Anger", "Emptiness", "Frustration", "Inadequacy", "Helplessness", "Fear", "Guilt", "Loneliness",
            "Depression",
            "Overwhelmed", "Resentment", "Failure", "Sadness", "Jealousy"]


@bot.command()
async def quote(ctx):
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    random_quote = json_data[0]['q'] + " -" + json_data[0]['a']
    await ctx.channel.send(random_quote)


@bot.event
async def on_ready():
    print(f"successfully logged in as {bot.user}")


@bot.event
async def on_member_join(member):
    print(f'hello {member}, have fun!')


@bot.event
async def on_member_remove(member):
    print(f'\'nothing lasts forever, goodbye {member}!\'')

@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a + b)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith("who is the goat?"):
        await message.channel.send("me😈")


@bot.command()
async def help_me(ctx):
    await ctx.send("available commands: \n quote - send a random motivational quote \n calc - calculate")


@bot.command()
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount)


@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'kicked {member.mention}')

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'banned {member.mention}')


@bot.command()
async def unban(ctx, *,member):
    banned_users = await ctx.guild.bans()
    member_name, member_tag = member.split('#')
    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_tag):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
            return


@bot.command()
async def ping(ctx):
    await ctx.send(f"ping is equal to {round(bot.latency * 1000)}ms")
    # if message.content.startswith(f"{prefix}quote"):
    #     random_quote = quote()
    #     await message.channel.send(random_quote)
    #
    # expiration = str(message.content.startswith(f"{prefix}calc"))
    # calculate = expiration.replace(f"{prefix}calc", "")
    # if expiration:
    #     await message.channel.send(f"the answer is:{eval(calculate)}")
    #
    # if message.content == 'hello':
    #     await message.channel.send(f'Hi {message.author}')
    # if message.content == 'bye':
    #     await message.channel.send(f'Goodbye {message.author}')
    #
    # if any(sad_msg in message.content for sad_msg in sad_msgs):
    #     await message.channel.send(random.choice(sad_msgs))


@bot.command()
async def square(ctx, arg):
    print(arg)
    await ctx.send(int(arg) ** 2)


bot.run('OTcxMzc2NzczNzY4MDUyODE4.YnJnHg.fxdAgG7NWAseI1AOxS6CN1jVtfY')

