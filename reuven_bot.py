import discord
from discord.ext import commands
import os
import requests
import json
import random


prefix = "^"
client = commands.Bot(command_prefix=prefix)

tomer = ["Anger", "Emptiness", "Frustration", "Inadequacy", "Helplessness", "Fear", "Guilt", "Loneliness", "Depression",
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
async def on_message(message):
    if message.content.startswith(prefix):
        if message.content.startswith(f"{prefix}help"):
            await message.channel.send(
                "available commands: \n quote - send a random motivational quote \n calc - calculate")

        if message.content.startswith(f"{prefix}quote"):
            random_quote = quote()
            await message.channel.send(random_quote)

        expiration = str(message.content.startswith(f"{prefix}calc"))
        calculate = expiration.replace(f"{prefix}calc", "")
        if expiration:
            await message.channel.send(f"the answer is:{eval(calculate)}")

        if message.content == 'hello':
            await message.channel.send(f'Hi {message.author}')
        if message.content == 'bye':
            await message.channel.send(f'Goodbye {message.author}')

    if any(tom in message.content for tom in tomer):
        await message.channel.send(random.choice(tomer))


@client.command()
async def square(ctx, arg):
    print(arg)
    await ctx.send(int(arg) ** 2)


client.run('OTcxMzc2NzczNzY4MDUyODE4.YnJnHg.fxdAgG7NWAseI1AOxS6CN1jVtfY')
