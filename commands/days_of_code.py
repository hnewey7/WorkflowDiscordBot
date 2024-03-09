'''
Module for handling days of code command.

Created on Monday 4th March 2024.
@author: Harry New

'''

import discord
import logging
import asyncio
import time

# - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - -

class ApproveDaysOfCode(discord.ui.View):

  def __init__(self,workflow):
    super().__init__()
    self.workflow = workflow
    self.close_check = False

  @discord.ui.button(label="Create Project",style=discord.ButtonStyle.success)
  async def create_project(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Creating days of code project.
    project = self.workflow.add_100days_project()
    
    # Sending update log in active channel.
    logger.info("Sending update log in active channel.")
    update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} added a project, `{project.name}`.")
    await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

    self.close_check = True
    await interaction.response.defer()

  @discord.ui.button(label="No Project", style=discord.ButtonStyle.danger)
  async def no_project(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.close_check = True
    await interaction.response.defer()

# - - - - - - - - - - - - - - - - -

async def send_new_project_message(interaction,workflow,client):
  """ To send message to Workflow Manager when no 100 Days of Code project is available."""
  initial_message = True
  while True:
    # Creating message.
    embed = discord.Embed(color=discord.Color.dark_red(),title="100 Days of Code",description="Currently no 100 Days of Code project available, would you like to create one?")
    # Creating view.
    view = ApproveDaysOfCode(workflow)
    
    # Sending message.
    if initial_message:
      await interaction.response.send_message(embed=embed,view=view,ephemeral=True)
      initial_message = False
    else:
      await interaction.edit_original_response(embed=embed,view=view)

    await client.wait_for('interaction')

    await asyncio.sleep(0.5)

    if view.close_check:
      await interaction.delete_original_response()
      break

async def send_existing_project_message(interaction,workflow,client):
  """ To send message to Workflow Manager when already 100 Days of Code project."""
  initial_message = True
  while True:
    # Creating message.
    embed = workflow.get_days_of_code().display_message()
    
    # Sending message.
    if initial_message:
      await interaction.response.send_message(embed=embed)
      initial_message = False
    else:
      await interaction.edit_original_response(embed=embed)

    await client.wait_for('interaction')

    await asyncio.sleep(0.5)

async def send_standard_message(interaction,workflow,client):
  """ To send message to standard member when 100 Days of Code project active."""
  project = workflow.get_days_of_code()
  initial_message = True
  while True:
    if interaction.user in project.members:
      # Sending message if member in project.
      embed = project.display_message(interaction.user)
      view = project.get_included_member_view(interaction)
    else:
      # Sending message if member not in project.
      embed = project.display_message(interaction.user)
      view = project.get_excluded_member_view()

    # Sending message.
    if initial_message:
      await interaction.response.send_message(embed=embed,view=view,ephemeral=True)
      initial_message = False
    else:
      await interaction.edit_original_response(embed=embed,view=view)

    await client.wait_for('interaction')

    await asyncio.sleep(0.5)

    if view.close_check:
      await interaction.delete_original_response()
      break

# - - - - - - - - - - - - - - - - -
    
async def restart_days_of_code_looping(workflows,client):
  """ Restarting looping to check progress for days of code projects."""
  while True:
    # Getting all days of code projects.
    days_of_code_projects: list = []
    for guild_id in workflows.keys():
      for project in workflows[guild_id].projects:
        if project.__class__.__name__ == "DaysOfCode":
          days_of_code_projects.append(project)

    # Checking if over 24 hours.
    for project in days_of_code_projects:
      for member_id in project.time_checked.keys():
        if time.time() - project.time_checked[member_id] > 24 * 60 * 60:
          # Updating time.
          project.time_checked[member_id] = time.time()
          # Updating progress.
          if project.progress[member_id][-1] == "m":
            project.progress[member_id][-1] = "n"
          # Adding new day.
          project.progress[member_id].append("m")
    
    # Waiting for interaction.
    await client.wait_for('interaction')