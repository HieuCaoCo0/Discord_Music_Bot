import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
from collections import deque
from config.setting import TOKEN, FFMPEG_PATH, FFMPEG_OPTIONS, YDL_OPTIONS, BOT_PREFIX

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = BOT_PREFIX, intents = intents)

SONG_QUEUES = {}

async def search_ytdlp_async(query, ydl_opt):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: _extract(query, ydl_opt))
def _extract(query, ydl_opt):
    with yt_dlp.YoutubeDL(ydl_opt) as ydl:
        return ydl.extract_info(query, download=False)

async def play_next_song(voice_client, guild_id, channel):
    if guild_id in SONG_QUEUES and SONG_QUEUES[guild_id]:
        audio_url, title = SONG_QUEUES[guild_id].popleft()
        ffmpeg_options = FFMPEG_OPTIONS.copy()

        source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable = FFMPEG_PATH)

        def after_playing(error):
            if error:
                print(f"Error occurred while playing: {error}")
            asyncio.run_coroutine_threadsafe(play_next_song(voice_client, guild_id, channel), bot.loop)

        # await interaction.followup.send(f"Now playing: {title}")
        voice_client.play(source, after = after_playing)
        asyncio.create_task(channel.send(f"Now playing: {title}"))
    else:
        # await channel.send("The queue is empty. Add more songs to play.")
        await voice_client.disconnect()
        del SONG_QUEUES[guild_id]

@bot.event
async def on_ready():
    sync = await bot.tree.sync()
    print(f'{bot.user} has connected to Discord!')
    print(f'guilds: {[guild.id for guild in bot.guilds]}')
    

@bot.tree.command(name="play", description="Play a song or add to the queue")
@app_commands.describe(song_query="Search query for the song")
async def play(interaction: discord.Interaction, song_query: str):
    await interaction.response.defer()

    if interaction.user.voice is None:
        await interaction.followup.send("You are not connected to a voice channel.")
        return  
    
    voice_channel = interaction.user.voice.channel
    
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        voice_client = await voice_channel.connect()
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    ydl_options = YDL_OPTIONS.copy()

    query = 'ytsearch1: ' + song_query
    result = await search_ytdlp_async(query, ydl_options)
    track = result.get('entries', [])

    if not  track:
        await interaction.followup.send("No results found for your query.")
        return
    
    first_track = track[0]
    print(first_track["title"])
    print(first_track["webpage_url"])
    # print(first_track["url"])

    audio_url = first_track['url']
    title = first_track.get('title', 'Untitled') 

    guild_id = str(interaction.guild.id)
    if guild_id not in SONG_QUEUES:
        SONG_QUEUES[guild_id] = deque()
    SONG_QUEUES[guild_id].append((audio_url, title))

    if voice_client.is_playing() or voice_client.is_paused():
        await interaction.followup.send(f"Added to queue: {title}")
    else:
        await interaction.followup.send(f"Now playing: {title}")
        await play_next_song(voice_client, guild_id, interaction.channel)

@bot.tree.command(name='pause', description='Pause the current song')
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    # Check if the bot is connected to a voice channel and if a song is currently playing
    if voice_client is None:
        return await interaction.response.send_message("I am not connected to a voice channel.")
    if not voice_client.is_playing():
        return await interaction.response.send_message("No song is currently playing.")
    
    voice_client.pause()
    await interaction.response.send_message("Paused the current song.")

@bot.tree.command(name='resume', description='Resume the current song')
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    # Check if the bot is connected to a voice channel and if a song is currently paused
    if voice_client is None:
        return await interaction.response.send_message("I am not connected to a voice channel.")
    if not voice_client.is_paused():
        return await interaction.response.send_message("No song is currently paused.")
    
    voice_client.resume()
    await interaction.response.send_message("Resumed the current song.")

@bot.tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    # Check if the bot is connected to a voice channel and if a song is currently playing
    if voice_client is None:
        return await interaction.response.send_message("I am not connected to a voice channel.")
    if not voice_client.is_playing() and not voice_client.is_paused():
        return await interaction.response.send_message("No song is currently playing.")

    voice_client.stop()
    await interaction.response.send_message("Skipped the current song.")

@bot.tree.command(name="stop", description="Stop the music and clear the queue")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()
    voice_client = interaction.guild.voice_client
    # Check if the bot is connected to a voice channel
    if voice_client is None:
        return await interaction.followup.send("I am not connected to a voice channel.")

    # Clear the song queue for the guild
    guild_id = str(interaction.guild.id)
    if guild_id in SONG_QUEUES:
        SONG_QUEUES[guild_id].clear()

    voice_client.stop()
    await interaction.followup.send("Stopped the music and disconnected!")
    await voice_client.disconnect()
    


bot.run(TOKEN)