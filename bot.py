import datetime
import json
import re
import sqlite3

import discord
import google.auth
from discord.ext import commands
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import database
from database import *

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=">", intents=intents)

global start_date
global end_date
global blocknumeber
blocknumber = "1"
start_date = ""
end_date = ""

##### EMBED COLORS ####
global BasiccommandCOL
global UserCommandsCOL
global HRCommandsCOL
global ErrorCOL
BasiccommandCOL = 0x69ABAB
UserCommandsCOL = 0x09D0EF
HRCommandsCOL = 0x0B0B45
ErrorCOL = 0xB3202C

config_file = open("config.json")
config = json.load(config_file)

bot.remove_command("help")
bot.remove_command("finish")

@bot.event
async def on_ready():
    print("MAINBOT READY")
    print("Remember to set quotablock")

def authorizationz(user):
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def mrs(user):
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

@bot.event
async def on_reaction_add(reaction, user):
    if(check_leaderboard(reaction.message.id, user.id)):
        if(reaction.emoji == u"\u25B6"):
            page, last_user_count = get_leaderboard_page(reaction.message.id, user.id)
            if(last_user_count < page * 10):
                return
            rows = get_users(page+1)
            embed = discord.Embed(title =f"Point Overview - Block {blocknumber}", description=f"Current quota block ending <t:{end_date}:R>.\n| <t:{start_date}> - <t:{end_date}> |", color=0x0B0B45)
            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = bot.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embed.add_field(name = user_name, value = '{:,}'.format(row[2]), inline=False)
                    last_user_count += 1
            
            update_leaderboard(page + 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed = embed)
            await reaction.message.clear_reactions()
            await reaction.message.add_reaction(u"\u25C0")
            if(last_user_count > (page+1) * 10):
                await reaction.message.add_reaction(u"\u25B6")
        
        if(reaction.emoji == u"\u25C0"):
            page, last_user_count = get_leaderboard_page(reaction.message.id, user.id)
            if(page == 1):
                return
            rows = get_users(page-1)
            embed = discord.Embed(title =f"Point Overview - Block {blocknumber}", description=f"Current quota block ending <t:{end_date}:R>.\n| <t:{start_date}> - <t:{end_date}> |", color=0x0B0B45)
            if(last_user_count <= page * 10):
                last_user_count -= 10 + (last_user_count-1) % 10
            else:
                last_user_count -= 20
            
            
            for row in rows:
                if(row[1] != None and row[2] != None):
                    user_name = bot.get_user(int(row[1]))
                    user_name = "#" + str(last_user_count) + " | " + str(user_name)
                    embed.add_field(name = user_name, value = '{:,}'.format(row[2]), inline=False)
                    last_user_count += 1
            
            
            update_leaderboard(page - 1, last_user_count, reaction.message.id)
            await reaction.message.edit(embed = embed)
            await reaction.message.clear_reactions()
            if(page - 1 > 1):
                await reaction.message.add_reaction(u"\u25C0")
            await reaction.message.add_reaction(u"\u25B6")
            
    
        
@bot.command(pass_context = True)
async def points(ctx, command = None, username = None, point = None):
    print(f"command: {command} | username: {username} | points: {point}")

    #print(username)
    if(command == None or point == None or username == None):
        if(command == None and point == None and username == None):
            points = get_user_point(ctx.message.author.id)
            embed = discord.Embed(description=f"You have {points} points!", color=UserCommandsCOL )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=ErrorCOL, description=f"Invalid command. \nUse !help to see a list of availble commands.")
            await ctx.send(embed=embed)
            return
            
    user = ctx.message.author
    
    if(command.lower() == "add"):
        if(not authorizationz(user)):
            #await request_points(ctx)
            embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to add points.")
            await ctx.send(embed=embed)
            return
        if(point.isdigit()):
            username_id = username[2:]
            username_id = username_id[:-1]
            username_id = username_id.replace("!","")
            if(username_id.isdigit()):
                add_points(username_id, point)
            else:
                from_server = ctx.guild
                user = from_server.get_member_named(username)
                if(user == None):
                    embed = discord.Embed(ccolor=ErrorCOL, description=f"Invalid user")
                    await ctx.send(embed=embed)
                    await ctx.send("Invalid user")
                    return
                else:
                    add_points(user.id, point)
            embed = discord.Embed(color=HRCommandsCOL, description=f"Points added.")
            await ctx.send(embed=embed)
        else:
            #await request_points()
            embed = discord.Embed(color=ErrorCOL, description=f"Invalid point number.")
            await ctx.send(embed=embed)
    else:
        if(command.lower() == "remove"):
            if(not authorizationz(user)):
                #await request_points(ctx)
                embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to remove points.")
                await ctx.send(embed=embed)
                return
            if(point.isdigit()):
                username_id = username[2:]
                username_id = username_id[:-1]
                username_id = username_id.replace("!","")
                if(username_id.isdigit()):
                    remove_points(username_id, point)
                else:
                    from_server = ctx.guild
                    user = from_server.get_member_named(username)
                    if(user == None):
                        embed = discord.Embed(color=ErrorCOL, description=f"Invalid User.")
                        await ctx.send(embed=embed)
                        return
                    else:
                        remove_points(user.id,point)
                embed = discord.Embed(color=HRCommandsCOL, description=f"Points removed.")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(color=ErrorCOL, description=f"Invalid point number.")
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(color=ErrorCOL, description=f"Invalid command. \nUse !help to see a list of availble commands.")
            await ctx.send(embed=embed)


