# DaBabyBot for Discord

# Imports
import discord
from discord.ext import commands
import os

# Intents
intents = discord.Intents().all()

# Bot setup
dababy = commands.Bot(command_prefix = "$", intents = intents)

# Start up
@dababy.event
async def on_ready():
    await dababy.change_presence(
        status = discord.Status.online, 
        activity = discord.Activity(type = discord.ActivityType.listening, name = "VIBEZ - DaBaby")
        )
    print("{0.user} IS RUNNING! LETSGOOOOOOOO!".format(dababy))

    # Developer commands
    # Load cogs
    @dababy.command()
    @commands.has_role("Developer")
    async def load(ctx, extension):
        dababy.load_extension(f"cogs.{extension}")
        await ctx.send(f"***{extension}*** cog has been loaded!")

    # Unload cogs
    @dababy.command()
    @commands.has_role("Developer")
    async def unload(ctx, extension):
        dababy.unload_extension(f"cogs.{extension}")
        await ctx.send(f"***{extension}*** cog has been unloaded!")

    # Reload cogs
    @dababy.command()
    @commands.has_role("Developer")
    async def reload( ctx, extension):
        dababy.unload_extension(f"cogs.{extension}")
        dababy.load_extension(f"cogs.{extension}")
        await ctx.send(f"***{extension}*** cog has been reloaded!")

# Automatically load all cogs on start
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        dababy.load_extension(f"cogs.{filename[:-3]}")
        print(f"Cog: {filename[:-3]} loaded!")

# Running bot
token_file = open("token.txt", "r")
token = token_file.read()
dababy.run(token)
