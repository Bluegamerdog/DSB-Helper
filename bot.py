import asyncio
import json
import os
import platform
import re
import sys
import time
import random

import discord
from colorama import Back, Fore, Style
from discord import app_commands
from discord.ext import commands

from database import *


config_file = open("config.json")
config = json.load(config_file)

bot = commands.Bot(command_prefix=">", intents=discord.Intents().all(),help_command=None)
tree = app_commands.CommandTree(discord.Client(intents=discord.Intents().all()))

def quota_get():
    global start_date
    global end_date
    global blocknumber
    start_date, end_date, blocknumber = get_quota()

##### EMBED COLORS ####
global BasiccommandCOL
global UserCommandsCOL
global HRCommandsCOL
global ErrorCOL
BasiccommandCOL = 0xFFFFFF
UserCommandsCOL = 0x0B0B45
HRCommandsCOL = 0x000000
ErrorCOL = 0xB3202C


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
    print(prfx + f"|| QUOTA BLOCK it set to: {start_date} | {end_date} | {blocknumber}")
    #Embed#
    embed = discord.Embed(title="Bot Startup Info • MainBot", color=discord.Color.green())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Runtime Information", value=f"Discord Version: {discord.__version__} || Python Version: {platform.python_version()}", inline=False)
    embed.add_field(name="Synced Slash Commands", value=len(synced), inline=False)
    embed.add_field(name="--------------------NOTES--------------------", value="", inline=False)
    if start_date != None and end_date != None and blocknumber != None:
        embed.add_field(name="", value=f"Quota set: S:{start_date} | E:{end_date} | B:{blocknumber}")
        quota = True
        notes = True
    if quota != True:
        embed.add_field(name="", value="Quota not set, please check the databse.")
    if notes != True:
        embed.add_field(name="", value="N/A")
    channel = bot.get_channel(1069974021246046310)  # Replace channel_id with the ID of the channel you want to send the message to
    await channel.send(embed=embed)

@bot.event
async def on_reaction_add(reaction, user):
    if(reaction.emoji == u"\u25B6") and user.id != bot.user.id:
        page, last_user_count = get_leaderboard_page(user.id, reaction.message.id)
        if(last_user_count < page * 10):
            return
        rows = get_users(page+1)
        if end_date == "" or start_date == "" or blocknumber == "":
            embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"-----------------------------------------------\nCurrent quota block has not yet been set up. \nPlease ping a member of DSBPC+.\n-----------------------------------------------", color=UserCommandsCOL)
        else:
            embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n| <t:{start_date}> - <t:{end_date}> |\n----------------------------------------------------------", color=UserCommandsCOL)
        for row in rows:
            if(row[1] != None and row[2] != None and row[2] >= 1): # added check for points >= 1
                user = bot.get_user(int(row[1]))
                user = "#" + str(last_user_count) + " | " + str(user.display_name)
                embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
                last_user_count += 1
        
        update_leaderboard(page + 1, last_user_count, reaction.message.id)
        await reaction.message.edit(embed = embed)
        await reaction.message.clear_reactions()
        await reaction.message.add_reaction(u"\u25C0")
        if(last_user_count > (page+1) * 10):
            await reaction.message.add_reaction(u"\u25B6")
    
    if(reaction.emoji == u"\u25C0") and user.id != bot.user.id:
        page, last_user_count = get_leaderboard_page(user.id, reaction.message.id)
        if(page == 1):
            return
        rows = get_users(page-1)
        if end_date == "" or start_date == "" or blocknumber == "":
            embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"-----------------------------------------------\nCurrent quota block has not yet been set up. \nPlease ping a member of DSBPC+.\n-----------------------------------------------", color=UserCommandsCOL)
        else:
            embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n| <t:{start_date}> - <t:{end_date}> |\n----------------------------------------------------------", color=UserCommandsCOL)
        if(last_user_count <= page * 10):
            last_user_count -= 10 + (last_user_count-1) % 10
        else:
            last_user_count -= 20
        
        
        for row in rows:
            if(row[1] != None and row[2] != None and row[2] >= 1): # added check for points >= 1
                user = bot.get_user(int(row[1]))
                user = "#" + str(last_user_count) + " | " + str(user.display_name)
                embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
                last_user_count += 1
        
        
        update_leaderboard(page - 1, last_user_count, reaction.message.id)
        await reaction.message.edit(embed = embed)
        await reaction.message.clear_reactions()
        if(page - 1 > 1):
            await reaction.message.add_reaction(u"\u25C0")
        await reaction.message.add_reaction(u"\u25B6")

