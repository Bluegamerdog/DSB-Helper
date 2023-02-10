import asyncio
import json
import os
import platform
import re
import sys
import time
import random
import datetime
import string

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

async def format_user(user_name):
    for i in range(len(user_name)):
        if(user_name[i] != ' '):
            break
        else:
            user_name = user_name[1:]
            
    for i in user_name[::-1]:
        if(i != " "):
            break
        else:
            user_name = user_name[:-1]    
    return user_name
    


##### EMBED COLORS ####
global BasiccommandCOL
global DSBCommandsCOL
global HRCommandsCOL
global ErrorCOL
global SuccessCOL
BasiccommandCOL = 0xFFFFFF
DSBCommandsCOL = 0x0B0B45
HRCommandsCOL = 0x000000
ErrorCOL = 0xB3202C
SuccessCOL = 0x4BB543

DSBSeverID = 949470602366976051
SupportServerID = 953638901677973554
global watching_command
watching_command = True

def get_vc_id(key):
    data = {
        "O1": 937473342884179980,
        "O2": 937473342884179981,
        "O3": 937473342884179982,
        "O4": 937473342884179983,
        "O5": 937473342884179984,
        "VIP": 937473342884179985,
        "QE": 992865433059340309,
        "D1": 949869157552390154,
        "D2": 949869187168370718,
        "D3": 949869232663986226,
        "DE": 950145200087511130,
        "C1": 949470602366976055,
        "C2": 949867772643520522,
        "C3": 949867813789630574,
        "CE": 950145105040388137,
        "MAIN": 939964909205192804
    }
    return data.get(key, None)

@bot.event
async def on_ready():
    #await bot.change_presence(activity=discord.Activity(type=discord.CustomActivity(name="Spying on OSA...")))
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
        if role.name in ["DSB"] or role.permissions.administrator and role.name not in ["DSB Private"]:
            return True
    return False

def DEVACCESS(user):
    allowed_ids = [776226471575683082, 395505414000607237, 1053377038490292264] # Blue, Orange and Shush
    if user.id in allowed_ids or user.guild_permissions.administrator:
        return True
    return False

@bot.event
async def on_message(message):
    if message.content.lower() == "lmfao":
        await message.reply("Who is Lmfao? 🤨\nHe's a hacker, he's a Chinese hacker.\nLmfao, he's working for the Koreans isn't he?")

