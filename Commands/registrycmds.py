import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from Functions.dbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

class RegistryCmds(commands.GroupCog, group_name='registry'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    @app_commands.command(name="new", description="This command is used to add new data to the registry database.")
    async def register_new(self, interaction: discord.Interaction, roblox_profile_link: str, user: discord.Member=None):
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

    @app_commands.command(name="update", description="This command is used to update a specifc users data in the registry database.")
    async def register_update(self, interaction: discord.Interaction, new_profile_link: str = None, user: discord.Member = None):
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

    @app_commands.command(name="purge", description="This command is used to purge the registry database. [DEVACCESS]")
    async def register_purge(self, interaction:discord.Interaction):
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
                reaction, user_r = await self.bot.wait_for('reaction_add', check=check, timeout=10)
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
                
    @app_commands.command(name="remove", description="Remove a user from the registry database. [DSBCOMM+]")
    async def register_remove(self, interaction:discord.Interaction, user_id:str):
        if not DSBCOMM_A(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to remove user!", description="You must be a member of DSBCOMM or above to remove users from the user database.", color=ErrorCOL))
            
        result = db_register_remove_user(int(user_id))
        embed = discord.Embed(title=f"<:dsbbotSuccess:953641647802056756> Successfully removed user!" if result else f"<:dsbbotFailed:953641818057216050> Failed to removed user!", description=f"Deleted id: `{user_id}`" if result else f"`{user_id}` was not found in the database.", color=discord.Color.green() if result else ErrorCOL)
        await interaction.response.send_message(embed=embed)
            
    @app_commands.command(name="view", description="This command is used to view data in the registry database.")
    async def register_view(self, interaction:discord.Interaction, user:discord.Member=None):
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