def authorizationalpha(user): # function to check if user is DSBPC+ 
    roles = user.roles
    for role in roles:
        if role.name in ["QSO Pre-Command", "QSO Command", "DSB Command", "Orange"] or role.permissions.administrator:
            return True
    return False

def authorizationz(user): # function to check if user is DSBPC+ 
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def mrs(user): # function to check if user is MR+
    roles = user.roles
    for role in roles:
        if role.name in ["Elite Defense Specialist", "Master Sergeant", "[DSB] Squadron Officer", "DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def allmrs(user):
    roles = user.roles
    for role in roles:
        if role.name in ["Elite Defense Specialist", "Master Sergeant", "[DSB] Squadron Officer", "DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False
        
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


            
 ## MANEGEMENT COMMANDS ##

@bot.tree.command(description="Restarts the DSB Helper. [DSBPC+]")
async def restart(interaction:discord.Interaction):
    user = interaction.user
    if authorizationz(user):
        embed=discord.Embed(color=0xb08102, description="DSB Helper restarting...")
        await interaction.response.send_message(embed=embed)
        print(f"------------------------------------\nBOT RESTARTED BY {user}\n------------------------------------")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        embed = discord.Embed(color=ErrorCOL, description="You are not permitted to use this command.")
        await interaction.response.send_message(embed=embed)
        
@bot.tree.command(name="shutdown", description="Shuts down DSB Helper [DSBCOMM+]")
async def shutdown(interaction:discord.Interaction):
    user = interaction.user
    if authorizationalpha(user):
        embed = discord.Embed(color=ErrorCOL, description="DSB Helper shutting down...")
        await interaction.response.send_message(embed=embed)
        print(f"------------------------------------\nBOT CLOSED BY {user}\n------------------------------------")
        await bot.close()
    else:
        embed = discord.Embed(color=ErrorCOL, description="You are not permitted to use this command.")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="watching", description=":lo:")
async def change_status(interaction: discord.Interaction, user:discord.Member=None):
    if user == None:
        members = bot.guilds[0].members
        random_member = random.choice(members)
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{random_member.display_name}")
        await bot.change_presence(activity=activity)
        await interaction.response.send_message("Status updated, watching randomized", ephemeral=True)
    else:
        activity = discord.Activity(type=discord.ActivityType.watching, name=f"{user.display_name}")
        await bot.change_presence(activity=activity)
        await interaction.response.send_message(f"Status updated, watching {user.display_name}", ephemeral=True)

@bot.tree.command(name="message",description="Blue's command...")
async def custom_message(interaction:discord.Interaction, channel:discord.TextChannel, message:str):
    allowed_ids = [776226471575683082, 395505414000607237, 1053377038490292264] # Blue, Orange and Shush
    if interaction.user.id in allowed_ids:
        await channel.send(f"{message}")
        await interaction.response.send_message("Done", ephemeral=True)
    else:
        await interaction.response.send_message("You did something wrong...", ephemeral=True)

## POINTS GROUP ##
class PointsGrp(app_commands.Group):
    pass

pointsgroup = PointsGrp(name="points")
bot.tree.add_command(pointsgroup)

@pointsgroup.command(name="add", description="Adds points to a user. [DSBPC+]")
async def add(interaction:discord.Interaction, username:discord.Member, point:int):
    user = interaction.user
    if(not authorizationz(user)): # check if user has permission
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to add points.")
        await interaction.response.send_message(embed=embed)
        return
    if(type(point)==int):
        username_id = username.id
        add_points(username_id, point) # add points to the user

        if int(point) <= 1: # check if the point is singular or plural
            embed = discord.Embed(color=HRCommandsCOL, description=f"Added {point} point to {username.mention}")
        else:
            embed = discord.Embed(color=HRCommandsCOL, description=f"Added {point} points to {username.mention}")
        await interaction.response.send_message(embed=embed) # respond with the result
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"Invalid point number.")
        await interaction.response.send_message(embed=embed) # respond with the result     
    
