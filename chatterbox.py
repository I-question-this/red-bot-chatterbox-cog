import discord
import logging
import os
import random
import re

from redbot.core import checks, commands, Config
from redbot.core.data_manager import cog_data_path
from redbot.core.bot import Red

from .eliza.eliza import eliza as Eliza

log = logging.getLogger("red.chatterbox")

class ChatterBox(commands.Cog):
    """ChatterBox cog"""

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self._conf = Config.get_conf(None, 191919191, cog_name=f"{self.__class__.__name__}", force_registration=True)
        self.eliza = Eliza()


    
    @commands.group()
    async def eliza(self, ctx: commands.Context) -> None:
        """Eliza commands"""


    @eliza.command(name="speak")
    async def speak_to_eliza(self, ctx: commands.Context, text:str) -> None:
        # Build response/talk to Eliza
        response = {}
        response['title'] = f"Dear {ctx.author.display_name},"
        response['description'] = f"{self.eliza.respond(text)}\n*--Eliza*"
        # Build embed
        embed = discord.Embed.from_dict(response)
        # Send embed
        return await ctx.send(embed=embed)

    @eliza.command(name="description")
    async def describe_eliza(self, ctx: commands.Context) -> None:
        # Build response
        response = {}
        response['title'] = "What is ELIZA?"
        response['description'] =\
            """
                **ELIZA** is an early natural language processing computer program.
                It attempts to play the role of a therapist by reflecting user's 
                statements back at them.
                More at the Wikipedia article:
                https://en.wikipedia.org/wiki/ELIZA
                The implementation of **ELIZA** in python3 can be found at this
                git repository:
                https://github.com/jezhiggins/eliza.py
            """
        # Build embed
        embed = discord.Embed.from_dict(response)
        # Send embed
        return await ctx.send(embed=embed)

