import asyncio
import datetime
import json
import math
import os
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

from database import *

config = json.load(open("config.json"))

bot = commands.Bot(command_prefix=">", intents=discord.Intents().all(),help_command=None)
tree = app_commands.CommandTree(discord.Client(intents=discord.Intents().all()))

def quota_get():
    global start_date
    global end_date
    global blocknumber
    start_date, end_date, blocknumber = get_quota()


##### EMBED COLORS ####
global BasiccommandCOL
BasiccommandCOL = 0xFFFFFF
global DSBCommandsCOL
DSBCommandsCOL = 0x0B0B45
global HRCommandsCOL
HRCommandsCOL = 0x000000
global ErrorCOL
ErrorCOL = 0xB3202C
global DarkRedCOL
DarkRedCOL = 0x8B0000
global SuccessCOL
SuccessCOL = 0x4BB543
global DarkGreenCOL
DarkGreenCOL = 0x006400
global DSBSeverID
DSBSeverID = 949470602366976051
global SupportServerID
SupportServerID = 953638901677973554
global watching_command
watching_command = True
global lmfao_event
lmfao_event = True


def get_point_quota(user, data=None):
    role_quota = {
        "Private First Class": (16, "Private First Class"),
        "Corporal": (16, "**Corporal**"),
        "Junior Defense Specialist": (20, "**Junior Defense Specialist**"),
        "Sergeant": (26, "**Sergeant**"),
        "Senior Defense Specialist": (34, "**Senior Defense Specialist**"),
        "Staff Sergeant": (36, "**Staff Sergeant**"),
        "Elite Defense Specialist": (40, "**Elite Defense Specialist**"),
        "Master Sergeant": (36, "**Master Sergeant**"),
        "[DSB] Squadron Officer": (38, "**[DSB] Squadron Officer**"),
        "Executive Officer": (None, "**Executive Officer**"),
        "Lieutenant": (None, "**Lieutenant**"),
        "DSB Marshal": (None, "**DSB Marshal**"),
        "DSB Squadron Leader": (None, "**DSB Squadron Leader**"),
        "Major": (None, "**Major** *[QSO Pre-Command]*"),
        "QSO Pre-Command": (None, "**QSO Pre-Command**"),
        "QSO Command": (None, "**QSO Command**")
    }
    
    for role in user.roles:
        if role.name in role_quota:
            quota, rank = role_quota[role.name]
            if data and data[4]:
                quota = int(quota - ((quota/14)*data[4]))
            return quota, rank
    
    return None, None

@bot.event
async def on_ready():
    quota_get()
    #Console#
    prfx = (Back.BLACK + Fore.BLUE) + Back.RESET + Fore.WHITE + Style.BRIGHT
    print(prfx + "|| Logged in as " + Fore.BLUE + bot.user.name + "  at  " + time.strftime("%H:%M:%S UTC", time.gmtime()))
    print(prfx + "|| Bot ID: " + Fore.BLUE + str(bot.user.id))
    print(prfx + "|| Discord Version: " + Fore.BLUE + discord.__version__)
    print(prfx + "|| Python Version: " + Fore.BLUE + str(platform.python_version()))
    print(prfx + "|| Syncing commands...")
    synced = await bot.tree.sync()
    print("\033[2K" + prfx + "|| Slash CMDs Synced: " + Fore.BLUE + str(len(synced)) + " Commands")
    print(prfx + "-----------------NOTES-----------------")
    if start_date != None and end_date != None and blocknumber != None:
        print(prfx + f"|| Quota data: found")
        quota = True
        notes = True
    if quota != True:
        print(prfx + f"|| Quota data: not found! Please check the database.")
        notes = True
    if notes != True:
        print(prfx + f"|| N/A")
         
    #Embed#
    embed = discord.Embed(title="Bot Startup Info • InDev", color=discord.Color.green())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Runtime Information", value=f"Discord Version: {discord.__version__} || Python Version: {platform.python_version()}", inline=False)
    embed.add_field(name="Synced Slash Commands", value=len(synced), inline=False)
    embed.add_field(name="--------------------NOTES--------------------", value="", inline=False)
    if start_date != None and end_date != None and blocknumber != None:
        embed.add_field(name="", value=f"Quota status: set")
        quota = True
        notes = True
    if quota != True:
        embed.add_field(name="", value="Quota not set, please check the database.")
    if notes != True:
        embed.add_field(name="", value="N/A")
    channel = bot.get_channel(1069974021246046310)  # Replace channel_id with the ID of the channel you want to send the message to
    await channel.send(embed=embed)

