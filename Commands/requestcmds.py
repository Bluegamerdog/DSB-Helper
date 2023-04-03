import math
import re
import discord
import random
from discord.ext import commands
from discord import app_commands
from discord import ui
from Functions.dbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import (get_point_quota, attendance_points, co_host_points, supervisor_points, ringleader_points, getrank, get_quota)

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
            embed.title="<:dsbbotFailed:953641818057216050> Cancelled Patrol Point Request!"
            embed.clear_fields()
            embed.set_footer(text=f"Cancelled by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
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
            embed.title="<:dsbbotFailed:953641818057216050> Cancelled Operation Point Request!"
            embed.clear_fields()
            embed.set_footer(text=f"Cancelled by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            embed.color=HRCommandsCOL
            await interaction.message.edit(embed=embed, view=None)
        else:
            return

class ExcuseButtons(discord.ui.View):
    def __init__(self, days:int, member:discord.Member):
        super().__init__()
        self.days = days
        self.member = member
        discord.ui.View.timeout = None
    
    @discord.ui.button(emoji="<:dsbbotAccept:1073668738827694131>", style=discord.ButtonStyle.grey)
    async def AcceptButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not DSBPC_A(interaction.user):
            return
        else:
            data = db_register_get_data(self.member.id)
            if data:
                quota, rank = get_point_quota(self.member)
                if quota == None:
                    return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> No quota found!", description=f"No quota was found for this operative."), ephemeral=True)
                if set_days_onloa(self.member.id, self.days):
                    updata = db_register_get_data(self.member.id)
                    if updata[4] != None:
                        quota_new = int(quota - ((quota/14)*updata[4]))
                    else:
                        quota_new = quota
                embed = interaction.message.embeds[0]
                embed.title= embed.title.replace("<:dsbbotUnderReview:953642762857771138>", "<:dsbbotAccept:1073668738827694131>")
                embed.color=DarkGreenCOL
                await interaction.message.edit(embed=embed, view=None)
            start_date, end_date, blocknumber = get_quota()
            return await interaction.response.send_message(f"{self.member.mention}", embed = discord.Embed(color=SuccessCOL, title=f"<:dsbbotSuccess:953641647802056756> Excuse Request Accepted!", description=f'New quota: **{quota_new} Points** <t:{end_date}:R>\nDays excused: **{updata[4]}**' if updata[4] == None else f'New quota: **{quota_new} Points** <t:{end_date}:R>\nDays excused: **{updata[4]} days**'))

    @discord.ui.button(emoji="<:dsbbotDeny:1073668785262833735>", style=discord.ButtonStyle.grey)
    async def DenyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not DSBPC_A(interaction.user):
            return
        else:
            embed = interaction.message.embeds[0]
            embed.title= embed.title.replace("<:dsbbotUnderReview:953642762857771138>", "<:dsbbotDeny:1073668785262833735>")
            embed.color=DarkRedCOL
            await interaction.message.edit(embed=embed, view=None)
            embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Block Excuse Request Denied!", description=f"Your block excuse request has been **denied**. The person who reviewed it will provide you with the reason shortly.")
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)
        
    @discord.ui.button(emoji="❌", style=discord.ButtonStyle.grey)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user == interaction.message.interaction.user:
            await interaction.message.delete()
        else:
            return

class ExcuseModal(ui.Modal, title="Block Excuse Request"):
    days = ui.TextInput(label='How many days?', placeholder="Please only enter digits. Must be in between 3 and 14 days.", max_length=2, required=True)
    reason = ui.TextInput(label='Reason?', style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        quota = get_quota()
        if int(self.days.value) > 14 or (int(self.days.value) < 3):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Invalud length!", description=f"You cannot be excused for less than 3 or more than 14 days. If you need to take a longer excuse, please file a regular Leave of Absence."), ephemeral=True)
        embed=discord.Embed(title=f"<:dsbbotUnderReview:953642762857771138> Block {quota[2]} Excuse Request", color=DSBCommandsCOL)
        embed.add_field(name="", value=f"**Rank and User:** {interaction.user.display_name}", inline=False)
        embed.add_field(name="", value=f"**Requested length:** {self.days} days" if int(self.days.value) > 1 else f"**Requested length:** {self.days} day", inline=False)
        embed.add_field(name="", value=f"**Reason:** ||{self.reason}||", inline=False)
        await interaction.response.send_message(embed=embed, view=ExcuseButtons(int(self.days.value), interaction.user))
        

class RequestCmds(commands.GroupCog, group_name='request'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        

    @app_commands.command(name="patrol", description="Request points for your patrols using this command.")
    @app_commands.describe(log="Message link to .qb findlog message from #bot-commands", length="The length of your patrol in minutes")
    async def request_log(self, interaction:discord.Interaction, length:int, log:str):
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
                amount += extra
        embed = discord.Embed(color=DSBCommandsCOL, title=f"<:dsbbotUnderReview:953642762857771138> __Patrol__ Point Request - {interaction.user.display_name}")
        embed.add_field(name="", value="")
        embed.add_field(name="", value=f"**{interaction.user.display_name}** has requested **{amount} points** for patrolling **{length} minutes**.\n\n→ **[Log Message]({log})**", inline=False)
        await interaction.response.send_message(embed = embed, view=PatrolrequestButtons(amount))

    @app_commands.command(name="operation", description="Request points for your operations using this command.")
    @app_commands.describe(operation="Example: `ECHO HH`", ringleader="The host of the operation, normally that would be you.", co_hosts="If anyone co-hosted your operation they would go here.", supervisors="If anyone soupervised your operation, they would go here.", attendees="Your attendance list goes here. Make sure to seperate the mentions using a comma.")
    async def request_op(self, interaction:discord.Interaction, operation:str, ringleader:discord.Member, supervisors:str=None, co_hosts:str=None, attendees:str=None):
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
                if str(co_host_id).__len__() > 20:
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
                    error_msg = f"`Co-Hosts:` {co_host_member.mention} is not a Supervised Staff Sergeant or above."
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
                if str(supervisor_id).__len__() > 20:
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
                    error_msg = f"`Supervisors:` {supervisor_member.mention} is not an Sergeant Major or above."
                    break
                soup_list.append(supervisor_member)
                points_dict[supervisor_member.id] = supervisor_points(supervisor_member) #= random.uniform(0.001, 1000000000)
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
                attendee_id = int(attendee.replace("<", "").replace("@", "").replace(">", "").replace(" ", ""))
                if str(attendee_id).__len__() > 20:
                    error_msg = f"`Attendees:` Please separate user mentions with commas."
                    break
                attendee_member = discord.utils.get(interaction.guild.members, id=attendee_id)
                if not attendee_member:
                    error_msg = f"`Attendees:` Could not find a member with ID {attendee_id}."
                    break
                if DSBPC_A(attendee_member):
                    error_msg = f"`Attendees:` {attendee_member.mention} is a member of DSB leadership. You cannot put members of DSB leadership and above as attendees. 😉"
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
            if not cohosts:
                cohtxt = "Something went wrong..."
            if not supervisors:
                souptxt = "Something went wrong..."
            if not attendees:
                atttxt = "Something went wrong..."
        
        if ringleader:
            if ITMR_A(ringleader):
                points_dict[ringleader.id] = ringleader_points(ringleader)
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
        
    @app_commands.command(name="excuse", description="Request to be excused for a few days for the current block.")
    @app_commands.choices(type=[
        #app_commands.Choice(name="Leave of Absence", value="LoA"),
        app_commands.Choice(name="Block excuse", value="ExC"),
    ])
    async def request_ex(self, interaction: discord.Interaction, type:app_commands.Choice[str]):
        if not DSBMEMBER(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only DSB Private First Class or above may interact with DSB Helper."), ephemeral=True)
        if not db_register_get_data(interaction.user.id):
            return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Interaction failed!", description="You were not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL), ephemeral=True)  
        #if type.value == "LoA":    
        #    await interaction.response.send_modal(LoAModal())
        if type.value == "ExC":
            await interaction.response.send_modal(ExcuseModal())