import asyncio
import datetime
import json
import platform
import random
import re
import string
import sys
import time
import discord
from colorama import Back, Fore, Style
from discord import app_commands
from discord.ext import commands


from Functions.dbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
#from Functions.randFunctions import *
from Commands.managementcmds import ManagementCmds

from Commands.operationcmds import OperationCmds, soupCmd
from Commands.othercmds import otherCmds
from Commands.pointscmds import PointCmds, mypointsCmd
from Commands.registrycmds import RegistryCmds
from Commands.requestcmds import RequestCmds
from Commands.testingcmds import testingCmds



bot = commands.Bot(command_prefix=">", intents=discord.Intents().all())
tree = app_commands.CommandTree(discord.Client(intents=discord.Intents().all()))
start_date, end_date, blocknumber = get_quota()
@bot.event  
async def on_ready():
    print("Loading imports...")
    await bot.add_cog(ManagementCmds(bot))
    await bot.add_cog(OperationCmds(bot))
    await bot.add_cog(soupCmd(bot))
    await bot.add_cog(otherCmds(bot))
    await bot.add_cog(PointCmds(bot))
    await bot.add_cog(mypointsCmd(bot))
    await bot.add_cog(RegistryCmds(bot))
    await bot.add_cog(RequestCmds(bot))
    #await bot.add_cog(testingCmds(bot))
    
    
    # Console output
    prfx = (Back.BLACK + Fore.BLUE) + Back.RESET + Fore.WHITE + Style.BRIGHT
    print(prfx + "|| Logged in as " + Fore.BLUE + bot.user.name + "  at  " + time.strftime("%H:%M:%S UTC", time.gmtime()))
    print(prfx + "|| Bot ID: " + Fore.BLUE + str(bot.user.id))
    print(prfx + "|| Discord Version: " + Fore.BLUE + discord.__version__)
    print(prfx + "|| Python Version: " + Fore.BLUE + str(platform.python_version()))
    print(prfx + "Syncing commands...")
    try:
        synced = await bot.tree.sync()
        print("\033[2K" + prfx + f"|| Slash CMDs Synced: {Fore.BLUE}{len(synced)} Commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")
        synced = []
    # Quota and notes output
    quota = False
    notes = False
    if start_date and end_date and blocknumber:
        print(prfx + f"|| Quota data: found")
        quota = True
        notes = True
    else:
        print(prfx + f"|| Quota data: not found! Please check the database.")
        notes = True
    
    # Embed message
    embed = discord.Embed(title="Bot Startup Info • MainBot", color=discord.Color.green())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Runtime Information", value=f"Discord Version: {discord.__version__} || Python Version: {platform.python_version()}", inline=False)
    embed.add_field(name="Synced Slash Commands", value=len(synced), inline=False)
    
    if quota:
        embed.add_field(name="Quota status", value="set", inline=False)
    else:
        embed.add_field(name="Quota status", value="not set, please check the database.", inline=False)
    
    if not notes:
        embed.add_field(name="Notes", value="N/A", inline=False)
    
    channel = bot.get_channel(1069974021246046310)  # Startup-channel ID
    await channel.send(embed=embed)
with open('token.json', 'r') as f:
    data = json.load(f)
    TOKEN = data['TOKEN']

@bot.event
async def on_message(message):
    if lmfao_event == True and message.author.id != 776226471575683082:
        if message.content.lower() == "lmfao":
            await message.reply("Who is Lmfao? 🤨\nHe's a hacker, he's a Chinese hacker.\nLmfao, he's working for the Koreans isn't he?")


## DEV COMMANDS ##
class MsgGrp(app_commands.Group):
    pass
messagegroup = MsgGrp(name="dev")
bot.tree.add_command(messagegroup)

@messagegroup.command(name="send_message", description="Sends a message to a specified channel")
async def send_message(interaction:discord.Interaction, channel:discord.TextChannel, message:str):
    if DEVACCESS(interaction.user):
        await channel.send(message)
        await interaction.response.send_message("Message sent!", ephemeral=True)
@messagegroup.command(name="edit_message", description="Edits the latest message sent by the bot")
async def edit_message(interaction:discord.Interaction, channel:discord.TextChannel, message:str):
    if DEVACCESS(interaction.user):
        async for msg in channel.history(limit=1):
            if msg.author == bot.user:
                await msg.edit(content=message)
                await interaction.response.send_message("Message edited!", ephemeral=True)
                break
        else:
            await interaction.response.send_message("No recent message from the bot found in this channel!", ephemeral=True)

  

