import asyncio
import json
import re
import sqlite3
import sys
import os
import time

import discord
from discord import app_commands
from discord.ext import commands

#import google.auth
#from google.auth.transport.requests import Request
#from google.oauth2.credentials import Credentials
#from googleapiclient.discovery import build

from database import *

config_file = open("config.json")
config = json.load(config_file)

bot = commands.Bot(command_prefix=">", intents=discord.Intents().all(),help_command=None)
tree = app_commands.CommandTree(discord.Client(intents=discord.Intents().all()))

global start_date
global end_date
global blocknumeber
blocknumber = "N/A"
start_date = "N/A"
end_date = "N/A"

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
    print("MAINBOT READY")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    print("Remember to set quotablock")


def authorizationalpha(user): # function to check if user is DSBPC+ 
    roles = user.roles
    for role in roles:
        if role.name in ["QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
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

@bot.event
async def on_message_edit(before, after):
    if(check_requests(after.id)):
        update_requests(after.id, -1)

@bot.event
async def on_command_error(ctx, error):
    try:
        #await request_points(ctx)
        pass
    except Exception as e:
        print("Some shit happened: " + str(error))
        print("Error from try catch : " + str(e))
        
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

'''
@bot.event
async def on_reaction_add(reaction, user):
    if(check_leaderboard(reaction.message.id, user.id)):
        if(reaction.emoji == u"\u25B6"):
            page, last_user_count = get_leaderboard_page(reaction.message.id, user.id)
            if(last_user_count < page * 10):
                return
            rows = get_users(page+1)
            if end_date == "" or start_date == "" or blocknumber == "":
                embedinfo = discord.Embed(description="-----------------------------------------------", color=UserCommandsCOL)
            else:
                embedinfo = discord.Embed(description="----------------------------------------------------------", color=UserCommandsCOL)
            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = bot.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embedinfo.add_field(name = user_name, value = '{:,}'.format(row[2]), inline=False)
                    last_user_count += 1
            
            update_leaderboard(page + 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed = embedinfo)
            await reaction.message.clear_reactions()
            await reaction.message.add_reaction(u"\u25C0")
            if(last_user_count > (page+1) * 10):
                await reaction.message.add_reaction(u"\u25B6")
        
        if(reaction.emoji == u"\u25C0"):
            page, last_user_count = get_leaderboard_page(reaction.message.id, user.id)
            if(page == 1):
                return
            rows = get_users(page-1)
            if end_date == "" or start_date == "" or blocknumber == "":
                embedinfo = discord.Embed(description="-----------------------------------------------", color=UserCommandsCOL)
            else:
                embedinfo = discord.Embed(description="----------------------------------------------------------", color=UserCommandsCOL)
            if(last_user_count <= page * 10):
                last_user_count -= 10 + (last_user_count-1) % 10
            else:
                last_user_count -= 20
            
            
            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = bot.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embedinfo.add_field(name = user_name, value = '{:,}'.format(row[2]), inline=False)
                    last_user_count += 1
            
            
            update_leaderboard(page - 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed = embedinfo)
            await reaction.message.clear_reactions()
            if(page - 1 > 1):
                await reaction.message.add_reaction(u"\u25C0")
            await reaction.message.add_reaction(u"\u25B6")
'''
            
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
    print(type(points))
    if points:
        if int(points) <= 1:
            embed = discord.Embed(color=UserCommandsCOL, description=f"{user.mention} has {points} point.")
        elif points:
            embed = discord.Embed(color=UserCommandsCOL, description=f"{user.mention} has {points} points.")
    else:
        embed = discord.Embed(color=UserCommandsCOL, description=f"{user.mention} has no points.")
    await interaction.response.send_message(embed=embed)
    
@pointsgroup.command(name="overview",description="Shows leaderboard for points.")
async def overview(interaction: discord.Interaction):
    rows = get_users(1)
    if end_date == "N/A" or start_date == "N/A" or blocknumber == "N/A":
        embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"-----------------------------------------------\nCurrent quota block has not yet been set-up. \nPlease ping a member of DSBPC+.\n-----------------------------------------------", color=UserCommandsCOL)
    else:
        embed = discord.Embed(title =f"**Point Overview - Block {blocknumber}**", description=f"----------------------------------------------------------\nCurrent quota block ending <t:{end_date}:R>.\n| <t:{start_date}> - <t:{end_date}> |\n----------------------------------------------------------", color=UserCommandsCOL)
    count = 1
    for row in rows:
        if(row[1] != None and row[2] != None):
            user = bot.get_user(int(row[1]))
            user = "#" + str(count) + " | " + str(user)
            embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
            count += 1
    
    await interaction.response.send_message(embed=embed)
    add_leaderboard(interaction.user.id, interaction.id, count)

@bot.tree.command(name="mypoints",description="View your point count.")
async def mypoints(interaction: discord.Interaction):
    points = get_user_point(interaction.user.id)
    if int(points) <= 1:
        embed = discord.Embed(color=UserCommandsCOL, description=f"You have {points} point.")
    elif points:
        embed = discord.Embed(color=UserCommandsCOL, description=f"You have {points} points!",)
    else:
        embed = discord.Embed(color=UserCommandsCOL, description=f"You have no points.")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="infoboard",description="Shows bot information and a list of commands.")
async def infoboard(interaction: discord.Interaction):
    embed = discord.Embed(description="Coming sometime soon...")
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

@bot.tree.command(name="updatequota",description="Updates the quota block number, start and end date. [DSBPC+]")
async def updatequota(interaction:discord.Interaction, start_date_new: int, end_date_new: int, blocknumber_new: int):
    user = interaction.user
    
    if authorizationz(user):
        global start_date
        global end_date
        global blocknumber
        blocknumber = blocknumber_new
        start_date = start_date_new
        end_date = end_date_new
        embed = discord.Embed(color=HRCommandsCOL, description=f"Quota block updated to:\n<t:{start_date}> - <t:{end_date}> || Block {blocknumber}")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to run this command.")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pointsreset",description="Resets the points of all users to zero. [DSBPC+]")
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
            await interaction.response.send_message(embed=embed)
        else:
            if response.content == 'yes':
                await reset_database()
                embed = discord.Embed(color=HRCommandsCOL, description=f"Point reset successful.")
                await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to use this command.")
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

@bot.tree.command(name="rloa",description="Used to request an LoA within DSB.")
async def rloa(interaction:discord.Interaction):
    embed = discord.Embed(description="Coming soon:tm:...")
    await interaction.response.send_message(embed=embed)




bot.run(config["bot_token"])