def DSBCOMM_A(user): # function to check if user is DSBPCOMM+
    roles = user.roles
    for role in roles:
        if role.name in ["QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator or user.id == "":
            return True
    return False

def DSBPC_A(user): # function to check if user is DSBPC+ 
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def FMR_A(user): # function to check if user is MR+
    roles = user.roles
    for role in roles:
        if role.name in ["Elite Defense Specialist", "Master Sergeant", "[DSB] Squadron Officer", "DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def ITMR_A(user): # MR in-training and above
    roles = user.roles
    for role in roles:
        if role.name in ["DSB MR", "DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def DSBMEMBER(user): # check if user has DSB role
    roles = user.roles
    for role in roles:
        if role.name in ["DSB"] and role.name not in ["DSB Private"] or role.permissions.administrator:
            return True
    return False

def DEVACCESS(user):
    allowed_ids = [776226471575683082, 395505414000607237, 1053377038490292264] # Blue, Orange and Shush
    if user.id in allowed_ids or user.guild_permissions.administrator:
        return True
    return False

def onLoA(user): # check if user has DSB role
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Leave of Absence"]:
            return True
    return False

def totalquota_withoutPC():
    rows = db_get_all_data()
    total_quota:int = 0
    for row in rows:
        member = bot.get_guild(DSBSeverID).get_member(row[1])
        if member:
            if DSBPC_A(member)==False and onLoA(member)==False:
                quota, rank = get_point_quota(member, row)
                if quota != None:
                    total_quota += quota
    return total_quota

def totalpoints_withoutPC():
    rows = db_get_all_data()
    total_points:int = 0
    for row in rows:
        member = bot.get_guild(DSBSeverID).get_member(row[1])
        if member:
            if DSBPC_A(member)==False:
                total_points += row[3]
    return total_points    

def get_quota_completion_percentage():
    total_quota = totalquota_withoutPC()
    if total_quota == 0:
        return 0
    else:
        return (totalpoints_withoutPC() / total_quota) * 100

def attendance_points(user):
    roles_ = {
        "Private First Class": 4,
        "Corporal": 4,
        "Junior Defense Specialist": 4,
        "Sergeant": 2,
        "Senior Defense Specialist": 2,
        "Staff Sergeant": 2,
        "Elite Defense Specialist": 2,
        "Master Sergeant": 2,
        "[DSB] Squadron Officer": 2,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None

def co_host_points(user):
    roles_ = {
        "Sergeant": 5,
        "Senior Defense Specialist": 5,
        "Staff Sergeant": 4,
        "Elite Defense Specialist": 5,
        "Master Sergeant": 5,
        "[DSB] Squadron Officer": 4,
        "DSB Pre-Command": 1,
        "DSB Command": 1,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None

def supervisor_points(user):
    roles_ = {
        "Elite Defense Specialist": 4,
        "Master Sergeant": 4,
        "[DSB] Squadron Officer": 5,
        "DSB Pre-Command": 1,
        "DSB Command": 1,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None

def ringleader_points(user):
    roles_ = {
        "Sergeant": 7,
        "Senior Defense Specialist": 7,
        "Staff Sergeant": 8,
        "Elite Defense Specialist": 8,
        "Master Sergeant": 8,
        "[DSB] Squadron Officer": 8,
        "DSB Pre-Command": 1,
        "DSB Command": 1,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None


@bot.event
async def on_message(message):
    if lmfao_event == True and message.author.id != 776226471575683082:
        if message.content.lower() == "lmfao":
            await message.reply("Who is Lmfao? 🤨\nHe's a hacker, he's a Chinese hacker.\nLmfao, he's working for the Koreans isn't he?")

@bot.event
async def on_reaction_add(reaction, user):    
    if str(reaction.emoji) == "<:dsbbotSuccess:953641647802056756>" and reaction.message.channel.id == 983194737882312714 and DSBPC_A(reaction.user):
        role_name = "DSB Leave of Absence"
        role = discord.utils.get(reaction.message.guild.roles, name=role_name)
        await reaction.message.author.add_roles(role)

## MANEGEMENT COMMANDS ##

#BOT MANEGMENT#
@bot.tree.command(description="Restarts the DSB Helper. [DSBPC+]")
async def restart(interaction:discord.Interaction):
    if not DSBPC_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Missing permissions!", description="You must be a member of DSBPC or above to use the restart command.", color=ErrorCOL))
    else:
        embed=discord.Embed(color=0x008000, title="][ Request successful ][",description="DSB Helper restarting...")
        await interaction.response.send_message(embed=embed)
        os.system("cls")
        os.execv(sys.executable, ['python'] + sys.argv)
        
@bot.tree.command(name="shutdown", description="Shuts down DSB Helper. [DSBCOMM+]")
async def shutdown(interaction:discord.Interaction):
    if not DSBCOMM_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Missing permissions!", description="You must be member of DSBCOMM or above to use the shutdown command.", color=ErrorCOL))
    else:
        embed = discord.Embed(color=ErrorCOL, description="DSB Helper shutting down...")
        await interaction.response.send_message(embed=embed)
        print(f"Bot closed by {interaction.user.name}")
        await bot.close()
        
@bot.tree.command(name="status", description="Set the bot's activity [DSBPC+]")
async def change_status(interaction: discord.Interaction, status_type:str, name:str=None):
    if not DSBPC_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Missing permissions!", description="You must be a member of DSBPC or above to change DSB Helpers activity.", color=ErrorCOL), ephemeral=True)
        
    activity_types = {
        "playing": discord.ActivityType.playing,
        "streaming": discord.ActivityType.streaming,
        "listening": discord.ActivityType.listening,
        "watching": discord.ActivityType.watching,
    }

    global watching_command
    if status_type in activity_types:
        activity = discord.Activity(type=activity_types[status_type], name=name)
        await bot.change_presence(activity=activity)
        return await interaction.response.send_message(f"Status updated, {status_type} {name}", ephemeral=True)
    elif status_type == "w_enable":
        if watching_command == False:
            watching_command = True
            return await interaction.response.send_message(f"`/watching` enabled ({watching_command})", ephemeral=True)
        elif watching_command == True:
            watching_command = False
            return await interaction.response.send_message(f"`/watching` disabled ({watching_command})", ephemeral=True)
    elif status_type == "remove":
        await bot.change_presence(activity=None)
        return await interaction.response.send_message("Cleared activity.", ephemeral=True)
    elif status_type == "lmfao_event":
        global lmfao_event
        if lmfao_event == True:
            lmfao_event = False
            return await interaction.response.send_message(f"`lmfao_event` disabled. {lmfao_event}", ephemeral=True)
        elif lmfao_event == False:
            lmfao_event = True
            return await interaction.response.send_message(f"`lmfao_event` enabled. {lmfao_event}", ephemeral=True)
    else:
        return await interaction.response.send_message("**Invalid status type, choose from:** `playing`, `streaming`, `listening`, `watching`, `w_enable`, `lmfao_event` or `remove`", ephemeral=True)

#MISC MANEGMENT# 
@bot.tree.command(name="watching", description=":lo:")
async def watching(interaction: discord.Interaction, user:discord.Member=None):
    global watching_command
    if not watching_command:
        return await interaction.response.send_message("This command is currently disabled.", ephemeral=True)
    elif user == None:
        members = bot.guilds[0].members
        random_member = random.choice(members)
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{random_member.display_name}")
        await bot.change_presence(activity=activity)
        await interaction.response.send_message("Status updated, watching randomized", ephemeral=True)
    else:
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{user.display_name}")
        await bot.change_presence(activity=activity)
        await interaction.response.send_message(f"Status updated, watching {user.display_name}", ephemeral=True)

@bot.tree.command(name="updatequota",description="Updates the quota block start to end date. [DSBPC+]")
async def updatequota(interaction:discord.Interaction, start_date_new: int, end_date_new: int, blocknumber_new: int):
    if not DSBPC_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to remove user!", description="You must be a member of DSBPC or above to update/change quota block data.", color=ErrorCOL))
    else:
        update_quota(start_date_new, end_date_new, blocknumber_new)
        embed = discord.Embed(color=HRCommandsCOL, title="Quota block change")
        embed.add_field(name="From:", value=f"<t:{start_date}> - <t:{end_date}> || Block {blocknumber}", inline=False)
        embed.add_field(name="To:", value=f"<t:{start_date_new}> - <t:{end_date_new}> || Block {blocknumber_new}", inline=False)
        await interaction.response.send_message(embed=embed)
        quota_get()

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
@messagegroup.command(name="react", description="Reacts to the latest message in a specified channel using a custom emoji")
async def react_emoji(interaction:discord.Interaction, channel:discord.TextChannel, emoji:str):
    if DEVACCESS(interaction.user):
        async for msg in channel.history(limit=1):
            try:
                await msg.add_reaction(emoji)
                await interaction.response.send_message("Emoji reacted!", ephemeral=True)
                break
            except discord.errors.HTTPException as e:
                await interaction.response.send_message(f"Error adding reaction: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("No recent message found in this channel!", ephemeral=True)



# REGISTRASTION #
class RegGrp(app_commands.Group):
    pass
registergroup = RegGrp(name="db")
bot.tree.add_command(registergroup)

@registergroup.command(name="register", description="This command is used to add new data to the registry database.")
async def register_new(interaction: discord.Interaction, roblox_profile_link: str, user: discord.Member=None):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!", description=f"Only DSB Private First Class or above may register.", color=ErrorCOL))
    if user and user != interaction.user and not DSBPC_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!", description=f"You must be a member of DSBPC or above to register other users.", color=ErrorCOL), ephemeral=True)
    if user == None or user == interaction.user:
        try:
            if db_register_new(str(interaction.user), interaction.user.id, roblox_profile_link):
                embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Successfully registered!",description=f"`Username:` {interaction.user}\n`User ID:` {interaction.user.id}\n`Roblox Profile:` {roblox_profile_link}", color=discord.Color.green())
            else:
                embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to register!", description=f"You are already in the database.\n*If you wish to update your data, use `/database update`.*", color=ErrorCOL)
        except Exception as e:
            embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!", description=f"An error occured: {str(e)}", color=ErrorCOL)
    else:
        try:
            if db_register_new(str(user), user.id, roblox_profile_link):
                embed = discord.Embed(title=f"<:dsbbotSuccess:953641647802056756> Successfully registered {user}!",description=f"`Username:` {user}\n`User ID:` {user.id}\n`Roblox Profile:` {roblox_profile_link}", color=discord.Color.green())
            else:
                embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to register!", description=f"User is already in the database.", color=ErrorCOL)
        except Exception as e:
            embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!", description=f"An error occured: {str(e)}", color=ErrorCOL)


    await interaction.response.send_message(embed=embed)

@registergroup.command(name="update_user", description="This command is used to update a specifc users data in the registry database.")
async def register_update(interaction: discord.Interaction, new_profile_link: str = None, user: discord.Member = None):
    if user!= interaction.user and not DSBPC_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Update failed!", description="You must be a member of DSBPC or above to update other users.", color=ErrorCOL))
        
    target_user = user or interaction.user
    username_updated = db_register_update_username(target_user.id, str(target_user))
    profile_link_updated = db_register_update_profile_link(target_user.id, new_profile_link) if new_profile_link else False
    result = None
    if username_updated and profile_link_updated:
        result = (f"`Updated Username:` {target_user}\n"f"`Updated Profile Link:` {new_profile_link}")
    elif username_updated:
        result = f"`Updated Username:` {target_user}"
    elif profile_link_updated:
        result = f"`Updated Profile Link:` {new_profile_link}"
    else:
        result = f"`{target_user}` already up to date."

    await interaction.response.send_message(
        embed=discord.Embed(title=(
                    f"<:dsbbotSuccess:953641647802056756> Successfully updated {target_user}!"
                    if username_updated or profile_link_updated else
                    f"<:dsbbotFailed:953641818057216050> No change made to {target_user}!"), description=result, color=(discord.Color.green() if username_updated or profile_link_updated else ErrorCOL)))

@registergroup.command(name="purge", description="This command is used to purge the registry database. [DSBCOMM+]")
async def register_purge(interaction:discord.Interaction):
    if not DEVACCESS(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to purge regirty!", description="You must be mentioned in `DEVACCESS` to purge the registry database.", color=ErrorCOL))
    else:
        await interaction.response.send_message(embed=discord.Embed(description="<:dsbbotUnderReview:1067970676041982053> Waiting for a response..."))
        embed = discord.Embed(color=HRCommandsCOL, description=f"<:dsbbotUnderReview:1067970676041982053> **Are you sure you want to purge the registry database?**\nReact with <:dsbbotApproved:953642750039953418> to confirm.", colour=ErrorCOL)
        msg = await interaction.edit_original_response(embed=embed)
        await msg.add_reaction("<:dsbbotApproved:953642750039953418>")
        
        
        # Wait for the user's reaction
        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) == '<:dsbbotApproved:953642750039953418>'
        try:
            reaction, user_r = await bot.wait_for('reaction_add', check=check, timeout=10)
        except asyncio.TimeoutError:
            embed = discord.Embed(color=ErrorCOL, description=f"<:dsbbotFailed:953641818057216050> Timed out waiting for reaction.")
            tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
            await asyncio.gather(*tasks)

        else:
            if DEVACCESS(user_r):
                success, result = db_register_purge()
                try:
                    if success:
                        embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Successfully purged registry!", description=f"`Deleted rows:` {result.rowcount}", color=discord.Color.green())
                        await interaction.edit_original_response(embed=embed)
                except Exception as e:
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to purge registry!", description=f"An error occured: {e}", color=ErrorCOL)
                        tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
                        await asyncio.gather(*tasks)
               
@registergroup.command(name="remove", description="Remove a user from the registry database. [DSBCOMM+]")
async def register_remove(interaction:discord.Interaction, user_id:str):
    if not DSBCOMM_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to remove user!", description="You must be a member of DSBCOMM or above to remove users from the user database.", color=ErrorCOL))
        
    result = db_register_remove_user(int(user_id))
    embed = discord.Embed(title=f"<:dsbbotSuccess:953641647802056756> Successfully removed user!" if result else f"<:dsbbotFailed:953641818057216050> Failed to removed user!", description=f"Deleted id: `{user_id}`" if result else f"`{user_id}` was not found in the database.", color=discord.Color.green() if result else ErrorCOL)
    await interaction.response.send_message(embed=embed)
        
@registergroup.command(name="view", description="This command is used to view data in the registry database.")
async def register_view(interaction:discord.Interaction, user:discord.Member=None):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Interaction failed!", description=f"Only DSB Private First Class or above may interact with DSB Helper.", color=ErrorCOL))
    if user == None:
        user = interaction.user
    result = db_register_get_data(user.id)
    if result:
        embed = discord.Embed(title=f"<:dsbbotSuccess:953641647802056756> Data for {user}", description=f"`Username:` {result[0]}\n`User ID:` {result[1]}\n`Roblox Profile:` {result[2]}", color=discord.Color.green())
    else:
        embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No data found!", description=f"No data was found for `{user}`.", color=ErrorCOL)
    await interaction.response.send_message(embed=embed)
    

## POINTS GROUP ##
class PointsGrp(app_commands.Group):
    pass
pointsgroup = PointsGrp(name="points")
bot.tree.add_command(pointsgroup)


class PatrolrequestButtons(discord.ui.View):
    def __init__(self, amount:int):
        super().__init__()
        self.amount = amount
        discord.ui.View.timeout = None
    
    @discord.ui.button(emoji="<:dsbbotAccept:1073668738827694131>", label="Accept", style=discord.ButtonStyle.grey)
    async def AcceptButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not DSBPC_A(interaction.user):
            return
        else:
            try:
                add_points(interaction.message.interaction.user.id, self.amount)
                embed = interaction.message.embeds[0]
                embed.title= embed.title.replace("<:dsbbotUnderReview:953642762857771138>", "<:dsbbotAccept:1073668738827694131>")
                embed.color=DarkGreenCOL
                await interaction.message.edit(embed=embed, view=None)
                embed=discord.Embed(color=SuccessCOL,title="<:dsbbotAccept:1073668738827694131> Point Request Accepted!", description=f"Your point request has been **accepted** and {self.amount} points have been added. You now have **{get_points(interaction.message.interaction.user.id)}** points. 😎")
                embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
                await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="Failed to proccess request!", description=f"`Error:` {e}"), ephemeral=True)

    @discord.ui.button(emoji="<:dsbbotDeny:1073668785262833735>", label="Decline", style=discord.ButtonStyle.grey)
    async def DenyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not DSBPC_A(interaction.user):
            return
        else:
            embed = interaction.message.embeds[0]
            embed.title= embed.title.replace("<:dsbbotUnderReview:953642762857771138>", "<:dsbbotDeny:1073668785262833735>")
            embed.color=DarkRedCOL
            await interaction.message.edit(embed=embed, view=None)
            embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Point Request Denied!", description=f"Your point request has been **denied**. The person who reviewed it will provide you with the reason shortly. 😄")
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)

    @discord.ui.button(emoji="❌", label="Cancel", style=discord.ButtonStyle.grey)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user == interaction.message.interaction.user:
            embed = interaction.message.embeds[0]
            embed.title="<:dsbbotFailed:953641818057216050> Cancelled __Patrol__ Point Request!"
            embed.clear_fields()
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Cancelled by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            embed.color=HRCommandsCOL
            await interaction.message.edit(embed=embed, view=None)
        else:
            return
            
class OperationrequestButtons(discord.ui.View):
    def __init__(self, points_dict):
        super().__init__()
        self.points_dict = points_dict
        discord.ui.View.timeout = None
    
    @discord.ui.button(emoji="<:dsbbotAccept:1073668738827694131>", label="Accept", style=discord.ButtonStyle.grey)
    async def AcceptButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not DSBPC_A(interaction.user):
            return
        else:
            try:
                for user_id, amount in self.points_dict.items():
                    add_points(user_id, amount)
                embed = interaction.message.embeds[0]
                embed.title= embed.title.replace("<:dsbbotUnderReview:953642762857771138>", "<:dsbbotAccept:1073668738827694131>")
                embed.color=DarkGreenCOL
                await interaction.message.edit(embed=embed, view=None)
                embed=discord.Embed(color=SuccessCOL,title="<:dsbbotAccept:1073668738827694131> Point Request Accepted!", description=f"The point request for this operation has been **accepted** and all points have been added. 🛡️")
                embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
                await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="Failed to proccess request!", description=f"`Error:` {e}"), ephemeral=True)

    @discord.ui.button(emoji="<:dsbbotDeny:1073668785262833735>", label="Decline", style=discord.ButtonStyle.grey)
    async def DenyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not DSBPC_A(interaction.user):
            return
        else:
            embed = interaction.message.embeds[0]
            embed.title= embed.title.replace("<:dsbbotUnderReview:953642762857771138>", "<:dsbbotDeny:1073668785262833735>")
            embed.color=DarkRedCOL
            await interaction.message.edit(embed=embed, view=None)
            embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Point Request Denied!", description=f"The point request for this operation has been **denied**. The person who reviewed it will provide the reason shortly. 😄")
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)

    @discord.ui.button(emoji="❌", label="Cancel", style=discord.ButtonStyle.grey)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user == interaction.message.interaction.user:
            embed = interaction.message.embeds[0]
            embed.title="<:dsbbotFailed:953641818057216050> Cancelled __Operation__ Point Request!"
            embed.clear_fields()
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Cancelled by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            embed.color=HRCommandsCOL
            await interaction.message.edit(embed=embed, view=None)
        else:
            return

class PointsRequestLogGrp(app_commands.Group):
    pass
pointsgroup_request_log = PointsRequestLogGrp(name="request")
pointsgroup.add_command(pointsgroup_request_log) 
    
@pointsgroup_request_log.command(name="patrol", description="Request points for your patrols using this command.")
@app_commands.describe(log="Message link to .qb findlog message from #bot-commands", length="The length of your patrol in minutes")
async def request_log(interaction:discord.Interaction, length:int, log:str):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only DSB Private First Class or above may interact with DSB Helper."), ephemeral=True)
    if not db_register_get_data(interaction.user.id):
        return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Interaction failed!", description="You were not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL), ephemeral=True)   
    message_link_pattern = re.compile(r"https://(?:ptb\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)")
    if not message_link_pattern.match(log):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid proof!", description=f"You must provide a Discord message link."), ephemeral=True)
    if length < 30 or length > 541:
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid length!", description=f"The length of your patrol must be at least 30 minutes." if length < 30 else "Your patrol should not be over 9hs or 540 minutes..."), ephemeral=True)
    else:
        if length <= 60:
            amount = 2
        else:
            amount = 2
            extra = math.floor((length - 60+7) / 30)
            print(amount, extra, (length - 60+7) / 30)
            amount += extra
    embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotUnderReview:953642762857771138> __Patrol__ Point Request - {interaction.user.display_name}")
    embed.add_field(name="", value="")
    embed.add_field(name="", value=f"**{interaction.user.display_name}** has requested **{amount} points** for patrolling **{length} minutes**.\n\n→ **[Log Message]({log})**", inline=False)
    await interaction.response.send_message(embed = embed, view=PatrolrequestButtons(amount))

