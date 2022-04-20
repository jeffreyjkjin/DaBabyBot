# Music for DaBabyBot

# Imports
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import pafy2 as pafy
import asyncio
import random
import time

# Intents
intents = discord.Intents().all()

# FFMPEG options
ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

# Player
class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.looping = False
        self.current_song = []
        self.startup()

    # Create entry for server    
    def startup(self):
        for guild in self.bot.guilds:
            self.song_queue[guild.id] = []

    # Helper functions
    # Check the queue for songs
    async def check_queue(self, ctx):
        self.current_song = []
        # If queue length is > 0, play the first song in queue
        if len(self.song_queue[ctx.guild.id]) > 0:
            await self.play_song(ctx, self.song_queue[ctx.guild.id].pop(0))

        # If looping is disabled
        if self.looping == False:
            if self.current_song in self.song_queue[ctx.guild.id]:
                self.song_queue[ctx.guild.id].pop(0)
            
        # If looping is enabled
        else:
            if self.current_song not in self.song_queue[ctx.guild.id]:
                self.song_queue[ctx.guild.id].insert(0, self.current_song)

    # Search for songs
    async def search_song(self, amount, song, get_url = False):
        info = await self.bot.loop.run_in_executor(None, lambda: youtube_dl.YoutubeDL({"format" : "bestaudio", "quiet" : True}).extract_info(f"ytsearch{amount}:{song}", download = False, ie_key = "YoutubeSearch"))
        if len(info["entries"]) == 0: return None

        return [entry["webpage_url"] for entry in info["entries"]] if get_url else info

    # Play a song
    async def play_song(self, ctx, song):
        # Play song
        url = pafy.new(song[0]).getbestaudio().url
        ctx.voice_client.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpeg_options)), after = lambda error: self.bot.loop.create_task(self.check_queue(ctx)))
        ctx.voice_client.source.volume = 0.5

        # Save current song
        self.current_song = song
    
    # Check if user is in a voice channel
    async def user_in_channel(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("Why you tweakin' fam? You're not connected to a voice channel. Join a voice channel before using this bot, noob.")
            return False

    # Check if user is in the same channel as bot
    async def user_same_channel(self, ctx):
        if ctx.author.voice.channel.id != ctx.voice_client.channel.id:
            await ctx.send("I'm not connected to your voice channel, noob.")
            return False

    # Check if queue is empty
    async def queue_empty(self, ctx):
        if len(self.song_queue[ctx.guild.id]) == 0:
            await ctx.send("There are currently no songs in the queue, noob.")
            return False

    # Check if song is being played
    async def song_playing(self, ctx):
        if self.current_song == [] and ctx.voice_client.is_playing() == False:
            await ctx.send("I'm currently not playing a song, noob.")
            return False

    # Check if bot is in a channel
    async def bot_in_channel(self, ctx):
        if ctx.guild.voice_client not in self.bot.voice_clients:
            await ctx.send("I'm not connected to a voice channel, noob.")
            return False

    # Create embed for the song that is being added to the queue
    async def queue_embed(self, ctx, song):
        video = pafy.new(song[0])
        embed = discord.Embed(
            title = f":hourglass: Added to Position #{len(self.song_queue[ctx.guild.id])} in the Queue! :hourglass:",
            colour = discord.Colour.dark_blue()
        )
        # Title of song
        embed.add_field(
            name = "Title",
            value = f"[{video.title}]({song[0]})",
            inline = False
            )
        # Author of song
        embed.add_field(
            name = "Author",
            value = video.author,
            inline = True
        )
        # Length of song
        embed.add_field(
            name = "Length",
            value = video.duration,
            inline = True
        )
        # Requester of song
        embed.add_field(
            name = "Requester",
            value = song[1],
            inline = True
        )
        embed.set_image(url = video.bigthumbhd)

        # If loop is enabled
        if self.looping == True:
            embed.set_footer(text = "Looping is currently enabled.")

        return embed

    # Create embed for the song that is currently playing
    async def song_embed(self, ctx, song):
        video = pafy.new(song[0])
        embed = discord.Embed(
            title = ":notes: Now Playing! :notes:",
            colour = discord.Colour.dark_blue()
        )
        # Title of song
        embed.add_field(
            name = "Title",
            value = f"[{video.title}]({song[0]})",
            inline = False
        )
        # Author of song
        embed.add_field(
            name = "Author",
            value = video.author,
            inline = True
        )
        # Length of song
        embed.add_field(
            name = "Length",
            value = video.duration,
            inline = True
        )
        # Requester of song
        embed.add_field(
            name = "Requester",
            value = song[1],
            inline = True
        )
        embed.set_image(url = video.bigthumbhd)

        # If loop is enabled
        if self.looping == True:
            embed.set_footer(text = "Looping is currently enabled.")

        return embed

    # Bot functions
    # Join the voice channel that the user is currently in
    @commands.command(aliases = ["add"])
    @commands.has_role("DaBaby")
    async def join(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is in a voice channel
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

        # Empty the queue
        self.song_queue[ctx.guild.id] = []

        # Disable looping
        self.looping = False

        # Join user's channel
        return await ctx.author.voice.channel.connect()

    # Leave the voice channel
    @commands.command(aliases = ["disconnect", "dc"])
    @commands.has_role("DaBaby")
    async def leave(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return
        
        # Leave channel
        self.song_queue[ctx.guild.id] = []
        return await ctx.voice_client.disconnect()
            
    # Search for a song to play
    @commands.command()
    @commands.has_role("DaBaby")
    async def play(self, ctx, *, song = None):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in the voice channel
        if ctx.guild.voice_client not in self.bot.voice_clients:
            await ctx.author.voice.channel.connect()

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If search contains no song
        if song is None:
            return await ctx.send("You must add a song to play, noob.")

        # If queue does not exist
        if ctx.guild.id not in self.song_queue:
            self.song_queue[ctx.guild.id] = []

        # Create embed for searching
        embed = discord.Embed(
            title = ":mag_right: Searching for Song... :mag:",
            description = f"Searching for '{song}'...",
            colour = discord.Colour.dark_blue()
        )

        # Send embed
        play_embed = await ctx.send(embed = embed)

        # If user's search is not a Youtube url
        if not ("youtube.com/watch?" in song or "https://youtu.be/" in song):

            # Search for songs
            result = await self.search_song(1, song, get_url = True)

            # If song couldn't be found
            if result is None:
                return await ctx.send("Cmon man. Song could not be found.")

            # If song was found
            else:
                song = [result[0], ctx.author.mention]

        # If a song is currently playing
        if ctx.voice_client.is_playing():
            # Add song to queue
            self.song_queue[ctx.guild.id].append(song)
            return await play_embed.edit(embed = await self.queue_embed(ctx, song))

        # Play song
        await self.play_song(ctx, song)
        return await play_embed.edit(embed = await self.song_embed(ctx, song))

    # Search 5 songs with user's keyword (update this)
    @commands.command()
    @commands.has_role("DaBaby")
    async def search(self, ctx, *, search = None):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in the voice channel
        if ctx.guild.voice_client not in self.bot.voice_clients:
            await ctx.author.voice.channel.connect()

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If search contains no song
        if search is None: 
            return await ctx.send("You must add a song to search, noob.")

        # If queue does not exist
        if ctx.guild.id not in self.song_queue:
            self.song_queue[ctx.guild.id] = []

        # Create embed for searching
        search_embed = discord.Embed(
            title = ":mag_right: Searching for Song... :mag:",
            description = f"Searching for '{search}'...",
            colour = discord.Colour.dark_blue()
        )

        # Send embed
        embed = await ctx.send(embed = search_embed)

        # Search for songs
        start = time.time()
        results = await self.search_song(5, search, get_url = True)
        runtime = round((time.time() - start), 2)

        # Create embed for each song searched
        search_embed = discord.Embed(
            title = f":mag_right: Results for '{search}': :mag:",
            description = "Showing the first 5 results. React with the number of the song to add it to the queue.",
            colour = discord.Colour.dark_blue()
            )
        position = 1
        for url in results:
            video = pafy.new(url)
            search_embed.add_field(
                name = f"{position}) {video.title}",
                value = f"**Author:** {video.author}\n**Length:** {video.duration}\n**URL:** {url}",
                inline = False
            )
            position += 1
        search_embed.set_footer(text = f"Results found in {runtime} seconds.")

        # Send search embed
        await embed.edit(embed = search_embed)

        # Add reactions to choose song
        valid = [
            "1\N{variation selector-16}\N{combining enclosing keycap}",
            "2\N{variation selector-16}\N{combining enclosing keycap}", 
            "3\N{variation selector-16}\N{combining enclosing keycap}", 
            "4\N{variation selector-16}\N{combining enclosing keycap}", 
            "5\N{variation selector-16}\N{combining enclosing keycap}"
            ]
        for reaction in valid:
            await embed.add_reaction(reaction)

        # Check user's choice
        response, user = await self.bot.wait_for(
            "reaction_add",
            check = lambda reaction, user: user == ctx.author and reaction.emoji in valid
            )
        i = 0
        for reaction in valid:
            if response.emoji == reaction:
                await embed.clear_reactions()
                break
            i += 1
        song = [results[i], ctx.author.mention]

        # If a song is currently playing
        if ctx.voice_client.is_playing():
            # Add song to queue
            self.song_queue[ctx.guild.id].append(song)
            return await embed.edit(embed = await self.queue_embed(ctx, song))
            
        # Play song
        await self.play_song(ctx, song)
        return await embed.edit(embed = await self.song_embed(ctx, song))

    # Display a list of the songs in the queue
    @commands.command()
    async def queue(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If queue is empty
        if await self.queue_empty(ctx) == False:
            return

        # If queue is not empty
        else:
            # Check how many songs are in queue
            if len(self.song_queue[ctx.guild.id]) >= 5:
                queue_len = 5
            else:
                queue_len = len(self.song_queue[ctx.guild.id])

	    # Create embed for queue
            embed = discord.Embed(
                title=":notes: DaBabyBot Song Queue :notes:",
                description = f"Displaying the next {queue_len} track(s) in the queue.",
                colour = discord.Colour.dark_blue()
                )
            queue_position = 1
            for song in self.song_queue[ctx.guild.id]:
                video = pafy.new(song[0])
                embed.add_field(
                    name = f"{queue_position}) {video.title}",
                    value = f"**Author:** {video.author}\n**Length:** {video.duration}\n **Requester:** {song[1]}\n **URL:** {song[0]}",
                    inline = False
                )
                queue_position += 1
                if queue_position > 5:
                    break
            embed.set_footer(text = f"There are currently {len(self.song_queue[ctx.guild.id])} song(s) in the queue.")
            return await ctx.send(embed = embed)

    # Clear queue
    @commands.command(aliases = ["emptyqueue"])
    @commands.has_role("DaBaby")
    async def clearqueue(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If queue is empty
        if await self.queue_empty(ctx) == False:
            return

        # Clear the queue
        self.song_queue[ctx.guild.id] = []
        
        # Send embed that the queue has been cleared
        embed = discord.Embed(
            title = ":eject: Queue Cleared! :eject:",
            description = "The queue has been cleared.",
            colour = discord.Colour.dark_blue()
        )
        return await ctx.send(embed = embed)

    # Vote to skip the current song
    @commands.command()
    async def skip(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If no song is being played
        if await self.song_playing(ctx) == False:
            return

        # Create poll embed
        poll_embed = discord.Embed(
            title = ":ballot_box: Vote to Skip Song! :ballot_box:",
            description = f"***{ctx.author.name}#{ctx.author.discriminator}*** has started a vote to skip the current song. This vote will end in ***20 seconds***.",
            colour = discord.Colour.dark_blue()
            )
        poll_embed.add_field(
            name="Skip",
            value = ":white_check_mark:"
            )
        poll_embed.add_field(
            name = "No Skip",
            value = ":no_entry_sign:"
            )

        # Send poll embed
        poll = await ctx.send(embed = poll_embed)
        poll_id = poll.id

        # Add reactions for voting
        await poll.add_reaction(u"\u2705") # Vote to skip
        await poll.add_reaction(u"\U0001F6AB") # Vote to not skip

        # Wait 20 seconds then count votes
        await asyncio.sleep(20)
        poll = await ctx.channel.fetch_message(poll_id)
        votes = {
            u"\u2705": 0,
             u"\U0001F6AB": 0
             }
        reacted = []
        for reaction in poll.reactions:
            if reaction.emoji in [u"\u2705", u"\U0001F6AB"]:
                async for user in reaction.users():
                    if user.voice.channel.id == ctx.voice_client.channel.id and user.id not in reacted and not user.bot:
                        votes[reaction.emoji] += 1
                        reacted.append(user.id)

        # If vote to skip passed
        if votes[u"\u2705"] > 0:
            if votes[u"\U0001F6AB"] == 0 or votes[u"\u2705"] > votes[u"\U0001F6AB"]:
                # Create embed for skipping song
                embed = discord.Embed(
                    title = ":fast_forward: Vote to Skip Song Passed! :fast_forward:",
                    description = "The current song playing was skipped.", 
                    colour = discord.Colour.green()
                )

                # If song is looping
                if self.looping == True:
                    self.song_queue[ctx.guild.id].pop(0)
            
                # Skip song
                await poll.clear_reactions()
                await poll.edit(embed = embed)
                return ctx.voice_client.stop()

        # If vote to skip failed
        else:
            # create embed for failing vote
            embed = discord.Embed(
                title = ":no_entry_sign: Vote to Skip Song Failed! :no_entry_sign:",
                description = f"Haha! The vote to skip this song failed ***{ctx.author.name}#{ctx.author.discriminator}*** is a big NOOB!",
                colour = discord.Colour.red()
                )
            await poll.clear_reactions()
            return await poll.edit(embed = embed)

    # Force skip the current song
    @commands.command(aliases = ["fs", "forceskip"])
    @commands.has_role("DaBaby")
    async def fskip(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If no song is being played
        if await self.song_playing(ctx) == False:
            return
        
        # If song is looping
        if self.looping == True:
            self.song_queue[ctx.guild.id].pop(0)

        # Create embed for skipping song
        embed = discord.Embed(
            title=":fast_forward: Song Skipped! :fast_forward:",
            description = "The current song playing was skipped.",
            colour = discord.Colour.green()
            )

        # Skip song
        ctx.voice_client.stop()
        return await ctx.send(embed = embed)

    # Pause the bot from playing music
    @commands.command(aliases = ["stop"])
    @commands.has_role("DaBaby")
    async def pause(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If no song is being played
        if await self.song_playing(ctx) == False:
            return

        # If song is already paused
        if ctx.voice_client.is_paused():
            return await ctx.send("I am already paused, noob.")

        # Create embed for pausing song
        embed = discord.Embed(
            title=":pause_button: Song Paused! :pause_button:",
            description = "The current song has been paused.",
            colour = discord.Colour.red()
            )

        # Pause song
        ctx.voice_client.pause()
        return await ctx.send(embed = embed)

    # Resume the bot from playing music
    @commands.command(aliases = ["start", "unpause"])
    @commands.has_role("DaBaby")
    async def resume(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If no song is being played
        if await self.song_playing(ctx) == False:
            return
        
        # If song is not paused
        if not ctx.voice_client.is_paused():
            return await ctx.send("I'm already playing song, noob")

        # Create embed for resuming song
        embed = discord.Embed(
            title=":play_pause: Song Resumed! :play_pause:",
            description = "The current song has been resumed.",
            colour = discord.Colour.green()
            )

        # Resume song
        ctx.voice_client.resume()
        return await ctx.send(embed = embed)

    # Shuffle queue
    @commands.command(aliases = ["mix"])
    @commands.has_role("DaBaby")
    async def shuffle(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If no song is being played
        if await self.queue_empty(ctx) == False:
            return

        # Shuffle queue
        random.shuffle(self.song_queue[ctx.guild.id])

        # Create embed for shuffling queue
        embed = discord.Embed(
            title=":twisted_rightwards_arrows:  Queue Shuffled! :twisted_rightwards_arrows: ",
            description = "The queue has been shuffled.",
            colour = discord.Colour.purple()
            )
        return await ctx.send(embed = embed)

    # Remove song from queue
    @commands.command()
    @commands.has_role("DaBaby")
    async def remove(self, ctx, queue_position):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If no song is being played
        if await self.queue_empty(ctx) == False:
            return

        # If queue position is not an integer
        queue_position = int(queue_position)
        if type(queue_position) != int:
            return await ctx.send("That's not a real number noob.")

        # If queue position is not in the queue
        if (queue_position - 1) not in range(0, len(self.song_queue[ctx.guild.id])):
            return await ctx.send("There is no song at that position in the queue, noob.")

        # Remove song from queue
        url = self.song_queue[ctx.guild.id].pop(queue_position - 1)
        video = pafy.new(url[0])

        # Create embed for removing song from queue
        embed = discord.Embed(
            title = ":x: Song Removed! :x:",
            description = f"***{video.title}*** has been removed from queue.",
            colour = discord.Colour.red()
            )
        return await ctx.send(embed = embed)

    # Show current song
    @commands.command(aliases = ["playing"])
    async def current(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If no song is being played
        if await self.song_playing(ctx) == False:
            return

        # Create embed for current song
        video = pafy.new(self.current_song[0])
        embed = discord.Embed(
            title = ":notes: Currently Playing! :notes:",
            colour = discord.Colour.dark_blue()
        )
        # Title of song
        embed.add_field(
            name = "Title",
            value = f"[{video.title}]({self.current_song[0]})",
            inline = False
        )
        # Author of song
        embed.add_field(
            name = "Author",
            value = video.author,
            inline = True
        )
        # Length of song
        embed.add_field(
            name = "Length",
            value = video.duration,
            inline = True
        )
        # Requester of song
        embed.add_field(
            name = "Requester",
            value = self.current_song[1],
            inline = True
        )
        embed.set_image(url = video.bigthumbhd)
        
        # If loop is enabled
        if self.looping == True:
            embed.set_footer(text = "Looping is currently enabled.")

        # Send embed
        return await ctx.send(embed = embed)

    # Loop current song
    @commands.command()
    @commands.has_role("DaBaby")
    async def loop(self, ctx):
        # If user is not in a voice channel
        if await self.user_in_channel(ctx) == False:
            return

        # If bot is not in a voice channel
        if await self.bot_in_channel(ctx) == False:
            return

        # If user is in the wrong channel
        if await self.user_same_channel(ctx) == False:
            return

        # If loop is disabled, enable it
        if self.looping == False:
            self.looping = True

            # If song is currently playing
            if ctx.voice_client.is_playing():
                if self.current_song not in self.song_queue[ctx.guild.id]:
                    self.song_queue[ctx.guild.id].insert(0, self.current_song)

            # Create embed for enabling loop
            embed = discord.Embed(
                title = ":repeat: Looping Enabled! :repeat:",
                description = "Looping has been enabled.",
                colour = discord.Colour.green()
            )
            return await ctx.send(embed = embed)

        # If loop is enabled, disable it
        else:
            self.looping = False
            # If song is currently playing
            if ctx.voice_client is not None:
                if self.current_song in self.song_queue[ctx.guild.id]:
                    self.song_queue[ctx.guild.id].remove(self.current_song)

            # Create embed for disabling loop
            embed = discord.Embed(
                title = ":x: Looping Disabled! :x:",
                description = "Looping has been disabled.",
                colour = discord.Colour.red()
            )
            return await ctx.send(embed = embed)

# Setup
def setup(bot):
    bot.add_cog(Player(bot))
