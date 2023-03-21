import discord
import os
import sys
import datetime
import random
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.dbFunctions import (update_quota, replace_value, db_register_get_data)
from Functions.randFunctions import (quota_get, get_quota, getrank, changerank, change_nickname, get_user_id_from_link)
from discord.ext import commands
from discord import app_commands
from discord import ui
from roblox import *

roblox = Client("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_A249C7CBC0AD0C2157BCF1D7468ADA824736AA27889516B8B6CE8ECDB36DFDA0E8060ADEB457C5E09FC7A1890499AE2CCB105774F5110EDA6967AE9F8874F2DFC554568F0B2FA0E495127FBB713B39EBD7E807009540475DE2E6F6BA203325747382D6C7E8C43A382240F49576850B55B885A0A662C1FBD19A3653331C1BFA49D9CBBFFE01FCF21CD676E01981AE859ECAF81BD219052904AB26A81F39E9ADB0B3F3D7C2A24533E9849EE3B183192EBD3F039E51530411037FC26143AD12687A31F0B087AA57FDBB2B4C562A3F7CCD909F418D6EC6F04E8031C523C20B475A4A85D0E0DED5DD0DDEDB4D417B12C2944870F884D3B6D6734DE67C97982D678E45007C16AC1E218D4A5DA104D7CF57B79F6039C257AC8782FC4505F4D193D269DB05439E3C0E49D59AB39EA77A8335CA77126CD1B4CAABCC3826905C6CBFB11A19860B85B78300560974E04A0B5F40CCCC40062C91554179133B4284E15DFE0AB4B114605E45BA8FE25F718E36753BCC60DB8DD76E")    

class ManagementCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    ## DEV COMMANDS ##
    @app_commands.command(name="restart",description="Restarts the DSB Helper. [DSBPC+]")
    async def restart(self, interaction:discord.Interaction):
        if not DSBPC_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be a member of DSBPC or above to use the restart command.", color=ErrorCOL))
        else:
            embed=discord.Embed(color=0x008000, title="<:dsbbotCaution:1067970676041982053> Restarting...")
            await interaction.response.send_message(embed=embed)
            print(f"=========\nBot restarted by {interaction.user}\n=========")
            os.execv(sys.executable, ['python'] + sys.argv)
            
    @app_commands.command(name="shutdown", description="Shuts down DSB Helper. [DSBCOMM+]")
    async def shutdown(self, interaction:discord.Interaction):
        if not DSBCOMM_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be member of DSBCOMM or above to use the shutdown command.", color=ErrorCOL))
        else:
            embed = discord.Embed(color=ErrorCOL, title="<:dsbbotCaution:1067970676041982053> Shutting down...")
            await interaction.response.send_message(embed=embed)
            print(f"=========\nBot closed by {interaction.user}\n=========")
            await self.bot.close()
    
    @app_commands.command(name="database", description="Able to change any value of the database. [DEVACCESS]")
    async def update_database(self, interaction:discord.Interaction, table:str, column:str, old:str, new:str):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be listed under DEVACCESS to use this command.", color=ErrorCOL))
        else:
            try:
                replace_value(table, column, old, new)
                return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Successfully updated!", description=f"**Table:** `{table}` || **Column:** `{column}`\n\nChanged: `{old}` -> `{new}`", color=SuccessCOL))
            except Exception as e:
                return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Error!", description=f"{e}", color=ErrorCOL), ephemeral=True)
    
    @app_commands.command(name="status", description="Set the bot's activity. [DSBPC+]")
    async def change_status(self, interaction: discord.Interaction, status_type:str, name:str=None):
        if not DSBPC_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be a member of DSBPC or above to change DSB Helpers activity.", color=ErrorCOL), ephemeral=True)
            
        activity_types = {
            "playing": discord.ActivityType.playing,
            "streaming": discord.ActivityType.streaming,
            "listening": discord.ActivityType.listening,
            "watching": discord.ActivityType.watching,
        }

        global watching_command
        if status_type in activity_types:
            activity = discord.Activity(type=activity_types[status_type], name=name)
            await self.bot.change_presence(activity=activity)
            return await interaction.response.send_message(f"Status updated, {status_type} {name}", ephemeral=True)
        elif status_type == "w_enable":
            if watching_command == False:
                watching_command = True
                return await interaction.response.send_message(f"`/watching` enabled ({watching_command})", ephemeral=True)
            elif watching_command == True:
                watching_command = False
                return await interaction.response.send_message(f"`/watching` disabled ({watching_command})", ephemeral=True)
        elif status_type == "remove":
            await self.bot.change_presence(activity=None)
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

    ## DATABASE MANAGEMENT ##
    @app_commands.command(name="rank", description="Used to promote/demoted DSB members. [DSBPC+]")
    @app_commands.choices(rank=[
    app_commands.Choice(name="Private First Class", value="PFC"),
    app_commands.Choice(name="Corporal", value="Crp"),
    app_commands.Choice(name="Sergeant", value="Sgt"),
    app_commands.Choice(name="Supervised Staff Sergeant", value="SvSSgt"),
    app_commands.Choice(name="Staff Sergeant", value="SSgt"),
    app_commands.Choice(name="Sergeant Major", value="SMaj"),
    app_commands.Choice(name="Chief Sergeant", value="CSgt"),])
    async def rank_cmd(self, interaction:discord.Interaction, user:discord.Member, rank:app_commands.Choice[str]):
        if not DSBPC_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be a member of DSBPC or above to use this command.", color=ErrorCOL), ephemeral=True)
        elif not DSBROLE(user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Denied!", description="You can only rank DSB members.", color=ErrorCOL), ephemeral=True)
        else:
            userrank = getrank(user)
            if rank.value=="SSgt" and userrank[1] <=18:
                if userrank[1] == 18:
                    oldrank_role = discord.utils.get(interaction.guild.roles, name="Supervised Staff Sergeant")
                    newrank_role = discord.utils.get(interaction.guild.roles, name="Staff Sergeant")
                    await user.edit(nick=change_nickname("Staff Sergeant", user.display_name))
                    await user.add_roles(newrank_role)
                    await user.remove_roles(oldrank_role)
                    embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Congrats!", description=f"You can now host your own operations, without the need for supervision! <a:dsbbotCelebration:1084176617993162762>", color=SuccessCOL)
                    embed.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                    return await interaction.response.send_message(content=f"{user.mention}", embed=embed)
                else:
                    return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Rank Error!", description="You can only promote **Supervised Staff Sergeants** to **Staff Sergeant**.", color=ErrorCOL), ephemeral=True)
                
            userrank = getrank(user)
            newrank = changerank(rank.value)
            if userrank[1] >= 252 or userrank==None:
                return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Unable!", description="I cannot rank members of DSB Pre-Command and above.", color=ErrorCOL), ephemeral=True)
            else:
                if userrank[1] == newrank[1]:
                    return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Already at that rank!", description=f"**{user.mention}** is already a **{userrank[0]}**.", color=ErrorCOL), ephemeral=True)
                elif newrank[1] > userrank[1]:   
                    #promote
                    try:
                        data = db_register_get_data(user.id)
                        userrank_role = discord.utils.get(interaction.guild.roles, name=str(userrank[0]))
                        newrank_role = discord.utils.get(interaction.guild.roles, name=str(newrank[0]))
                        
                        group = await roblox.get_group(15155104)
                        await user.edit(nick=change_nickname(newrank[0], user.display_name))
                        await group.get_member(get_user_id_from_link(data[2])).set_rank(newrank[1])
                        await user.add_roles(newrank_role) 
                        await user.remove_roles(userrank_role)
                        if newrank[1] >= 18 and userrank[1] < 18:
                            mr_role = discord.utils.get(interaction.guild.roles, name="Operation Ringleader")
                            await user.add_roles(mr_role)
                        if newrank[1] >= 20 and userrank[1] < 20:
                            soup_role = discord.utils.get(interaction.guild.roles, name="Operation Supervisor")
                            await user.add_roles(soup_role)
                        embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Promotion!", description=f"You have been promoted from **{userrank[0]}** to **{newrank[0]}**! <a:dsbbotCelebration:1084176617993162762>", color=SuccessCOL)
                        embed.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                        return await interaction.response.send_message(content=f"{user.mention}", embed=embed)
                    except Exception as e:
                        print(e)
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Error!", description=f"{e}", color=ErrorCOL)
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                        
                elif newrank[1] < userrank[1]:
                    #demote
                    try:
                        data = db_register_get_data(user.id)
                        group = await roblox.get_group(15155104)
                        await group.get_member(get_user_id_from_link(data[2])).set_rank(newrank[1])
                        userrank_role = discord.utils.get(interaction.guild.roles, name=str(userrank[0]))
                        newrank_role = discord.utils.get(interaction.guild.roles, name=str(newrank[0]))
                        await user.edit(nick=change_nickname(newrank[0], user.display_name))
                        await user.add_roles(newrank_role)
                        await user.remove_roles(userrank_role)
                        if userrank[1] >= 16 and newrank[1] <16:
                            mr_role = discord.utils.get(interaction.guild.roles, name="Operation Ringleader")
                            await user.remove_roles(mr_role)
                        if userrank[1] >= 20 and newrank[1] < 20:
                            soup_role = discord.utils.get(interaction.guild.roles, name="Operation Supervisor")
                            await user.remove_roles(soup_role)
                        embed = discord.Embed(title="<:dsbbotCaution:1067970676041982053> Demotion!", description=f"You have been demoted from **{userrank[0]}** to **{newrank[0]}**.", color=ErrorCOL)
                        embed.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                        return await interaction.response.send_message(content=f"{user.mention}", embed=embed)
                    except Exception as e:
                        print(e)
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Error!", description=f"{e}", color=ErrorCOL)
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    print("Something was missed...")
            
    
    #MISC MANEGMENT# 
    @app_commands.command(name="watching", description=":lo:")
    async def watching(self, interaction: discord.Interaction, user:discord.Member=None):
        global watching_command
        if not watching_command:
            return await interaction.response.send_message("This command is currently disabled.", ephemeral=True)
        elif user == None:
            members = self.bot.guilds[0].members
            random_member = random.choice(members)
            activity = discord.Activity(type=discord.ActivityType.watching, name=f"{random_member.display_name}")
            await self.bot.change_presence(activity=activity)
            await interaction.response.send_message("Status updated, watching randomized", ephemeral=True)
        else:
            activity = discord.Activity(type=discord.ActivityType.watching, name=f"{user.display_name}")
            await self.bot.change_presence(activity=activity)
            await interaction.response.send_message(f"Status updated, watching {user.display_name}", ephemeral=True)

    @app_commands.command(name="updatequota",description="Updates the quota block start to end date. [DSBPC+]")
    async def updatequota(self, interaction:discord.Interaction, start_date_new: int, end_date_new: int, blocknumber_new: int):
        if not DSBPC_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to remove user!", description="You must be a member of DSBPC or above to update/change quota block data.", color=ErrorCOL))
        else:
            start_date, end_date, blocknumber = get_quota()
            update_quota(start_date_new, end_date_new, blocknumber_new)
            embed = discord.Embed(color=HRCommandsCOL, title="Quota block change")
            embed.add_field(name="From:", value=f"<t:{start_date}> - <t:{end_date}> || Block {blocknumber}", inline=False)
            embed.add_field(name="To:", value=f"<t:{start_date_new}> - <t:{end_date_new}> || Block {blocknumber_new}", inline=False)
            await interaction.response.send_message(embed=embed)
            quota_get()