@bot.command(pass_context = True)
async def help(ctx):
    embed = discord.Embed(title = "Command list", color=BasiccommandCOL)
    embed.add_field(name = ">help", value = config["help_help"], inline = False)
    embed.add_field(name = ">points", value = config["points_help"], inline = False)
    embed.add_field(name = ">pov", value = config["leaderboard_help"], inline = False)
    embed.add_field(name = ">ping", value = config["ping_help"], inline = False)
    embed.add_field(name = ">whois", value = config["whois_help"], inline = False)
    await ctx.send(embed = embed)
    
@bot.command()
async def whois(ctx, user:discord.Member=None):
        roles = []
        if user is None:
            user = ctx.author
        for role in user.roles:
            if role.name == '@everyone':
                continue
            roles.append(str(role.mention))
        roles.reverse()
        ct = user.created_at.strftime("%a, %d %b, %Y | %H:%M")
        jt = user.joined_at.strftime("%a, %d %b %Y | %H:%M")
        embed=discord.Embed(description=user.mention,color=BasiccommandCOL,timestamp=ctx.message.created_at)
        embed.set_author(icon_url=user.avatar, name=f"{user}'s User Info")
        embed.set_thumbnail(url=user.avatar)
        embed.set_footer(text=f'ID: {user.id}')
        embed.add_field(name="Joined Server On:", value=jt,inline=True)
        embed.add_field(name="Created Account On:", value=ct,inline=True)
        if len(str(" | ".join([x.mention for x in user.roles]))) > 1024:
            embed.add_field(name=f"Roles[{len(user.roles)}]:", value="Too many to display.", inline=False)
        else:
            role_count = len([role for role in user.roles if role.name != '@everyone'])
            embed.add_field(name=f"Roles[{role_count}]:", value=" | ".join(roles),inline=False)

            
        embed.add_field(name="Bot:", value=f'{("Yes" if user.bot==True else "No")}',inline=True)
        await ctx.send(embed=embed)
    

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def ping(ctx):
    await ctx.send(f"🏓Pong! Took `{round(bot.latency * 1000)}`ms")


@bot.command()
async def updatequota(ctx, start_date_new: int, end_date_new: int, blocknumber_new: int):
    user = ctx.message.author
    
    if authorizationz(user):
        global start_date
        global end_date
        global blocknumber
        blocknumber = blocknumber_new
        start_date = start_date_new
        end_date = end_date_new
        embed = discord.Embed(color=HRCommandsCOL, description=f"Quota block updated to: <t:{start_date}> - <t:{end_date}> || Block {blocknumber}")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to run this command.")
        await ctx.send(embed=embed)

@bot.command(pass_context = True)
async def pov(ctx):
    rows = get_users(1)
    embed = discord.Embed(title =f"Point Overview - Block {blocknumber}", description=f"Current quota block ending <t:{end_date}:R>.\n| <t:{start_date}> - <t:{end_date}> |", color=UserCommandsCOL)
    count = 1
    for row in rows:
        if(row[1] != None and row[2] != None):
            user = bot.get_user(int(row[1]))
            user = "#" + str(count) + " | " + str(user)
            embed.add_field(name = user, value = '{:,}'.format(row[2]), inline=False)
            count += 1 
    msg_sent = await ctx.send(embed=embed)
    add_leaderboard(ctx.message.author.id, msg_sent.id, count)
    if(count == 11):
        await msg_sent.add_reaction(u"\u25B6")
    
    
@bot.command(pass_context=True)
async def reset(ctx):
    user = ctx.message.author

    if authorizationz(user):
        # Reset the points
        # Add code to reset the points here
        await reset_database()
        embed = discord.Embed(color=HRCommandsCOL, description=f"Point reset successful.")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission to use this command.")
        await ctx.send(embed=embed)
            
@bot.command()
async def viewpoints(ctx, user: discord.User):
    points = get_user_points(user.id)
    if points:
        embed = discord.Embed(color=UserCommandsCOL, description=f"{user.name} has {points} points.")
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=UserCommandsCOL, description=f"{user.name} has no points.")
        await ctx.send(embed=embed)


#Added 01/08/2023 
@bot.command()
async def soup(ctx):
    user = ctx.message.author
    role_name = "[DSB] Operation Supervisors"
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    
    if mrs(user)==False:
        embed = discord.Embed(color=UserCommandsCOL, description=f"You need to be EDS+ to use this command.")
        await ctx.send(embed=embed)
    else:
        if role in ctx.author.roles:
            try:
                await ctx.author.remove_roles(role)
                embed = discord.Embed(color=UserCommandsCOL, description=f"Role successfully removed.")
                await ctx.send(embed=embed)
            except Exception as e:
                print(e)
                embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to remove the role.")
                await ctx.send(embed=embed)
        else:
            try:
                await ctx.author.add_roles(role)
                embed = discord.Embed(color=UserCommandsCOL, description=f"Role successfully added.")
                await ctx.send(embed=embed)
            except Exception as e:
                print(e)
                embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to add the role.")
                await ctx.send(embed=embed)



bot.run(config["bot_token"])