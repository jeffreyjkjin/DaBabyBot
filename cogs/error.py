# Error for DaBabyBot

# Imports
import discord
from discord.ext import commands

# Intents
intents = discord.Intents().all()

# Error
class Error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Error checking
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # If required role is missing
        if isinstance(error, commands.MissingRole):
            return await ctx.send(f"{ctx.author.mention} Why you tweakin' fam? You don't have permission to use that command, noob.")

        # If command does not exist
        elif isinstance(error, commands.CommandNotFound):
            return await ctx.send(f"{ctx.author.mention} Why you tweakin' fam? This command does not exist, noob.")

        # If command is missing argument.
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"{ctx.author.mention} Why you tweakin' fam? You need to add a parameter to use this command, noob.")
            
        # If unknown error
        else:
            return await ctx.send(f":question: **Unknown Error Detected!** :question:\n```\n{error}\n```")

# Setup
def setup(bot):
    bot.add_cog(Error(bot))