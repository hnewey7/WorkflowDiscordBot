'''
Module for defining miscellaneous commands.

Created on Wednesday 24th January 2024.
@author: Harry New

'''

import logging

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