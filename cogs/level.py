# Leveling for DaBabyBot

# Imports
import discord
from discord.ext import commands
import json
import os
import random
import math

# Intents
intents = discord.Intents().all()

# Level
class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Helper functions
    # Check if user is in userdb and add user to it if not
    async def check_user(self, userdb, user):
        # Create entry for user with userid, xp and lvl
        if not str(user.id) in userdb:
            userdb[str(user.id)] = {}
            userdb[str(user.id)]["xp"] = 0
            userdb[str(user.id)]["lvl"] = 1

    # Add xp to userS
    async def add_xp(self, userdb, user):
        # User gains 1-3 xp per message
        userdb[str(user.id)]["xp"] += random.randrange(1, 3)

    # Check if user leveled up
    async def level_up(self, userdb, user, channel):
        # Get xp/lvl from database
        xp = userdb[str(user.id)]["xp"]
        lvl = userdb[str(user.id)]["lvl"]
        
        # xp requirement doubles per level
        next_lvl = int(100 * (2 ** (lvl - 1)))
        if xp >= next_lvl:
            userdb[str(user.id)]["lvl"] = lvl + 1

            # Create embed when user levels up
            file = discord.File("./gifs/dababy_dancing5.gif")
            embed = discord.Embed(
                title = ":rotating_light: Gamer Level Increased!!! :rotating_light:",
                description = f"{user.mention} has leveled up to **LEVEL {lvl + 1}!**",
                colour = discord.Colour.dark_blue()
            )
            embed.set_image(url = "attachment://dababy_dancing5.gif")
            embed.set_footer(text = "LETSGOOOOOOOO!")
            await channel.send(file = file, embed = embed)

    # Generate rank embed
    async def show_rank(self, userdb, user, channel):
        # Get xp/lvl from database
        xp = userdb[str(user.id)]["xp"]
        lvl = userdb[str(user.id)]["lvl"]

        # Calculate boxes for progress bar
        next_lvl = int(100 * (2 ** (lvl - 1)))
        blue_boxes = math.floor(15 * (xp / next_lvl))
        white_boxes = 15 - blue_boxes
        name = str(user)

        # Create embed to display user's rank
        embed = discord.Embed(
            title = f":100: {name[:-5]}'s Stat Page :100:",
            colour = discord.Colour.dark_blue()
        )
        embed.set_thumbnail(url = user.avatar_url)
        # User name
        embed.add_field(
            name = "Name",
            value = user.mention,
            inline = True
         )
        # Level
        embed.add_field(
            name = "Level",
            value = lvl,
            inline = True
        )
        # Total xp
        embed.add_field(
            name = "XP",
            value = xp,
            inline = True
        )
        # Progress bar
        embed.add_field(
            name = "Progress",
            value = ":blue_square:" * blue_boxes + ":white_large_square:" * white_boxes,
            inline = False
        )
        embed.set_footer(text = f"XP needed for next level: {next_lvl}")
        await channel.send(embed = embed)

    # Bot functions
    # Create new entry for new members on join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Open database
        with open("users.json", "r") as file:
            userdb = json.load(file)

        # Check if user is in database, else create a new entry for them
        await self.check_user(userdb, member)

        # Close database
        with open("users.json", "w") as file:
            json.dump(userdb, file)

    # Give xp on message
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            # Open database
            with open("users.json", "r") as file:
                userdb = json.load(file)

            # Check if user is in database, add xp and check if leveled up
            await self.check_user(userdb, message.author)
            await self.add_xp(userdb, message.author)
            await self.level_up(userdb, message.author, message.channel)

            # Close database
            with open("users.json", "w") as file:
                json.dump(userdb, file)

    # Check rank
    @commands.command(aliases = ["level"])
    async def rank(self, message):
        # Open database
        with open("users.json", "r") as file:
            userdb = json.load(file)

        # Check if user is in database, then display their rank
        await self.check_user(userdb, message.author)
        await self.show_rank(userdb, message.author, message.channel)

        # Close database
        with open("users.json", "w") as file:
            json.dump(userdb, file)

# Setup
def setup(bot):
    bot.add_cog(Level(bot))