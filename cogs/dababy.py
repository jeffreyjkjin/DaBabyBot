# DaBaby Commands for DaBabyBot

# Imports
import discord
from discord.ext import commands
import os
import random

# Intents
intents = discord.Intents().all()

# DaBaby
class DaBaby(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    
    # LETSGOOOOOOOO! command
    @commands.command()
    async def dababy(self, ctx):
        return await ctx.send(f"LETSGOOOOOOOO! {ctx.author.mention}")

    # Random DaBaby gif command
    @commands.command(aliases = ["letsgo"])
    async def dababygif(self, ctx):
        # Get random DaBaby gif
        gifs = os.listdir("./gifs")
        random_gif = random.choice(gifs)

        # Create embed
        file = discord.File("./gifs/" + random_gif)
        embed = discord.Embed(
            title = "LETSGOOOOOOOO!",
            colour = discord.Colour.dark_blue()
        )
        embed.set_image(url = f"attachment://{random_gif}")
        embed.set_footer(text = "You know it's Baby!")
        return await ctx.send(file = file, embed = embed)

# Setup
def setup(bot):
    bot.add_cog(DaBaby(bot))