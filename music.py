import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.core import command

from random import shuffle
from youtube_dl import YoutubeDL

from roles import voice_channel_moderator_roles

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.current_song = None
        self.music_queue = []
        self.skip_votes = set()

        self.YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True"}
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        self.vc = ""

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if not member.id == self.bot.user.id:
            return

        elif before.channel is None:
            voice = self.vc
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing:
                    time = 0
                if time == 20:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)[
                    "entries"
                ][0]
            except Exception:
                return False

        return {"source": info["formats"][0]["url"], "title": info["title"]}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]["source"]

            self.current_song = self.music_queue.pop(0)

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(),
            )
        else:
            self.is_playing = False
            self.current_song = None

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]["source"]

            if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])

            await ctx.send(
                f""":arrow_forward: Lejátszás: {self.music_queue[0][0]['title']} | Zene kérve {self.music_queue[0][2]} által."""
            )

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(),
            )
            self.current_song = self.music_queue.pop(0)

        else:
            self.is_playing = False
            self.current_song = None

    @commands.command(
        name="p",
        help="YouTube zene lejátszása. \U0001F3B5",
        aliases=["play"],
    )
    async def p(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Csatlakozz egy hangcsatornához!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Sikertelen zene lekérés. Helytelen formátum."
                )
            else:
                await ctx.send(
                    f""":headphones: {song["title"]} hozzáadva a várólistához {ctx.author.mention} által."""
                )
                self.music_queue.append(
                    [song, voice_channel, ctx.author.mention])

                if self.is_playing == False:
                    await self.play_music(ctx)
    #spongebob
    @commands.command(
        name="sp",
        help="Enes Spondzsbob lejátszása. \U0001F3B5",
        aliases=["spongebob"],
    )
    async def sp(self, ctx):
        query = "enes spongebob"

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Csatlakozz egy hangcsatornához!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Sikertelen zene lekérés. Helytelen formátum."
                )
            else:
                await ctx.send(
                    f""":headphones: {song["title"]} hozzáadva a várólistához {ctx.author.mention} által."""
                )
                self.music_queue.append(
                    [song, voice_channel, ctx.author.mention])

                if self.is_playing == False:
                    await self.play_music(ctx)
    #spongebob vége
    @commands.command(
        name="cp",
        help="Jelenleg játszó szám kiírása. \U0001F440",
        aliases=["playing"],
    )
    async def cp(self, ctx):
        msg = "Nem játszik egyetlen szám sem." if self.current_song is None else f"""Lejátszás: {self.current_song[0]['title']} | hozzáadva {self.current_song[2]} által.\n"""
        await ctx.send(msg)

    @commands.command(
        name="q",
        help="Várólista kiírása. \U0001F440",
        aliases=["queue"],
    )
    async def q(self, ctx):
        print(self.music_queue)
        retval = ""
        for (i, m) in enumerate(self.music_queue):
            retval += f"""{i+1}. | {m[0]['title']} | hozzáadva {m[int(2)]} által.\n"""

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("Üres a várólista.")

    @commands.command(name="cq", help="Várólista törlése.", aliases=["clear"])
    async def cq(self, ctx):
        self.music_queue = []
        await ctx.send("""Várólista törölve!""")

    @commands.command(name="shuffle", help="Megkeveri a várólistát.")
    async def shuffle(self, ctx):
        shuffle(self.music_queue)
        await ctx.send("""Várólista keverve!""")

    @commands.command(
        name="s", help="Jelenlegi szám átlépése.", aliases=["skip"]
    )
    async def skip(self, ctx):
        if self.vc != "" and self.vc:
            await ctx.send("""Zene átlépve!""")
            self.skip_votes = set()
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(
        name="voteskip",
        help="Zene átléptetésének megszavazása.",
        aliases=["vs"],
    )
    async def voteskip(self, ctx):
        if ctx.voice_client is None:
            return
        num_members = len(ctx.voice_client.channel.members) - 1
        self.skip_votes.add(ctx.author.id)
        votes = len(self.skip_votes)
        if votes >= num_members / 2:
            await ctx.send(f"A szavazás többséggel átment | ({votes}/{num_members}).")
            await self.skip(ctx)

    @commands.command(
        name="l",
        help="A szoba elhagyására kényszeríti a botot. \U0001F634",
        aliases=["leave"],
    )
    @commands.has_any_role(*voice_channel_moderator_roles)
    async def leave(self, ctx, *args):
        if self.vc.is_connected():
            await ctx.send("""Viszlát pafook! :slight_smile:""")
            await self.vc.disconnect(force=True)

    @commands.command(
        name="pn", help="Zene várólista tetejére való áthelyezése. \U0001F4A5"
    )
    @commands.has_any_role(*voice_channel_moderator_roles)
    async def playnext(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Csatlakozz egy hangcsatornához!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Sikertelen zene lekérés. Helytelen formátum."
                )
            else:
                vote_message = await ctx.send(
                    f":headphones: {song['title']} a várólista tetejére lesz áthelyezve {ctx.author.mention} által.\n"
                    "30 másodperced van reagálni egy :+1: reakcióval ezen az üzeneten.\n"
                    "A kért zeneszám 50% feletti többség esetén fog lejátszódni."
                )
                await vote_message.add_reaction("\U0001F44D")
                await asyncio.sleep(30)
                voters = len(voice_channel.members)
                voters = voters - 1 if self.vc else voters
                result_vote_msg = await ctx.fetch_message(vote_message.id)
                votes = next(react for react in result_vote_msg.reactions if str(
                    react.emoji) == "\U0001F44D").count - 1
                if votes >= voters / 2:
                    self.music_queue.insert(
                        0,
                        [song, voice_channel, ctx.author.mention]
                    )
                    await ctx.send(
                        f":headphones: {song['title']} hozzáadva következő zenéként."
                    )
                else:
                    self.music_queue.append(
                        [song, voice_channel, ctx.author.mention]
                    )
                    await ctx.send(
                        f":headphones: Sikertelen szavzás: {song['title']} a várólista végére kerül."
                    )

                if self.is_playing == False or (
                    self.vc == "" or not self.vc.is_connected() or self.vc == None
                ):
                    await self.play_music(ctx)

    """Pause the currently playing song."""

    @commands.command(name="pause", help="Jelenleg játszó zene szüneteltetése.")
    @commands.has_any_role(*voice_channel_moderator_roles)
    async def pause(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send("Jelenleg semmit sem játszok!", delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f":pause_button:  {ctx.author.mention} Zene szüneteltetve!")

    """Resume the currently playing song."""

    @commands.command(name="resume", help="Folytatja a jelenleg játszó számot.")
    @commands.has_any_role(*voice_channel_moderator_roles)
    async def resume(self, ctx):
        vc = ctx.voice_client

        if not vc or vc.is_playing():
            return await ctx.send("Már játszok egy számot!", delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f":play_pause:  {ctx.author.mention} Zene folytatása!")

    @commands.command(
        name="r",
        help="Zene várólistáról való levétele a megadott sorszámnál. \U0001F4A9",
        aliases=["remove"],
    )
    @commands.has_any_role(*voice_channel_moderator_roles)
    async def remove(self, ctx, *args):
        query = "".join(*args)
        index = 0
        negative = True if (query[0] == "-") else False
        if not negative:
            for i in range(len(query)):
                convert = (int)(query[i])
                index = index * 10 + convert
        index -= 1

        if negative:
            await ctx.send("A sorszám nem lehet kisebb mint 1.")
        elif index >= len(self.music_queue):
            await ctx.send("Helytelen sorszám. Nincs ilyen szám a várólistában!")
        else:
            await ctx.send(
                f""":x: {query}. | Zene levéve a várólistáról {ctx.author.mention} által."""
            )
            self.music_queue.pop(index)


    @commands.command(
        name="rep",
        help="Újraindítja a jelenlegi zeneszámot. \U000027F2",
        aliases=["restart"],
    )
    @commands.has_any_role(*voice_channel_moderator_roles)
    async def restart(self, ctx):
        song=[]
        if(self.current_song != None):
            song= self.current_song[0]
            voice_channel = ctx.author.voice.channel
            self.music_queue.insert(
                0,
                [song, voice_channel, ctx.author.mention]
            )
            self.vc.stop()
            if len(self.music_queue) > 0:
                self.is_playing = True

                m_url = self.music_queue[0][0]["source"]

                if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                    self.vc = await self.music_queue[0][1].connect()
                    await ctx.send("Nincs zene hozzáadva.")
                else:
                    await self.vc.move_to(self.music_queue[0][1])

                    await ctx.send(
                        f""":repeat: Újrajátszás: {self.music_queue[0][0]['title']} | kérve {self.music_queue[0][2]} által."""
                    )

                    self.vc.play(
                        discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                        after=lambda e: self.play_next(),
                    )
                    self.current_song = self.music_queue.pop(0)

        else:
            self.is_playing = False
            self.current_song = None
            await ctx.send(f""":x: Nem megy éppen zene.""")