@pointsgroup_request_log.command(name="operation", description="Request points for your operations using this command.")
@app_commands.describe(operation="Example: `ECHO HH`", ringleader="The host of the operation, normally that would be you.", co_hosts="If anyone co-hosted your operation they would go here.", supervisors="If anyone soupervised your operation, they would go here.", attendees="Your attendance list goes here. Make sure to seperate the mentions using a comma.")
async def request_op(interaction:discord.Interaction, operation:str, ringleader:discord.Member, supervisors:str=None, co_hosts:str=None, attendees:str=None):
    if not ITMR_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description=f"This command is limited to DSB Sergeant+."), ephemeral=True)
    if not db_register_get_data(interaction.user.id):
        return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Interaction failed!", description="You were not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL), ephemeral=True)   
    embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotUnderReview:953642762857771138> __Operation__ Points Request - Operation {operation}")
    points_dict = {}
    
    if co_hosts:
        cohost_list = []
        cohosts = co_hosts.split(",")
        for co_host in cohosts:
            error_msg = None
            co_host = co_host.replace(" ", "")
            if not co_host.startswith("<@") or not co_host.endswith(">"):
                error_msg = "Co-Host: Invalid format for co-hosts. Format `<@USERID>, <@USERID>`"
                break
            co_host_id = int(co_host.replace("<", "").replace("@", "").replace(">", "").replace(" ", ""))
            if str(co_host_id).__len__() > 18:
                error_msg = f"`Co-Hosts:` Please separate user mentions with commas."
                break
            co_host_member = discord.utils.get(interaction.guild.members, id=co_host_id)
            if co_host_member is None:
                error_msg = f"`Co-Hosts:` Could not a find member."
                break
            if not db_register_get_data(co_host_member.id):
                error_msg = f"`Co-Hosts:` {co_host_member.mention} was not found in the database."
                break
            if co_host_points(co_host_member) == None:
                error_msg = f"`Co-Hosts:` {co_host_member.mention} is not DSB MR or above."
                break
            if co_host_member.id in points_dict:
                error_msg = f"`Co-Hosts:` {co_host_member.mention} was mentioned twice."
                break
            cohost_list.append(co_host_member)
            points_dict[co_host_member.id] = co_host_points(co_host_member)
        if error_msg:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid Input! || Error", description=error_msg), ephemeral=True)
        cohtxt = ", ".join([f"{cohost.display_name}[{points_dict[cohost.id]}]" for cohost in cohost_list])
    soup_list = []
    if supervisors:
        supervisorss = supervisors.split(",")
        for supervisor in supervisorss:
            error_msg = None
            supervisor_id = int(supervisor.replace("<", "").replace("@", "").replace(">", "").replace(" ", ""))
            if str(supervisor_id).__len__() > 19:
                error_msg = f"`Supervisors:` Please separate user mentions with commas."
                break
            if supervisor == f"<@{ringleader.id}>":
                error_msg = "`Supervisors:` You cannot mention the ringleader as a supervisor."
                break
            supervisor_member = discord.utils.get(interaction.guild.members, id=supervisor_id)
            if not supervisor_member:
                error_msg = "`Supervisors:` Could not find a member."
                break
            if not db_register_get_data(supervisor_member.id):
                error_msg = f"`Supervisors:` {supervisor_member.mention} was not found in the database."
                break
            if supervisor_id in points_dict:
                error_msg = f"`Supervisors:` {supervisor_member.mention} was mentioned twice."
                break
            if supervisor_points(supervisor_member) == None:
                error_msg = f"`Supervisors:` {supervisor_member.mention} is not Sergeant+."
                break
            soup_list.append(supervisor_member)
            points_dict[supervisor_member.id] = supervisor_points(supervisor_member)
        if error_msg:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid Input! || Error", description=error_msg), ephemeral=True)
        souptxt = ", ".join([f"{supervisor.display_name}[{supervisor_points(supervisor)}]" for supervisor in soup_list])
    attendees_list = []
    if attendees:
        attendeess = attendees.split(",")
        for attendee in attendeess:
            error_msg = None
            attendee = attendee.replace(" ", "")
            if attendee == f"<@{ringleader.id}>":
                error_msg = "Attendees: You cannot mention the ringleader as an attendee."
                break
            attendee_id = int(attendee[2:-1])
            attendee_member = discord.utils.get(interaction.guild.members, id=attendee_id)
            if not attendee_member:
                error_msg = f"`Attendees:` Could not find a member with ID {attendee_id}."
                break
            if DSBPC_A(attendee_member):
                error_msg = f"`Attendees:` {attendee_member.mention} is a member of DSBPC or above. You cannot put DSBPC members and above as attendee. 😉"
                break
            if not db_register_get_data(attendee_id):
                error_msg = f"`Attendees:` {attendee_member.mention} was not found in the database."
                break
            if attendance_points(attendee_member) == None:
                error_msg = f"`Attendees:` {attendee_member.mention} is not a valid attendee. No point value found for this rank/person."
                break
            attendees_list.append(attendee_member)
            points_dict[attendee_member.id] = attendance_points(attendee_member)
        if error_msg:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid Input! || Error", description=error_msg), ephemeral=True)
        atttxt = ", ".join([f"{attendee.display_name}[{attendance_points(attendee)}]" for attendee in attendees_list])
    else:
        if not co_hosts:
            cohtxt = "Something went wrong..."
        if not supervisors:
            souptxt = "Something went wrong..."
        if not attendees:
            atttxt = "Something went wrong..."
    
    if ringleader:
        if ITMR_A(ringleader):
            points_dict[ringleader.id] = ringleader_points(ringleader)
            print(points_dict)
            embed.add_field(name="", value=f"`Ringleader:` {ringleader.display_name}[{ringleader_points(ringleader)}]")
        else:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Invalid Input", description=f"{ringleader.mention} is not DSB MR or above."))
    if co_hosts:
        embed.add_field(name="", value=f"`Co-Host:` {cohtxt}" if cohost_list.__len__() == 1 else f"`Co-Hosts:` {cohtxt}",inline=False)
    if supervisors:
        embed.add_field(name="", value=f"`Supervisor:` {souptxt}" if soup_list.__len__() == 1 else f"`Supervisors:` {souptxt}",inline=False)
    if attendees_list:
        embed.add_field(name="", value=f"`Attendee:` {atttxt}"if attendees_list.__len__() == 1 else f"`Attendees:` {atttxt}", inline=False)
    await interaction.response.send_message(embed = embed, view=OperationrequestButtons(points_dict))
   
