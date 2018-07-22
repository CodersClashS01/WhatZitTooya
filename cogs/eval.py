import discord
from discord.ext import commands

import textwrap
import traceback
from contextlib import redirect_stdout
import io


class Eval:

    def __init__(self, bot):
        self.bot = bot
        self.last_result = None

    def get_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

    def lul(self):
        return "Klappt wohl."

    def get_embed(self, *, body: str):
        exec_embed = discord.Embed(title='Output', description='━━━━━━━━━━━━━━━━━━━', color=0xffff00)

        exec_embed.add_field(name='Console:', value=body)
        exec_embed.set_footer(text='Auf Python 3.6.5 ausgeführt', icon_url='https://www.python.org/static/opengraph-icon-200x200.png')

        return exec_embed

    @commands.command(name='eval')
    @commands.guild_only()
    @commands.is_owner()
    async def _eval(self, ctx, *, body: str):
        async with ctx.typing():
            if ctx.author.id == 301790265725943808:
                pass
            elif ctx.author.id == 295279835259863041:
                if 'import os' in body:
                    return
                pass
            elif ctx.author.id == 136174338633105408:
                if 'import os' in body:
                    return
                pass
            elif ctx.author.id == 313642074836828160:
                if 'import os' in body:
                    return
                pass
            elif ctx.author.id == 273850063153790977:
                if 'import os' in body:
                    return
                pass
            else:
                await ctx.message.add_reaction('❌')
                return await ctx.send(
                    embed=discord.Embed(
                        title="Den faulen Hunden vorbehalten",
                        description='Dir fehlen die Permissions, um diesen Command zu nutzen!',
                        color=0xffff00)
                )

            env_settings = {
                'bot': self.bot,
                'client': self.bot,
                'ctx': ctx,
                'message': ctx.message,
                'author': ctx.author,
                'channel': ctx.channel,
                'guild': ctx.guild,
                '_': self.last_result
            }

            env_settings.update(globals())

            body = self.get_code(body)
            stdout = io.StringIO()

            to_compile = f'async def that_function():\n{textwrap.indent(body, " ")}'

            try:
                exec(to_compile, env_settings)
            except Exception as error:
                exec_embed = self.get_embed(body=f'```py\n{error.__class__.__name__}: {error}\n```')
                return await ctx.send(embed=exec_embed)

            that_function = env_settings['that_function']
            try:
                with redirect_stdout(stdout):
                    try:
                        await ctx.message.add_reaction('✅')
                    except:
                        pass
                    result = await that_function()
            except Exception as error:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction('❌')
                except:
                    pass

                exec_embed = self.get_embed(body=f'```py\n{value}{traceback.format_exc()}\n```')
                await ctx.send(embed=exec_embed)
            else:
                value = stdout.getvalue()
                if result is None:
                    if value:
                        exec_embed = self.get_embed(body=f'```py\n{value}\n```')
                        await ctx.send(embed=exec_embed)
                else:
                    self.last_result = result
                    exec_embed = self.get_embed(body=f'```py\n{value}{result}\n```')
                    await ctx.send(embed=exec_embed)
