import re
import urllib.request
from youtubesearchpython import Video
import discord
import pafy
from discord import FFmpegPCMAudio
from discord.ext import commands
import datetime

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix="$")


async def get_video_title(video_url):
    video = Video.getInfo(video_url)
    return video['title'] + " [" + str(datetime.timedelta(seconds=int(video['duration']['secondsText']))) + "]"


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.command()
async def play(ctx, *args):
    def check(m):
        if m.author == ctx.author and m.channel == ctx.channel:
            try:
                int(m.content)
                return True
            except ValueError:
                return False
        return False

    await ctx.send("Chotto matte...")
    if ctx.message.author.voice is None:
        await ctx.send("You're not in the voice channel!")
        return
    channel = ctx.message.author.voice.channel

    voice = discord.utils.get(ctx.guild.voice_channels, name=channel.name)
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_client is None:
        voice_client = await voice.connect()
    else:
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.move_to(channel)
    search = '+'.join(args)
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    titles = []
    for i in range(5):
        #await ctx.send(str(i + 1) + ":  " + await get_video_title("https://www.youtube.com/watch?v=" + video_ids[i]))
        title = await get_video_title("https://www.youtube.com/watch?v=" + video_ids[i])
        titles.append(str(i + 1) + ": " + title)
    title = "\n".join(titles)
    await ctx.send("Select the song number(1 - 5): ")
    await ctx.send(title)
    res = await client.wait_for("message", check=check)
    num = int(res.content) - 1
    if num < 0:
        num = 0
    if num > 4:
        num = 4
    await ctx.send("You've selected: https://www.youtube.com/watch?v=" + video_ids[num])
    song = pafy.new(video_ids[num])
    audio = song.getbestaudio()
    source = FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
    voice_client.play(source)


@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("THe current song is now paused!")
    else:
        await ctx.send("Nothing is playing rn!")

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
        await ctx.send("The music has been resumed!")
    else:
        await ctx.send("Nothing is paused rn!")


@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.send("The music has been stopped!")
    else:
        await ctx.send("Nothing to stop!")


client.run('your_api_key_here')
