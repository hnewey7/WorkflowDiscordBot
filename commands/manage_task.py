'''
Module for !manage_tasks command.

Created on Tuesday 6th February 2024.
@author: Harry New

'''

from typing import Any
import discord
import logging
import asyncio

from discord.interactions import Interaction
from .misc import get_admin_role

# - - - - - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - - - - - -
    
class TaskSelectMenu(discord.ui.Select):

  def __init__(self,command,workflow,client):
    super().__init__()
    self.command = command
    self.guild = command.guild
    self.workflow = workflow
    self.client = client

  async def callback(self, interaction: discord.Interaction):
    async_tasks = []
    async_tasks.append(asyncio.create_task(self.proceed_task(interaction)))
    # Getting tasks from selected task.
    available_tasks = get_available_tasks(self.command,self.workflow)
    selected_tasks = []
    for selected_task in self.values:
      for available_task in available_tasks:
        if selected_task == available_task.name:
          selected_tasks.append(available_task)
    # Creating tasks for each selected task.
    for task in selected_tasks:
      async_tasks.append(asyncio.create_task(self.send_task_message(task)))
    await asyncio.wait(async_tasks,return_when=asyncio.ALL_COMPLETED)
    await interaction.delete_original_response()

  async def proceed_task(self,interaction:discord.Interaction):
    await interaction.response.defer()

  async def send_task_message(self,task):
    initial_check = True
    while True:
      # Getting task members.
      task_members = []
      for member_id in task.member_ids:
        task_members.append(self.guild.get_member(member_id))
    
      # Getting description.
      if task.description:
        description = task.description
      else:
        description = ""

      # Creating individual teams message.
      embed = discord.Embed(color=discord.Color.blurple(),title=task.name,description=description)
      # Adding status to message.
      status = f"**`{task.status}`**"
      embed.add_field(name="Status:",value=status,inline=True)
      # Adding priority to message.
      if task.priority:
        embed.add_field(name="Priority:",value=task.priority,inline=True)
      # Adding members to message.
      if len(task_members) != 0:
        description = ""
        for member in task_members:
          description += f'- {member.name}\n'
      else:
        description = "No members."
      embed.add_field(name="Current members:",value=description,inline=True)

      view = IndividualTaskView(task,self.guild,self.client,self.workflow)

      # Toggling buttons.
      available_members = get_member_selection(task,self.workflow,self.guild,True)
      if len(available_members) == 0:
        view.assign_member.disabled = True

      available_members = get_member_selection(task,self.workflow,self.guild,False)
      if len(available_members) == 0:
        view.remove_member.disabled = True

      if initial_check:
        message = await self.command.channel.send(embed=embed,view=view,delete_after=300)
        initial_check = False
        await self.client.wait_for("interaction")
      else:
        await message.edit(embed=embed,view=view,delete_after=300)
        await self.client.wait_for("interaction")

      # Checking to close message.
      if view.close_check:
        await message.delete()
        break


