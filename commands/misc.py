'''
Module for defining miscellaneous commands.

Created on Wednesday 24th January 2024.
@author: Harry New

'''

import logging
import discord

# Help command.
async def help_command(command,client):
    # Getting channel.
    channel = command.channel
    # Creating embed.
    embed = discord.Embed(colour=discord.Colour.blurple(),title="Help",description="Available commands to use with the Workflow Bot:")
    # Creating fields for each command.
    admin_role = await get_admin_role(command.guild)
    embed.add_field(name="`!set_active_channel`", value=f"Sets the current channel to the active channel and displays all existing projects in the workflow. Allows the {admin_role.mention} to add, edit and delete projects and tasks.",inline=False)
    embed.add_field(name="`!teams`", value=f"Displays all existing teams on the server and allows the {admin_role.mention} to add, edit and delete teams.",inline=False)
    # Sending message.
    await channel.send(embed=embed,delete_after=300)

# Disconnect command.
async def disconnect_command(client):
    await client.close()

# Show workflow command.
async def show_workflow_command(workflow):
    print(workflow.projects)

# Show guild ids.
async def show_guild_command(command):
    print(command.guild.id)

# Delete all roles.
async def delete_roles_command(command):
    for role in command.guild.roles:
        if role.name != "Workflow Manager" and role.name != "WorkflowBot" and role.name != "@everyone":
            await role.delete()
            logging.info(f"Removing role, {role.name}")

# - - - - - - - - - - - - - - - - - - -

# Getting admin role. 
async def get_admin_role(guild):
    # Getting workflow manager role.
    for role in await guild.fetch_roles():
        if role.name == "Workflow Manager":
            return role