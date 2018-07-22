import discord
from discord.ext import commands

import random
from giphypy.client import Giphy


class FunCommands:

    def __init__(self, bot):
        self.bot = bot
        self.giphy = Giphy(api_key='dc6zaTOxFJmzC', loop=bot.event_loop)

        self.jokes = ["Deine Mutter ist sogar in Minecraft rund.",
                      "Warum kann deine Mutter den Enderdrache in Minecraft nicht besiegen? Weil sie nicht durch das Portal passt.",
                      'Gott: "Ich kann Länder und Flüsse erschaffen." Notch: "Ich auch." Gott: Ich kann lebewessen erschafen. Notch: "Ich auch." Gott: "Ich kann runde Dinge erschaffen." Notch: (left the game) XD',
                      "Wie nennt man Minecraft-Filme? Blockbuster",
                      "Was macht ein Creeper an einem warmen Sommer Tag? Den Rasen sprengen.",
                      "Was macht Steve wenn er sich fit halten will. Er rennt einmal um den Block",
                      "Dein Niveau ist wie Beddrock …ganz tief unten",
                      'Kommt Steve zum Elternsprechtag fragt die Lehrerin: „Wo sind deine Eltern?" Steve:„Von der Lore überfahren" Lehrerin:„und deine Großeltern ?" Steve:„auch von der Lore überfahren" Lehrerin:„Und was hast du dann den ganzen Tag gemacht ???„ Steve:„Lore gefahren“ XDDD',
                      "Warum ist die minecraft Welt Unendlich. Damit deine Mutter hinein past",
                      "Ein Creeper hat mir neulich einen Witz erzählt.Ein absoluter Knaller.",
                      "Treffen sich 2 Creeper im Keller sagt der eine zum anderen wollen wir hochgehen?",
                      'Geht Poishii in eine Höhle, kommt wieder raus und sagt : "ihh eine Spinne!" Geht Minimichecker in die Höhle, kommt wieder raus und sagt: " ihhh eine Spinne!" Geht Lumpi in die Höhle, kommt die Spinne raus und sagt : „ihhh ein Lumpi!“',
                      "Warum verließ der Enderman die Party?\nWeil ihn alle anstarrten",
                      "Deine Mutter ist so dumm, sie stirbt sogar im Kreativmodus.",
                      "Wenn Chuck Norris Minecraft spielt, steht im Chat „Herobrine hat das Spiel verlassen“…",
                      "Auf meinem Grabstein wird einmal stehen: Respawning in 3, 2, 1… Connection lost",
                      "Was sagt ein Creeper wenn ihm ein Essen sehr gut geschmeckt hat? BOMBASTISCH",
                      "In Bedwars: Mein Bett wurde abgebaut. Kann ich bei dir schlafen.",
                      "Deine Mutter ist mal ins Nether gegangen, Das ist der Grund warum dort alle Gahsts weinen.",
                      "Deine Mutter ist so verfressen das sie bei minecraft im friedlichen Modus essen brauch",
                      "Für was sorgt der Creeper an Silvester? Für einen großen Knaller",
                      "Warum kann deine Mutter in Skywars nicht runterfallen?\nAntwort: Sie bleibt zwischen den Inseln stecken",
                      "Warum schneidet Steve die Beine von seinem Bett ab? Damit er einen tieferen schlaf hat",
                      "Warum warum wurde Steve in der Schulegemobbt? Er war der kantigste von allen.",
                      "Was machen zwei wütende Schafe ? - Sie kriegen sich in die Wolle!",
                      "Wie macht der Zug? Noob Noob",
                      "Warum mag steve keine creeper\nAntwort:Er lässt seine träume platzen",
                      "Warum ist Poishii am Mond der schnellste??? Er kann Moonwalk :D",
                      "Was ist eine witch im sand? Eine Sandwitch",
                      "Mutter :PC Ausschalten, Kind : Ok… laufe nur noch 1mal um die Welt",
                      "Warum schafft deine Mutter kein Mlg?\nweil das anticheat sie wegen Absturzgefahr nicht springen lässt.",
                      "Deine Mutter ist so fett, immer wenn sie spawnt durch brennt bei jeden die Grafikkarte",
                      "Chuck Norris speilt minecraft ohne Pixel.",
                      "Für was sorgt die Spinne ? Für ein tolles Netzwerk",
                      "Was ist deine Mutter in Minecraft? Ein Matrix Fehler",
                      "Warum stinken die Zombies in Minecraft ? Weil sie sich nicht alle Ecken waschen können",
                      "Deine Mutter ist so fett wenn sie platzt ist sogar das TNT neidisch!!",
                      "Warum ist der Creeper so traurig? Weil er in dein Gesicht geguckt hat",
                      "Deine Mutter ist do fett sie fällt sogar durch Bedrock",
                      "Treffen sich 2 Skelette . Beide Tot",
                      "Ich habe meine Enderperle verworfen! Willst du meine neue Perle sein?",
                      "Wieso bekommt poishii alles günstiger? -weil er reduced",
                      "Deine Mutter ist so fett, sie braucht in Minecraft eine eigene Skingröße",
                      "Was ist das Lieblingslied eines Ghasts? Fireball",
                      "Creeper1: Lass uns den Zombie mal wegsprängen! Creeper2: Halts Maul, wir können nicht sprechen!",
                      "Was haben steves und Pizza Margaritha gemeinsam? Sie haben beide nix drauf",
                      "Arbeites du bei LIDL oder warum Kassierst du so?",
                      "Deine Mutter spielt Minecraft mit runden Blöcken.",
                      "Ein Creeper zum anderen:„Ich habe platzangst!“"
                     ]

    async def get_image(self, ctx, rgif):
        info_dict = await self.giphy.search(rgif)
        gif_url = str(info_dict.get('data')[0].get('images').get('downsized').get('url'))

        try:
            async with self.bot.client_session.get(gif_url) as response:
                gif = await response.read()

            await ctx.send(file=discord.File(gif, 'gif.gif'))
        except IndexError:
            return

    @commands.command(name='rgif')
    @commands.guild_only()
    async def _random_gif(self, ctx, *, keyword: str):
        async with ctx.typing():
            self.bot.event_loop.run_until_complete(self.get_image(ctx=ctx, rgif=keyword))

    @_random_gif.error
    async def _random_gif_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nrgif <Suchbegriff>\n```"
                )
            )

    @commands.command(name="avatar")
    @commands.guild_only()
    async def _avatar(self, ctx, *, user: discord.Member):
        img_embed = discord.Embed(
            title=f"{user.name}s Profilbild",
            description="━━━━━━━━━━━━━━━━━━━",
            color=0x00fdfd
        )
        img_embed.set_image(url=user.avatar_url)

        await ctx.send(embed=img_embed)

    @_avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(embed=discord.Embed(
                title="━━━━━━━━━━━━━━━━━━━",
                description="Ich konnte den Avatar dieses Nutzers leider nicht abrufen. Bitte versuche es erneut.",
                color=0x00fdfd)
            )
        if isinstance(error, commands.MissingRequiredArgument):
            img_embed = discord.Embed(
                title=f"{ctx.author.name}s Profilbild",
                description="━━━━━━━━━━━━━━━━━━━",
                color=0x00fdfd
            )
            img_embed.set_image(url=ctx.author.avatar_url)

            await ctx.send(embed=img_embed)

    @commands.command(name="schlechter_witz")
    async def _witz(self, ctx):
        joke = random.choice(self.jokes)

        await ctx.send(
            embed=discord.Embed(
                title="Schlechter Witz gefällig? Bitteschön.",
                description=joke,
                color=0x00fdfd
            )
        )
