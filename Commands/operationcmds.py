import random
import string
import discord
from colorama import Back, Fore, Style
from discord.ext import commands
from discord import app_commands
from Functions.dbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *

class OperationCmds(commands.GroupCog, group_name='operation'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="announce", description="*Placeholder...")
    @app_commands.choices(op_type=[
        app_commands.Choice(name="ALPHA", value="ALPHA"),
        app_commands.Choice(name="BRAVO", value="BRAVO"),
        app_commands.Choice(name="CHARLIE", value="CHARLIE"),
        app_commands.Choice(name="DELTA-CHARLIE", value="DELTA-CHARLIE"),
        app_commands.Choice(name="ECHO", value="ECHO"),
        app_commands.Choice(name="DELTA-ECHO", value="DELTA-ECHO"),
        app_commands.Choice(name="FOXTROT", value="FOXTROT"),
        app_commands.Choice(name="DELTA-FOXTROT", value="DELTA-FOXTROT"),
        app_commands.Choice(name="GOLF", value="GOLF"),
        app_commands.Choice(name="DELTA-GOLF", value="DELTA-GOLF"),
        app_commands.Choice(name="HOTEL", value="HOTEL"),
        ])
    async def announce(self, interaction: discord.Interaction, op_type:app_commands.Choice[str], unix_start:str=None, trello_link:str=None, co_host:discord.Member=None, supervisor:discord.Member=None, lengh:str=None):
        user = interaction.user
        if ITMR_A(user):
            def random_string(length):
                letters = string.ascii_uppercase
                return ''.join(random.choice(letters) for i in range(length))

            operation_PLs = random_string(3)
            
            operationinfo = discord.Embed(title=f"<:DSB:1060271947725930496> Defensive Squadron Bravo - Scheduled Operation", description=f"Operation **`{op_type} {operation_PLs}`** has been scheduled and will take place <t:{unix_start}:R>.", color=DSBCommandsCOL)
            operationinfo.add_field(name="", value="", inline=False)
            if co_host and supervisor:
                co_host=co_host.display_name
                supervisor=supervisor.display_name
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Co-host` - {co_host}\n`Soupervisor` - {supervisor}\n`Length` - The operation will last for {lengh}.\n`Trello Card` - {trello_link}")
            elif co_host:
                co_host=co_host.display_name
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Co-host` - {co_host}\n`Length` - The operation will last for {lengh}.\n`Trello Card` - {trello_link}")
            elif supervisor:
                supervisor=supervisor.display_name
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Soupervisor` - {supervisor}\n`Length` - The operation will last for {lengh}.\n`Trello Card` - {trello_link}")
            else:
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Length` - The operation will last for {lengh}.\n`Trello Card` - {trello_link}")
            operationinfo.add_field(name="", value="", inline=False)
            operationinfo.add_field(name="Able to attend?", value="Please react below to confirm your attendance.", inline=False)
            dsbrole = "<@&1041286178613243954>"
            allowed_mentions = discord.AllowedMentions.all()
            await interaction.response.send_message(dsbrole, allowed_mentions=allowed_mentions)
            msg_sent = await interaction.edit_original_response(embed=operationinfo)
            op_create_scheduled(op_type, operation_PLs, unix_start, trello_link, msg_sent.id)
            await msg_sent.add_reaction("<:DSB:1060271947725930496>")
        else:
            embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="start", description="*Placeholder...")
    @app_commands.choices(vc=[
        app_commands.Choice(name="[QSO] On Duty 1", value="937473342884179980"),
        app_commands.Choice(name="[QSO] On Duty 2", value="937473342884179981"),
        app_commands.Choice(name="[QSO] On Duty 3", value="937473342884179982"),
        app_commands.Choice(name="[QSO] On Duty 4", value="937473342884179983"),
        app_commands.Choice(name="[QSO] On Duty 5", value="937473342884179984"),
        app_commands.Choice(name="[QSO] VIP Raid", value="937473342884179985"),
        app_commands.Choice(name="[QSO] Events", value="992865433059340309"),
        app_commands.Choice(name="[DSB] On Duty 1", value="949869157552390154"),
        app_commands.Choice(name="[DSB] On Duty 2", value="949869187168370718"),
        app_commands.Choice(name="[DSB] On Duty 3", value="949869232663986226"),
        app_commands.Choice(name="[DSB] Events", value="950145200087511130"),
        app_commands.Choice(name="[SQD] On Duty 1", value="949470602366976055"),
        app_commands.Choice(name="[SQD] On Duty 2", value="949867772643520522"),
        app_commands.Choice(name="[SQD] On Duty 3", value="949867813789630574"),
        app_commands.Choice(name="[SQD] Events", value="950145105040388137"),
        ])
    @app_commands.choices(op_type=[
        app_commands.Choice(name="ALPHA", value="ALPHA"),
        app_commands.Choice(name="BRAVO", value="BRAVO"),
        app_commands.Choice(name="CHARLIE", value="CHARLIE"),
        app_commands.Choice(name="DELTA-CHARLIE", value="DELTA-CHARLIE"),
        app_commands.Choice(name="ECHO", value="ECHO"),
        app_commands.Choice(name="DELTA-ECHO", value="DELTA-ECHO"),
        app_commands.Choice(name="FOXTROT", value="FOXTROT"),
        app_commands.Choice(name="DELTA-FOXTROT", value="DELTA-FOXTROT"),
        app_commands.Choice(name="GOLF", value="GOLF"),
        app_commands.Choice(name="DELTA-GOLF", value="DELTA-GOLF"),
        app_commands.Choice(name="HOTEL", value="HOTEL"),
        ])
    async def commence(self, interaction:discord.Interaction, status:str, vc:app_commands.Choice[str], operation_pal:str=None, op_type:str=None):
        user = interaction.user
        if ITMR_A(user):
            if operation_pal == None and op_type:
                def random_string(length):
                    letters = string.ascii_uppercase
                    return ''.join(random.choice(letters) for i in range(length))
                vc_id_u = int(vc.value)
                profile_link_u = get_roblox_link(interaction.user.id)
                operation_pal = random_string(3)
                operationinfo = discord.Embed(title=f"<:DSB:1060271947725930496> Spontaneous operation!", description=f"Operation `{op_type} {operation_pal}` is currently being hosted by **{user.display_name}**.\n\n`Voice Channel` - <#{vc_id_u}>\n`Profile link` - {profile_link_u}\n`Current status` - {status}.", color=DSBCommandsCOL)
                dsbrole = "<@&1041286178613243954>"
                allowed_mentions = discord.AllowedMentions.all()
                await interaction.response.send_message(dsbrole, allowed_mentions=allowed_mentions)
                msg_sent = await interaction.edit_original_response(embed=operationinfo)
                op_create_spontaneous(op_type, operation_pal, msg_sent.id)
            else:
                opinfo = op_get_info(operation_pal)
                if opinfo:
                    vc_id_u = int(vc.value)
                    profile_link_u = get_roblox_link(interaction.user.id)
                    op_ann = await interaction.channel.fetch_message(opinfo[6])
                    embed = discord.Embed(title=f"<:DSB:1060271947725930496> Scheduled operation!", 
                                        description=f"Operation `{opinfo[0]} {opinfo[1]}` is now commencing.\n\n`Voice Channel` - <#{vc_id_u}>\n`Profile link` - {profile_link_u}\n`Current status` - {status}.", 
                                        color=DSBCommandsCOL)
                    #await interaction.response.send_message(embed=operationinfo, allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False))
                    dsbrole = "<@&1041286178613243954>"
                    allowed_mentions = discord.AllowedMentions.all()
                    await op_ann.reply(dsbrole, allowed_mentions=allowed_mentions, embed=embed)
                    succemb = discord.Embed(description="Operation started successfully.", color=DSBCommandsCOL)
                    await interaction.response.send_message(embed=succemb, ephemeral=True)  
                else:
                    embed = discord.Embed(description=f"Operation with PALs `{operation_pal}` not found!", color=ErrorCOL)
                    await interaction.response.send_message(embed=embed, ephemeral=True)   
        else:
            embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command.")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="end", description="Used to conclude your operations.")
    async def conclude(self, interaction:discord.Interaction, pal:str):
        user = interaction.user
        if DSBMEMBER(user):
            if ITMR_A(user):
                result = op_get_info(pal)
                if result:
                    op_ann = await interaction.channel.fetch_message(result[6])
                    op_emb = op_ann.embeds[0]
                    op_emb.title = "<:DSB:1060271947725930496> Defensive Squadron Bravo - Concluded Operation"
                    embed = discord.Embed(description=f"Operation `{result[0]} {result[1]}` has been concluded, thank you for attending.", color=DSBCommandsCOL)
                    op_conclude(pal)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await op_ann.edit(embed=op_emb)
                    await op_ann.reply(embed=embed)
                else:
                    embed = discord.Embed(description=f"Operation with PALs `{pal}` not found!", color=ErrorCOL)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command.")
                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dossier", description="*Placeholder...")
    async def dossier(self, interaction:discord.Interaction, operation:str, time_and_date:str, ringleader:str, attendees:str, purpose:str, summary:str, picture:discord.Attachment, co_host:str=None, supervisors:str=None):
        dossierem = discord.Embed(title=f"OPERATION: {operation}")
        dossierem.add_field(name="`Time & Date:`", value=f"{time_and_date}")
        dossierem.add_field(name="`Purpose of Operation:`", value=f"{purpose}")
        dossierem.add_field(name="`Ringleader:`", value=f"{ringleader}", inline=False)
        if co_host:
            dossierem.add_field(name="Co-host(s):", value=f"{co_host}")
        if supervisors:
            dossierem.add_field(name="Supervisor(s):", value=f"{supervisors}")
        dossierem.add_field(name="`Attendees:`", value=f"{attendees}")
        dossierem.add_field(name="`Operation Summary:`", value=f"{summary}", inline=False)
        dossierem.set_image(url=picture)
        await interaction.response.send_message(embed=dossierem)
        await interaction.followup.send(embed=discord.Embed(description="Make sure you make a point request for this operation using the PALs. 😉"), ephemeral=True)

    @app_commands.command(name="cancel", description="Used to cancel a scheduled operation.")
    async def cancel(self, interaction:discord.Interaction, pal:str, reason:str):
        if DSBMEMBER(interaction.user):
            if ITMR_A(interaction.user):
                result = op_get_info(pal)
                if result:
                    op_ann = await interaction.channel.fetch_message(result[6])
                    op_emb = op_ann.embeds[0]
                    op_emb.title = "<:DSB:1060271947725930496> Defensive Squadron Bravo - Cancelled Operation"
                    embed = discord.Embed(description=f"Operation `{result[0]} {result[1]}` has been cancelled.", color=ErrorCOL)
                    op_cancel(pal)
                    embed.add_field(name="", value=f"*Reason: {reason}*")
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await op_ann.edit(embed=op_emb)
                    await op_ann.reply(embed=embed)
                else:
                    embed = discord.Embed(description=f"Operation with PALs `{pal}` not found!", color=ErrorCOL)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
    
class soupCmd(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="soup",description="Adds or removes the `Operation Supervisor` role. [SMaj+]")
    async def soup(self, interaction:discord.Interaction):
        if not FMR_A(interaction.user):
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"This command is limited to DSB Sergeant Major+."))
        else:
            role_name = "Operation Supervisor"
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