@pointsgroup.command(name="excuse_quota", description="Changes the quota for a user for the current block. [DSBPC+]")
async def loa_quota(interaction:discord.Interaction, member:discord.Member, set_amount:int):
    if(not DSBPC_A(interaction.user)): # check if user has permission
        embed = discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Failed to set days!", description=f"You must be a member of DSBPC or above to use this command.")
        return await interaction.response.send_message(embed=embed, ephemeral=True)
    if set_amount > 14:
        return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to set days!", description=f"`set_amount` cannot be over 14 days."), ephemeral=True)
    data = db_register_get_data(member.id)
    if data:
        quota, rank = get_point_quota(member)
        if data[4]:
            quota_new = int(quota - ((quota/14)*data[4]))
        if set_days_onloa(member.id, set_amount):
            updata = db_register_get_data(member.id)
            if updata[4] is not None:
                quota_new = int(quota - ((quota/14)*updata[4]))
            else:
                quota_new = quota
            return await interaction.response.send_message(f"{member.mention}", embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Default quota set for {member.display_name}!" if set_amount == 0 else f"<:dsbbotSuccess:953641647802056756> New quota for {member.display_name}!", description=f'New quota: **{quota_new} Points** <t:{end_date}:R>\nDays excused: **{updata[4]}**' if updata[4] == None else f'New quota: **{quota_new} Points** <t:{end_date}:R>\nDays excused: **{updata[4]} days**'))
        else:
            return await interaction.response.send_message(embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotFailed:953641818057216050> Failed to set!", description=f"Something went wrong..."), ephemeral=True)
    else:
        return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> `{member}` not found!", description="User not found in registry database.", color=ErrorCOL), ephemeral=True)

@pointsgroup.command(name="add", description="Adds points to a user. [DSBPC+]")
async def add(interaction:discord.Interaction, member:discord.Member, amount:int):
    user = interaction.user
    if(not DSBPC_A(user)): # check if user has permission
        embed = discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Failed to add points to user!", description=f"You must be a member of DSBPC or above to add points.")
        await interaction.response.send_message(embed=embed)
        return
    if(type(amount)==int and int(amount) >= 1):
        if add_points(member.id, amount) == True: # add points to the user
            embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Successfully added {amount} point to `{member}`!" if amount == 1 else f"<:dsbbotSuccess:953641647802056756> Successfully added {amount} points to `{member}`!", description=f"**{member.display_name}** now has **{get_points(member.id)}** point." if int(get_points(member.id)) == 1 else f"**{member.display_name}** now has **{get_points(member.id)}** points." )
        else:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to add points to `{member}`!", description="User not found in registry database.", color=ErrorCOL)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to add points to `{member}`!", description="Invalid point number.", color=ErrorCOL)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@pointsgroup.command(name="remove", description="Removes points from a user. [DSBPC+]")
async def remove(interaction:discord.Interaction, member:discord.Member, amount:int):
    if not DSBPC_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Failed to remove points from user!", description=f"You must be a member of DSBPC or above to remove points."))
    if(type(amount)==int and int(amount)>=1):
        if remove_points(member.id, amount) == True: #removes points from user
            embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Successfully removed {amount} point from `{member}`!" if amount == 1 else f"<:dsbbotSuccess:953641647802056756> Successfully removed {amount} points from `{member}`!" , description=f"**{member.display_name}** now has **{get_points(member.id)}** point." if int(get_points(member.id)) == 1 else f"**{member.display_name}** now has **{get_points(member.id)}** points.")
        else:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to remove points from `{member}`!", description="User not found in registry database.", color=ErrorCOL)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to remove points from `{member}`!", description="Invalid point number.", color=ErrorCOL)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
