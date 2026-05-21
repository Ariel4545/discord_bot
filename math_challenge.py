import discord
from discord.ext import commands
import random
import asyncio
import time

class MathChallenge(commands.Cog):
    """
    Interactive multiplayer speed-math challenges and server-wide math leaderboards.
    Implements the v0.05 milestone.
    """
    def __init__(self, bot):
        self.bot = bot
        # Active quizzes per channel: {channel_id: {"question": str, "answer": float, "difficulty": str, "start_time": float}}
        self.active_quizzes = {}
        # In-memory leaderboard: {guild_id: {user_id: {"score": int, "wins": int, "correct_answers": int}}}
        self.leaderboards = {}

    def generate_question(self, difficulty: str):
        """Generates random math questions based on difficulty."""
        difficulty = difficulty.lower()
        if difficulty == "easy":
            # Simple addition or subtraction
            a = random.randint(1, 50)
            b = random.randint(1, 50)
            op = random.choice(["+", "-"])
            expr = f"{a} {op} {b}"
            ans = a + b if op == "+" else a - b
            return expr, float(ans)
            
        elif difficulty == "medium":
            # Multiplication/Division combined with addition/subtraction
            a = random.randint(2, 12)
            b = random.randint(3, 15)
            c = random.randint(1, 20)
            op1 = random.choice(["*", "+", "-"])
            if op1 == "*":
                expr = f"{a} * {b} + {c}"
                ans = a * b + c
            else:
                expr = f"{a * b} / {a} - {c}"
                ans = b - c
            return expr, float(ans)
            
        else:  # Hard
            # Powers, roots, or linear equation solving
            choice = random.choice(["power", "root", "linear"])
            if choice == "power":
                a = random.randint(2, 5)
                b = random.randint(2, 4)
                c = random.randint(5, 50)
                expr = f"{a}**{b} - {c}"
                ans = (a ** b) - c
            elif choice == "root":
                squares = [4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144]
                sq = random.choice(squares)
                a = int(sq ** 0.5)
                b = random.randint(5, 30)
                expr = f"sqrt({sq}) * {b}"
                ans = a * b
            else:  # Linear solving: ax + b = c
                a = random.randint(2, 10)
                x = random.randint(1, 12)
                b = random.randint(1, 30)
                c = a * x + b
                expr = f"Solve for x: {a}x + {b} = {c}"
                ans = x
            return expr, float(ans)

    @commands.command(name="quiz")
    async def math_quiz(self, ctx, difficulty: str = "easy"):
        """Starts a competitive multiplayer speed-math challenge in the channel."""
        channel_id = ctx.channel.id
        if channel_id in self.active_quizzes:
            await ctx.send("🚨 There is already an active math quiz in this channel! Answer it first.")
            return

        difficulty = difficulty.lower()
        if difficulty not in ["easy", "medium", "hard"]:
            await ctx.send("❌ Invalid difficulty! Please choose: `easy`, `medium`, or `hard`.")
            return

        expr, ans = self.generate_question(difficulty)
        self.active_quizzes[channel_id] = {
            "question": expr,
            "answer": ans,
            "difficulty": difficulty,
            "start_time": time.time()
        }

        diff_colors = {
            "easy": discord.Color.green(),
            "medium": discord.Color.gold(),
            "hard": discord.Color.red()
        }

        embed = discord.Embed(
            title="⚡ Multiplayer Speed-Math Quiz!",
            description=f"Type the correct answer first to win points!\n\n"
                        f"Difficulty: **{difficulty.upper()}**\n"
                        f"Question: **`{expr}`**",
            color=diff_colors[difficulty]
        )
        embed.set_footer(text="Be the first to answer! You have 25 seconds.")
        await ctx.send(embed=embed)

        def check(m):
            if m.channel.id != channel_id or m.author.bot:
                return False
            try:
                val = float(m.content.strip())
                return abs(val - ans) < 1e-5
            except ValueError:
                return False

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=25.0)
        except asyncio.TimeoutError:
            self.active_quizzes.pop(channel_id, None)
            timeout_embed = discord.Embed(
                title="⏰ Time's Up!",
                description=f"Nobody answered in time! The correct answer was **{ans}**.",
                color=discord.Color.dark_gray()
            )
            await ctx.send(embed=timeout_embed)
            return

        # Calculate speed and scoring
        quiz_data = self.active_quizzes.pop(channel_id, None)
        time_taken = time.time() - quiz_data["start_time"]
        
        base_points = {"easy": 10, "medium": 20, "hard": 40}[difficulty]
        speed_bonus = max(0, int((25 - time_taken) * 0.8))
        total_points = base_points + speed_bonus

        # Update leaderboard record
        guild_id = ctx.guild.id
        user_id = msg.author.id
        
        if guild_id not in self.leaderboards:
            self.leaderboards[guild_id] = {}
        if user_id not in self.leaderboards[guild_id]:
            self.leaderboards[guild_id][user_id] = {"score": 0, "wins": 0, "correct_answers": 0}
            
        self.leaderboards[guild_id][user_id]["score"] += total_points
        self.leaderboards[guild_id][user_id]["wins"] += 1
        self.leaderboards[guild_id][user_id]["correct_answers"] += 1

        win_embed = discord.Embed(
            title="🎉 Correct Answer!",
            description=f"{msg.author.mention} answered correctly in **{time_taken:.2f}s**!",
            color=discord.Color.from_rgb(0, 229, 255)  # Glowing neon cyan
        )
        win_embed.add_field(name="Question", value=f"`{expr}`", inline=True)
        win_embed.add_field(name="Answer", value=f"**{ans}**", inline=True)
        win_embed.add_field(
            name="Points Awarded", 
            value=f"🏆 **+{total_points}** *(Base: {base_points}, Speed Bonus: {speed_bonus})*", 
            inline=False
        )
        win_embed.set_footer(text=f"Total Score: {self.leaderboards[guild_id][user_id]['score']} pts")
        
        await ctx.send(embed=win_embed)

    @commands.command(name="leaderboard")
    async def quiz_leaderboard(self, ctx):
        """Displays the top speed-math champions in this server."""
        guild_id = ctx.guild.id
        if guild_id not in self.leaderboards or not self.leaderboards[guild_id]:
            await ctx.send("📊 No scores recorded yet! Start a quiz using `^quiz`.")
            return

        sorted_players = sorted(
            self.leaderboards[guild_id].items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )[:10]

        embed = discord.Embed(
            title="🏆 Math Challenge Leaderboard",
            description="The fastest, sharpest minds in this server!",
            color=discord.Color.from_rgb(255, 215, 0)  # Gold
        )

        medals = ["🥇", "🥈", "🥉"]
        for idx, (user_id, stats) in enumerate(sorted_players):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"User {user_id}"
            prefix = medals[idx] if idx < 3 else f"#{idx+1}"
            embed.add_field(
                name=f"{prefix} {name}",
                value=f"Points: **{stats['score']}** | Correct: **{stats['correct_answers']}** | Wins: **{stats['wins']}**",
                inline=False
            )

        embed.set_footer(text="Think you've got what it takes? Run ^quiz hard to climb the ranks!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(MathChallenge(bot))
