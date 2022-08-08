import discord
from discord.ext import commands
import os
import requests
import json
import random

bot_prefix = "R"
client = commands.Bot(command_prefix=bot_prefix)

sad_msgs = ["Anger", "Emptiness", "Frustration", "Inadequacy", "Helplessness", "Fear", "Guilt", "Loneliness",
            "Depression",
            "Overwhelmed", "Resentment", "Failure", "Sadness", "Jealousy"]


def quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote


@client.event
async def on_ready():
    print("we have logged in as {0.user}".format(client))


@client.event
async def on_member_join(member):
    print(f'hello {member}, have fun!')


@client.event
async def on_member_remove(member):
    print(f'\'nothing lasts forever, goodbye {member}!\'')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("who is the goat?"):
        await message.channel.send("me😈")


@client.command()
async def help_me(ctx):
    if ctx.author == client.user:
        await ctx.send("available commands: \n quote - send a random motivational quote \n calc - calculate")


@client.command()
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount)

@client.command()
async def kick(ctx, member: discord.Member, * , reason=None):
    await member.kick(reason=reason)

@client.command()
async def ban(ctx, member: discord.Member, * , reason=None):
    await member.ban(reason=reason)


@client.command()
async def ping(ctx):
    await ctx.send(f"ping is equal to {round(client.latency * 1000)}ms")
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


@client.command()
async def square(ctx, arg):
    print(arg)
    await ctx.send(int(arg) ** 2)


client.run('OTcxMzc2NzczNzY4MDUyODE4.YnJnHg.fxdAgG7NWAseI1AOxS6CN1jVtfY')
