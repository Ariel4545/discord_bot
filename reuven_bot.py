import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv
import math_helper

# Load environment variables
load_dotenv()

# Intents are required in discord.py 2.0+
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content
intents.members = True          # Required for on_member events and unban

bot_prefix = '^'
bot = commands.Bot(command_prefix=bot_prefix, intents=intents)
evaluator = math_helper.MathEvaluator()

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
async def add(ctx, a: float, b: float):
    """Adds two numbers."""
    res = a + b
    embed = discord.Embed(
        title="🔢 Addition",
        description=f"Expression: `{math_helper.format_num(a)} + {math_helper.format_num(b)}`",
        color=discord.Color.teal()
    )
    embed.add_field(name="Result", value=f"**{math_helper.format_num(res)}**", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def sub(ctx, a: float, b: float):
    """Subtracts two numbers."""
    res = a - b
    embed = discord.Embed(
        title="🔢 Subtraction",
        description=f"Expression: `{math_helper.format_num(a)} - {math_helper.format_num(b)}`",
        color=discord.Color.teal()
    )
    embed.add_field(name="Result", value=f"**{math_helper.format_num(res)}**", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def mul(ctx, a: float, b: float):
    """Multiplies two numbers."""
    res = a * b
    embed = discord.Embed(
        title="🔢 Multiplication",
        description=f"Expression: `{math_helper.format_num(a)} × {math_helper.format_num(b)}`",
        color=discord.Color.teal()
    )
    embed.add_field(name="Result", value=f"**{math_helper.format_num(res)}**", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def div(ctx, a: float, b: float):
    """Divides two numbers."""
    if b == 0:
        embed = discord.Embed(
            title="❌ Division Error",
            description="Cannot divide by zero!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        res = a / b
        embed = discord.Embed(
            title="🔢 Division",
            description=f"Expression: `{math_helper.format_num(a)} ÷ {math_helper.format_num(b)}`",
            color=discord.Color.teal()
        )
        embed.add_field(name="Result", value=f"**{math_helper.format_num(res)}**", inline=False)
        await ctx.send(embed=embed)


@bot.command()
async def calc(ctx, *, expression: str):
    """Safely evaluates a complex math expression (e.g., ^calc (2 + 3) * 4)."""
    try:
        res = evaluator.eval_expression(expression, ctx.channel.id)
        formatted_res = math_helper.format_num(res)
        
        embed = discord.Embed(
            title="🧮 Calculator",
            description=f"Input: `{expression}`",
            color=discord.Color.teal()
        )
        embed.add_field(name="Result", value=f"**{formatted_res}**", inline=False)
        embed.set_footer(text="Tip: Use 'ans' to reference this result in the next calculation!")
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Calculation Error",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command()
async def stats(ctx, *, numbers: str):
    """Performs complete statistical analysis on space-separated numbers."""
    try:
        num_list = [float(x) for x in numbers.split()]
        res = math_helper.analyze_stats(num_list)
        
        embed = discord.Embed(
            title="📊 Statistical Analysis",
            color=discord.Color.blue()
        )
        embed.add_field(name="🔢 Count (N)", value=str(res["count"]), inline=True)
        embed.add_field(name="➕ Sum (Σ)", value=str(math_helper.format_num(res["sum"])), inline=True)
        embed.add_field(name="📈 Mean (μ)", value=str(math_helper.format_num(res["mean"])), inline=True)
        
        embed.add_field(name="📉 Median", value=str(math_helper.format_num(res["median"])), inline=True)
        embed.add_field(name="🎯 Mode", value=res["mode"], inline=True)
        embed.add_field(name="📏 Range", value=f"{math_helper.format_num(res['min'])} to {math_helper.format_num(res['max'])}", inline=True)
        
        embed.add_field(name="🔄 Variance (s²)", value=str(math_helper.format_num(res["variance"])), inline=True)
        embed.add_field(name="📉 Std Dev (s)", value=str(math_helper.format_num(res["stddev"])), inline=True)
        embed.add_field(name="⚠️ Min / Max", value=f"Min: {math_helper.format_num(res['min'])}\nMax: {math_helper.format_num(res['max'])}", inline=True)
        
        await ctx.send(embed=embed)
    except ValueError:
        embed = discord.Embed(
            title="❌ Error",
            description="Please provide a valid list of space-separated numbers (e.g., `^stats 10 20 30`).",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command()
async def prime(ctx, number: int):
    """Checks if a number is prime and returns its factorization/divisors."""
    try:
        res = math_helper.factor_prime(number)
        
        embed = discord.Embed(
            title=f"🔢 Primality Check: {number}",
            color=discord.Color.purple()
        )
        status = "🟢 **PRIME!**" if res["is_prime"] else "🔴 **COMPOSITE (Not Prime)**"
        embed.add_field(name="Status", value=status, inline=False)
        
        if not res["is_prime"] and res["factors"]:
            factor_parts = []
            for p, e in sorted(res["factors"].items()):
                if e == 1:
                    factor_parts.append(f"{p}")
                else:
                    factor_parts.append(f"{p}^{e}")
            factorization_str = " × ".join(factor_parts)
            embed.add_field(name="Prime Factorization", value=f"`{factorization_str}`", inline=False)
            
        divs = res["divisors"]
        if len(divs) <= 30:
            divs_str = ", ".join(str(d) for d in divs)
        else:
            divs_str = ", ".join(str(d) for d in divs[:30]) + f"... (+ {len(divs) - 30} more)"
            
        embed.add_field(name=f"All Divisors ({len(divs)})", value=f"`{divs_str}`", inline=False)
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command()
async def solve(ctx, a: float, b: float, c: float = None):
    """Solves linear (ax + b = 0) or quadratic (ax^2 + bx + c = 0) equations."""
    try:
        res = math_helper.solve_equation(a, b, c)
        
        embed = discord.Embed(
            title="📐 Equation Solver",
            color=discord.Color.dark_gold()
        )
        
        if c is None:
            embed.description = f"Solving linear equation: `{math_helper.format_num(a)}x + {math_helper.format_num(b)} = 0`"
        else:
            embed.description = f"Solving quadratic equation: `{math_helper.format_num(a)}x² + {math_helper.format_num(b)}x + {math_helper.format_num(c)} = 0`"
            
        if isinstance(res, str):
            embed.add_field(name="Solution", value=f"**{res}**", inline=False)
        else:
            formatted_roots = [str(math_helper.format_num(root)) for root in res]
            if len(formatted_roots) == 1:
                embed.add_field(name="Root", value=f"x = **{formatted_roots[0]}**", inline=False)
            else:
                embed.add_field(name="Root 1 (x₁)", value=f"**{formatted_roots[0]}**", inline=True)
                embed.add_field(name="Root 2 (x₂)", value=f"**{formatted_roots[1]}**", inline=True)
                
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command()
async def convert(ctx, value: float, from_unit: str, to_unit: str):
    """Converts a value between compatible units (temp, length, weight, data)."""
    try:
        res = math_helper.convert_units(value, from_unit, to_unit)
        formatted_val = math_helper.format_num(value)
        formatted_res = math_helper.format_num(res)
        
        embed = discord.Embed(
            title="🔄 Unit Converter",
            description=f"Converted from `{from_unit}` to `{to_unit}`",
            color=discord.Color.dark_magenta()
        )
        embed.add_field(name="Input", value=f"{formatted_val} {from_unit}", inline=True)
        embed.add_field(name="Output", value=f"**{formatted_res} {to_unit}**", inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            title="❌ Conversion Error",
            description=str(e),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


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
        "**Available Commands:**\n\n"
        "**🔢 Standard Arithmetics**\n"
        "`^add <a> <b>` - Add two numbers\n"
        "`^sub <a> <b>` - Subtract two numbers\n"
        "`^mul <a> <b>` - Multiply two numbers\n"
        "`^div <a> <b>` - Divide two numbers (zero-safe)\n"
        "`^square <n>` - Square a number\n\n"
        "**🧮 Advanced Math Suite**\n"
        "`^calc <expr>` - Safely solve math expressions (e.g., `^(2+3)*4`, `^sin(pi/2)`, `^log(100, 10)`)\n"
        "  *Tip: References `ans` for the last calculation result in the channel!*\n"
        "`^stats <numbers>` - Detailed statistical profiling on space-separated data\n"
        "`^prime <number>` - Check primality, factorize, and list divisors (max 1B)\n"
        "`^solve <a> <b> [c]` - Solves linear ($ax+b=0$) & quadratic ($ax^2+bx+c=0$) equations\n"
        "`^convert <val> <from> <to>` - High-precision conversions (Temp, Length, Weight, Data)\n\n"
        "**🛠 Utility & Moderation**\n"
        "`^ping` - Check bot latency\n"
        "`^quote` - Get a random motivational quote\n"
        "`^clear <n>` - Purge messages\n"
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
async def square(ctx, arg: float):
    """Squares a number."""
    res = arg ** 2
    embed = discord.Embed(
        title="🔢 Square",
        description=f"Expression: `{math_helper.format_num(arg)}²`",
        color=discord.Color.teal()
    )
    embed.add_field(name="Result", value=f"**{math_helper.format_num(res)}**", inline=False)
    await ctx.send(embed=embed)


# Start the bot using the token from .env
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("Error: No DISCORD_TOKEN found in .env file.")