@pointsgroup.command(name="view",description="View someone else's current point count.")
async def view(interaction: discord.Interaction, user:discord.Member=None):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only DSB Private First Class or above may interact with DSB Helper."), ephemeral=True)
    else:
        embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data found for {user.display_name}!" if user and user != interaction.user else f"<:dsbbotSuccess:953641647802056756> Point data found!")
        if user == None:
            user = interaction.user
        points = get_points(user.id)
        if points is False:
            return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No point data found for `{user}`!", description="User not found in registry database.", color=ErrorCOL))
        embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data found!")
        data = db_register_get_data(user.id)
        quota, rank = get_point_quota(user, data)
        if quota and onLoA(user) == False:
            percent = float(points / quota * 100)
            if percent > 200:
                qm = "🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟"
            elif percent >= 200:
                qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪"
            elif percent >= 190:
                qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟦"
            elif percent >= 180:
                qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟦🟦"
            elif percent >= 170:
                qm = "🟪🟪🟪🟪🟪🟪🟪🟦🟦🟦"
            elif percent >= 160:
                qm = "🟪🟪🟪🟪🟪🟪🟦🟦🟦🟦"
            elif percent >= 150:
                qm = "🟪🟪🟪🟪🟪🟦🟦🟦🟦🟦"
            elif percent >= 140:
                qm = "🟪🟪🟪🟪🟦🟦🟦🟦🟦🟦"
            elif percent >= 130:
                qm = "🟪🟪🟪🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 120:
                qm = "🟪🟪🟦🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 110:
                qm = "🟪🟦🟦🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 100:
                qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 90:
                qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦⬛"
            elif percent >= 80:
                qm = "🟦🟦🟦🟦🟦🟦🟦🟦⬛⬛"
            elif percent >= 70:
                qm = "🟦🟦🟦🟦🟦🟦🟦⬛⬛⬛"
            elif percent >= 60:
                qm = "🟦🟦🟦🟦🟦🟦⬛⬛⬛⬛"
            elif percent >= 50:
                qm = "🟦🟦🟦🟦🟦⬛⬛⬛⬛⬛"
            elif percent >= 40:
                qm = "🟦🟦🟦🟦⬛⬛⬛⬛⬛⬛"
            elif percent >= 30:
                qm = "🟦🟦🟦⬛⬛⬛⬛⬛⬛⬛"
            elif percent >= 20:
                qm = "🟦🟦⬛⬛⬛⬛⬛⬛⬛⬛"
            elif percent >= 10:
                qm = "🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛"
            else:
                qm = "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛"
            embed.add_field(name=f"{qm} {percent:.1f}% || {points}/{quota}", value="")
            if not data[4]:
                embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**", inline=False)
            else:
                embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**\nDays excused: **{data[4]}d**", inline=False)
        elif quota and onLoA(user):
            percent = float(points / quota * 100)
            if percent > 200:
                qm = "🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟"
            elif percent >= 200:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟪🟪🟪"
            elif percent >= 190:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟪🟪🟦"
            elif percent >= 180:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟪🟦🟦"
            elif percent >= 170:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟦🟦🟦"
            elif percent >= 160:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟦🟦🟦🟦"
            elif percent >= 150:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟦🟦🟦🟦🟦"
            elif percent >= 140:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟦🟦🟦🟦🟦🟦"
            elif percent >= 130:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 120:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 110:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 100:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
            elif percent >= 90:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦⬛"
            elif percent >= 80:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦⬛⬛"
            elif percent >= 70:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦⬛⬛⬛"
            elif percent >= 60:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦⬛⬛⬛⬛"
            elif percent >= 50:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦⬛⬛⬛⬛⬛"
            elif percent >= 40:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦⬛⬛⬛⬛⬛⬛"
            elif percent >= 30:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
            elif percent >= 20:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
            elif percent >= 10:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
            else:
                qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
            quota = 0
            embed.add_field(name=f"{qm} {percent:.1f}% || {points}/{quota}", value="")
            if not data[4]:
                embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**", inline=False)
            else:
                embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**\nDays excused: **{data[4]}d**", inline=False)
        else:
            embed.add_field(name="", value="")
            embed.add_field(name="", value=f"Rank: {rank}\nPoints: **{points}**", inline=False)
        
        await interaction.response.send_message(embed=embed)


