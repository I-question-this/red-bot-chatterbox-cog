import asyncio
import discord
import logging
import os
import random
import re

from redbot.core import checks, commands, Config
from redbot.core.data_manager import cog_data_path
from redbot.core.bot import Red

import aiml
from .eliza.eliza import eliza as Eliza

log = logging.getLogger("red.chatterbox")

class ChatterBox(commands.Cog):
    """ChatterBox cog"""

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self._conf = Config.get_conf(None, 191919191, cog_name=f"{self.__class__.__name__}", force_registration=True)
        self.setup_alice()
        self.eliza = Eliza()


    @commands.Cog.listener()
    async def on_message(self, message: discord.message) -> None:
        """Listen to every message ever.
        This is how the bot will respond to button pushes.
        It will only respond if the message is sent within a registered channel though.
        """
        if isinstance(message.channel, discord.abc.PrivateChannel):
            return
        author = message.author
        valid_user = isinstance(author, discord.Member) and not author.bot
        if not valid_user:
            return
        if await self.bot.is_automod_immune(message):
            return

        if self.bot.user.mentioned_in(message):
            response = self.response_from_eliza(message.content)
            async with message.channel.typing():
                await asyncio.sleep(random.randint(1, 3))
                await message.channel.send(f"{author.mention} {response}")
   

    @commands.group()
    async def eliza(self, ctx: commands.Context) -> None:
        """Eliza commands"""


    def response_from_eliza(self, text:str) -> str:
        return self.eliza.respond(text)


    @eliza.command(name="speak")
    async def speak_to_eliza(self, ctx: commands.Context, text:str) -> None:
        # Build response/talk to Eliza
        response = {}
        response['title'] = f"Dear {ctx.author.display_name},"
        response['description'] = f"{self.response_from_eliza(test)}\n*--Eliza*"
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


    @commands.group()
    async def alice(self, ctx: commands.Context) -> None:
        """Alice commands"""


    def response_from_alice(self, text:str) -> str:
        # Clean out the message
        for ch in  ['/', "'", ".", "\\", "(", ")", '"', '\n']:
            text = text.replace(ch, '')
        response = self.alice.respond(text)
        self.alice.saveBrain(self.alice_brain)
        return response


    def setup_alice(self):
        # Load up default ALICE
        self.alice = aiml.Kernel()
        self.alice.setTextEncoding(None)
        chdir = os.path.join( aiml.__path__[0],'botdata','standard' )
        self.alice.bootstrap(learnFiles="startup.xml", commands="load alice", chdir=chdir)
        # Setup/load brain file
        self.alice_brain = os.path.join(cog_data_path(), "ChatterBox/alice.brain")
        if os.path.isfile(self.alice_brain):
            # Load the existing brain file
            self.alice.bootstrap(brainFile=self.alice_brain)
        else:
            # Create a new brain file
            self.alice.saveBrain(self.alice_brain)


    @alice.command(name="speak")
    async def speak_to_alice(self, ctx: commands.Context, text:str) -> None:
        # Build response/talk to Eliza
        response = {}
        response['title'] = f"Dear {ctx.author.display_name},"
        response['description'] = f"{self.response_from_alice(text)}\n*--ALICE*"
        # Build embed
        embed = discord.Embed.from_dict(response)
        # Send embed
        return await ctx.send(embed=embed)


    @alice.command(name="description")
    async def describe_alice(self, ctx: commands.Context) -> None:
        # Build response
        response = {}
        response['title'] = "What is ALICE?"
        response['description'] =\
            """
                **ALICE** is a chatter bot inspired by **ELIZA**. It has won multiple
                Loebner Prize awards, but has not been able to pass the Turing Test.
                It is writen in AIML (Artificial Intelligence Markup Language) and
                is open source.
                More at the Wikipedia article:
                https://en.wikipedia.org/wiki/Artificial_Linguistic_Internet_Computer_Entity
                The python3 AIML interpreter, and copy of **ALICE** are found at this git 
                repository:
                https://github.com/paulovn/python-aiml
            """
        # Build embed
        embed = discord.Embed.from_dict(response)
        # Send embed
        return await ctx.send(embed=embed)
