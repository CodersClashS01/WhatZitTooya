import discord
from discord.ext import commands

import asyncio
import youtube_dl
import datetime
import random


class YTDLSource:

    def __init__(self):

        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': "mp3",
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }

        self.ytdl = youtube_dl.YoutubeDL(self.ytdl_opts)

    async def create_source(self, request, search: str, loop=None):

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(search, download=False))

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:

                if entry is not None:
                    process_info = entry
                    break
            if process_info is None:
                return "Beim Verarbeiten der Anfrage trat ein Fehler auf."

        url = process_info['webpage_url']
        processed_info = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))

        if processed_info is None:
            return "Beim Verarbeiten der Anfrage trat ein Fehler auf."

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:

                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    return "Beim Verarbeiten der Anfrage trat ein Fehler auf."

        return [info, request]

    def get_embed(self, ctx, data):
        embed = discord.Embed(title="Nun wird gespielt", description="━━━━━━━━━━━━━━━━━━━", url=data['webpage_url'], color=0x00fdfd)

        duration = str(datetime.timedelta(seconds=data['duration']))
        upload_date = f"{data['upload_date'][6:8]}.{data['upload_date'][4:6]}.{data['upload_date'][0:4]}"

        embed.set_thumbnail(url=data['thumbnail'])
        embed.add_field(name="**Titel:**", value=f"{data['title']}", inline=False)
        embed.add_field(name="**Uploader:**", value=f"__{data['uploader']}__", inline=True)
        embed.add_field(name="**Datum des Uploads:**", value=f"__{upload_date}__", inline=True)
        embed.add_field(name="**Kanal:**", value=f"{data['uploader_url']}", inline=False)
        embed.add_field(name="**Dauer:**", value=f"__{duration}__", inline=True)
        embed.add_field(name="**Requester:**", value=f"{ctx.author.mention}", inline=True)

        return embed


