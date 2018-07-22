import discord
from discord.ext import commands
from PIL import Image
import os
import json
import asyncio

ship = Image.open('BS/schwarz.png')
ship.thumbnail((90, 100))
channellist = []
games = {}
gamenumber = {}


class SchiffeVersenken:

    def __init__(self, bot):
        self.bot = bot

        self.offeneid = 0
        self.currentnumber = 0
        self.server = None
        self.ways = ["A:1", "A:2", "A:3", "A:4", "A:5", "A:6",
                     "B:1", "B:2", "B:3", "B:4", "B:5", "B:6",
                     "C:1", "C:2", "C:3", "C:4", "C:5", "C:6",
                     "D:1", "D:2", "D:3", "D:4", "D:5", "E:6",
                     "E:1", "E:2", "E:3", "E:4", "D:5", "E:6",
                     "F:1", "F:2", "F:3", "F:4", "F:5", "F:6"]
        self.convert = {"A": 45, "B": 135, "C": 225, "D": 319, "E": 410, "F": 500}
        self.geht = ["A1", "A2", "A3", "A4", "A5", "A6",
                     "B1", "B2", "B3", "B4", "B5", "B6",
                     "C1", "C2", "C3", "C4", "C5", "C6",
                     "D1", "D2", "D3", "D4", "D5", "E6",
                     "E1", "E2", "E3", "E4", "E5", "E6",
                     "F1", "F2", "F3", "F4", "F5", "F6"]

    async def on_ready(self):
        with open('config.json', 'r') as f:
            settings = json.load(f)
        guild = self.bot.get_guild(int(settings['bs_guild_id']))
        try:
            for i in guild.text_channels:
                await i.delete()
        except AttributeError:
            pass

    @commands.command(name='sv')
    @commands.guild_only()
    async def _sv(self, ctx):
        if ctx.message.author.id not in games:
            try:
                gamenumber1 = gamenumber[self.offeneid]
                gamenumber[ctx.message.author.id] = gamenumber[self.offeneid]
                self.offeneid = 0
                games[gamenumber1][ctx.message.author.id] = {}
                games[gamenumber1][ctx.message.author.id]["Schiffe"] = []
                games[gamenumber1][ctx.message.author.id]["Battle"] = 0
                games[gamenumber1][ctx.message.author.id]["Treffer"] = []
                games[gamenumber1][ctx.message.author.id]["Schüsse"] = []
                games[gamenumber1]["Spieler2"] = ctx.message.author.id
                games[gamenumber1]["nichtdran"] = 0
                Spieler1 = self.bot.get_user(games[gamenumber1]["Spieler1"])
                Spieler2 = self.bot.get_user(games[gamenumber1]["Spieler2"])
                await ctx.author.send(embed=discord.Embed(
                    title="Schiffe Versenken",
                    color=0x00fdfd,
                    description=f'Spiel wird gestartet {Spieler1.mention} vs {Spieler2.mention}'
                ))

                await ctx.send(embed=discord.Embed(
                    title="Schiffe Versenken",
                    color=0x00fdfd,
                    description=f'Spiel`{gamenumber1}` wird gestartet {Spieler1.mention} vs {Spieler2.mention} '
                                f'Für weitere Details, schaut bitte die Nachrichten an, '
                                f'die ich euch privat geschickt habe'
                ))
                await Spieler1.send(embed=discord.Embed(
                    title="Schiffe Versenken",
                    color=0x00fdfd,
                    description=f'Spiel wird gestartet {Spieler1.mention} vs {Spieler2.mention}'
                ))

                self.create_image(Spieler1, Spieler2, gamenumber1)
                await self.send_inv(ctx, Spieler1, Spieler2, gamenumber1)

            except KeyError:
                self.currentnumber += 1
                gamenumber1 = gamenumber[ctx.message.author.id] = self.currentnumber
                games[gamenumber1] = {}
                games[gamenumber1][ctx.message.author.id] = {}
                games[gamenumber1][ctx.message.author.id]["Schiffe"] = []
                games[gamenumber1][ctx.message.author.id]["Treffer"] = []
                games[gamenumber1][ctx.message.author.id]["Schüsse"] = []
                games[gamenumber1]["Spieler1"] = ctx.message.author.id
                games[gamenumber1]["dran"] = 0
                await ctx.author.send(embed=discord.Embed(
                    title="Schiffe Versenken",
                    color=0x00fdfd,
                    description="Warte auf einen weiteren Spieler..."
                ))

                self.offeneid = ctx.message.author.id

        else:
            await ctx.send("Du bist bereits in einem Spiel")

    def create_image(self, sp1, sp2, gn):
        os.makedirs(f"BS/Games/{gn}")
        Spielfeld1 = Image.open('BS/Spielfeld.png')
        Spielfeld1.save(f"BS/Games/{gn}/{sp1.id}.png")
        Spielfeld2 = Image.open('BS/Spielfeld.png')
        Spielfeld2.save(f"BS/Games/{gn}/{sp2.id}.png")

    async def send_inv(self, ctx, sp1, sp2, gn):
        with open('config.json', 'r') as f:
            settings = json.load(f)
        guild = self.bot.get_guild(int(settings['bs_guild_id']))
        caty = await guild.create_category(f"Game {gn}", overwrites=None)
        overwrites10 = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            sp1: discord.PermissionOverwrite(read_messages=True),
            sp2: discord.PermissionOverwrite(read_messages=True)
        }
        gamenumber1 = gamenumber[sp1.id]
        games[gamenumber1]["kf"] = 0
        kf = await guild.create_text_channel(name="Kampffeld", category=caty, overwrites=overwrites10)
        games[gamenumber1]["kf"] = kf.id
        for i in guild.text_channels:
            invite = await i.create_invite(reason=None)
            await sp1.send(invite)
            await sp1.send("Du hast 10sec um den Server zu joinen")
            await sp2.send(invite)
            await sp2.send("Du hast 10sec um den Server zu joinen")
            break
        overwrites1 = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            sp1: discord.PermissionOverwrite(read_messages=True)
        }
        overwrites2 = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            sp2: discord.PermissionOverwrite(read_messages=True)
        }
        if sp1 in guild.members and sp2 in guild.members:
            pass
        else:
            await asyncio.sleep(10)
        games[gamenumber1]["channel"] = []
        meh = await guild.create_text_channel(name=sp1.name, overwrites=overwrites1, category=caty)
        channellist.insert(len(channellist) + 1, meh.id)
        meh1 = await guild.create_text_channel(name=sp2.name, overwrites=overwrites2, category=caty)
        channellist.insert(len(channellist) + 1, meh1.id)
        games[gamenumber1]["channel"].insert(0, meh.id)
        games[gamenumber1]["channel"].insert(1, meh1.id)
        await meh.send("Willkommen zu Schiffe Versenken. Das Spielfeld ist 6x6, "
                       "das bedeutet es geht von A->F und 1->6.\n"
                       "Um ein Schiff zusetzen gibst du z.B. `A:1` ein. "
                       "Sobald du und dein Gegner 6 Schiffe plaziert habt,"
                       "geht es auch schon los! Weitere Infos nachher im Kampflog.")
        await meh1.send(
            "Willkommen zu Schiffe Versenken. Das Spielfeld ist 6x6,\n das bedeutet es geht von A->F und 1->6.\n"
            "Um ein Schiff zusetzen gibst du z.B. `A:1` ein. Dein Spielfeld kannst du unter dem Command `Spielfeld` "
            "ansehen. Sobald du und dein Gegner 6 Schiffe plaziert habt,"
            "geht es auch schon los! Weitere Infos nachher im Kampflog.")

    async def on_message(self, message):
        if message.channel.id in channellist:
            if message.content in self.ways:
                try:
                    gamenumber1 = gamenumber[message.author.id]
                    if not len(games[gamenumber1][message.author.id]["Schiffe"]) == 6:
                        output = SchiffeVersenken(self.bot).calc(message.content, message.author.id, gamenumber1)
                        if output not in games[gamenumber1][message.author.id]["Schiffe"]:
                            games[gamenumber1][message.author.id]["Schiffe"].insert(
                                len(games[gamenumber1][message.author.id]["Schiffe"]) + 1, output
                            )
                            games[gamenumber1]["Battle"] = False
                            await SchiffeVersenken(self.bot).check(games[gamenumber1]["Spieler1"], gamenumber1, games[gamenumber1]["Spieler2"])
                        else:
                            cl = self.bot.get_channel(message.channel.id)
                            await cl.send("Dort befindet sich schon ein Schiff. Leider gibt es keine AufeinanderSchiffe")
                    else:
                        cl = self.bot.get_channel(message.channel.id)
                        await cl.send("Du hast schon 6 Schiffe plaziert :c")

                except KeyError as k:
                    await message.channel.send(k)

        try:
            if message.channel.id == games[gamenumber[message.author.id]]["kf"] and \
                    games[gamenumber[message.author.id]]["Battle"] == 1 and not message.author.id == self.bot.user.id:
                if message.content.upper() in self.geht:
                    kf = self.bot.get_channel(games[gamenumber[message.author.id]]["kf"])
                    splitted = tuple(message.content[:2])
                    if message.author.id == games[gamenumber[message.author.id]]["dran"]:
                        if splitted in games[gamenumber[message.author.id]] \
                            [games[gamenumber[message.author.id]]["nichtdran"]]["Schiffe"]:

                            if splitted not in games[gamenumber[message.author.id]] \
                                [games[gamenumber[message.author.id]]["dran"]]["Schüsse"]:
                                games[gamenumber[message.author.id]][message.author.id]["Schüsse"].insert(len(games[gamenumber[message.author.id]][message.author.id]["Schüsse"]) + 1, splitted)
                                await SchiffeVersenken(self.bot).hit(splitted, message, games[gamenumber[message.author.id]]["nichtdran"])
                                await SchiffeVersenken(self.bot).test_win(message, gamenumber[message.author.id])
                            else:
                                await kf.send("Dort hast du schonmal geschossen. Du bist nochmal")
                        else:
                            await kf.send(embed=discord.Embed(
                                title="Daneben",
                                description=f"Dort befindet sich nichts. "
                                            f"<@{games[gamenumber[message.author.id]]['nichtdran']}> ist nun dran",
                                color=discord.Color.blue()
                            ))
                            meh = games[gamenumber[message.author.id]]["dran"]
                            muh = games[gamenumber[message.author.id]]["nichtdran"]
                            games[gamenumber[message.author.id]]["dran"] = muh
                            games[gamenumber[message.author.id]]["nichtdran"] = meh
                    else:
                        await kf.send(embed=discord.Embed(
                          title="Fehlgeschlagen",
                          description="Du bist leider nicht dran",
                          color=discord.Color.red()
                        ))

            elif message.channel.id == games[gamenumber[message.author.id]]["kf"] and  \
                    games[gamenumber[message.author.id]["Battle"]] == 0:
                c1 = self.bot.get_channel(message.channel.id)
                await c1.send("Der Kampf geht erst los, sobald alle Spieler 6 Schiffe gesetzt haben.")
            else:
                pass
        except KeyError:
            pass
        except TypeError:
            pass

    async def test_win(self, message, gamenumber):
        dran = games[gamenumber]["dran"]
        nichtdran = games[gamenumber]["nichtdran"]
        if len(games[gamenumber][nichtdran]["Treffer"]) == 6:
            kf = self.bot.get_channel(games[gamenumber]["kf"])
            winna = games[gamenumber]["nichtdran"]
            await kf.send(embed=discord.Embed(
                title="Gewonnen!",
                description="<@" + str(winna) + "> hat das Spiel Gewonnen!\n\nIn 10sec werden die Channels gelöscht.",
                color=0x00fdfd
            ))
            await SchiffeVersenken().delete_game(message)
        elif len(games[gamenumber][dran]["Treffer"]) == 6:
            kf = self.bot.get_channel(games[gamenumber]["kf"])
            winna = games[gamenumber]["dran"]
            await kf.send(embed=discord.Embed(
                title="Gewonnen!",
                description="<@" + str(winna) + "> hat das Spiel Gewonnen!\n\nIn 10sec werden die Channels gelöscht.",
                color=0x00fdfd
            ))
            await SchiffeVersenken(self.bot).delete_game(message)
        else:
            pass

    async def delete_game(self, message):
        gamenumber1 = gamenumber[message.author.id]
        await asyncio.sleep(10)
        c1 = self.bot.get_channel(games[gamenumber[message.author.id]]["channel"][0])
        c2 = self.bot.get_channel(games[gamenumber[message.author.id]]["channel"][1])
        kf = self.bot.get_channel(games[gamenumber[message.author.id]]["kf"])
        await c1.delete()
        await c2.delete()
        await kf.delete()
        one = games[gamenumber1]["nichtdran"]
        second = games[gamenumber1]["dran"]
        os.remove(f"BS/Games/{gamenumber[message.author.id]}/{str(one)}.png")
        os.remove(f"BS/Games/{gamenumber[message.author.id]}/{str(second)}.png")
        os.rmdir(f"BS/Games/{gamenumber[message.author.id]}")

    async def hit(self, split, message, seconduser):
        kf = self.bot.get_channel(games[gamenumber[message.author.id]]["kf"])
        await kf.send(embed=discord.Embed(
            title="Getroffen",
            color=discord.Color.blue(),
            description=f"Getroffen bei {split}.<@{seconduser}> ist nun dran."
        ))
        games[gamenumber[message.author.id]][message.author.id]["Treffer"].insert(
            len(games[gamenumber[message.author.id]][message.author.id]["Treffer"]) + 1, split)
        meh = games[gamenumber[message.author.id]]["dran"]
        muh = games[gamenumber[message.author.id]]["nichtdran"]
        games[gamenumber[message.author.id]]["dran"] = muh
        games[gamenumber[message.author.id]]["nichtdran"] = meh

    def calc(self, eingabe, check, gn):
        moglich = ["A:1", "A:2", "A:3", "A:4", "A:5", "A:6",
                   "B:1", "B:2", "B:3", "B:4", "B:5", "B:6",
                   "C:1", "C:2", "C:3", "C:4", "C:5", "C:6",
                   "D:1", "D:2", "D:3", "D:4", "D:5", "E:6",
                   "E:1", "E:2", "E:3", "E:4", "D:5", "E:6",
                   "F:1", "F:2", "F:3", "F:4", "F:5", "F:6"]
        if eingabe in moglich:
            meh = str(eingabe).split(":")

            if int(meh[1]) == 1:
                imagenew = Image.open(f"BS/Games/{gn}/{check}.png")
                imagenew.paste(ship, (self.convert[meh[0]], 37), ship)
                imagenew.save(f"BS/Games/{gn}/{check}.png")
                return str(meh[0]), str(meh[1])
            else:
                links = self.convert[meh[0]]
                if meh[1] >= "5":
                    rechts = (int(meh[1]) - 1) * 94 + 52
                else:
                    rechts = (int(meh[1]) - 1) * 94 + 40
                imagesecond = Image.open(f"BS/Games/{gn}/{check}.png")
                imagesecond.paste(ship, (links, rechts), ship)
                imagesecond.save(f"BS/Games/{gn}/{check}.png")
                return str(meh[0]), str(meh[1])

    async def check(self, pl1id, gamenumber, pl2id):
        kf = games[gamenumber]["kf"]
        c1 = games[gamenumber]["channel"][0]
        c2 = games[gamenumber]["channel"][1]
        player2 = games[gamenumber][games[gamenumber]["Spieler2"]]["Schiffe"]
        player1 = games[gamenumber][games[gamenumber]["Spieler1"]]["Schiffe"]
        if len(player1) == 6 and len(player2) == 6:
            await self.bot.get_channel(c1).send("Du und dein Gegner haben 6 Schiffe platziert. "
                                           "Gehe nun in den #Kampffeld Channel rein, um den Kampf zu starten!")
            await self.bot.get_channel(c2).send("Du und dein Gegner haben 6 Schiffe platziert. "
                                           "Gehe nun in den #Kampffeld Channel rein, um den Kampf zu starten!")
            await self.bot.get_channel(kf).send(f"@everyone Willkommen zum Kampf. Der unten genannte Spieler beginnt. "
                                           f"Um ein Schiff anzugreifen gibst du z.B. `A1` ein. <@{pl1id}> beginnt!")
            games[gamenumber]["Battle"] = 0
            games[gamenumber]["Battle"] = 1
            games[gamenumber]["dran"] = pl1id
            games[gamenumber]["nichtdran"] = pl2id

    @commands.command(name='clear_guild')
    @commands.is_owner()
    async def _clear_guild(self, ctx):
        for i in ctx.guild.text_channels:
            await i.delete()

    @commands.command()
    @commands.guild_only()
    async def spielfeld(self, ctx):
        try:
            spielnummer = gamenumber[ctx.author.id]
            await ctx.send(
                file=discord.File(fp=f"BS/Games/{spielnummer}/{ctx.author.id}.png",
                                  filename="Dein_derzeitiges_Spielfeld.png"))
        except FileNotFoundError:
            await ctx.send("Du befindest dich in keinem Spiel")
        except KeyError:
            await ctx.send("Du befindest dich in keinem Spiel")
