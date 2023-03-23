import discord
import os
import sys
import datetime
import random
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.dbFunctions import (update_quota, replace_value, db_register_get_data)
from Functions.randFunctions import (quota_get, get_quota, getrank, changerank, change_nickname, get_user_id_from_link, get_point_quota, set_days_onloa)
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
    #Welcome command
    @app_commands.command(name="welcome", description="Used to induct new DSB members once they've joined the server.")
    async def welcome_pvt(self, interaction:discord.Interaction, member:discord.Member):
        if not DSBPC_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of DSBPC or above to use this command."), ephemeral=True)
        DSBPvt = discord.utils.get(interaction.guild.roles, name="DSB Private")
        DSBRole = discord.utils.get(interaction.guild.roles, name="DSB")
        ServerAccessRole = discord.utils.get(interaction.guild.roles, name="Server Access")
        channel = await self.bot.fetch_channel(949869101537439744) # Channel ID (currently: #dsb-on-duty)
        await member.add_roles(DSBPvt, DSBRole, ServerAccessRole)
        await channel.send(f"DSB, please welcome {member.mention}!")
        await member.send(embed=discord.Embed(color=DSBCommandsCOL, title=f"Welcome to Defensive Squadron Bravo {member.name}!", description=f"Alrighty...you should now have your roles...\n\nHello and welcome to QSO's Defensive Squadron Bravo. I am DSB Helper and as my name already suggests, I help manage this squadron.\n\nFirst things first, please update to your nickname to include `DSB Pvt` as your rank tag and your Roblox username. Additionally please add the `| DSB` suffix to your name in main QSO, you'll receive the DSB role once you pass your private phase. The DSB Private phase, in short, is our version of the OiT phase from main QSO, with a couple of amendments. You can find more information about the Private phase in <#960601856298602617> and an end date for said Private phase will be given to you as soon as possible.\n\nNext, please read through  <#954443926264217701>, <#957983615315222529>, <#957789241813917766> and all the other miscellaneous infoboards. I should also note that while in DSB, you are to never speak ill of other squadrons or display an form of squadron elitism or egotism. If found to be participating in these actions, you will be swiftly removed without warning.\n\nAnd on that note, DSB Management wishes you the best of luck on your Private phase, and we hope to see you excel as a defensive operative.\n\n<:DSB:1060271947725930496> *In the face of danger, we stand our ground!* <:DSB:1060271947725930496>"))
        await interaction.response.send_message(embed=discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Success!",description=f"{member.name} should now have their roles and should have received the welcome message :D"), ephemeral=True)
    
    @app_commands.command(name="accept", description="Used to accept new DSB members into the roblox group.")
    async def accept_pvt(self, interaction:discord.Interaction, member:discord.Member):
        if not DSBPC_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of DSBPC or above to use this command."), ephemeral=True)
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing Permission!", description=f"This command is currently disabled as we wait for Aera to update the roblox group."), ephemeral=True)      

    @app_commands.command(name="excuse", description="Changes the quota for a user for the current block. [DSBPC+]")
    @app_commands.describe(member="The operative you're excusing.", days="The amount of days the operative is being excused for. Cannot be more than 14 days.")
    async def loa_quota(self, interaction:discord.Interaction, member:discord.Member, days:int):
        if(not DSBPC_A(interaction.user)): # check if user has permission
            embed = discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of DSBPC or above to use this command.")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        if days > 14:
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to set days!", description=f"You cannot excuse for more than 14 days."), ephemeral=True)
        if DSBPC_A(member):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> No quota found!", description=f"DSB Pre-Command and above have no quota to be excused from."), ephemeral=True)
        data = db_register_get_data(member.id)
        if data:
            quota, rank = get_point_quota(member)
            if quota == None:
                return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> No quota found!", description=f"No quota was found for this operative."), ephemeral=True)
            if data[4]:
                quota_new = int(quota - ((quota/14)*data[4]))
            if set_days_onloa(member.id, days):
                updata = db_register_get_data(member.id)
                if updata[4] is not None:
                    quota_new = int(quota - ((quota/14)*updata[4]))
                else:
                    quota_new = quota
                start_date, end_date, blocknumber = get_quota()
                return await interaction.response.send_message(f"{member.mention}", embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Default quota set for {member.display_name}!" if days == 0 else f"<:dsbbotSuccess:953641647802056756> New quota for {member.display_name}!", description=f'New quota: **{quota_new} Points** <t:{end_date}:R>\nDays excused: **{updata[4]}**' if updata[4] == None else f'New quota: **{quota_new} Points** <t:{end_date}:R>\nDays excused: **{updata[4]} days**'))
            else:
                return await interaction.response.send_message(embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotFailed:953641818057216050> Failed to set!", description=f"Something went wrong..."), ephemeral=True)
        else:
            return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> User not found!", description=f"{member.display_name} was not found in registry database.", color=ErrorCOL), ephemeral=True)
    

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