@pointsgroup.command(name="remove", description="Removes points from a user. [DSBPC+]")
async def remove(interaction:discord.Interaction,username:discord.Member,point:int):
    user = interaction.user
    if(not authorizationz(user)): # Check if user has permission to remove points
        #await request_points(ctx)
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to remove points.")
        await interaction.response.send_message(embed=embed)
        return
    if(type(point)==int):
        username_id = username.id
        remove_points(username_id, point) #removes points from user
        if int(point) <= 1: #checks if points is singular or plural
            embed = discord.Embed(color=HRCommandsCOL, description=f"Removed {point} point from {username.mention}")
        else:
            embed = discord.Embed(color=HRCommandsCOL, description=f"Removed {point} points from {username.mention}")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"Invalid point number.")
        await interaction.response.send_message(embed=embed)
        
@pointsgroup.command(name="view",description="View someone else's current point count.")
async def view(interaction: discord.Interaction, user:discord.Member):
    points = get_user_points(user.id)
    if points:
        if points == 1:
            embed = discord.Embed(color=UserCommandsCOL, description=f"{user.mention} has {points} point.")
        elif points:
            embed = discord.Embed(color=UserCommandsCOL, description=f"{user.mention} has {points} points.")
    else:
        embed = discord.Embed(color=UserCommandsCOL, description=f"{user.mention} has no points.")
    await interaction.response.send_message(embed=embed)
    
@pointsgroup.command(name="overview",description="Shows leaderboard for points.")
async def overview(interaction: discord.Interaction):
    gettingembed = discord.Embed(description="Getting data...")
    await interaction.response.send_message(embed=gettingembed)
    rows = get_users(1)
    embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n| <t:{start_date}> - <t:{end_date}> |\n----------------------------------------------------------", color=UserCommandsCOL)
    count = 1
    for row in rows:
        if(row[1] != None and row[2] != None and row[2] >= 1): # added check for points >= 1
            user = bot.get_user(int(row[1]))
            user = "#" + str(count) + " | " + str(user.name)
            embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
            count += 1
    msg_sent = await interaction.edit_original_response(embed=embed)
    add_leaderboard(interaction.user.id, msg_sent.id, count)
    if(count >= 11):
        await msg_sent.add_reaction(u"\u25B6")