@bot.event
async def on_reaction_add(reaction, user):
    #next 
    if(reaction.emoji == u"\u25B6") and user.id != bot.user.id:
        page, last_user_count = get_leaderboard_page(reaction.message.id)
        if(last_user_count < page * 10):
            return
        rows = get_users_amount(page+1)
        embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n<t:{start_date}> - <t:{end_date}>\n----------------------------------------------------------", color=DSBCommandsCOL)
        has_points = False
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
                user = "#" + str(last_user_count) + " | " + str(nickname)
                embed.add_field(name = user, value = '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1       
        update_leaderboard(page + 1, last_user_count, reaction.message.id)
        await reaction.message.edit(embed = embed)
        await reaction.message.clear_reactions()
        await reaction.message.add_reaction(u"\u25C0")
        await reaction.message.add_reaction("<:dsbbotRefresh:1071533380581208146>")
        if(last_user_count > (page+1) * 10):
            await reaction.message.add_reaction(u"\u25B6")
    
    # Refresh
    if(str(reaction.emoji) == '<:dsbbotRefresh:1071533380581208146>') and user.id != bot.user.id:
        page, last_user_count = get_leaderboard_page(reaction.message.id)
        rows = get_users_amount(page)
        embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n<t:{start_date}> - <t:{end_date}>\n----------------------------------------------------------", color=DSBCommandsCOL)
        last_user_count = (page - 1) * 10 + 1
        
        has_points = False
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1): # added check for points >= 1
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
                user = "#" + str(last_user_count) + " | " + str(nickname)
                embed.add_field(name = user, value = '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1
        if not has_points and last_user_count == 1:
            embed.add_field(name="", value="")
            embed.add_field(name="", value="*<:dsbbotCaution:1067970676041982053> No point data found, it seems no one currently has any points.*")
        
        update_leaderboard(page, last_user_count, reaction.message.id)
        await reaction.message.edit(embed = embed)
        await reaction.message.clear_reactions()
        if(page > 1):
            await reaction.message.add_reaction(u"\u25C0")
            await reaction.message.add_reaction("<:dsbbotRefresh:1071533380581208146>")
        elif(last_user_count > (page) * 10):
            await reaction.message.add_reaction("<:dsbbotRefresh:1071533380581208146>")
            await reaction.message.add_reaction(u"\u25B6")
        else:
            await reaction.message.add_reaction("<:dsbbotRefresh:1071533380581208146>")
        
    # Prev
    if(reaction.emoji == u"\u25C0") and user.id != bot.user.id:
        page, last_user_count = get_leaderboard_page(reaction.message.id)
        if(page == 1):
            return
        rows = get_users_amount(page-1)
        embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n<t:{start_date}> - <t:{end_date}>\n----------------------------------------------------------", color=DSBCommandsCOL)
        if(last_user_count <= page * 10):
            last_user_count -= 10 + (last_user_count-1) % 10
        else:
            last_user_count -= 20
        
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
                user = "#" + str(last_user_count) + " | " + str(nickname)
                embed.add_field(name = user, value = '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1
        update_leaderboard(page - 1, last_user_count, reaction.message.id)
        await reaction.message.edit(embed = embed)
        await reaction.message.clear_reactions()
        if(page - 1 > 1):
            await reaction.message.add_reaction(u"\u25C0")
        await reaction.message.add_reaction("<:dsbbotRefresh:1071533380581208146>")
        await reaction.message.add_reaction(u"\u25B6")
        
    
    if str(reaction.emoji) == "<:dsbbotSuccess:953641647802056756>" and reaction.message.channel.id == 983194737882312714 and DSBPC_A(reaction.user):
        role_name = "On LoA"
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
    elif status_type == "w_disable":
        watching_command = False
        return await interaction.response.send_message(f"`/watching` command is now disabled ({watching_command})", ephemeral=True)
    elif status_type == "w_enable":
        watching_command = True
        return await interaction.response.send_message(f"`/watching` command is now enabled ({watching_command})", ephemeral=True)
    elif status_type == "remove":
        await bot.change_presence(activity=None)
        return await interaction.response.send_message("Cleared activity.", ephemeral=True)
    else:
        return await interaction.response.send_message("**Invalid status type, choose from:** `playing`, `streaming`, `listening`, `watching`, `w_disable`, `w_enable` or `remove`", ephemeral=True)

#MISC MANEGMENT# 
@bot.tree.command(name="watching", description=":lo:")
async def change_status(interaction: discord.Interaction, user:discord.Member=None):
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
    if not DSBCOMM_A(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to purge regirty!", description="You must be a member of DSBCOMM or above to purge the registry database.", color=ErrorCOL))

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
            if DSBCOMM_A(user_r):
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

class requestButtons(discord.ui.View):
    def __init__(self, amount:int):
        super().__init__()
        self.amount = amount
    
    @discord.ui.button(emoji="<:dsbbotAccept:1073668738827694131>", label="Accept", style=discord.ButtonStyle.grey)
    async def AcceptButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not DSBPC_A(interaction.user):
            return
        else:
            try:
                add_points(interaction.message.interaction.user.id, self.amount)
                embed = interaction.message.embeds[0]
                embed.title=f"<:dsbbotSuccess:953641647802056756> Point Request - {interaction.message.interaction.user.display_name}"
                embed.color=SuccessCOL
                await interaction.message.edit(embed=embed, view=None)
                embed=discord.Embed(color=SuccessCOL,title="<:dsbbotAccept:1073668738827694131> Point Request Accepted!", description=f"Your point request has been **accepted** and {self.amount} points have been added. You now have **{get_points(interaction.message.interaction.user.id)}** points.  😎")
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
            embed.title=f"<:dsbbotFailed:953641818057216050> Point Request - {interaction.message.interaction.user.display_name}"
            embed.color=ErrorCOL
            await interaction.message.edit(embed=embed, view=None)
            embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Point Request Denied!", description=f"Your point request has been **denied**. The person who reviewed it will provide you with the reason shortly.  😄")
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)
            
    @discord.ui.button(emoji="❌", label="Cancel", style=discord.ButtonStyle.grey)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user == interaction.message.interaction.user:
            embed = interaction.message.embeds[0]
            embed.title="<:dsbbotFailed:953641818057216050> Cancelled Point Request!"
            embed.remove_field(1)
            embed.remove_field(2)
            embed.remove_field(3)
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Cancelled by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            embed.color=HRCommandsCOL
            await interaction.message.edit(embed=embed, view=None)
        else:
            return
            
    

@pointsgroup.command(name="request", description="Used to request points.")
async def request(interaction:discord.Interaction, amount:int, log:str):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only DSB Private First Class or above may interact with DSB Helper."), ephemeral=True)
    if not db_register_get_data(interaction.user.id):
        return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Interaction failed!", description="You were not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL), ephemeral=True)   
    message_link_pattern = re.compile(r"https://(?:ptb\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)")
    if not message_link_pattern.match(log):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid log!", description=f"Input `log` must be a Discord message link."), ephemeral=True)
    if not amount >=1:
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid amount!", description=f"The requested amount of points must be **greater than 1**."), ephemeral=True)
    else:
        embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotUnderReview:953642762857771138> Point Request - {interaction.user.display_name}")
        embed.add_field(name="", value="")
        embed.add_field(name="", value=f"**{interaction.user.display_name}** has requested **{amount}** points.\n\n**`Log:`** {log}", inline=False)
        await interaction.response.send_message(embed = embed, view=requestButtons(amount))


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
    elif user == interaction.user or user == None:
        user = interaction.user
        points = get_points(user.id)
        if points is False:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No point data found!", description="You are not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL)
        elif points:
            embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data found!", description=f"**You** have **{points}** point." if points == 1 else f"**You** have **{points}** points.")

    else:
        if not user:
            user = interaction.user
        points = get_points(user.id)
        if points is False:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No point data found for `{user}`!", description="User not found in registry database.", color=ErrorCOL)
        elif points:
            embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data found for `{user}`!", description=f"**{user.display_name}** has **{points}** point." if points == 1 else f"**{user.display_name}** has **{points}** points.")
    await interaction.response.send_message(embed=embed)

