import discord
from discord.ext import commands

import asyncio
import aiohttp
import asyncpg
import os
import json
import traceback

from cogs import eval, fun, help, moderation, utility, voice, xp_system, battleships
from cogs.utils import config, errors

initial_queries = [
    'CREATE TABLE IF NOT EXISTS guild_config (guild_id BIGINT PRIMARY KEY NOT NULL, xp_enabled BOOLEAN NOT NULL, log_channel_id BIGINT);',

    'CREATE TABLE IF NOT EXISTS xp (guild_id BIGINT NOT NULL, user_id BIGINT NOT NULL, user_xp FLOAT, '
    'user_level INTEGER, PRIMARY KEY ("guild_id", "user_id"));',

    'CREATE TABLE IF NOT EXISTS reports (report_id SERIAL, guild_id BIGINT NOT NULL, user_id BIGINT NOT NULL, '
    'report_reason TEXT NOT NULL, report_time TIMESTAMP NOT NULL, PRIMARY KEY (guild_id, user_id));',

    'CREATE TABLE IF NOT EXISTS voting (vote_id SERIAL, guild_id BIGINT NOT NULL, user_id BIGINT NOT NULL, '
    'vote_question TEXT NOT NULL, vote_msg_id BIGINT NOT NULL, vote_option1 BIGINT[], vote_option2 BIGINT[], '
    'vote_option3 BIGINT[], vote_option4 BIGINT[], vote_option5 BIGINT[], vote_option6 BIGINT[], '
    'vote_option7 BIGINT[], vote_option8 BIGINT[], vote_option9 BIGINT[], PRIMARY KEY (vote_id));'
]
_cogs = [
    eval.Eval,
    fun.FunCommands,
    help.HelpCommand,
    moderation.Moderation,
    utility.BotSettings,
    utility.Voting,
    voice.Voice,
    xp_system.LevelSystem,
    xp_system.LevelSystemManager,
    battleships.SchiffeVersenken
]


async def create_tables(bot):
    for query in initial_queries:
        await bot.db.execute(query)

    con = await bot.db.acquire()
    for guild in bot.guilds:
        try:
            config_query = 'INSERT INTO guild_config("guild_id", "xp_enabled") VALUES ($1, $2);'

            async with con.transaction():
                await bot.db.execute(config_query, guild.id, False)
        except:
            pass

        for member in guild.members:
            xp_query = 'INSERT INTO xp VALUES ($1, $2, $3, $4);'

            async with con.transaction():
                try:
                    await bot.db.execute(xp_query, guild.id, member.id, 0, 0)
                except:
                    pass

    await bot.db.release(con)


