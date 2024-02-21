'''
Module for defining miscellaneous commands.

Created on Wednesday 24th January 2024.
@author: Harry New

'''

import logging
import discord

# Help command.
async def help_command(interaction,workflow):
    # Getting channel and guild.
    channel = interaction.channel
    guild = interaction.guild
    # Creating embed.
    embed = discord.Embed(colour=discord.Colour.blurple(),title="Help",description="Available commands to use with the Workflow Bot:")
    # Creating fields for each command.
    admin_role = await get_admin_role(guild)
    manager_roles = get_team_manager_roles(guild,workflow)

    # Creating team manager mentions.
    manager_mentions = ""
    for manager_role in manager_roles:
      manager_mentions += manager_role.mention + " "
    if manager_roles:
      manager_mentions += ""

    embed.add_field(name="`/set_active_channel`", value=f"***Required {admin_role.mention}***\nSets the current channel to the active channel and displays all existing projects in the workflow. Allows the {admin_role.mention} to add, edit and delete projects and tasks.",inline=False)
    embed.add_field(name="`/teams`", value=f"***Required {admin_role.mention}***\nDisplays all existing teams on the server and allows the {admin_role.mention} to add, edit and delete teams.",inline=False)
    embed.add_field(name="`/manage_projects`", value=f"***Required {admin_role.mention} {manager_mentions}\n***Allows projects to be selected and displays all information about them. Changes can be made to each project including editing project properties, managing tasks and archiving completed tasks. {admin_role.mention} are able to manage teams assigned to each project and finish the project.",inline=False)
    embed.add_field(name="`/manage_tasks`", value=f"Allows members to select from what tasks have been assigned to them and make edits to that task. {manager_mentions} are able to edit more details about the task.",inline=False)

    # Sending message.
    await interaction.response.send_message(embed=embed,delete_after=300)

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

# Check for team manager.
def check_team_manager(member,guild,workflow):
  for role in member.roles:
    for manager_role in get_team_manager_roles(guild,workflow):
      if role == manager_role:
        return True
  return False

# Getting each manager role.
def get_team_manager_roles(guild,workflow):
  manager_roles = []
  # Getting manager id from each team.
  for team in workflow.teams:
    manager_roles.append(guild.get_role(team.manager_role_id))
  return manager_roles

# Get all projects for a member.
def get_projects_for_member(member,workflow):
  # Getting projects.
  projects = []
  for role in member.roles:
    for team in workflow.teams:
      if role.id == team.role_id:
        projects.extend(team.get_projects_from_ids(workflow))
  return projects

# Checking team managers for project.
def check_team_manager_project(member,project,guild,workflow):
  for team in project.get_teams_from_ids(workflow):
    if guild.get_role(team.manager_role_id) in member.roles:
      return True
    
# Checking team members for project.
def check_team_member_task(member,task) -> bool:
  if member.id in task.member_ids:
    return True