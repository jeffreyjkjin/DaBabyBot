# Greetings for DaBabyBot

# Imports
import discord
from discord.ext import commands

# Intents
intents = discord.Intents().all()

# Message
class Greeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
    
    # On join
    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        channel = ctx.guild.system_channel
        if channel is not None:
            # Create embed join message in server
            file1 = discord.File("./gifs/dababy_dancing1.gif")
            embed = discord.Embed(
                title = ":rotating_light: Attention All Gamers! :rotating_light:", 
                description = f"Welcome to the traphouse {ctx.mention}! Fill 'em with vibes and get in and ride!",
                colour = discord.Colour.dark_blue()
                )
            embed.set_image(url = "attachment://dababy_dancing1.gif")
            embed.set_footer(text = "LETSGOOOOOOOO!") 
            await channel.send(file = file1, embed = embed)

            # Create embed join message in direct message
            file2 = discord.File("./gifs/dababy_dancing2.gif")
            embed_dm = discord.Embed(
                title = "LETSGOOOOOOOO!",
                description = f"DaBaby personally welcomes you to the gang! You a real G {ctx.mention}!!!",
                colour = discord.Colour.dark_blue()
            )
            embed_dm.set_image(url = "attachment://dababy_dancing2.gif")
            embed_dm.set_footer(text = "You know it's Baby!")
            return await ctx.send(file = file2, embed = embed_dm)

    # On leave
    @commands.Cog.listener()
    async def on_member_remove(self, ctx):
        channel = ctx.guild.system_channel
        if channel is not None:
            # Create embed message
            file = discord.File("./gifs/dababy_dancing3.gif")
            embed = discord.Embed(
                title = ":clown_face: Noob has just left the gang! :clown_face:",
                description = f"{ctx.mention} has left the traphouse cuz his mom's a ho! :wheelchair:",
                colour = discord.Colour.red()
            )
            embed.set_image(url = "attachment://dababy_dancing3.gif")
            embed.set_footer(text = "downbad ratio'd caught in 4k")
        return await channel.send(file = file, embed = embed)

# Setup
def setup(bot):
    bot.add_cog(Greeting(bot))