class overviewButtons(discord.ui.View):
    discord.ui.View.timeout = None
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.gray)
    async def PreviousButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        page, last_user_count = get_leaderboard_page(interaction.message.id)
        if page == 1:
            button.disabled = True
            return await interaction.response.defer()
        rows = get_users_amount(page-1)
        if(last_user_count <= page * 10):
            last_user_count -= 10 + (last_user_count-1) % 10
        else:
            last_user_count -= 20
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1): # added check for points >= 1
                user = bot.get_user(int(row[1]))
                if user:
                    member = bot.get_guild(DSBSeverID).get_member(user.id)
                    if member:
                        nickname = member.nick or user.name
                    else:
                        nickname = user.name
                else:
                    nickname = "User not found"
                user = str(last_user_count) + ". || " + str(nickname)
                embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1
        update_leaderboard(page - 1, last_user_count, interaction.message.id)
        page_u, last_user_count_u = get_leaderboard_page(interaction.message.id)
        embed.set_footer(text=f"Page {page_u}")
        await interaction.message.edit(embed=embed, view=overviewButtons())
        await interaction.response.defer()

    @discord.ui.button(emoji="<:dsbbotRefresh:1071533380581208146>", style=discord.ButtonStyle.gray)
    async def RefreshButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        page, last_user_count = get_leaderboard_page(interaction.message.id)
        rows = get_users_amount(page)
        last_user_count = (page - 1) * 10 + 1
        has_points = False
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1):
                has_points = True
                user = bot.get_user(int(row[1]))
                if user:
                    member = bot.get_guild(DSBSeverID).get_member(user.id)
                    if member:
                        nickname = member.nick or user.name
                    else:
                        nickname = user.name
                else:
                    nickname = "User not found"
                user = str(last_user_count) + ". || " + str(nickname)
                embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1
        if not has_points:
            embed.add_field(name="", value="***No point data over `0` found in `rows`.***")
        update_leaderboard(page, last_user_count, interaction.message.id)
        page_u, last_user_count_u = get_leaderboard_page(interaction.message.id)
        embed.set_footer(text=f"Page {page_u}")
        await interaction.message.edit(embed=embed, view=overviewButtons())
        await interaction.response.defer()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.gray)
    async def NextButton(self, interaction:discord.Interaction, button:discord.ui.Button):        
        page, last_user_count = get_leaderboard_page(interaction.message.id)
        if(last_user_count-1 < page * 10):
            button.disabled = True
            return await interaction.response.defer()
        rows = get_users_amount(page+1)
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1): # added check for points 
                user = bot.get_user(int(row[1]))
                if user:
                    member = bot.get_guild(DSBSeverID).get_member(user.id)
                    if member:
                        nickname = member.nick or user.name
                    else:
                        nickname = user.name
                else:
                    nickname = "User not found"
                user = str(last_user_count) + ". || " + str(nickname)
                embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1     
        update_leaderboard(page + 1, last_user_count, interaction.message.id)
        page_u, last_user_count_u = get_leaderboard_page(interaction.message.id)
        embed.set_footer(text=f"Page {page_u}")
        await interaction.message.edit(embed=embed, view=overviewButtons())
        await interaction.response.defer()
        
    @discord.ui.button(label="||", style=discord.ButtonStyle.gray, disabled=True)
    async def EmptyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass

    @discord.ui.button(emoji="ℹ️", style=discord.ButtonStyle.gray)
    async def InfoButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        embed.remove_footer()
        embed.title = f"Quota Summary - Block {blocknumber}"
        embed.description = f"Quota block {blocknumber} ends <t:{end_date}:R>. \n<t:{start_date}> - <t:{end_date}>"
        
        data = db_register_get_data(interaction.user.id)
        if data:
            if not data[4]:
                quota, rank = get_point_quota(interaction.user)
            else:
                quota, rank = get_point_quota(interaction.user)
                if quota is not None:
                    quota = int(quota - ((quota/14)*data[4]))

        completion_percentage = get_quota_completion_percentage()
        if completion_percentage > 200:
            qm = "🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟"
        elif completion_percentage >= 200:
            qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪"
        elif completion_percentage >= 190:
            qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟦"
        elif completion_percentage >= 180:
            qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟦🟦"
        elif completion_percentage >= 170:
            qm = "🟪🟪🟪🟪🟪🟪🟪🟦🟦🟦"
        elif completion_percentage >= 160:
            qm = "🟪🟪🟪🟪🟪🟪🟦🟦🟦🟦"
        elif completion_percentage >= 150:
            qm = "🟪🟪🟪🟪🟪🟦🟦🟦🟦🟦"
        elif completion_percentage >= 140:
            qm = "🟪🟪🟪🟪🟦🟦🟦🟦🟦🟦"
        elif completion_percentage >= 130:
            qm = "🟪🟪🟪🟦🟦🟦🟦🟦🟦🟦"
        elif completion_percentage >= 120:
            qm = "🟪🟪🟦🟦🟦🟦🟦🟦🟦🟦"
        elif completion_percentage >= 110:
            qm = "🟪🟦🟦🟦🟦🟦🟦🟦🟦🟦"
        elif completion_percentage >= 100:
            qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
        elif completion_percentage >= 90:
            qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦⬛"
        elif completion_percentage >= 80:
            qm = "🟦🟦🟦🟦🟦🟦🟦🟦⬛⬛"
        elif completion_percentage >= 70:
            qm = "🟦🟦🟦🟦🟦🟦🟦⬛⬛⬛"
        elif completion_percentage >= 60:
            qm = "🟦🟦🟦🟦🟦🟦⬛⬛⬛⬛"
        elif completion_percentage >= 50:
            qm = "🟦🟦🟦🟦🟦⬛⬛⬛⬛⬛"
        elif completion_percentage >= 40:
            qm = "🟦🟦🟦🟦⬛⬛⬛⬛⬛⬛"
        elif completion_percentage >= 30:
            qm = "🟦🟦🟦⬛⬛⬛⬛⬛⬛⬛"
        elif completion_percentage >= 20:
            qm = "🟦🟦⬛⬛⬛⬛⬛⬛⬛⬛"
        elif completion_percentage >= 10:
            qm = "🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛"
        else:
            qm = "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛"
        embed.add_field(name=f"Total quota completion:", value=f"{qm} {completion_percentage:.1f}% || {totalpoints_withoutPC()}/{totalquota_withoutPC()}")
        await interaction.message.edit(embed=embed, view=overviewButtons())
        await interaction.response.defer()

