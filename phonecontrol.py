import discord

from discord.ext import commands
from const import *

class PhoneControl(commands.Cog):
    def __init__(self, bot, multimer):
        self.bot = bot
        self.multimer = multimer
    
    @commands.command(aliases=['tog', 't'], brief='Toggle a flag. Aliases: tog/t')
    async def toggle(self, context, name):
        self.multimer.toggle(name)
        await self.send_status(context, name)

    @commands.command(aliases=['e'], brief='Enable a flag. Alias: e')
    async def enable(self, context, name):
        self.multimer.set_flag(name, True)
        await self.send_status(context, name)

    @commands.command(aliases=['d'], brief='Disable a flag. Alias: d')
    async def disable(self, context, name):
        self.multimer.set_flag(name, False)
        await self.send_status(context, name)
    
    async def send_status(self, context, name):
        status = 'enabled' if self.multimer.is_enabled(name) else 'disabled'
        await context.send(f'**{name}** {status}!')

    @commands.command(aliases=['f'], brief='See all flags. Alias: f')
    async def flags(self, context):
        embed = discord.Embed(color=discord.Color.blue())
        embed.set_author(name='Flags')
        lines = []
        for name, value in self.multimer.flags.items():
            value = 'on' if value else 'off'
            lines.append(f'**{name}**: {value}')
        embed.description = '\n'.join(lines)
        await context.send(embed=embed)

def add_to(bot, multimer):
    bot.add_cog(PhoneControl(bot, multimer))