# Admin Commands for DaBabyBot

# Imports
import discord
from discord.ext import commands
import time
import asyncio

# Intents
intents = discord.Intents().all()

# Admin
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    # Helper functions
    # Create confirmation message for kick/ban
    async def confirm(self, ctx, type, member, reason):
        embed = discord.Embed(
            title = ":rotating_light: Confirmation Required! :rotating_light:",
            description = f"Are you sure you want to {type} ***{member}*** from ***{ctx.guild}***?",
            colour = discord.Colour.dark_blue()
        )
        embed.add_field(
            name = "Reason",
            value = f"{reason}",
            inline = False
        )
        embed.add_field(
            name = "Yes",
            value = ":white_check_mark:"
            )
        embed.add_field(
            name = "No",
            value = ":no_entry_sign:"
            )
        embed.set_footer(text = "You have 30 seconds to confirm.")
        return embed
    
    # Create direct message embed for kick/ban
    async def embed_dm(self, ctx, type, reason):
        embed = discord.Embed(
            title = f":leg: You've been {type} from {ctx.guild}! :leg:",
            colour = discord.Colour.red()
        )
        # Kick reason
        embed.add_field(
            name = "Reason",
            value = f"{reason}",
            inline = True
        )
        embed.set_image(url = "attachment://dababy_dancing3.gif")
        embed.set_footer(text = "Picture of me and your mom, noob!")
        return embed

    # Create kicked embed
    async def kicked(self, ctx, member):
        embed = discord.Embed(
            title = f":leg: User Kicked! :leg:",
            description = f"Noob ***{member}*** has been kicked because his mom's a ho!",
            colour = discord.Colour.green()
        )
        embed.set_footer(text = "LETSGOOOOOOOO!")
        return embed
    
    # Create banned embed
    async def banned(self, ctx, member):
        embed = discord.Embed(
            title = ":hammer: User Banned! :hammer:",
            description = f"Noob ***{member}*** has been banned because his mom's a ho!",
            colour = discord.Colour.green()
        )
        embed.set_footer(text = "LETSGOOOOOOOO!")
        return embed

    # Create confirmation failed embed
    async def failed(self, ctx, type, member):
        embed = discord.Embed(
            title = "Confirmation Failed!",
            description = f"The ***{member}*** has not been {type}.",
            colour = discord.Colour.red()
        )
        embed.set_footer(text = "Cmon man!")
        return embed

    # Kick user command
    @commands.command()
    @commands.has_any_role("Admin", "Owner")
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        # Send embed to confirm kick
        embed = await ctx.send(embed = await self.confirm(ctx, "kick", member, reason))

        # Add reactions for confirming
        reactions = [
            u"\u2705",
             u"\U0001F6AB"
             ]
        await embed.add_reaction(u"\u2705") # Yes
        await embed.add_reaction(u"\U0001F6AB") # No

        # Check confirmation
        try:
            response, user = await self.bot.wait_for(
                "reaction_add",
                check = lambda reaction, user: user == ctx.author and reaction.emoji in reactions,
                timeout = 30.0
            )

        # If not confirmed after 30s
        except asyncio.TimeoutError:
            await embed.clear_reactions()
            return await embed.edit(embed = await self.failed(ctx, "kicked", member))

        # If user reacts
        else:
            await embed.clear_reactions()
            # Yes to kick user
            if response.emoji == u"\u2705":
                # Send embed dm message for kick
                file = discord.File("gifs/dababy_dancing3.gif")
                await member.send(file = file, embed = await self.embed_dm(ctx, "kick", reason))

                # Kick user
                await member.kick(reason = reason)

                # Send embed for kick
                return await embed.edit(embed = await self.kicked(ctx, member))

            # No to kick user
            if response.emoji == u"\U0001F6AB":
                # Send embed for failed kick
                return await embed.edit(embed = await self.failed(ctx, "kicked", member))

    # Ban user command
    @commands.command()
    @commands.has_any_role("Admin", "Owner")
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        # Send embed to confirm ban
        embed = await ctx.send(embed = await self.confirm(ctx, "ban", member, reason))

        # Add reactions for confirming
        reactions = [
            u"\u2705",
             u"\U0001F6AB"
             ]
        await embed.add_reaction(u"\u2705") # Yes
        await embed.add_reaction(u"\U0001F6AB") # No

        # Check confirmation
        try:
            response, user = await self.bot.wait_for(
                "reaction_add",
                check = lambda reaction, user: user == ctx.author and reaction.emoji in reactions,
                timeout = 30.0
            )

        # If not confirmed after 30s
        except asyncio.TimeoutError:
            await embed.clear_reactions()
            return await embed.edit(embed = await self.failed(ctx, "banned", member))

        # If user reacts
        else:
            await embed.clear_reactions()

            # Yes to ban user
            if response.emoji == u"\u2705":
                # Send embed dm message for ban
                file = discord.File("gifs/dababy_dancing3.gif")
                await member.send(file = file, embed = await self.embed_dm(ctx, "ban", reason))

                # Ban user
                await member.ban(reason = reason)

                # Send embed for ban
                return await embed.edit(embed = await self.banned(ctx, "ban", member))

            # No to ban user
            if response.emoji == u"\U0001F6AB":
                # Send embed for failed ban
                return await embed.edit(embed = await self.failed(ctx, "banned", member))

    # Unban user command
    @commands.command()
    @commands.has_any_role("Admin", "Owner")
    async def unban(self, ctx, *, unban):
        # Get ban list
        banlist = await ctx.guild.bans()
        for banned_user in banlist:
            # Check if user is in ban list
            if str(banned_user.user) == unban:
                # Unban user
                await ctx.guild.unban(banned_user.user)

                # Create embed for ban
                embed = discord.Embed(
                    title = ":unlock:  User Unbanned! :unlock:",
                    description = f"***{unban}*** has been unbanned from the server!",
                    colour = discord.Colour.green()
                )
                embed.set_footer(text = "LETSGOOOOOOOO!")
                return await ctx.send(embed = embed)

        # If user isn't in ban list
        return await ctx.send(f"***{unban}*** cannot be found in the ban list!")

    # Show banlist of server command
    @commands.command()
    @commands.has_any_role("Admin", "Owner")
    async def banlist(self, ctx):
        # Get ban list
        banlist = await ctx.guild.bans()

        # If ban list is empty
        if len(banlist) == 0:
            return await ctx.send(f"The ban list for {ctx.guild} is empty. Start banning some people, noob.") 

        # Create embed for ban list
        embed = discord.Embed(
            title = f":police_car: {ctx.guild} Ban List! :police_car:",
            colour = discord.Colour.dark_blue()
        )
        # Iterate through ban list and add to embed
        for banned_user in banlist:
            embed.add_field(
                name = f"{banned_user.user}",
                value = f"**Reason:** {banned_user.reason}",
                inline = False
            )
        return await ctx.send(embed = embed)

    # Clear messages
    @commands.command(aliases = ["delete", "purge"])
    @commands.has_any_role("Admin", "Owner")
    async def clear(self, ctx, amount = None):
       # If amount was not specified
        if amount == None:
            return await ctx.send("How many messages do I have to clear, noob?")

        # If amount is above 100
        amount = int(amount)
        if amount > 100:
            return await ctx.send("I can't delete that many messages, noob.")

        # Delete messages
        start = time.time()
        await ctx.channel.purge(limit = amount + 1)
        runtime = round((time.time() - start), 2)

        # Create embed for ban
        embed = discord.Embed(
            title = ":broom:  Messages Cleared! :broom:",
            description = f"***{amount}*** messages have been cleared from this channel in ***{runtime}*** seconds.",
            colour = discord.Colour.dark_blue()
        )
        return await ctx.send(embed = embed) 

# Setup
def setup(bot):
    bot.add_cog(Admin(bot))