@pointsgroup.command(name="overview",description="Shows leaderboard for points.")
async def overview(interaction: discord.Interaction):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only DSB Private First Class or above may interact with DSB Helper."), ephemeral=True)
    else:
        gettingembed = discord.Embed(description="Getting data...")
        await interaction.response.send_message(embed=gettingembed)
        rows = get_users_amount(1)                                                                   
        embed = discord.Embed(title =f"Point Overview  -  Block {blocknumber}", description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nQuota block {blocknumber} ends <t:{end_date}:R>. \n<t:{start_date}> - <t:{end_date}>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color=DSBCommandsCOL)
        count = 1
        has_points = False
        embed.set_footer(text=f"Page 1")
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1):
                has_points = True
                user = bot.get_user(int(row[1]))
                if user:
                    member = bot.get_guild(DSBSeverID).get_member(user.id)
                    if member:
                        nickname = member.nick or user.name
                    else:
                        nickname = user.name
                else:
                    nickname = "User not found"
                user = str(count) + ". || " + str(nickname)
                embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                count += 1
        if not has_points:
            embed.add_field(name="", value="")
            embed.add_field(name="", value="*No point data found, it seems no one currently has any points.*")
        msg_sent = await interaction.edit_original_response(embed=embed, view=overviewButtons())
        add_leaderboard(interaction.user.id, msg_sent.id, count)

@pointsgroup.command(name="reset",description="Resets the points of all users to zero. [DSBPC+]")
async def reset(interaction:discord.Interaction):
    if not DSBPC_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to reset points!", description="You must be a member of DSBCOMM or above to reset the points.", color=ErrorCOL))
    else:
        await interaction.response.send_message(embed=discord.Embed(description="<:dsbbotUnderReview:1067970676041982053> Waiting for response..."))
        embed = discord.Embed(color=HRCommandsCOL, description=f"<:dsbbotUnderReview:1067970676041982053> **Are you sure you want to reset the points?**\nReact with <:dsbbotApproved:953642750039953418> to confirm.", colour=ErrorCOL)
        msg = await interaction.edit_original_response(embed=embed)
        await msg.add_reaction("<:dsbbotApproved:953642750039953418>")
        
        
        # Wait for the user's reaction
        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) == '<:dsbbotApproved:953642750039953418>'
        try:
            reaction, user_r = await bot.wait_for('reaction_add', check=check, timeout=10)
        except asyncio.TimeoutError:
            embed = discord.Embed(color=ErrorCOL, description=f"<:dsbbotFailed:953641818057216050> Timed out waiting for reaction.")
            tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
            await asyncio.gather(*tasks)

        else:
            if DSBPC_A(user_r):
                success = await reset_points()
                print(success)
                if success:
                    embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Point reset successful!", description=f"Set all points and days excused to 0.", color=discord.Color.green())
                    await interaction.edit_original_response(embed=embed)
                else:
                    embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Point reset failed!", description=f"Something went wrong...", color=ErrorCOL)
                    tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
                    await asyncio.gather(*tasks)

