import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from Functions.dbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

class otherCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="whois",description="Displays a user's information.")
    async def whois(self, interaction: discord.Interaction, user:discord.Member=None):
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

    @app_commands.command(name="ping",description="Shows the bot's response time.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓Pong! Took `{round(self.bot.latency * 1000)}`ms")