@pointsgroup.command(name="reset",description="Resets the points of all users to zero. [DSBPC+]")
async def reset(interaction:discord.Interaction):
    user = interaction.user
    if authorizationz(user):
        # Send a message asking the user to confirm the reset
        embed = discord.Embed(color=HRCommandsCOL, description=f"Are you sure you want to reset the points? Respond with 'yes' to confirm.")
        await interaction.response.send_message(embed=embed)
        
        # Wait for the user's response
        def check(m):
            return m.content == 'yes' and m.channel == interaction.channel and m.author == interaction.user
        try:
            response = await bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            embed = discord.Embed(color=ErrorCOL, description=f"Timed out waiting for response.")
            await response.reply(embed=embed)
        else:
            if response.content == 'yes':
                if authorizationz(response.author):
                    await reset_database()
                    embed = discord.Embed(color=HRCommandsCOL, description=f"Point reset successful.")
                    await response.reply(embed=embed)
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to use this command.")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mypoints",description="View your point count.")
async def mypoints(interaction: discord.Interaction):
    points = get_user_point(interaction.user.id)
    if points:
        if points == 1:
            embed = discord.Embed(color=UserCommandsCOL, description=f"You have {points} point.")
        elif points:
            embed = discord.Embed(color=UserCommandsCOL, description=f"You have {points} points!",)
    else:
        embed = discord.Embed(color=UserCommandsCOL, description=f"You have no points.")
    await interaction.response.send_message(embed=embed)

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
        #await interaction.response.send_message(f'You chose {self.values[0]}.')
        if self.values[0] == "DHI":
            embed = discord.Embed(title="**DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=UserCommandsCOL)
            embed.add_field(name="Credits", value="Bluegamerdog - Backend API and bot host\nObviously_Shush - Frontend & Misc\nThe suffering - Bug testing")
            embed.set_footer(text="DSB Helper 1.0")
            embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/lnHKwZ40MRhYKuNJpNUS8NQiaekqkgfW9TaGj-B5Yg0/https/tr.rbxcdn.com/580b2e0cd698decfa585464b50a4278c/150/150/Image/Png")
        elif self.values[0] == "BC":
            embed = discord.Embed(title="**Basic Commands**", description="All servers members can use these commands. They are represented by the color white.", color=BasiccommandCOL)
            embed.add_field(name="**/whois**", value="Displays someones general and server informations.", inline=False)
            embed.add_field(name="**/ping**", value="Shows the bot's response time in miliseconds.", inline=False)
        elif self.values[0] == "DC":
            embed = discord.Embed(title="**DSB Commands**", description="All DSB members PFC and above have access to these and are represented by the navy blue.", color=UserCommandsCOL)
            embed.add_field(name="**/points overview**", value="Displays a leaderboard for points.", inline=False)
            embed.add_field(name="**/points view**", value="View someone else's current point count.", inline=False)
            embed.add_field(name="**/mypoints**", value="View your current point count.", inline=False)
            embed.add_field(name="**/soup**", value="Adds or removes the Op. Supervisor Role. [EDS+]", inline=False)
            embed.add_field(name="**/rloa**", value="Coming soon:tm:...", inline=False)
        elif self.values[0] == "MC":
            embed = discord.Embed(title="**Management Commands**", description="DSB Pre-Command and above have access to these. They are represented by the color black.", color=HRCommandsCOL)
            embed.add_field(name="**/points add/remove**", value="Adds/removes points to/from a user.", inline=False)
            embed.add_field(name="**/pointsreset**", value="Resets the points of all users to zero.", inline=False)
            embed.add_field(name="**/updatequota**", value="Updates the quota block number, start and end date.", inline=False)
            embed.add_field(name="**/restart**", value="Restarts the DSB Helper.", inline=False)
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
    embed = discord.Embed(title="**DSB Helper Infoboard**", description="The DSB Helper mainly manages the points based quota system. Provided are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=UserCommandsCOL)
    embed.add_field(name="Credits", value="Bluegamerdog - Backend API\nOrangePurgatory - Temporary bot host\nObviously_Shush - Frontend & Misc\nThe suffering - Bug testing")
    embed.set_footer(text="DSB Helper 1.0")
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/lnHKwZ40MRhYKuNJpNUS8NQiaekqkgfW9TaGj-B5Yg0/https/tr.rbxcdn.com/580b2e0cd698decfa585464b50a4278c/150/150/Image/Png")
    await interaction.response.send_message(embed=embed, view=InfoboardView())
    
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

@bot.tree.command(name="updatequota",description="Updates the quota block start to end date. [DSBPC+]")
async def updatequota(interaction:discord.Interaction, start_date_new: int, end_date_new: int, blocknumber_new: int):
    user = interaction.user
    
    if authorizationz(user):
        update_quota(start_date_new, end_date_new, blocknumber_new)
        embed = discord.Embed(color=HRCommandsCOL, title="Quota block change")
        embed.add_field(name="From:", value=f"<t:{start_date}> - <t:{end_date}> || Block {blocknumber}", inline=False)
        embed.add_field(name="To:", value=f"<t:{start_date_new}> - <t:{end_date_new}> || Block {blocknumber_new}", inline=False)
        await interaction.response.send_message(embed=embed)
        quota_get()
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to run this command.")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="soup",description="Adds or removes the Op. Supervisor Role. [EDS+]")
async def soup(interaction:discord.Interaction):
    user = interaction.user
    role_name = "[DSB] Operation Supervisors"
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    
    if mrs(user)==False:
        embed = discord.Embed(color=UserCommandsCOL, description=f"You need to be EDS+ to use this command.")
        await interaction.response.send_message(embed=embed)
    else:
        if role in interaction.user.roles:
            try:
                await interaction.user.remove_roles(role)
                embed = discord.Embed(color=UserCommandsCOL, description=f"Role successfully removed.")
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                print(e)
                embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to remove the role.")
                await interaction.response.send_message(embed=embed)
        else:
            try:
                await interaction.user.add_roles(role)
                embed = discord.Embed(color=UserCommandsCOL, description=f"Role successfully added.")
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                print(e)
                embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to add the role.")
                await interaction.response.send_message(embed=embed)





bot.run(config["bot_token"])