@bot.tree.command(name="mypoints",description="View your point count.")
async def mypoints(interaction: discord.Interaction):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only DSB Private First Class or above may interact with DSB Helper."), ephemeral=True)
    else:
        points = get_points(interaction.user.id)
        if points is False:
            return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No point data found!", description="You were not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL))
        else:            
            embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data found!")
            data = db_register_get_data(interaction.user.id)
            quota, rank = get_point_quota(interaction.user, data)
            if quota and onLoA(interaction.user) == False:
                percent = float(points / quota * 100)
                if percent > 200:
                    qm = "🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟"
                elif percent >= 200:
                    qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟪"
                elif percent >= 190:
                    qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟪🟦"
                elif percent >= 180:
                    qm = "🟪🟪🟪🟪🟪🟪🟪🟪🟦🟦"
                elif percent >= 170:
                    qm = "🟪🟪🟪🟪🟪🟪🟪🟦🟦🟦"
                elif percent >= 160:
                    qm = "🟪🟪🟪🟪🟪🟪🟦🟦🟦🟦"
                elif percent >= 150:
                    qm = "🟪🟪🟪🟪🟪🟦🟦🟦🟦🟦"
                elif percent >= 140:
                    qm = "🟪🟪🟪🟪🟦🟦🟦🟦🟦🟦"
                elif percent >= 130:
                    qm = "🟪🟪🟪🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 120:
                    qm = "🟪🟪🟦🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 110:
                    qm = "🟪🟦🟦🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 100:
                    qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 90:
                    qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦⬛"
                elif percent >= 80:
                    qm = "🟦🟦🟦🟦🟦🟦🟦🟦⬛⬛"
                elif percent >= 70:
                    qm = "🟦🟦🟦🟦🟦🟦🟦⬛⬛⬛"
                elif percent >= 60:
                    qm = "🟦🟦🟦🟦🟦🟦⬛⬛⬛⬛"
                elif percent >= 50:
                    qm = "🟦🟦🟦🟦🟦⬛⬛⬛⬛⬛"
                elif percent >= 40:
                    qm = "🟦🟦🟦🟦⬛⬛⬛⬛⬛⬛"
                elif percent >= 30:
                    qm = "🟦🟦🟦⬛⬛⬛⬛⬛⬛⬛"
                elif percent >= 20:
                    qm = "🟦🟦⬛⬛⬛⬛⬛⬛⬛⬛"
                elif percent >= 10:
                    qm = "🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛"
                else:
                    qm = "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛"
                embed.add_field(name=f"{qm} {percent:.1f}% || {points}/{quota}", value="")
                if not data[4]:
                    embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**", inline=False)
                else:
                    embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**\nDays excused: **{data[4]}d**", inline=False)
            elif quota and onLoA(interaction.user):
                percent = float(points / quota * 100)
                if percent > 200:
                    qm = "🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟"
                elif percent >= 200:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟪🟪🟪"
                elif percent >= 190:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟪🟪🟦"
                elif percent >= 180:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟪🟦🟦"
                elif percent >= 170:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟪🟦🟦🟦"
                elif percent >= 160:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟪🟦🟦🟦🟦"
                elif percent >= 150:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟪🟦🟦🟦🟦🟦"
                elif percent >= 140:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟪🟦🟦🟦🟦🟦🟦"
                elif percent >= 130:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 120:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 110:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 100:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦🟦"
                elif percent >= 90:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦🟦⬛"
                elif percent >= 80:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦🟦⬛⬛"
                elif percent >= 70:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦🟦⬛⬛⬛"
                elif percent >= 60:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦🟦⬛⬛⬛⬛"
                elif percent >= 50:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦🟦⬛⬛⬛⬛⬛"
                elif percent >= 40:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:🟦⬛⬛⬛⬛⬛⬛"
                elif percent >= 30:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
                elif percent >= 20:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
                elif percent >= 10:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
                else:
                    qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:⬛⬛⬛⬛⬛⬛⬛"
                quota = 0
                embed.add_field(name=f"{qm} {percent:.1f}% || {points}/{quota}", value="")
                if not data[4]:
                    embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**", inline=False)
                else:
                    embed.add_field(name="", value=f"\n\nRank: **{rank}**\nPoints: **{points}**\nDays excused: **{data[4]}d**", inline=False)
            else:
                embed.add_field(name="", value="")
                embed.add_field(name="", value=f"Rank: {rank}\nPoints: **{points}**", inline=False)
            await interaction.response.send_message(embed=embed)





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
            embed = discord.Embed(title="**<:DSB:1060271947725930496> DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.\n*Board is still outdated, command wise.*", color=DSBCommandsCOL)
            embed.add_field(name="Credits", value="- Main developer: Blue\n- Bot host: Orange\n- Frontend Design: Shush & Polish\n- Bot testing: the suffering + Polish")
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
    embed = discord.Embed(title="**DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.\n*Board is still outdated, command wise.*", color=DSBCommandsCOL)
    embed.add_field(name="Credits", value="- Main developer: Blue\n- Bot host: Orange\n- Frontend Design: Shush & Polish\n- Bot testing: the suffering + Polish")
    embed.set_footer(text="DSB Helper v.idk")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/lnHKwZ40MRhYKuNJpNUS8NQiaekqkgfW9TaGj-B5Yg0/https/tr.rbxcdn.com/580b2e0cd698decfa585464b50a4278c/150/150/Image/Png")
    await interaction.response.send_message(embed=embed, view=InfoboardView())

@bot.tree.command(name="soup",description="Gives/revokes the Op. Supervisor Role. [EDS+]")
async def soup(interaction:discord.Interaction):
    if not FMR_A(interaction.user):
        return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"You must be DSB Elite Defense Specialist+ to use this command."))
    else:
        role_name = "[DSB] Operation Supervisors"
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role in interaction.user.roles:
            try:
                await interaction.user.remove_roles(role)
                embed = discord.Embed(color=DSBCommandsCOL, description=f"<:dsbbotSuccess:953641647802056756> Role successfully removed.")
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                print(e)
                embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to remove the role.")
                await interaction.response.send_message(embed=embed)
        else:
            try:
                await interaction.user.add_roles(role)
                embed = discord.Embed(color=DSBCommandsCOL, description=f"<:dsbbotSuccess:953641647802056756> Role successfully added.")
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                print(e)
                embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to add the role.")
                await interaction.response.send_message(embed=embed)

@bot.tree.command(name="whois",description="Displays a user's information.")
async def whois(interaction: discord.Interaction, user:discord.Member=None):
        roles = []
        if user is None:
            user = interaction.user
        for role in user.roles:
            if role.name == '@everyone':
                continue
            roles.append(str(role.mention))
        roles.reverse()
        ct = user.created_at.strftime("%a, %d %b, %Y | %H:%M")
        jt = user.joined_at.strftime("%a, %d %b %Y | %H:%M")
        if user:
            embed=discord.Embed(description=f"{user.mention}  •  ID: {user.id}",color=BasiccommandCOL)
        embed.set_author(icon_url=user.avatar, name=f"{user}'s User Info")
        embed.set_thumbnail(url=user.avatar)
        #embed.set_footer(text=f'ID: {user.id}')
        embed.add_field(name="Joined Server On:", value=jt,inline=True)
        embed.add_field(name="Created Account On:", value=ct,inline=True)
        if len(str(" | ".join([x.mention for x in user.roles]))) > 1024:
            embed.add_field(name=f"Roles[{len(user.roles)}]:", value="Too many to display.", inline=False)
        else:
            role_count = len([role for role in user.roles if role.name != '@everyone'])
            embed.add_field(name=f"Roles[{role_count}]:", value=" | ".join(roles),inline=False)   
        #embed.add_field(name="Bot:", value=f'{("Yes" if user.bot==True else "No")}',inline=False)
        await interaction.response.send_message(embed=embed)
    
@bot.tree.command(name="ping",description="Shows the bot's response time.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓Pong! Took `{round(bot.latency * 1000)}`ms")





bot.run(config["bot_token"])