class IndividualTaskView(discord.ui.View):

  def __init__(self,task,guild,client,workflow):
    super().__init__()
    self.task = task
    self.guild = guild
    self.client = client
    self.close_check = False
    self.workflow = workflow

  def create_member_menu(self,menu_type:bool):
    # Getting available members.
    available_members = get_member_selection(self.task,self.workflow,self.guild,menu_type)
    member_select = MemberSelectMenu(self.guild,self.task,menu_type)
    member_select.placeholder = "Members"
    member_select.max_values = len(available_members)
    member_select.options = available_members
    return member_select
  
  def create_priority_menu(self):
    priority_select = PrioritySelectMenu(self.task)
    priority_select.placeholder = "Priority"
    priority_select.max_values = 1
    priority_select.options = get_priority_selection()
    return priority_select
  
  def create_status_menu(self):
    status_select = StatusSelectMenu(self.task)
    status_select.placeholder = "Status"
    status_select.max_values = 1
    status_select.options = get_status_selection()
    return status_select

  @discord.ui.button(label="Change Description",style=discord.ButtonStyle.primary)
  async def change_description(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending description modal.
    await interaction.response.send_modal(DescriptionModal(self.task))

  @discord.ui.button(label="Change Status",style=discord.ButtonStyle.primary)
  async def change_status(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending message to change status.
    view = discord.ui.View()
    # Creating embed.
    embed = discord.Embed(color=discord.Color.blurple(),description=f"Select a status for the task:")
    # Creating select menu.
    select_menu = self.create_status_menu()
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()

  @discord.ui.button(label="Change Priority",style=discord.ButtonStyle.primary)
  async def change_priority(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending message to set priority.
    view = discord.ui.View()
    # Creating embed.
    embed = discord.Embed(color=discord.Color.blurple(),description=f"Select a priority for the task:")
    # Creating select menu.
    select_menu = self.create_priority_menu()
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()

  @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
  async def finish_edit(self,interaction:discord.Interaction,button:discord.Button):
    self.close_check = True

  @discord.ui.button(label="Assign Member",style=discord.ButtonStyle.primary,row=3)
  async def assign_member(self,interaction:discord.Interaction,button:discord.ui.Button):
    view = discord.ui.View()
    # Creating embed.
    embed = discord.Embed(color=discord.Color.blurple(),description=f"Select a member to assign to the task:")
    # Creating select menu.
    select_menu = self.create_member_menu(True)
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()

  @discord.ui.button(label="Remove Member",style=discord.ButtonStyle.primary,row=3)
  async def remove_member(self,interaction:discord.Interaction,button:discord.Button):
    view = discord.ui.View()
    # Creating embed.
    embed = discord.Embed(color=discord.Color.blurple(),description=f"Select a member to remove from the task:")
    # Creating select menu.
    select_menu = self.create_member_menu(False)
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()


class MemberSelectMenu(discord.ui.Select):

  def __init__(self,guild,task,menu_type):
    super().__init__()
    self.guild = guild
    self.task = task
    self.menu_type = menu_type

  async def callback(self, interaction: discord.Interaction):
    for member_title in self.values:
      member = self.guild.get_member_named(member_title)
      if self.menu_type:
        if member.id not in self.task.member_ids:
          self.task.member_ids.append(member.id)
          logger.info(f"Assigned {member.name} to ({self.task.name})")
      else:
        self.task.member_ids.remove(member.id)
        logger.info(f"Removed {member.name} from ({self.task.name})")
    await interaction.response.defer()


class PrioritySelectMenu(discord.ui.Select):
  
  def __init__(self,task):
    super().__init__()
    self.task = task

  async def callback(self, interaction: discord.Interaction):
    # Setting priority from selected value.
    self.task.change_priority(self.values[0])
    logger.info(f"Changed priority of ({self.task.name}) to {self.values}")
    await interaction.response.defer()


class StatusSelectMenu(discord.ui.Select):

  def __init__(self,task):
    super().__init__()
    self.task = task
  
  async def callback(self, interaction: discord.Interaction):
    # Setting status from selected value.
    self.task.change_status(self.values[0])
    logger.info(f"Changed status of ({self.task.name}) to {self.values[0]}.")
    await interaction.response.defer()

# - - - - - - - - - - - - - - - - - - - - - -
    
class DescriptionModal(discord.ui.Modal,title="Change Description"):

  def __init__(self,task):
    super().__init__()
    self.task = task 
  
  # Requires description input.
  description_input = discord.ui.TextInput(label="Please enter a new task description:",style=discord.TextStyle.long,placeholder="Description",required=False)

  async def on_submit(self, interaction: discord.Interaction):
    # Changing description.
    self.task.change_description(self.description_input.value)
    await interaction.response.defer()

# - - - - - - - - - - - - - - - - - - - - - -

def get_available_tasks(command,workflow):
  user = command.author
  # Getting teams from the user's roles.
  teams = []
  for role in user.roles:
    for team in workflow.teams:
      if role.id == team.manager_role_id:
        teams.append(team)
  # Getting project ids from all teams.
  project_ids = []
  for team in teams:
    for project in team.get_projects_from_ids(workflow):
      if project.id not in project_ids:
        project_ids.append(project.id)
  # Getting projects from project ids.
  projects = []
  for project_id in project_ids:
    projects.append(workflow.get_project_by_id(project_id))
  # Getting tasks from projects.
  available_tasks = []
  for project in projects:
    for task in project.tasks:
      if not task.archive:
        available_tasks.append(task)
  return available_tasks

def create_task_options(tasks):
  # Creating task options.
  available_task_options = []
  for task in tasks:
    option = discord.SelectOption(label=task.name)
    available_task_options.append(option)
  return available_task_options

# - - - - - - - - - - - - - - - - - - - - - -

def get_member_selection(task,workflow,guild,menu_type):
  # Getting members.
  member_selection = []
  if menu_type:
    for team in workflow.get_project_by_id(task.project).get_teams_from_ids(workflow):
      role = guild.get_role(team.role_id)
      for member in role.members:
        if member not in member_selection and member.id not in task.member_ids:
          member_selection.append(member)
  else:
    for member_id in task.member_ids:
      member = guild.get_member(member_id)
      member_selection.append(member)
  
  # Creating discord options.
  member_selection_options = []
  for member in member_selection:
    option = discord.SelectOption(label=member.name)
    member_selection_options.append(option)

  return member_selection_options

def get_priority_selection():
  priorities = ["LOW","MEDIUM","HIGH","URGENT","EMERGENCY"]
  options = []
  for priority in priorities:
    option = discord.SelectOption(label=priority)
    options.append(option)
  return options

def get_status_selection():
  statuses = ["PENDING","COMPLETED"]
  options = []
  for status in statuses:
    option = discord.SelectOption(label=status)
    options.append(option)
  return options

# - - - - - - - - - - - - - - - - - - - - - -

async def manage_tasks(command,client,workflow):
  if await get_admin_role(command.guild) in command.author.roles:
    logger.info("Command request approved.")
    channel = command.channel
    # Creating embed and view.
    embed = discord.Embed(color=discord.Color.blurple(),description="Please select a task to manage:")
    view = discord.ui.View()
    # Creating select menu.
    task_select_menu = TaskSelectMenu(command,workflow,client)
    available_tasks = get_available_tasks(command,workflow)
    available_task_options = create_task_options(available_tasks)
    if len(available_tasks) != 0:
      task_select_menu.placeholder = "Tasks"
      task_select_menu.max_values = len(available_tasks)
      task_select_menu.options = available_task_options
      view.add_item(task_select_menu)
      # Sending  message to channel.
      await channel.send(embed=embed,view=view,delete_after=300)
    else:
      embed = discord.Embed(color=discord.Color.blurple(),description="No tasks to manage.")
      await channel.send(embed=embed,delete_after=300)
  else:
    # Sending private message.
    await command.user.send("You do not have the necessary role to manage tasks.")