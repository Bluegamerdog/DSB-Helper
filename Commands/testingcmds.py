import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from Functions.dbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

class testingCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="testingstuff", description="bonk")
    async def testing(self, interaction: discord.Interaction, user:discord.Member=None):
        

        await interaction.response.defer(ephemeral=True)


class patrolCmds(commands.GroupCog, group_name="patrol"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="start", description="Start a log.")
    async def startlog(self, interaction:discord.Interaction):
        loginfo = discord.Embed(title="<:DSB:1060271947725930496> New DSB log!", description=f"**Your log ID is `xxxxxx`.**\nUse this to interact with your log.\n\nEnsure you have joined a voice channel before you begin your patrol!")
        loginfo.add_field(name="Useful links", value="[DSB Infoboard](https://discord.com/channels/949470602366976051/954443926264217701)\nTo be added...\nTo be added...\nTo be added...")
        loginfo.set_footer(text="The current centralised time is " + str(datetime.utcnow()))
        if await interaction.user.send(embed=loginfo):
            startedlog = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Your log has begun!", description="More information has been sent to your DMs.\n*Have a nice patrol!*", color=0x0b9f3f)
            await interaction.response.send_message(embed=startedlog)
        else:
            faillog = discord.Embed(title="<:dsbbotFailed:953641818057216050> Process failed!", description="Something went wrong!", color=0xb89715)
            await interaction.response.send_message(embed=faillog)
