import discord
from discord.ext import commands

import time


class BotSettings:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="status")
    async def _status(self, ctx):
        time1 = time.perf_counter()
        first_status_embed = discord.Embed(
            title="Lebe ich noch?",
            description="━━━━━━━━━━━━━━━━━━━\n"
                        f"\n❤ **Heartbeat:** {round(self.bot.latency, 1)}\n"
                        f"<:discord:466619235733340170> **Gilden:** {len(self.bot.guilds)}\n"
                        f"👪 **Members insgesamt:** {len(self.bot.users)}\n"
                        f"🏓 **Ping:** *Wird berechnet..*",
            color=0x00fdfd
        )
        status_msg = await ctx.send(embed=first_status_embed)
        time2 = time.perf_counter()
        speed = time2 - time1
        second_status_embed = discord.Embed(
            title="Lebe ich noch?",
            description="━━━━━━━━━━━━━━━━━━━\n"
                        f"\n❤ **Heartbeat:** {round(self.bot.latency, 1)}\n"
                        f"<:discord:466619235733340170> **Gilden:** {len(self.bot.guilds)}\n"
                        f"👪 **Members insgesamt:** {len(self.bot.users)}\n"
                        f"🏓 **Ping:** {round(speed * 1000)}ms",
            color=0x00fdfd
        )
        await status_msg.edit(new_content=None, embed=second_status_embed)


class VoteParser(commands.clean_content):

    async def convert(self, ctx, argument):
        result = await super().convert(ctx, argument)

        if not result:
            return await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands!",
                    description=f"Verwendung:\n```\nvote start question|option1|option2...|option9\n```",
                    color=0x00fdfd
                )
            )

        if '|' in result:
            result = result.split("|")
        else:
            return await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Verwendung:\n```\nvote start <Thema|Option1|Option2|Option3|...|Option9>\n```",
                    color=0x00fdfd
                )
            )

        if len(result) >= 10 or len(result) <= 2:
            return await ctx.send(
                embed=discord.Embed(
                    title="Falsche Nutzung des Commands",
                    description="Es können nur maximal **neun** Optionen zum Abstimmen angegeben werden! **Zwei** "
                                "müssen neben der Frage immer gegeben sein.",
                    color=0x00fdfd
                )
            )
        else:
            return result


