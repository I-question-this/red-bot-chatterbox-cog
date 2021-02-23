import asyncio
import discord
import logging
import os
import random
import re
import subprocess
import tempfile

from redbot.core import checks, commands, Config
from redbot.core.data_manager import cog_data_path
from redbot.core.bot import Red

import aiml
from .eliza.eliza import eliza as Eliza

log = logging.getLogger("red.chatterbox")

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
ALICE_LEARN_FILES_DIR = os.path.join(FILE_DIR, "alice")


class ChatterBox(commands.Cog):
    """ChatterBox cog"""

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self._conf = Config.get_conf(None, 191919191, cog_name=f"{self.__class__.__name__}", force_registration=True)
        self.alice_bot_brain = os.path.join(cog_data_path(), "ChatterBox/alice.brain")


    @commands.Cog.listener()
    async def on_ready(self):
        self.setup_alice()
        self.eliza_bot = Eliza()


    @staticmethod
    async def clean_input(ctx, text:str) -> str:
        """Removes characters that confuse bots
        Parameters
        ----------
        text: str
            Text to be clean.
        Returns
        -------
        str
            The cleaned text.
        """
        words = list()
        converter = commands.MemberConverter()
        for word in text.split():
            try:
                member = await converter.convert(ctx, word)
                words.append("-".join(member.display_name.split()))
            except discord.ext.commands.errors.BadArgument:
                words.append(word)
        text = " ".join(words)
        return text


    @commands.command(name="speak")
    async def main_speak(self, ctx: commands.Context, *words) -> None:
        """The main way to talk to Dad

        Parameters
        ----------
        text: str
            The text to speak to the bot with.
        """
        text = " ".join(words)
        response = await self.response_from_alice(ctx, text)

        await ctx.channel.send(response)

        await self.speak_in_voice_channel(ctx, response)


    async def speak_in_voice_channel(self, ctx: commands.Context,
            text) -> None:
        # Check if the user is in voice chat
        if ctx.author.voice is not None:
            # Check if already connected for this server
            voice_client = discord.utils.get(
                    self.bot.voice_clients, guild=ctx.guild)
            if voice_client is None:
                # create voice client
                voice_client = await ctx.author.voice.channel.connect()

            # If already playing audio, wait
            while voice_client.is_playing():
                asyncio.sleep(1)

            # Create the voice file
            # We need to hold on to the directory handle so it doesn't
            # get deleted before we're done with the files inside.
            self.tmp_dir_handle = tempfile.\
                TemporaryDirectory(prefix="chatterbox")
            tmp_dir = self.tmp_dir_handle.name
            message_file = os.path.join(tmp_dir, "msg.txt")
            audio_file = os.path.join(tmp_dir, "msg.wav")
            with open(message_file, "w") as fout:
                fout.write(text)
            try:
                res = subprocess.run(("espeak", "-f", message_file, "-w",
                    audio_file), 
                        capture_output=True)
                if res.returncode == 0:
                    # Create the audio source
                    audio_source = discord.FFmpegPCMAudio(audio_file)
                    # Play the audio
                    voice_client.play(audio_source, after=None)
                else:
                    log.error(f"Espeak failed because: {res.stderr}")
            except FileNotFoundError:
                    log.error(f"Espeak failed because: "\
                            "Can't find it in the path. Is it installed?")


    @commands.group()
    async def eliza(self, ctx: commands.Context) -> None:
        """Eliza commands"""


    async def response_from_eliza(self, ctx, text:str) -> str:
        return self.eliza_bot.respond(await self.clean_input(ctx, text))


    @eliza.command(name="speak")
    async def speak_to_eliza(self, ctx: commands.Context, *words) -> None:
        # Build response/talk to Eliza
        response = {}
        response['title'] = f"Dear {ctx.author.display_name},"
        text = " ".join(words)
        response['description'] =\
                f"{await self.response_from_eliza(ctx, text)}\n*--Eliza*"
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


    async def response_from_alice(self, ctx, text:str) -> str:
        response = self.alice_bot.respond(await self.clean_input(ctx, text))
        self.alice_bot.saveBrain(self.alice_bot_brain)
        return response


    def setup_alice(self):
        # Load up default ALICE
        self.alice_bot = aiml.Kernel()
        self.alice_bot.setTextEncoding(None)
        self.alice_bot.bootstrap(learnFiles="startup.xml", 
                commands="load alice", chdir=ALICE_LEARN_FILES_DIR)
        # Tell Alice it's name is the string Discord uses to mention users.
        self.alice_bot.setBotPredicate(
                "name", "-".join(self.bot.user.name.split()))
        # Setup/load brain file
        if os.path.isfile(self.alice_bot_brain):
            # Load the existing brain file
            self.alice_bot.bootstrap(brainFile=self.alice_bot_brain)
        else:
            # Create a new brain file
            self.alice_bot.saveBrain(self.alice_bot_brain)


    @alice.command(name="speak")
    async def speak_to_alice(self, ctx: commands.Context, *words) -> None:
        # Build response/talk to Eliza
        response = {}
        response['title'] = f"Dear {ctx.author.display_name},"
        text = " ".join(words)
        response['description'] = f"{await self.response_from_alice(ctx, text)}\n*--ALICE*"
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


    @alice.command(name="reset")
    @checks.is_owner()
    async def reset_alice(self, ctx: commands.Context) -> None:
        """Invoking this command will delete Alice's brain."""
        # Delete the brain
        os.remove(self.alice_bot_brain)
        # Restart alice
        self.setup_alice()
        # Inform user
        await ctx.send("Alice has been reset")

