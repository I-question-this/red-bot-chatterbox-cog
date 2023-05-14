from .chatterbox import ChatterBox

async def setup(bot):
    await bot.add_cog(ChatterBox(bot))