class Voting:
    def __init__(self, bot):
        self.bot = bot
        self.nums = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

    @commands.group(name='vote')
    @commands.guild_only()
    async def _vote(self, ctx):
        if ctx.invoked_subcommand is None:
            con = await self.bot.db.acquire()
            async with con.transaction():
                select_query = 'SELECT "vote_id", "vote_question", "user_id" FROM voting WHERE "guild_id" = $1;'

                results = await self.bot.db.fetch(select_query, ctx.guild.id)
            await self.bot.db.release(con)

            vote_embed = discord.Embed(
                title="Aktive Abstimmungen auf diesem Server:",
                description="━━━━━━━━━━━━━━━━━━━",
                color=0x00fdfd
            )

            for result in results:
                creator = ctx.guild.get_member(result['user_id'])
                vote_embed.add_field(
                    name=f"Abstimmung Nr.{result['vote_id']} von {creator}",
                    value=f"```\nThema: {result['vote_question']}\n```",
                    inline=False
                )

            await ctx.send(embed=vote_embed)

    @_vote.command(name="start")
    async def _start(self, ctx, *, args: VoteParser):
        subject = args.pop(0)

        vote_embed = discord.Embed(
            title="Eine neue Abstimmung wurde gestartet!",
            description="━━━━━━━━━━━━━━━━━━━",
            color=0x00fdfd
        )
        vote_embed.add_field(
            name=f"__**{subject}**__",
            value="Bitte reacte mit den unten angefügten Emotes!",
            inline=False
        )

        vote_message = await ctx.send(embed=vote_embed)

        query_part = ', '.join("'{}'::bigint[]" for i in args)

        count = 0
        for arg in args:
            vote_embed.add_field(
                name=f"{arg}",
                value="```\n0\n```",
                inline=True
            )
            await vote_message.add_reaction(self.nums[count])

            count += 1

        await vote_message.edit(new_content=None, embed=vote_embed)

        con = await self.bot.db.acquire()
        async with con.transaction():
            insert_query = f'INSERT INTO voting VALUES(DEFAULT, $1, $2, $3, $4, {query_part});'

            await self.bot.db.execute(insert_query, ctx.guild.id, ctx.author.id, subject, vote_message.id)
        await self.bot.db.release(con)

    @_vote.command(name='end')
    async def _end(self, ctx, *, vote_id: str):
        try:
            vote_id = int(vote_id)
        except:
            return

        con = await self.bot.db.acquire()
        async with con.transaction():
            select_query = 'SELECT * FROM voting WHERE "guild_id" = $1 AND "user_id" = $2 AND "vote_id" = $3;'

            try:
                result = await self.bot.db.fetchrow(select_query, ctx.guild.id, ctx.author.id, vote_id)

                if result is None:
                    await self.bot.db.release(con)
                    return await ctx.send(
                        embed=discord.Embed(
                            title="Utility -> Voting",
                            description="Du hast nicht die Berechtigungen, diese Abstimmung zu beenden.",
                            color=0x00fdfd
                        )
                    )
            except:
                await self.bot.db.release(con)
                return await ctx.send(
                    embed=discord.Embed(
                        title="Utility -> Voting",
                        description="Es wurde keine Abstimmung mit dieser Nummer gefunden.",
                        color=0x00fdfd
                    )
                )
        await self.bot.db.release(con)

        vote_msg = None
        for channel in ctx.guild.text_channels:
            try:
                vote_msg = await channel.get_message(result['vote_msg_id'])
            except:
                pass

            if vote_msg is not None:
                try:
                    await vote_msg.clear_reactions()

                    con = self.bot.db.acquire()
                    async with con.transaction():
                        del_vote = 'DELETE FROM voting WHERE "vote_id" = $1;'
                        await self.bot.db.execute(del_vote, result['vote_id'])
                    await self.bot.db.release(con)

                    await ctx.send(
                        embed=discord.Embed(
                            title="Utility -> Voting",
                            description=f"Die Abstimmung Nr. {result['vote_id']} wurde erfolgreich beendet.",
                            color=0x00fdfd
                        )
                    )
                except:
                    pass

    @_end.error
    async def _end_error(self, ctx, error):
        def check(m):
            return len(m.content) > 0 and m.author == ctx.author and m.channel == ctx.message.channel

        if isinstance(error, commands.MissingRequiredArgument):
            con = await self.bot.db.acquire()
            async with con.transaction():
                select_query = 'SELECT "vote_id", "vote_question", "vote_msg_id", "user_id" FROM voting WHERE "guild_id" = $1 AND "user_id" = $2;'

                results = await self.bot.db.fetch(select_query, ctx.guild.id, ctx.author.id)
            await self.bot.db.release(con)

            vote_embed = discord.Embed(
                title="Deine aktiven Abstimmungen auf diesem Server:",
                description="━━━━━━━━━━━━━━━━━━━",
                color=0x00fdfd
            )

            result_ids = []
            for result in results:
                vote_embed.add_field(
                    name=f"Abstimmung Nr.{result['vote_id']}",
                    value=f"```\nThema: {result['vote_question']}\n```",
                    inline=False
                )
                result_ids.append(result['vote_id'])
            vote_embed.add_field(name="Bitte tippe eine gültige Vote-ID in den Chat",
                                 value="Diese wird dir oberhalb als Nr. der Abstimmung angezeigt.")

            await ctx.send(embed=vote_embed)

            msg = await self.bot.wait_for('message', check=check)
            try:
                int(msg.content)
            except:
                return

            if int(msg.content) not in result_ids:
                await ctx.send(
                    embed=discord.Embed(
                        title="Utility -> Voting",
                        description="Es wurde keine Abstimmung mit dieser Nummer gefunden.",
                        color=0x00fdfd
                    )
                )
            else:
                con = await self.bot.db.acquire()
                async with con.transaction():
                    select_vote = 'SELECT * FROM voting WHERE "vote_id" = $1;'
                    try:
                        result = await self.bot.db.fetchrow(select_vote, int(msg.content))

                        if result is None:
                            await self.bot.db.release(con)
                            return await ctx.send(
                                embed=discord.Embed(
                                    title="Utility -> Voting",
                                    description="Du hast nicht die Berechtigungen, diese Abstimmung zu beenden.",
                                    color=0x00fdfd
                                )
                            )
                    except:
                        await self.bot.db.release(con)
                        return await ctx.send(
                            embed=discord.Embed(
                                title="Utility -> Voting",
                                description="Es wurde keine Abstimmung mit dieser Nummer gefunden.",
                                color=0x00fdfd
                            )
                        )
                await self.bot.db.release(con)

                vote_msg = None
                for channel in ctx.guild.text_channels:
                    try:
                        vote_msg = await channel.get_message(result['vote_msg_id'])
                    except:
                        pass

                    if vote_msg is not None:
                        try:
                            await vote_msg.clear_reactions()

                            con = await self.bot.db.acquire()
                            async with con.transaction():
                                del_vote = 'DELETE FROM voting WHERE "vote_id" = $1;'
                                await self.bot.db.execute(del_vote, result['vote_id'])
                            await self.bot.db.release(con)

                            await ctx.send(
                                embed=discord.Embed(
                                    title="Utility -> Voting",
                                    description=f"Die Abstimmung Nr. {result['vote_id']} wurde erfolgreich beendet.",
                                    color=0x00fdfd
                                )
                            )
                        except:
                            pass

    async def on_raw_reaction_add(self, payload):
        try:
            guild = self.bot.get_guild(payload.guild_id)
        except AttributeError:
            return
        channel = guild.get_channel(payload.channel_id)
        user = guild.get_member(payload.user_id)
        if user == self.bot.user:
            return
        message = await channel.get_message(payload.message_id)
        partial_emoji = payload.emoji
        emoji = str(payload.emoji)

        con = await self.bot.db.acquire()
        async with con.transaction():
            vote_query = 'SELECT * FROM voting WHERE "vote_msg_id" = $1;'
            try:
                row = await self.bot.db.fetchrow(vote_query, message.id)

                if row is None:
                    return
            except:
                return
        await self.bot.db.release(con)

        try:
            choice_index = str(self.nums.index(emoji))
        except ValueError:
            return

        await message.remove_reaction(partial_emoji, user)

        if row[f'vote_option{int(choice_index) + 1}'] is None:
            vote_users = []
        else:
            vote_users = row[f'vote_option{int(choice_index) + 1}']

        if user.id in vote_users:
            return
        else:
            new_embed = None
            for key, value in row.items():
                try:
                    if user.id in value:

                        already_voted_index = int(key.strip('vote_option'))
                        value.remove(user.id)

                        con = await self.bot.db.acquire()
                        async with con.transaction():
                            remove_user_query = f'UPDATE voting SET "vote_option{already_voted_index}" = $1 WHERE "vote_msg_id" = $2;'
                            await self.bot.db.execute(remove_user_query, value, message.id)
                        await self.bot.db.release(con)

                        embed_name = message.embeds[0].fields[already_voted_index].name
                        embed_value = message.embeds[0].fields[already_voted_index].value

                        vote_count = int('\n'.join(embed_value.split('\n')[1:-1])) - 1
                        embed_value = f'```\n{vote_count}\n```'

                        new_embed = message.embeds[0].set_field_at(index=already_voted_index, name=embed_name, value=embed_value)
                    else:
                        pass
                except TypeError:
                    pass

            vote_users.append(user.id)

            embed_name = message.embeds[0].fields[int(choice_index) + 1].name
            embed_value = message.embeds[0].fields[int(choice_index) + 1].value

            field_index = int(choice_index) + 1
            vote_count = int('\n'.join(embed_value.split('\n')[1:-1])) + 1
            embed_value = f'```\n{vote_count}\n```'

            embed_name = message.embeds[0].fields[int(choice_index) + 1].name
            embed_value = message.embeds[0].fields[int(choice_index) + 1].value

            field_index = int(choice_index) + 1
            vote_count = int('\n'.join(embed_value.split('\n')[1:-1])) + 1
            embed_value = f'```\n{vote_count}\n```'

            if new_embed is None:
                new_embed = message.embeds[0].set_field_at(index=field_index, name=embed_name, value=embed_value)
            else:
                new_embed = new_embed.set_field_at(index=field_index, name=embed_name, value=embed_value)

            await message.edit(new_content=None, embed=new_embed)

            con = await self.bot.db.acquire()
            async with con.transaction():
                update_query = f'UPDATE voting SET "vote_option{int(choice_index) + 1}" = $1::bigint[] WHERE "vote_msg_id" = $2;'
                await self.bot.db.execute(update_query, vote_users, message.id)
            await self.bot.db.release(con)

    async def on_message_delete(self, message):
        pass