class Voice:

    def __init__(self, bot):

        self.bot = bot
        self.ffmpeg_opts = " -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

        self.toene05 = ["c0.5", "d0.5", "e0.5", "f0.5", "g0.5", "a0.5", "h0.5"]
        self.toene1 = ["c1", "d1", "e1", "f1", "g1", "a1", "h1"]
        self.pauses = ["longa", "breve", "sembibreve", "minim", "crotchet", "quaver"]

        self.states = {}
        self.volume = {}
        self.mute = {}
        self.queue = {}
        self.requester = {}
        self.current = {}
        self.skip_votes = {}

        self.channels = [
            "http://stream01.iloveradio.de/iloveradio1.mp3,I Love Radio",
            "http://br-br1-obb.cast.addradio.de/br/br1/obb/mp3/128/stream.mp3,Bayern 1",
            "http://mp3channels.webradio.antenne.de:80/antenne,Antenne Bayern",
            "http://fhin.4broadcast.de/galaxyin.mp3,Radio Galaxy",
            "http://hr-youfm-live.cast.addradio.de/hr/youfm/live/mp3/128/stream.mp3,YOU FM",
            "http://mp3.planetradio.de/planetradio/hqlivestream.mp3,Planet Radio",
            "http://mp3channels.webradio.antenne.de/rockantenne,ROCK ANTENNE",
            "http://mp3stream7.apasf.apa.at:8000,Ö3",
            "http://raj.krone.at:80/kronehit-ultra-hd.aac,Kronehit",
            "http://radio.vgmradio.com:8040/stream,VGM Radio",
            "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p,BBC Radio 1",
            "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p,BBC Radio 2",
            "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio3_mf_p,BBC Radio 3",
            "http://us2.internet-radio.com:8281/live,Bollywood",
            "http://ibizaglobalradio.streaming-pro.com:8024/,Ibiza Global Radio"
        ]

    def radio(self, *, radio_channel):

        if radio_channel == "iloveradio":
            return "http://stream01.iloveradio.de/iloveradio1.mp3,I Love Radio"
        elif radio_channel == "bayern1":
            return "http://br-br1-obb.cast.addradio.de/br/br1/obb/mp3/128/stream.mp3,Bayern 1"
        elif radio_channel == "antenne":
            return "http://mp3channels.webradio.antenne.de:80/antenne,Antenne Bayern"
        elif radio_channel == "radiogalaxy":
            return "http://fhin.4broadcast.de/galaxyin.mp3,Radio Galaxy"
        elif radio_channel == "youfm":
            return "http://hr-youfm-live.cast.addradio.de/hr/youfm/live/mp3/128/stream.mp3,YOU FM"
        elif radio_channel == "planetradio":
            return "http://mp3.planetradio.de/planetradio/hqlivestream.mp3,Planet Radio"
        elif radio_channel == "rockantenne":
            return "http://mp3channels.webradio.antenne.de/rockantenne,ROCK ANTENNE"
        elif radio_channel == "oe3":
            return "http://mp3stream7.apasf.apa.at:8000,Ö3"
        elif radio_channel == "kronehit":
            return "http://raj.krone.at:80/kronehit-ultra-hd.aac,Kronehit"
        elif radio_channel == "vgm":
            return "http://radio.vgmradio.com:8040/stream,VGM Radio"
        elif radio_channel == "bbc1":
            return "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p,BBC Radio 1"
        elif radio_channel == "bbc2":
            return "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p,BBC Radio 2"
        elif radio_channel == "bbc3":
            return "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio3_mf_p,BBC Radio 3"
        elif radio_channel == "bollywood":
            return "http://us2.internet-radio.com:8281/live,Bollywood"
        elif radio_channel == "ibiza":
            return "http://ibizaglobalradio.streaming-pro.com:8024/,Ibiza Global Radio"
        elif radio_channel == "random":
            return random.choice(self.channels)
        elif radio_channel == "help":
            return "EMBED"
        else:
            return "NOPE"

    def pause(self, *, arg: str):
        return {
            'longa': 4,
            'breve': 2,
            'semibreve': 1,
            'minim': 0.5,
            'crotchet': 0.25,
            'quaver': 0.125
        }.get(arg)

    async def play_next_song(self, ctx, error=None):

        if error:
            return await ctx.send(f"Beim Verarbeiten der Anfrage trat ein Fehler auf: {error}")

        if not self.queue[str(ctx.guild.id)].empty():

            try:
                del self.skip_votes[str(ctx.guild.id)]
            except KeyError:
                pass

            song_info = await self.queue[str(ctx.guild.id)].get()
            info_dict = song_info[0]
            current_request = song_info[1]
            self.requester[str(ctx.guild.id)] = current_request.author
            song_embed = YTDLSource().get_embed(current_request, info_dict)
            self.current[str(ctx.guild.id)] = [info_dict, current_request]

            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(info_dict['url'], before_options=self.ffmpeg_opts, options='-vn'))

            self.states[str(ctx.guild.id)].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(ctx, e), self.bot.loop).result())
            try:
                self.states[str(ctx.guild.id)].source.volume = self.volume[str(ctx.guild.id)]
            except KeyError:
                pass

            await ctx.send(embed=song_embed)

    async def play_next_note(self, note, error):
        pass

    @commands.command(name='join')
    @commands.guild_only()
    async def _join(self, ctx):
        async with ctx.typing():
            if ctx.voice_client is not None:
                    voice = await ctx.voice_client.move_to(ctx.author.voice.channel)
            else:
                    voice = await ctx.author.voice.channel.connect()
                    self.states[str(ctx.guild.id)] = voice

    @_join.error
    async def join_error(self, ctx, error: Exception):
        if isinstance(error, commands.CommandInvokeError):
            return await ctx.send("Bitte verbinde dich zuerst mit einem Voicechannel.")

    @commands.command(name='leave')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx):
        async with ctx.typing():
            if ctx.voice_client is None:
                return await ctx.send("Ich bin mit keinem Voice-Channel verbunden.")

            try:
                if self.queue[str(ctx.guild.id)].qsize() >= 0:
                    del self.queue[str(ctx.guild.id)]

                del self.states[str(ctx.guild.id)]
                del self.requester[str(ctx.guild.id)]
                del self.current[str(ctx.guild.id)]

                try:
                    del self.skip_votes[str(ctx.guild.id)]
                except KeyError:
                    pass
                try:
                    del self.volume[str(ctx.guild.id)]
                except KeyError:
                    pass
                try:
                    del self.mute[str(ctx.guild.id)]
                except KeyError:
                    pass
            except KeyError:
                pass
            finally:
                await ctx.voice_client.disconnect()

    @commands.command(name='skip')
    @commands.guild_only()
    async def _skip(self, ctx):
        async with ctx.typing():
            if not self.states[str(ctx.guild.id)].is_playing():
                return await ctx.send("Im Moment wird nichts abgespielt.")

            try:
                if len(self.skip_votes[str(ctx.guild.id)]) >= 0:
                    pass
            except KeyError:
                self.skip_votes[str(ctx.guild.id)] = set()

            if ctx.author.voice.channel is not None and ctx.author.voice.channel == self.states[str(ctx.guild.id)].channel:

                voter = ctx.author
                current_requester = self.requester[str(ctx.guild.id)]
                if voter.id == current_requester.id:
                    await ctx.send("Der Requester überspringt den Song.")
                    try:
                        del self.skip_votes[str(ctx.guild.id)]
                    except KeyError:
                        pass
                    self.states[str(ctx.guild.id)].stop()
                elif voter.id not in self.skip_votes[str(ctx.guild.id)]:
                    self.skip_votes[str(ctx.guild.id)].add(voter.id)
                    votes = len(self.skip_votes[str(ctx.guild.id)])

                    if votes >= 3:
                        await ctx.send("3 oder mehr Skip-Votes wurden nun erreicht. Der Song wird geskippt.")
                        del self.skip_votes[str(ctx.guild.id)]

                        self.states[str(ctx.guild.id)].stop()
                    else:
                        await ctx.send(f"Skip-Vote wurde hinzugefügt. Momentan {votes}/3 Votes.")
                else:
                    await ctx.send("Du hast bereits dafür gevotet, diesen Song zu überspringen.")
            else:
                await ctx.send(f"Du kannst nur Skip-Votes hinzufügen, wenn du in "
                               f"{self.states[str(ctx.guild.id)].channel.mention} mithörst.")

    @commands.command(name='pause')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx):
        async with ctx.typing():
            try:
                self.states[str(ctx.guild.id)].pause()
            except Exception as error:
                await ctx.send(f"Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten: {error}")

    @commands.command(name='resume')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx):
        async with ctx.typing():
            try:
                self.states[str(ctx.guild.id)].resume()
            except Exception as error:
                await ctx.send(f"Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten: {error}")

    @commands.command(name='stop')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx):
        async with ctx.typing():
            try:
                try:
                    del self.queue[str(ctx.guild.id)]
                except:
                    pass

                self.states[str(ctx.guild.id)].stop()
            except Exception as error:
                await ctx.send(f"Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten: {error}")

    @commands.command(name='volume')
    @commands.guild_only()
    async def _volume(self, ctx, *, volume: str):
        async with ctx.typing():
            try:
                vol_source = self.states[str(ctx.guild.id)].source.volume

                volume = int(volume) if len(volume) > 0 else vol_source
                player_volume = volume / 100
            except:
                return await ctx.send("Bitte gib eine Zahl von 1-100 an, um die Lautstärke des Players zu ändern!")

            try:
                if player_volume <= 1.0:
                    self.states[str(ctx.guild.id)].source.volume = player_volume
                    self.volume[str(ctx.guild.id)] = player_volume
                    await ctx.send(f"Die Lautstärke des Players wurde auf {volume}% gesetzt.")
                elif player_volume > 1.0:
                    return await ctx.send("Du kannst den Player nicht lauter als 100% machen. Nur leiser..")
            except Exception as error:
                await ctx.send(f"Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten: {error}")

    @commands.command(name='mute')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _mute(self, ctx):
        async with ctx.typing():
            try:
                vol_source = self.states[str(ctx.guild.id)].source.volume

                if 0.0 < vol_source <= 1.0:
                    self.mute[str(ctx.guild.id)] = vol_source

                    vol_source = 0.0
                    self.states[str(ctx.guild.id)].source.volume = vol_source
                    await ctx.send("Der Player wurde erfolgreich gemutet.")
                elif vol_source == 0.0:
                    vol_source = self.mute[str(ctx.guild.id)]
                    self.states[str(ctx.guild.id)].source.volume = vol_source
                    del self.mute[str(ctx.guild.id)]
                    await ctx.send("Der Player wurde erfolgreich entmutet.")
                else:
                    await ctx.send("Beim Verarbeiten der Anfrage ist ein Fehler aufgetreten.")
            except Exception as error:
                await ctx.send(f"Beim Verabreiten der Anfrage ist ein Fehler aufgetreten: {error}")

    @commands.command(name='queue')
    @commands.guild_only()
    async def _queue(self, ctx):
        async with ctx.typing():
            try:
                if self.queue[str(ctx.guild.id)].qsize() >= 0:
                    pass
            except KeyError:
                self.queue[str(ctx.guild.id)] = asyncio.Queue()

            if self.queue[str(ctx.guild.id)].qsize() > 0:
                pl_embed = discord.Embed(title="Queue", description="━━━━━━━━━━━━━━━", color=0x00fdfd)
                count = 1

                for element in range(self.queue[str(ctx.guild.id)].qsize()):

                    item = await self.queue[str(ctx.guild.id)].get()
                    await self.queue[str(ctx.guild.id)].put(item)

                    pl_embed.add_field(name=f"{count}. Song:", value=item[0]['title'], inline=False)

                    count += 1

                await ctx.send(embed=pl_embed)
            else:
                await ctx.send("In der Queue sind momentan keine Songs.")

    async def play_compose(self, ctx, arguments, error=None):
        arg = arguments.pop(0)
        if arg.lower() in self.toene05 or arg.lower() in self.toene1:
            player = discord.FFmpegPCMAudio(f'klavier/{arg.lower()}.mp3')
            source = discord.PCMVolumeTransformer(player)
            self.states[str(ctx.guild.id)].play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_compose(ctx, arguments, e), self.bot.loop).result())
        elif arg.lower() in self.pauses:
            await asyncio.sleep(self.pause(arg=arg.lower()))
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="Voice -> Compose",
                    description=f"Ein Fehler ist aufgetreten: Die Note `{arg}` wurde nicht gefunden.",
                    color=0x00fdfd
                )
            )

    @commands.command(name='compose')
    @commands.guild_only()
    async def _compose(self, ctx, *noten):

        if not ctx.guild.voice_client:
            await ctx.invoke(self._join)

        asyncio.get_event_loop().run_until_complete(self.play_compose(ctx, list(noten)))

    @_compose.error
    async def _compose_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\ncompose <Noten und Pausen> (siehe help oder Docs)\n```",
                    color=0x00fdfd
                )
            )

    @commands.command(name='playing')
    @commands.guild_only()
    async def _playing(self, ctx):
        async with ctx.typing():
            song_embed = YTDLSource().get_embed(self.current[str(ctx.guild.id)][1], self.current[str(ctx.guild.id)][0])
            await ctx.send(embed=song_embed)

    @commands.command(name='play')
    @commands.guild_only()
    async def play_yt(self, ctx, *, search: str):
        async with ctx.typing():
            info_dict = await YTDLSource().create_source(request=ctx, search=search)
            if info_dict == "Beim Verarbeiten der Anfrage trat ein Fehler auf.":
                return await ctx.send(info_dict)

            if not ctx.voice_client:
                await ctx.invoke(self._join)

            try:
                if self.queue[str(ctx.guild.id)].qsize() >= 0:
                    pass
                else:
                    self.queue[str(ctx.guild.id)] = asyncio.Queue()
            except KeyError:
                self.queue[str(ctx.guild.id)] = asyncio.Queue()

            if self.states[str(ctx.guild.id)].is_playing() or self.states[str(ctx.guild.id)].is_paused():
                if ctx.author.voice.channel == self.states[str(ctx.guild.id)].channel:
                    await self.queue[str(ctx.guild.id)].put(info_dict)
                    await ctx.send("Song wurde zur Queue hinzugefügt.")
            else:
                await self.queue[str(ctx.guild.id)].put(info_dict)
                await self.play_next_song(ctx)

    @commands.command(name='radio')
    @commands.guild_only()
    async def play_radio(self, ctx, *, channel: str):
        async with ctx.typing():
            radio_string = self.radio(radio_channel=channel)

            if radio_string == "NOPE":
                return await ctx.send("Sorry, aber ich konnte diesen Kanal nicht finden. Für eine Liste der gültigen Kanäle, tippe bitte `.radio embed` in den Chat.")
            elif radio_string == "EMBED":
                channel_embed = discord.Embed(title="Radio-Channels:", description="━━━━━━━━━━━━━━━━━━━━━━", color=0x00fdfd)

                channel_embed.add_field(name="I Love Radio <iloveradio>",
                                        value="http://stream01.iloveradio.de/iloveradio1.mp3",
                                        inline=False)
                channel_embed.add_field(name="Bayern 1 <bayern1>",
                                        value="http://br-br1-obb.cast.addradio.de/br/br1/obb/mp3/128/stream.mp3",
                                        inline=False)
                channel_embed.add_field(name="Antenne Bayern <antenne>",
                                        value="http://mp3channels.webradio.antenne.de:80/antenne",
                                        inline=False)
                channel_embed.add_field(name="Radio Galaxy <radiogalaxy>",
                                        value="http://fhin.4broadcast.de/galaxyin.mp3",
                                        inline=False)
                channel_embed.add_field(name="YOU FM <youfm>",
                                        value="http://hr-youfm-live.cast.addradio.de/hr/youfm/live/mp3/128/stream.mp3",
                                        inline=False)
                channel_embed.add_field(name="Planet Radio <planetradio>",
                                        value="http://mp3.planetradio.de/planetradio/hqlivestream.mp3",
                                        inline=False)
                channel_embed.add_field(name="ROCK ANTENNE <rockantenne>",
                                        value="http://mp3channels.webradio.antenne.de/rockantenne",
                                        inline=False)
                channel_embed.add_field(name="Ö3 <oe3>",
                                        value="http://mp3stream7.apasf.apa.at:8000",
                                        inline=False)
                channel_embed.add_field(name="Kronehit <kronehit>",
                                        value="http://raj.krone.at:80/kronehit-ultra-hd.aac",
                                        inline=False)
                channel_embed.add_field(name="VGM Radio <vgm>",
                                        value="http://radio.vgmradio.com:8040/stream",
                                        inline=False)
                channel_embed.add_field(name="BBC Radio 1 <bbc1>",
                                        value="http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p",
                                        inline=False)
                channel_embed.add_field(name="BBC Radio 2 <bbc2>",
                                        value="http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p",
                                        inline=False)
                channel_embed.add_field(name="BBC Radio 3 <bbc3>",
                                        value="http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio3_mf_p",
                                        inline=False)
                channel_embed.add_field(name="Bollywood <bollywood>",
                                        value="http://us2.internet-radio.com:8281/live", inline=False)
                channel_embed.add_field(name="Ibiza Global Radio <ibiza>",
                                        value="http://ibizaglobalradio.streaming-pro.com:8024/",
                                        inline=False)
                channel_embed.add_field(name="Zufällig <random>",
                                        value="Spielt einen zufälligen Sender ab",
                                        inline=False)

                await ctx.send(embed=channel_embed)
            else:
                radio_url, radio_channel = radio_string.split(",")

                if not ctx.voice_client:
                    await ctx.invoke(self._join)

                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(radio_url, before_options=self.ffmpeg_opts, options='-vn'))
                self.states[str(ctx.guild.id)].play(source)
                await ctx.send(f"Nun wird gespielt: {radio_channel}")