@pointsgroup.command(name="overview",description="Shows leaderboard for points.")
async def overview(interaction: discord.Interaction):
    if not DSBMEMBER(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only DSB Private First Class or above may interact with DSB Helper."), ephemeral=True)
    else:
        gettingembed = discord.Embed(description="Getting data...")
        await interaction.response.send_message(embed=gettingembed)
        rows = get_users_amount(1)                                                                   
        embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n<t:{start_date}> - <t:{end_date}>\n----------------------------------------------------------", color=DSBCommandsCOL)
        count = 1
        has_points = False
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
                user = "#" + str(count) + " | " + str(nickname)
                embed.add_field(name = user, value = '{:,}'.format(int(row[3])), inline=False)
                count += 1
        if not has_points and count == 1:
            embed.add_field(name="", value="")
            embed.add_field(name="", value="*<:dsbbotCaution:1067970676041982053> No point data found, it seems no one currently has any points.*")
        msg_sent = await interaction.edit_original_response(embed=embed)
        add_leaderboard(interaction.user.id, msg_sent.id, count)
        await msg_sent.add_reaction("<:dsbbotRefresh:1071533380581208146>")
        if(count >= 11):
            await msg_sent.add_reaction(u"\u25B6")

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
            if DSBCOMM_A(user_r):
                success = await reset_points()
                print(success)
                if success:
                    embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Point reset successful!", description=f"Set all points to `0`", color=discord.Color.green())
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
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No point data found!", description="You are not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL)
        elif points:
            embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data found!", description=f"**You** have **{points}** point." if points == 1 else f"**You** have **{points}** points.")
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
            embed = discord.Embed(title="**<:DSB:1060271947725930496> DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=DSBCommandsCOL)
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
    embed = discord.Embed(title="**DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=DSBCommandsCOL)
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