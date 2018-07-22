import discord
from discord.ext import commands
import math
import random


class LevelSystemManager:

    def __init__(self, bot):
        self.bot = bot

    async def level_system_enable(self, ctx):
        select_query = 'SELECT * FROM guild_config WHERE "guild_id" = $1;'
        update_query = 'UPDATE guild_config SET "xp_enabled" = $1 WHERE "guild_id" = $2;'

        row = await self.bot.db.fetchrow(select_query, ctx.guild.id)

        try:
            if not row['xp_enabled']:
                con = await self.bot.db.acquire()
                async with con.transaction():
                    await self.bot.db.execute(update_query, True, ctx.guild.id)
                await self.bot.db.release(con)

                await ctx.send(
                    embed=discord.Embed(
                        title='XP-System -> Aktivieren',
                        description="Das XP-System wurde erfolgreich aktiviert!",
                        color=0x00fdfd
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title='XP-System -> Aktivieren',
                        description="Das XP-System ist bereits aktiviert!",
                        color=0x00fdfd
                    )
                )
        except Exception as error:
            await ctx.send(
                embed=discord.Embed(
                    title='XP-System -> Aktivieren',
                    description=f"Ein Fehler ist aufgetreten: {error}",
                    color=0x00fdfd
                )
            )

    async def level_system_disable(self, ctx):
        select_query = f'SELECT * FROM guild_config WHERE "guild_id" = $1;'
        update_query = 'UPDATE guild_config SET "xp_enabled" = $1 WHERE "guild_id" = $2;'

        row = await self.bot.db.fetchrow(select_query, ctx.guild.id)

        try:
            if row['xp_enabled']:
                con = await self.bot.db.acquire()
                async with con.transaction():
                    await self.bot.db.execute(update_query, False, ctx.guild.id)
                await self.bot.db.release(con)

                await ctx.send(
                    embed=discord.Embed(
                        title='XP-System -> Deaktivieren',
                        description="Das XP-System wurde erfolgreich deaktiviert!",
                        color=0x00fdfd
                    )
                )
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title='XP-System -> Deaktivieren',
                        description="Das XP-System ist bereits deaktiviert!",
                        color=0x00fdfd
                    )
                )
        except Exception as error:
            await ctx.send(
                embed=discord.Embed(
                    title='XP-System -> Deaktivieren',
                    description=f"Ein Fehler ist aufgetreten: {error}",
                    color=0x00fdfd
                )
            )

    @commands.command(name='server-xp')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _server_xp(self, ctx, *, keyword: str):
        if keyword == 'enable':
            await self.level_system_enable(ctx)
        elif keyword == 'disable':
            await self.level_system_disable(ctx)
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Nur `enable` oder `disable` sind als Argument für den Command zugelassen.",
                    color=0x00fdfd
                )
            )

    @_server_xp.error
    async def server_xp_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title="Fehlende Permissions",
                    description="Um diesen Command verwenden zu können, musst du die Permission `Manage Guild` haben.",
                    color=0x00fdfd
                )
            )
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nserver-xp <enable|disable>\n```",
                    color=0x00fdfd
                )
            )


class LevelSystem:

    def __init__(self, bot):
        self.bot = bot
        self.factor = (1 / 1.2)

    def get_user_level(self, xp_value: float):
        if xp_value > 0:
            return self.factor * math.log(xp_value + 1)
        else:
            return 0

    def xp_for_level(self, level: float):
        base = level / self.factor
        return math.pow(base, math.e)

    def xp_for_next_level(self, xp_value: float):
        current_level = self.get_user_level(xp_value)
        next_level = math.floor(current_level) + 1
        xp_for_next_level = self.xp_for_level(next_level)
        xp_for_current_level = self.xp_for_level(current_level)

        return xp_for_next_level - xp_for_current_level

    async def generate_xp(self, message: discord.Message):
        if message.author == self.bot.user:
            return False
        select_query = 'SELECT * FROM guild_config WHERE "guild_id" = $1;'
        row = await self.bot.db.fetchrow(select_query, message.guild.id)

        try:
            if row['xp_enabled']:
                if len(message.content) > 0:
                    user_xp = random.randint(1, math.floor(10 * math.log(len(message.content) + 1)))
                else:
                    user_xp = random.randint(1, 5)
            else:
                return False

            return user_xp

        except Exception as error:
            return await message.channel.send(
                embed=discord.Embed(
                    title='XP-System',
                    description=f"Ein Fehler ist aufgetreten: {error}",
                    color=0x00fdfd
                )
            )

    async def add_user_xp(self, message: discord.Message, xp: float):
        if message.author.id == self.bot.user.id:
            return

        try:
            # Erstmal Queries schreiben, und die bisherigen User-Daten aus der Datenbank holen
            select_xp_query = 'SELECT * FROM xp WHERE "user_id" = $1 AND "guild_id" = $2;'
            select_query = 'SELECT * FROM guild_config WHERE "guild_id" = $1;'
            update_xp_query = 'UPDATE xp SET "user_xp" = $1, "user_level" = $2 WHERE "user_id" = $3 AND "guild_id" = $4;'

            xp_row = await self.bot.db.fetchrow(select_xp_query, message.author.id, message.guild.id)
            config_row = await self.bot.db.fetchrow(select_query, message.guild.id)

            if config_row['xp_enabled']:
                new_xp = xp_row['user_xp'] + xp
                current_level = self.get_user_level(new_xp)

                # Aktualisiere Datenbank
                con = await self.bot.db.acquire()
                async with con.transaction():
                    await self.bot.db.execute(update_xp_query, new_xp, math.floor(current_level), message.author.id, message.guild.id)
                await self.bot.db.release(con)

                if xp_row['user_level'] < math.floor(current_level):
                    await message.channel.send(
                        embed=discord.Embed(
                            title="Levelup!",
                            description=f"{message.author.mention}, du bist nun Level {math.floor(current_level)}!",
                            color=0x00fdfd
                        )
                    )
            else:
                pass
        except Exception as error:
            await message.channel.send(
                embed=discord.Embed(
                    title='XP-System',
                    description=f"Ein Fehler ist aufgetreten: {error}",
                    color=0x00fdfd
                )
            )

    async def remove_user_xp(self, message: discord.Message, xp: float, grund: str):
        if message.author.id == self.bot.user.id:
            return

        try:
            select_xp_query = 'SELECT * FROM xp WHERE "user_id" = $1 AND "guild_id" = $2;'
            select_config_query = 'SELECT * FROM guild_config WHERE "guild_id" = $1;'
            update_query = 'UPDATE xp SET "user_xp" = $1 WHERE "user_id" = $2 AND "guild_id" = $3;'

            xp_row = await self.bot.db.fetchrow(select_xp_query, message.author.id, message.guild.id)
            config_row = await self.bot.db.fetchrow(select_config_query, message.guild.id)

            if config_row['xp_enabled']:
                new_xp = xp_row['user_xp'] - xp

                con = await self.bot.db.acquire()
                async with con.transaction():
                    await self.bot.db.execute(update_query, new_xp, message.author.id, message.guild.id)
                await self.bot.db.release(con)

                await message.author.send(
                    embed=discord.Embed(
                        title="Dir wurden XP abgezogen!",
                        description=f"Grund:\n```\n{grund}\n```",
                        color=0x00fdfd
                    )
                )
            else:
                pass
        except Exception as error:
            await message.channel.send(
                embed=discord.Embed(
                    title='XP-System',
                    description=f"Ein Fehler ist aufgetreten: {error}",
                    color=0x00fdfd
                )
            )

    async def get_user_xp(self, message: discord.Message):
        select_xp_query = 'SELECT * FROM xp WHERE "user_id" = $1 AND "guild_id" = $2;'
        try:
            xp_row = await self.bot.db.fetchrow(select_xp_query, message.author.id, message.guild.id)
            return xp_row['user_xp']
        except Exception as error:
            await message.channel.send(
                embed=discord.Embed(
                    title='XP-System',
                    description=f"Ein Fehler ist aufgetreten: {error}",
                    color=0x00fdfd
                )
            )

    @commands.command(name='xp')
    @commands.guild_only()
    async def _xp(self, ctx):
        async with ctx.typing():
            current_xp = await self.get_user_xp(ctx)

            await ctx.send(
                embed=discord.Embed(
                    description=f"Du hast momentan {math.floor(current_xp)} XP.",
                    color=0x00fdfd
                )
            )

    @commands.command(name='level')
    @commands.guild_only()
    async def _level(self, ctx):
        async with ctx.typing():
            current_xp = await self.get_user_xp(ctx.message)
            current_level = self.get_user_level(current_xp)
            needed_xp = self.xp_for_next_level(current_xp)

            await ctx.send(
                embed=discord.Embed(
                    description=f"Du bist momentan Level {math.floor(current_level)}. "
                                f"Du brauchst noch {math.floor(needed_xp)} XP für ein Level-Up.",
                    color=0x00fdfd
                )
            )

    @commands.command(name='leaderboard')
    @commands.guild_only()
    async def _leaderboard(self, ctx):
        async with ctx.typing():
            select_query = 'SELECT * FROM xp WHERE "guild_id" = $1 ORDER BY "user_xp" DESC LIMIT 10;'
            results = await self.bot.db.fetch(select_query, ctx.guild.id)

            lb_embed = discord.Embed(
                title="Leaderboard",
                description="━━━━━━━━━━━━━━━━━━━",
                color=0x00fdfd
            )

            count = 1
            for result in results:
                member = ctx.guild.get_member(result['user_id'])
                current_level = self.get_user_level(result['user_xp'])
                lb_embed.add_field(name=f"{count}. Platz:", value=f"{member.mention}: XP: {math.floor(result['user_xp'])}, "
                                                                  f"Level: {math.floor(current_level)}", inline=False)
                count += 1

            await ctx.send(embed=lb_embed)
