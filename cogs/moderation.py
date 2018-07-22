import discord
from discord.ext import commands

import asyncio
import datetime


class Moderation:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='kick')
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, member: discord.Member, *, reason: str):
        if member == ctx.author:
            return await ctx.send(
                embed=discord.Embed(
                    title='Moderation -> Kick',
                    description='Du kannst dich nicht selbst kicken.',
                    color=0x00fdfd
                )
            )
        elif member == self.bot.user:
            return await ctx.send(
                embed=discord.Embed(
                    title='Moderation -> Kick',
                    description='Ich kann mich nicht selbst kicken.',
                    color=0x00fdfd
                )
            )
        else:
            con = await self.bot.db.acquire()
            async with con.transaction():
                select_query = 'SELECT * FROM guild_config WHERE "guild_id" = $1;'

                row = await self.bot.db.fetchrow(select_query, ctx.guild.id)
                logchannel = ctx.guild.get_channel(row['log_channel_id']) if row['log_channel_id'] is not None else ctx
            await self.bot.db.release(con)

            ban_embed = discord.Embed(
                title='Ein User wurde gekickt!',
                description='',
                color=0x00fdfd
            )
            ban_embed.add_field(name="Dieser User wurde gekickt:", value=member.mention, inline=False)
            ban_embed.add_field(name="Grund:", value=f'```\n{reason}\n```', inline=False)
            ban_embed.add_field(name="Wurde gekickt von:", value=ctx.author.mention, inline=False)
            ban_embed.set_thumbnail(url=member.avatar_url)

            await member.kick(reason=reason)
            await logchannel.send(embed=ban_embed)

    @_kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nkick <User (Mention)> <Grund für den Kick>\n```",
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Mir fehlt die Permission `kick_members`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Dir fehlt die Permission `kick_members`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

    @commands.command(name='ban')
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx, member: discord.Member, *, reason: str):
        if member == ctx.author:
            return await ctx.send(
                embed=discord.Embed(
                    title='Moderation -> Ban',
                    description='Du kannst dich nicht selber bannen.',
                    color=0x00fdfd
                )
            )
        elif member == self.bot.user:
            return await ctx.send(
                embed=discord.Embed(
                    title='Moderation -> Ban',
                    description='Ich kann mich nicht selber bannen.',
                    color=0x00fdfd
                )
            )
        else:
            con = await self.bot.db.acquire()
            async with con.transaction():
                select_query = 'SELECT * FROM guild_config WHERE "guild_id" = $1;'

                row = await self.bot.db.fetchrow(select_query, ctx.guild.id)
                logchannel = ctx.guild.get_channel(row['log_channel_id']) if row['log_channel_id'] is not None else ctx
            await self.bot.db.release(con)

            ban_embed = discord.Embed(
                title='Ein User wurde gebannt!',
                description='',
                color=0x00fdfd
            )
            ban_embed.add_field(name="Dieser User wurde gebannt:", value=member.mention, inline=False)
            ban_embed.add_field(name="Grund:", value=f'```\n{reason}\n```', inline=False)
            ban_embed.add_field(name="Wurde gebannt von:", value=ctx.author.mention, inline=False)
            ban_embed.set_thumbnail(url=member.avatar_url)

            await member.ban(delete_message_days=5, reason=reason)
            await logchannel.send(embed=ban_embed)

            # Log-Zeug einfügen

    @_ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nban <User (Mention)> <Grund für den Bann>\n```",
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Mir fehlt die Permission `ban_members`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Dir fehlt die Permission `ban_members`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

    @commands.command(name='set_logchannel')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _set_log_channel(self, ctx, *, log_channel: discord.TextChannel):
        con = await self.bot.db.acquire()
        async with con.transaction():
            update_query = 'UPDATE guild_config SET "log_channel_id" = $1 WHERE "guild_id" = $2;'

            await self.bot.db.execute(update_query, log_channel.id, ctx.guild.id)
        await self.bot.db.release(con)

        await ctx.send(
            embed=discord.Embed(
                title="Logchannel",
                description=f"Der Logchannel wurde erfolgreich auf {log_channel.mention} geupdatet!",
                color=0x00fdfd
            )
        )

    @_set_log_channel.error
    async def _set_log_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Dir fehlt die Permission `manage_guild`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nset_logchannel <TextChannel (Mention)>\n```",
                    color=0x00fdfd
                )
            )

    @commands.command(name='current_logchannel')
    @commands.guild_only()
    async def _current_log_channel(self, ctx):
        con = await self.bot.db.acquire()
        async with con.transaction():
            select_query = 'SELECT "log_channel_id" FROM guild_config WHERE "guild_id" = $1;'

            log_channel = await self.bot.db.fetch(select_query, ctx.guild.id)
        await self.bot.db.release(con)

        if log_channel[0]['log_channel_id'] is not None:
            await ctx.send(
                embed=discord.Embed(
                    title="Logchannel",
                    description=f"Der aktuelle Logchannel auf dem Server ist <#{log_channel[0]['log_channel_id']}>.",
                    color=0x00fdfd
                )
            )
        else:
            await ctx.send(
                embed=discord.Embed(
                    title="Logchannel",
                    description="Auf dem Server ist momentan kein Logchannel gesetzt. Benutze "
                                "`set_logchannel <TextChannel (Mention)>`, um einen Channel einzurichten.",
                    color=0x00fdfd
                )
            )

    @commands.command(name='report')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _report(self, ctx, member: discord.Member, *, reason: str):
        if member == ctx.author:
            return await ctx.send(
                embed=discord.Embed(
                    title='Moderation -> Warn',
                    description='Du kannst dich nicht selbst reporten.',
                    color=0x00fdfd
                )
            )
        elif member == self.bot.user:
            return await ctx.send(
                embed=discord.Embed(
                    title='Moderation -> Warn',
                    description='Ich kann mich nicht selbst reporten.',
                    color=0x00fdfd
                )
            )
        else:
            con = await self.bot.db.acquire()
            async with con.transaction():
                select_query = 'SELECT * FROM guild_config WHERE "guild_id" = $1;'
                insert_query = 'INSERT INTO reports("guild_id", "user_id", "report_reason", "report_time") VALUES($1, $2, $3, $4);'

                row = await self.bot.db.fetchrow(select_query, ctx.guild.id)
                await self.bot.db.execute(insert_query, ctx.guild.id, member.id, reason, datetime.datetime.now())

                logchannel = ctx.guild.get_channel(row['log_channel_id']) if row['log_channel_id'] is not None else ctx
            await self.bot.db.release(con)

            report_embed = discord.Embed(
                title='Ein User wurde reportet!',
                description='━━━━━━━━━━━━━━━━━━━',
                color=0x00fdfd
            )
            report_embed.add_field(
                name='Dieser User wurde reportet:',
                value=member.mention,
                inline=False
            )
            report_embed.add_field(
                name='Grund:',
                value=f'```\n{reason}\n```',
                inline=False
            )
            report_embed.add_field(
                name='Reportet von:',
                value=ctx.author.mention,
                inline=False
            )
            report_embed.set_thumbnail(
                url=member.avatar_url
            )

            await member.send(embed=report_embed)
            await logchannel.send(embed=report_embed)

    @_report.error
    async def _report_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Dir fehlt die Permission `manage_guild`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Mir fehlt die Permission `manage_guild`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nreport <User (Mention)> <Grund>\n```",
                    color=0x00fdfd
                )
            )

    @commands.command(name='reports')
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def _reports(self, ctx, *, member: discord.Member):
        report_embed = discord.Embed(
            title=f'Reports',
            description='━━━━━━━━━━━━━━━━━━━',
            color=0x00fdfd
        )
        report_embed.set_author(
            name=str(member.name),
            icon_url=str(member.avatar_url)
        )

        con = await self.bot.db.acquire()
        async with con.transaction():
            select_query = 'SELECT * FROM reports WHERE "user_id" = $1 AND "guild_id" = $2;'

            reports = await self.bot.db.fetch(select_query, member.id, ctx.guild.id)
        await self.bot.db.release(con)

        for report in reports:
            report_id = report['report_id']
            reason = report['report_reason']
            report_time = str(report['report_time']).split('.')[0]
            report_embed.add_field(
                name=f'Report Nr. {report_id} vom {report_time}:',
                value=f'```\n{reason}\n```',
                inline=False
            )

        await ctx.send(embed=report_embed)

    @_reports.error
    async def _reports_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nreports <User (Mention)>\n```",
                    color=0x00fdfd
                )
            )

    @commands.command(name='clear')
    @commands.guild_only()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.guild)
    @commands.has_permissions(manage_messages=True)
    async def _clear(self, ctx, *, amount: str):
        clear_embed = discord.Embed(
                        title='Moderation -> Clear',
                        description='━━━━━━━━━━━━━━━━━━━',
                        color=0x00fdfd
                    )

        try:
            amount = int(amount) + 1 if len(amount) > 0 else 2
            if amount >= 100:
                clear_embed.add_field(name='Problem:',
                                      value='Das Limit der Nachrichten, die zur selben Zeit gelöscht werden können, '
                                            'liegt bei 100.')
                return await ctx.send(embed=clear_embed)

            await ctx.channel.purge(limit=amount)

            clear_embed.add_field(
                name='Nachrichten gelöscht!',
                value=f'Es wurden erfolgreich {amount} Nachrichten aus {ctx.channel.mention} gelöscht!'
            )

            del_message = await ctx.send(
                embed=clear_embed
            )
            await asyncio.sleep(5)
            await del_message.delete()
        except ValueError:
            clear_embed.add_field(
                name='Problem:',
                value='Gib bitte eine gültige Menge an Nachrichten an, die gelöscht werden soll.'
            )
            return await ctx.send(
                embed=clear_embed
            )
        except discord.HTTPException:
            clear_embed.add_field(
                name='Problem:',
                value='Nachrichten, älter als 2 Wochen, kann man nicht löschen.'
            )
            return await ctx.send(
                embed=clear_embed
            )

    @_clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Dir fehlt die Permission `manage_messages`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=discord.Embed(
                    title='Fehlende Permissions',
                    description='Mir fehlt die Permission `manage_messages`, um diesen Command ausführen zu können.',
                    color=0x00fdfd
                )
            )

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nclear <Menge an Nachrichten>\n```",
                    color=0x00fdfd
                )
            )