# INFOBOARD COMMAND #
class InfoboardOptions(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="DSB Helper Infoboard", description="A list of all basic commands.", value="DHI"),
            discord.SelectOption(label="Basic Commands", description="A list of all basic commands.", value="BC"),
            discord.SelectOption(label="DSB Commands", description="A list of all commands available to DSB members.", value="DC"),
            discord.SelectOption(label="Management Commands", description="A list of all commands available to DSBPC+.", value="MC"),
            #discord.SelectOption(label="Squadrons Infoboard", description="Shows some general information about the server and squadrons.", value="SI")
        ]
        super().__init__(placeholder="Select a dropdown...", options=options, min_values=1, max_values=1)
        
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "DHI":
            embed = discord.Embed(title="**<:DSB:1060271947725930496> DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=DSBCommandsCOL)
            embed.add_field(name="Credits", value="- Main developer: Blue\n- Bot host: Orange\n- Frontend Design: Blue, Shush & Polish\n- Bot testing: the suffering + Polish")
            embed.set_footer(text="DSB Helper v.idk")
            embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/lnHKwZ40MRhYKuNJpNUS8NQiaekqkgfW9TaGj-B5Yg0/https/tr.rbxcdn.com/580b2e0cd698decfa585464b50a4278c/150/150/Image/Png")
        elif self.values[0] == "BC":
            embed = discord.Embed(title="**Basic Commands**", description="All servers members can use these commands. They are represented by the color white.", color=BasiccommandCOL)
            embed.add_field(name="**/whois**", value="Displays someones general and server informations.", inline=False)
            embed.add_field(name="**/ping**", value="Shows the bot's response time in miliseconds.", inline=False)
        elif self.values[0] == "DC":
            embed = discord.Embed(title="**<:DSB:1060271947725930496> DSB Commands**", description="All DSB members PFC and above have access to these and are represented by the navy blue.", color=DSBCommandsCOL)
            embed.add_field(name="**/points overview**", value="Displays a leaderboard for points.", inline=False)
            embed.add_field(name="**/points view**", value="View someone else's current point count.", inline=False)
            embed.add_field(name="**/mypoints**", value="View your current point count.", inline=False)
            embed.add_field(name="**/soup**", value="Adds or removes the Op. Supervisor Role. [EDS+]", inline=False)
            #embed.add_field(name="**/rloa**", value="Coming soon:tm:...", inline=False)
        elif self.values[0] == "MC":
            embed = discord.Embed(title="**Management Commands**", description="DSB Pre-Command and above have access to these. They are represented by the color black.", color=HRCommandsCOL)
            embed.add_field(name="**/points add/remove**", value="Adds/removes points to/from a user.", inline=False)
            embed.add_field(name="**/points reset**", value="Resets the points of all users to zero.", inline=False)
            embed.add_field(name="**/updatequota**", value="Updates the quota block number, start and end date.", inline=False)
            embed.add_field(name="**/restart**", value="Restarts DSB Helper.", inline=False)
            embed.add_field(name="**/shutdown**", value="Shuts down DSB Helper. [DSBCOMM+]", inline=False)
        #elif self.values[0] == "SI":
        #    embed = discord.Embed(title="**Server Info**")
        
        await interaction.response.edit_message(embed=embed)
        
class InfoboardView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(InfoboardOptions())

@bot.tree.command(name="infoboard",description="Shows bot information and a list of commands.")
async def infoboard(interaction: discord.Interaction):
    embed = discord.Embed(title="**DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=DSBCommandsCOL)
    embed.add_field(name="Credits", value="- Main developer: Blue\n- Bot host: Orange\n- Frontend Design: Blue, Shush & Polish\n- Bot testing: the suffering + Polish")
    embed.set_footer(text="DSB Helper v.idk")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/lnHKwZ40MRhYKuNJpNUS8NQiaekqkgfW9TaGj-B5Yg0/https/tr.rbxcdn.com/580b2e0cd698decfa585464b50a4278c/150/150/Image/Png")
    await interaction.response.send_message(embed=embed, view=InfoboardView())



bot.run(TOKEN)