async def run():
    # Erstmal das Config-File erstellen/checken
    if not os.path.isfile('config.json'):
        with open('config.json', 'w+') as f:
            # Allgemeine Konfiguration für den Bot erstellen
            settings = {'token': input("Was ist dein Bot-Token? "),
                        'prefix': input("Was soll der Präfix sein? "),
                        'owner_id': input("Wir brauchen einen Owner. Gib bitte seine ID an: "),
                        'bs_guild_id': input("Gib die ID der Gilde an, die für Schiffe Versenken verwendet werden soll (siehe vorher Docs): "),
                        'pg_user': input("Was ist dein PostgreSQL-Benutzername? "),
                        'pg_pass': input("Was ist dein PostgreSQL-Passwort? "),
                        'pg_db': input("Wie heißt die Datenbank zum Verbinden? "),
                        'pg_host': input("Was ist die IP des Hosts der Datenbank? "
                                         "(Falls der lokale Rechner, tippe bitte 127.0.0.1 ein) "),
                        'pg_port': input("Wie lautet der Connection-Port für PostgreSQL? (Standardport ist 5432) ")
                        }
            json.dump(settings, f, sort_keys=True, indent=4)
    else:
        config.check_config()

    with open('config.json', 'r') as f:
        settings = json.load(f)

        login_data = {"user": settings['pg_user'], "password": settings['pg_pass'],
                      "database": settings['pg_db'], "host": settings['pg_host'], "port": settings['pg_port']}
        db = await asyncpg.create_pool(**login_data)

        description = "Discord-Bot für den CodersClash-Wettbewerb"

        bot = Bot(prefix=settings['prefix'], description=description, db=db, owner_id=settings['owner_id'])

        try:
            await bot.start(settings['token'])
        except KeyboardInterrupt:
            await db.close()
            await bot.logout()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or(kwargs['prefix']),
            description=kwargs.pop('description'),
            case_insensitive=True
        )

        self.prefix = kwargs.pop('prefix')
        self.db = kwargs.pop('db')
        self.owner_id = int(kwargs.pop('owner_id'))
        self.client_session = aiohttp.ClientSession(loop=self.loop)
        self.event_loop = asyncio.get_event_loop()

        self.remove_command("help")
        for cog in _cogs:
            try:
                self.add_cog(cog(self))
            except Exception as error:
                raise errors.CogError

    async def on_ready(self):
        """
        Der Bot hat sich erfolgreich connectet. Etwas in die Konsole printen, und Cogs hinzufügen.
        """

        await create_tables(self)

        print(f"===============\nEingeloggt als:\n{self.user.name}\n{self.user.id}\n===============")
        await self.change_presence(
            activity=discord.Activity(name=f"deine Commands. | {self.prefix}help",
                                      type=discord.ActivityType.listening), status=discord.Status.dnd)

    async def on_guild_join(self, guild):

        con = await self.db.acquire()
        async with con.transaction():
            config_query = 'INSERT INTO guild_config("guild_id", "xp_enabled") VALUES ($1, $2);'
            xp_query = 'INSERT INTO xp VALUES ($1, $2, $3, $4);'

            await self.db.execute(config_query, guild.id, False)
            for member in guild.members:
                await self.db.execute(xp_query, guild.id, member.id, 0, 0)

        await self.db.release(con)

    async def on_guild_remove(self, guild):
        con = await self.db.acquire()
        async with con.transaction():
            _queries = [
                'DELETE FROM xp WHERE "guild_id" = $1;',
                'DELETE FROM guild_config WHERE "guild_id" = $1;',
                'DELETE FROM reports WHERE "guild_id" = $1;',
                'DELETE FROM voting WHERE "guild_id" = $1;'
            ]

            for query in _queries:
                await self.db.execute(query, guild.id)
        await self.db.release(con)

    async def on_member_join(self, member):
        con = await self.db.acquire()
        async with con.transaction():
            xp_query = f'INSERT INTO xp VALUES($1, $2, $3, $4);'

            await self.db.execute(xp_query, member.guild.id, member.id, 0, 0)
        await self.db.release(con)

    async def on_member_remove(self, member):
        if not member.id == self.user.id:
            con = await self.db.acquire()
            async with con.transaction():
                delete_member_query = 'DELETE FROM xp WHERE "guild_id" = $1 AND "user_id" = $2;'
                delete_vote_query = 'DELETE FROM voting WHERE "user_id" = $1 AND "guild_id" = $2;'
                delete_report_query = 'DELETE FROM reports WHERE "user_id" = $1 AND "guild_id" = $2;'

                await self.db.execute(delete_member_query, member.guild.id, member.id)
                await self.db.execute(delete_vote_query, member.id, member.guild.id)
                await self.db.execute(delete_report_query, member.id, member.guild.id)
            await self.db.release(con)

    async def on_message(self, message):

        if message.guild is not None:
            user_xp = await self.get_cog("LevelSystem").generate_xp(message=message)

            if user_xp is not False:
                await self.get_cog("LevelSystem").add_user_xp(message=message, xp=user_xp)

        await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass


asyncio.get_event_loop().run_until_complete(run())
