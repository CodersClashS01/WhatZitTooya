import discord
from discord.ext import commands


class HelpCommand:

    def __init__(self, bot):
        self.bot = bot

        self.help_message = {}
        self.authorm = {}

    @commands.command(name="help")
    async def _help(self, ctx):
        async with ctx.typing():
            embed = discord.Embed(
                title="Hilfe zu den Bot-Commands",
                description="━━━━━━━━━━━━━━━━━━━",
                color=0x00fdfd
            )
            embed.add_field(
                name="Mein Präfix ist:",
                value=f"```\n{self.bot.prefix}\n```",
                inline=False
            )
            embed.add_field(
                name="Musik-Commmands",
                value="Click: 🎵",
                inline=False
            )
            embed.add_field(
                name="Moderation-Commands:",
                value="Click: 👮",
                inline=False
            )
            embed.add_field(
                name="Fun-Commands:",
                value="Click: 👯",
                inline=False,
            )
            embed.add_field(
                name="XP-System",
                value="Click: 🔮",
                inline=False
            )
            embed.add_field(
                name="Utility",
                value="Click: ⚙\n"
                      "Admin only",
                inline=False
            )
            embed.add_field(
                name="Lösche dieses Embed",
                value="Click: ❌",
                inline=False
            )
            self.help_message[ctx.author.id] = await ctx.send(embed=embed)
            self.authorm[ctx.message.author.id] = ctx.author

            await self.help_message[ctx.author.id].add_reaction('🏠')
            await self.help_message[ctx.author.id].add_reaction('🎵')
            await self.help_message[ctx.author.id].add_reaction('👮')
            await self.help_message[ctx.author.id].add_reaction('👯')
            await self.help_message[ctx.author.id].add_reaction('🔮')
            await self.help_message[ctx.author.id].add_reaction('⚙')
            await self.help_message[ctx.author.id].add_reaction('❌')

    async def on_reaction_add(self, reaction, user):
        try:
            nachricht = reaction.message
            if not user.bot:
                if reaction.emoji == "🏠" and user.id == self.authorm[user.id].id and nachricht.id == self.help_message[user.id].id:
                    embed = discord.Embed(
                        title="Hilfe zu den Bot-Commands",
                        description="━━━━━━━━━━━━━━━━━━━",
                        color=0x00fdfd
                    )
                    embed.add_field(
                        name="Mein Präfix ist:",
                        value=f"```\n{self.bot.prefix}\n```",
                        inline=False
                    )
                    embed.add_field(
                        name="Music-Commmands",
                        value="Click: 🎵",
                        inline=False
                    )
                    embed.add_field(
                        name="Moderating-Commands:",
                        value="Click: 👮",
                        inline=False
                    )
                    embed.add_field(
                        name="Fun-Commands:",
                        value="Click: 👯",
                        inline=False,
                    )
                    embed.add_field(
                        name="XP-System",
                        value="Click: 🔮",
                        inline=False
                    )
                    embed.add_field(
                        name="Settings",
                        value="Click: ⚙\n"
                              "Admin only",
                        inline=False
                    )
                    embed.add_field(
                        name="Lösche dieses Embed",
                        value="Click: ❌",
                        inline=False
                    )
                    await self.help_message[user.id].edit(new_content=None, embed=embed)
                    await self.help_message[user.id].remove_reaction("🏠", self.authorm[user.id])

                elif reaction.emoji == "🎵" and user.id == self.authorm[user.id].id and nachricht.id == self.help_message[user.id].id:
                    embed = discord.Embed(
                        title="Musik-Commmands",
                        description="━━━━━━━━━━━━━━━━━━━",
                        color=0x00fdfd
                    )
                    embed.add_field(
                        name="join",
                        value="Joint deinem aktuellen Voicechannel.",
                        inline=False
                    )
                    embed.add_field(
                        name="leave",
                        value="Stoppt das derzeit laufende Lied und verlässt den Channel.",
                        inline=False
                    )
                    embed.add_field(
                        name="play <Suchbegriff/YouTube-Link>",
                        value="Sucht ein Lied auf YouTube, und spielt es ab.",
                        inline=False
                    )
                    embed.add_field(
                        name="pause",
                        value="Pausiert das derzeit laufende Lied",
                        inline=False
                    )
                    embed.add_field(
                        name="resume",
                        value="Setzt das gestoppte Lied fort",
                        inline=False
                    )
                    embed.add_field(
                        name="skip",
                        value="Überspringt das aktuelle Lied.",
                        inline=False
                    )
                    embed.add_field(
                        name="volume <1-100>",
                        value="Ändert die Lautstärke des Players auf die angegebenen Prozent.",
                        inline=False
                    )
                    embed.add_field(
                        name="mute",
                        value="Mutet/Entmutet den Player.",
                        inline=False
                    )
                    embed.add_field(
                        name="queue",
                        value="Zeigt die aktuelle Queue an.",
                        inline=False
                    )
                    embed.add_field(
                        name="playing",
                        value="Versendet das Info-Embed zum aktuell laufenden Lied.",
                        inline=False
                    )
                    embed.add_field(
                        name="compose <noten/pausen>",
                        value="Spielt eine von dir komponierte Melodie in einem Voicechannel ab.\n*Mögliche Noten/Pausen:"
                              "c0.5, d0.5, e0.5, f0.5, g0.5, a0.5, h0.5, c1, d1, e1, f1, g1, a1, h1, longa, breve, sembibreve, minim, crotchet, quaver*",
                        inline=False
                    )
                    embed.add_field(
                        name="radio <Channel>",
                        value="Spielt einen Radiokanal.\nMit `radio help` erhältst du eine Liste der verfügbaren Kanäle.",
                        inline=False
                    )
                    await self.help_message[user.id].edit(new_content=None, embed=embed)
                    await self.help_message[user.id].remove_reaction("🎵", self.authorm[user.id])

                elif reaction.emoji == "👮" and user.id == self.authorm[user.id].id and nachricht.id == self.help_message[user.id].id:
                    embed = discord.Embed(
                        title="Moderation-Commands",
                        description="━━━━━━━━━━━━━━━━━━━",
                        color=0x00fdfd
                    )
                    embed.add_field(
                        name="**Hinweis:**",
                        value="Alle diese Commands erfordern mindestens eine der folgenden Permissions (User und Bot):\n"
                              "`manage_messages`, `manage_guild`, `kick_members`, `ban_members`",
                        inline=False
                    )
                    embed.add_field(
                        name="set_logchannel <TextChannel (Mention)>",
                        value="Richtet auf dem Server einen Logchannel ein.",
                        inline=False
                    )
                    embed.add_field(
                        name="current_logchannel",
                        value="Zeigt den aktuellen Logchannel auf dem Server an.",
                        inline=False
                    )
                    embed.add_field(
                        name="clear <Menge>",
                        value="Löscht die gegebene Menge an Nachrichten aus einem Channel.",
                        inline=False
                    )
                    embed.add_field(
                        name="kick <User (Mention)> <Grund>",
                        value="Kickt einen User.",
                        inline=False
                    )
                    embed.add_field(
                        name="ban <User (Mention)> <Grund>",
                        value="Bannt einen User. *Löscht die Nachrichten der letzten 5 Tage.*",
                        inline=False
                    )
                    embed.add_field(
                        name="report <User (Mention)>",
                        value="Reportet einen User.",
                        inline=False
                    )
                    embed.add_field(
                        name="reports <User (Mention)>",
                        value="Zeigt die Reports eines Users an.",
                        inline=False
                    )
                    await self.help_message[user.id].edit(new_content=None, embed=embed)
                    await self.help_message[user.id].remove_reaction("👮", self.authorm[user.id])

                elif reaction.emoji == "👯" and user.id == self.authorm[user.id].id and nachricht.id == self.help_message[user.id].id:
                    embed = discord.Embed(
                        title="Fun-Commands",
                        description="━━━━━━━━━━━━━━━━━━━",
                        color=0x00fdfd
                    )
                    embed.add_field(
                        name="rgif <Suchwort>",
                        value="Sucht und versendet ein Random GIF von Giphy"
                    )
                    embed.add_field(
                        name="avatar <User (Mention) (optional)>",
                        value="Schickt das Profilbild eines Users in den Chat. Wenn keiner angegeben, verschickt er das"
                              "des Benutzers des Commands."
                    )
                    embed.add_field(
                        name="schlechter_witz",
                        value="Versendet einen wahnsinnig schlechten, random ausgewählten Witz."
                    )
                    await self.help_message[user.id].edit(new_content=None, embed=embed)
                    await self.help_message[user.id].remove_reaction("👯", self.authorm[user.id])

                elif reaction.emoji == "🔮" and user.id == self.authorm[user.id].id and nachricht.id == self.help_message[user.id].id:
                    embed = discord.Embed(
                        title="XP-System",
                        description="━━━━━━━━━━━━━━━━━━━",
                        color=0x00fdfd
                    )
                    embed.add_field(
                        name="xp",
                        value="Zeigt dir deine aktuellen XP an.",
                        inline=False
                    )
                    embed.add_field(
                        name="level",
                        value="Zeigt dir dein aktuelles Level an.",
                        inline=False
                    )
                    embed.add_field(
                        name="leaderboard",
                        value="Zeigt dir die 10 Members mit den aktuell meisten XP auf dem Server an.",
                        inline=False
                    )
                    embed.add_field(
                        name="server-xp <enable | disable>",
                        value="Aktiviert oder deaktiviert das XP-System auf diesem Server "
                              "\n(Manage-Guild-Permission erforderlich)",
                        inline=False
                    )
                    await self.help_message[user.id].edit(new_content=None, embed=embed)
                    await self.help_message[user.id].remove_reaction("🔮", self.authorm[user.id])

                elif reaction.emoji == "⚙" and user.id == self.authorm[user.id].id and nachricht.id == self.help_message[user.id].id:
                    embed = discord.Embed(
                        title="Utility-Commands",
                        description="━━━━━━━━━━━━━━━━━━━",
                        color=0x00fdfd
                    )
                    embed.add_field(
                        name="status",
                        value="Zeigt ein Status-Embed mit ein paar Infos zum Bot an."
                    )
                    embed.add_field(
                        name="eval <Dein Code>",
                        value="Führt Python-Code im Codeblock (3 Backticks) aus.\n*Nur vom Bot-Owner verwendbar*"
                    )
                    embed.add_field(
                        name="vote",
                        value="Zeigt die aktuell aktiven Abstimmungen auf diesem Server an."
                    )
                    embed.add_field(
                        name="vote start <Frage | Option1 | Option2 | ... | Option9>",
                        value="Erstellt eine Neue Abstimmung auf diesem Server."
                    )
                    embed.add_field(
                        name="vote end <Vote-ID>",
                        value="Beendet eine Abstimmung auf diesem Server."
                    )
                    await self.help_message[user.id].edit(new_content=None, embed=embed)
                    await self.help_message[user.id].remove_reaction("⚙", self.authorm[user.id])

                elif reaction.emoji == '❌' and user.id == self.authorm[user.id].id and nachricht.id == self.help_message[user.id].id:
                    await self.help_message[user.id].delete()
                else:
                    pass
        except KeyError:
            pass
