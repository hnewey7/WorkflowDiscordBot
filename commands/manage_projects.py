'''
Module related to the !manage_projects command.

Created on Saturday 3rd February 2024.
@author: Harry New

Utility:
  - Workflow Managers can select from all existing projects and will receive summary. From the
    summary they can chose to assign and remove teams to the project, change the title, descri
    ption, deadline and status.
  - Mangers can select from projects assigned to their teams and choose to add or remove tasks
    , and request completion.
  - Standard team members do not have access to this command and will receive an error message.

'''

from typing import Any
import discord
import asyncio
import logging

from discord.interactions import Interaction
from .misc import get_admin_role, check_team_manager, get_projects_for_member
from .manage_task import IndividualTaskView,get_member_selection

# - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - -

class ProjectSelectMenu(discord.ui.Select):#

  def __init__(self,workflow,command,client):
    super().__init__()
    self.workflow = workflow
    self.command = command
    self.guild = command.guild
    self.client = client

  async def callback(self, interaction: discord.Interaction):
    async_tasks = []
    async_tasks.append(asyncio.create_task(self.proceed_task(interaction)))
    # Getting project from selected project.
    available_projects = self.workflow.projects
    selected_projects = []
    for selected_project in self.values:
      for available_project in available_projects:
        if selected_project == available_project.name:
          selected_projects.append(available_project)
    # Creating tasks for each selected project.
    for project in selected_projects:
      async_tasks.append(asyncio.create_task(self.send_project_message(project)))
    await asyncio.wait(async_tasks,return_when=asyncio.ALL_COMPLETED)
    await interaction.delete_original_response()

  async def proceed_task(self,interaction:discord.Interaction):
    await interaction.response.defer()
  
  async def send_project_message(self,project):
    initial_check = True
    archive_check = False
    while True:
      description = ""
      if project.description:
        description += project.description
      # Creating project message.
      embed = discord.Embed(color=discord.Color.blurple(),title=project.name + f" - due <t:{project.get_unix_deadline()}:R>" ,description=description)
      # Adding status to message.
      status = f"**`{project.status}`**"
      embed.add_field(name="Status:",value=status,inline=True)
      # Adding priority to message.
      if project.priority:
        embed.add_field(name="Priority:",value=f"**`{project.priority}`**",inline=True)
      # Adding teams to message.
      teams_list = ""
      if len(project.get_teams_from_ids(self.workflow)) != 0:
        for team in project.get_teams_from_ids(self.workflow):
          team_role = self.guild.get_role(team.role_id)
          teams_list += f"- {team_role.mention}\n"
      else:
        teams_list += "No teams."
      embed.add_field(name="Teams:",value=teams_list,inline=True)
      # Adding tasks to message.
      task_list = ""
      if len(project.tasks) != 0:
        for task in project.tasks:
          index = 0
          if not task.archive:
            index += 1
            task_members_mention = ""
            task_status = ""
            if task.status:
              task_status += f"**`{task.status}`**"
            for member_id in task.member_ids:
              member = await self.guild.fetch_member(member_id)
              task_members_mention += member.mention 
            task_list += f'{index}. {task.name} Due <t:{task.get_unix_deadline()}:R> {task_members_mention}\n' if task.deadline and task.status != "COMPLETED" else \
            f'{index}. {task.name} {task_status} {task_members_mention}\n'
      else:
        task_list += "No tasks."
      embed.add_field(name="Tasks:",value=task_list,inline=False)

      # Creating relevant view.
      if await get_admin_role(self.guild) in self.command.author.roles:
        view = WorkflowManagerIndividualProjectView(project,self.workflow,self.client,self.guild,self.command)
        # Toggling buttons.
        available_teams = get_team_selection(project,self.workflow,True)
        if len(available_teams) == 0:
          view.assign_team.disabled = True
        available_teams = get_team_selection(project,self.workflow,False)
        if len(available_teams) == 0:
          view.remove_team.disabled = True
        if get_completed_count(project) == 0:
          view.archive_completed.disabled = True
        if get_archive_count(project) == 0:
          view.show_archive.disabled = True
        if archive_check:
          view.show_archive.disabled = True
        else:
          view.hide_archive.disabled = True
      else:
        view = TeamManagerIndividualProjectView(project,self.workflow,self.client,self.guild,self.command)
        # Toggling buttons.
        if get_completed_count(project) == 0:
          view.archive_completed.disabled = True
        if get_archive_count(project) == 0:
          view.show_archive.disabled = True
        if archive_check:
          view.show_archive.disabled = True
        else:
          view.hide_archive.disabled = True

      if archive_check:
        task_list = ""
        if len(project.tasks) != 0:
          for task in project.tasks:
            index = 0
            if task.archive:
              index += 1
              task_members_mention = ""
              task_status = ""
              if task.status:
                task_status += f"**`{task.status}`**"
              for member_id in task.member_ids:
                member = await self.guild.fetch_member(member_id)
                task_members_mention += member.mention 
              task_list += f'{index}. {task.name} Due <t:{task.get_unix_deadline()}:R> {task_members_mention}\n' if task.deadline and task.status != "COMPLETED" else \
              f'{index}. {task.name} {task_status} {task_members_mention}\n'
        else:
          task_list += "No tasks."
        embed.add_field(name="Archived Tasks:",value=task_list,inline=False)

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
      
      # Adding archive to message.
      if view.archive_check:
        archive_check = True
      else:
        archive_check = False

        

class WorkflowManagerIndividualProjectView(discord.ui.View):

  def __init__(self,project,workflow,client,guild,command):
    super().__init__()
    self.project = project
    self.workflow = workflow
    self.client = client
    self.guild = guild
    self.command = command
    self.close_check = False
    self.archive_check = False

  @discord.ui.button(label="Change Title",style=discord.ButtonStyle.primary)
  async def change_title(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending modal for changing project title.
    await interaction.response.send_modal(ChangeTitleModal(self.project))

  @discord.ui.button(label="Change Deadline",style=discord.ButtonStyle.primary)
  async def change_deadline(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending modal for changing project deadline.
    await interaction.response.send_modal(ChangeDeadlineModal(self.project))

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
  async def finish_edit(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.close_check = True

  @discord.ui.button(label="Assign Team",style=discord.ButtonStyle.primary,row=2)
  async def assign_team(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending select team message.
    embed = discord.Embed(colour=discord.Color.blurple(),title="",description=f"Select a team to assign to {self.project.name}:")
    # Creating view for message.
    view = discord.ui.View()
    select_menu = self.create_team_menu(True)
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()

  @discord.ui.button(label="Remove Team",style=discord.ButtonStyle.primary,row=2)
  async def remove_team(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending select team message.
    embed = discord.Embed(colour=discord.Color.blurple(),title="",description=f"Select a team to remove from {self.project.name}:")
    # Creating view for message.
    view = discord.ui.View()
    select_menu = self.create_team_menu(False)
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()

  @discord.ui.button(label="Add Task",style=discord.ButtonStyle.primary,row=2)
  async def add_task(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending add task modal.
    await interaction.response.send_modal(AddTaskModal(project=self.project))
  
  @discord.ui.button(label="Edit Task",style=discord.ButtonStyle.primary,row=2)
  async def edit_task(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending edit task modal.
    await interaction.response.send_modal(EditTaskModal(self.project,self.guild,self.client,self.workflow,self.command))
  
  @discord.ui.button(label="Delete Task",style=discord.ButtonStyle.primary,row=2)
  async def delete_task(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending delete task modal.
    await interaction.response.send_modal(DelTaskModal(project=self.project))

  @discord.ui.button(label="Archive Completed",style=discord.ButtonStyle.primary,row=4)
  async def archive_completed(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Setting all completed tasks to archive.
    for task in self.project.tasks:
      if task.status == "COMPLETED":
        task.archive = True
    await interaction.response.defer()

  @discord.ui.button(label="Show Archive",style=discord.ButtonStyle.primary,row=4)
  async def show_archive(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.archive_check = True
    await interaction.response.defer()

  @discord.ui.button(label="Hide Archive",style=discord.ButtonStyle.primary,row=4)
  async def hide_archive(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.archive_check = False
    await interaction.response.defer()

  def create_team_menu(self,menu_type:bool):
    # Getting available teams.
    available_teams = get_team_selection(self.project,self.workflow,menu_type)
    member_select = TeamSelectMenu(self.workflow,self.project,menu_type)
    member_select.placeholder = "Teams"
    member_select.max_values = len(available_teams)
    member_select.options = available_teams
    return member_select
  
  def create_status_menu(self):
    status_select = StatusSelectMenu(self.project)
    status_select.placeholder = "Status"
    status_select.max_values = 1
    status_select.options = get_status_selection()
    return status_select

  def create_priority_menu(self):
    priority_select = PrioritySelectMenu(self.project)
    priority_select.placeholder = "Priority"
    priority_select.max_values = 1
    priority_select.options = get_priority_selection()
    return priority_select


class TeamManagerIndividualProjectView(discord.ui.View):

  def __init__(self,project,workflow,client,guild,command):
    super().__init__()
    self.project = project
    self.workflow = workflow
    self.client = client
    self.guild = guild
    self.command = command
    self.close_check = False
    self.archive_check = False

  @discord.ui.button(label="Request Approval",style=discord.ButtonStyle.primary)
  async def request_completion(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Changing project status to APPROVAL PENDING.
    self.project.status = "APPROVAL PENDING"
    await interaction.response.defer()

  @discord.ui.button(label="Archive Completed",style=discord.ButtonStyle.primary)
  async def archive_completed(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Setting all completed tasks to archive.
    for task in self.project.tasks:
      if task.status == "COMPLETED":
        task.archive = True
    await interaction.response.defer()

  @discord.ui.button(label="Show Archive",style=discord.ButtonStyle.primary)
  async def show_archive(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.archive_check = True
    await interaction.response.defer()

  @discord.ui.button(label="Hide Archive",style=discord.ButtonStyle.primary)
  async def hide_archive(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.archive_check = False
    await interaction.response.defer()

  @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
  async def finish_edit(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.close_check = True

  @discord.ui.button(label="Add Task",style=discord.ButtonStyle.primary,row=2)
  async def add_task(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending add task modal.
    await interaction.response.send_modal(AddTaskModal(project=self.project))
  
  @discord.ui.button(label="Edit Task",style=discord.ButtonStyle.primary,row=2)
  async def edit_task(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending edit task modal.
    await interaction.response.send_modal(EditTaskModal(self.project,self.guild,self.client,self.workflow,self.command))
  
  @discord.ui.button(label="Delete Task",style=discord.ButtonStyle.primary,row=2)
  async def delete_task(self,interaction:discord.Interaction,button:discord.ui.Button):
    # Sending delete task modal.
    await interaction.response.send_modal(DelTaskModal(project=self.project))


class TeamSelectMenu(discord.ui.Select):
  
  def __init__(self,workflow,project,menu_type):
    super().__init__()
    self.workflow = workflow
    self.project = project
    self.menu_type = menu_type

  async def callback(self, interaction: discord.Interaction):
    for team_title in self.values:
      team = self.workflow.get_team_from_name(team_title)
      if self.menu_type:
        self.project.add_team(team)
        logger.info(f"Assigned {team.name} to ({self.project.name})")
      else:
        self.project.remove_team(team)
        logger.info(f"Removed {team.name} from ({self.project.name})")
    await interaction.response.defer()


class StatusSelectMenu(discord.ui.Select):

  def __init__(self,project):
    super().__init__()
    self.project = project
  
  async def callback(self, interaction: discord.Interaction):
    # Setting status from selected value.
    self.project.change_status(self.values[0])
    logger.info(f"Changed status of ({self.project.name}) to {self.values[0]}.")
    await interaction.response.defer()


class PrioritySelectMenu(discord.ui.Select):
  
  def __init__(self,project):
    super().__init__()
    self.project = project

  async def callback(self, interaction: discord.Interaction):
    # Setting priority from selected value.
    self.project.change_priority(self.values[0])
    logger.info(f"Changed priority of ({self.project.name}) to {self.values}")
    await interaction.response.defer()


# - - - - - - - - - - - - - - - - - -
    
class ChangeTitleModal(discord.ui.Modal,title="Change Title"):

  def __init__(self,project):
    super().__init__()
    self.project = project

  # Requires new title.
  title_input = discord.ui.TextInput(label="Please enter a new title:",style=discord.TextStyle.short,placeholder="Title",required=True)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    # Changing title.
    self.project.name = self.title_input.value
    await interaction.response.defer()


class ChangeDeadlineModal(discord.ui.Modal,title="Change Deadline"):

  def __init__(self,project):
    super().__init__()
    self.project = project

  # Requires new deadline.
  deadline_input = discord.ui.TextInput(label="Please enter a deadline (dd mm yyyy):",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=True,max_length=10)

  async def on_submit(self, interaction: discord.Interaction) -> None:
    # Changing title.
    self.project.edit_deadline(self.deadline_input.value)
    await interaction.response.defer()


class AddTaskModal(discord.ui.Modal,title="Add Task"):

  def __init__(self,project):
    super().__init__()
    self.project = project

  # Requires task name and deadline.
  task_input = discord.ui.TextInput(label="Please enter a task name:",style=discord.TextStyle.short,placeholder="Name",required=True,max_length=100)
  deadline_input =  discord.ui.TextInput(label="Please enter a task deadline (dd mm yyyy):",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=False,max_length=10)

  async def on_submit(self, interaction: discord.Interaction):
    # Checking if deadline entered.
    if self.deadline_input.value == "":
      self.project.add_task(self.task_input.value,None)
    else:
      # Adding task to project.
      self.project.add_task(self.task_input.value,self.deadline_input.value)
    await interaction.response.defer()


class DelTaskModal(discord.ui.Modal,title="Delete Task"):

  def __init__(self,project):
    super().__init__()
    self.project = project

  # Requires task number to delete.
  number_input = discord.ui.TextInput(label="Please enter a task number:",style=discord.TextStyle.short,placeholder="Task Number",required=True,max_length=2)

  async def on_submit(self, interaction: discord.Interaction):
    # Deleting task from project.
    count = 0
    for task in self.project.tasks:
      if not task.archive:
        count += 1
      if count == int(self.number_input.value):
        self.project.tasks.remove(task)
        await interaction.response.defer()


class EditTaskModal(discord.ui.Modal,title="Edit Task"):

  def __init__(self,project,guild,client,workflow,command):
    super().__init__()
    self.project = project
    self.guild = guild
    self.client = client
    self.workflow = workflow
    self.command = command

  # Requires task number
  number_input = discord.ui.TextInput(label="Please enter a task number:",style=discord.TextStyle.short,placeholder="Task Number",required=True,max_length=2)

  async def on_submit(self, interaction: discord.Interaction):
    # Editing task from project.
    count = 0
    for task in self.project.tasks:
      if not task.archive:
        count += 1
      if count == int(self.number_input.value):
        break
    
    # Creating tasks.
    tasks = []
    tasks.append(await asyncio.create_task(progress(interaction)))
    tasks.append(await asyncio.create_task(send_edit_task_message(task,self.guild,self.client,self.workflow,self.command)))
    await asyncio.wait(tasks)

# - - - - - - - - - - - - - - - - - -
      
async def progress(interaction):
  await interaction.response.defer()

async def send_edit_task_message(task,guild,client,workflow,command):
  # Sending edit task message.
  initial_check = True
  while True:
    # Getting task members.
    task_members = []
    for member_id in task.member_ids:
      task_members.append(guild.get_member(member_id))
  
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
    # Adding log to message.
    if len(task.logs.keys()) != 0:
      log_list = ""
      for log_date in task.logs.keys():
        # Getting log author.
        log_author = guild.get_member(task.logs[log_date][1])
        log_list += f"`{log_date}` {task.logs[log_date][0]} {log_author.mention}\n"
      embed.add_field(name="Log:",value=log_list,inline=False)

    view = IndividualTaskView(task,guild,client,workflow)

    # Toggling buttons.
    available_members = get_member_selection(task,workflow,guild,True)
    if len(available_members) == 0:
      view.assign_member.disabled = True

    available_members = get_member_selection(task,workflow,guild,False)
    if len(available_members) == 0:
      view.remove_member.disabled = True

    if initial_check:
      message = await command.channel.send(embed=embed,view=view,delete_after=300)
      initial_check = False
      await client.wait_for("interaction")
    else:
      await message.edit(embed=embed,view=view,delete_after=300)
      await client.wait_for("interaction")

    # Checking to close message.
    if view.close_check:
      await message.delete()
      break


# - - - - - - - - - - - - - - - - - -
    
def create_project_options(projects):
  options = []
  for project in projects:
    option = discord.SelectOption(label=project.name)
    options.append(option)
  return options

def get_team_selection(project,workflow,menu_type):
  available_teams = []
  if menu_type:
    # Selecting from unassigned teams.
    for team in workflow.teams:
      if team not in project.get_teams_from_ids(workflow):
        available_teams.append(team)
    # Selecting from assigned teams.
  else:
    for team in project.get_teams_from_ids(workflow):
      available_teams.append(team)

  # Converting to select options.
  options = []
  for team in available_teams:
    option = discord.SelectOption(label=team.name)
    options.append(option)
  return options

def get_status_selection():
  statuses = ["PENDING","COMPLETED"]
  options = []
  for status in statuses:
    option = discord.SelectOption(label=status)
    options.append(option)
  return options

def get_priority_selection():
  priorities = ["LOW","MEDIUM","HIGH","URGENT","EMERGENCY"]
  options = []
  for priority in priorities:
    option = discord.SelectOption(label=priority)
    options.append(option)
  return options

def get_completed_count(project):
  count = 0
  for task in project.tasks:
    if task.status == "COMPLETED" and task.archive == False:
      count += 1
  return count

def get_archive_count(project):
  count = 0
  for task in project.tasks:
    if task.archive:
      count += 1
  return count

# - - - - - - - - - - - - - - - - - -

async def manage_projects(command,client,workflow):
  # Workflow Manager functionality.
  if await get_admin_role(command.guild) in command.author.roles:
    logger.info("Command request approved.")
    channel = command.channel
    # Creating embed and view.
    embed = discord.Embed(color=discord.Color.blurple(),description="Please select a project to manage:")
    view = discord.ui.View()
    # Creating project select menu.
    project_select_menu = ProjectSelectMenu(workflow,command,client)
    available_projects = workflow.projects
    available_project_options = create_project_options(available_projects)
    if len(available_projects) != 0:
      project_select_menu.placeholder = "Projects"
      project_select_menu.max_values = len(available_projects)
      project_select_menu.options = available_project_options
      view.add_item(project_select_menu)
      # Sending  message to channel.
      await channel.send(embed=embed,view=view,delete_after=300)
    else:
      embed = discord.Embed(color=discord.Color.blurple(),description="No projects to manage.")
      await channel.send(embed=embed,delete_after=300)
  # Team Manager functionality.
  else:
    if check_team_manager(command.author,command.guild,workflow):
      logger.info("Command request approved.")
      channel = command.channel
      # Creating embed and view.
      embed = discord.Embed(color=discord.Color.blurple(),description="Please select a project to manage:")
      view = discord.ui.View()
      # Creating project select menu.
      project_select_menu = ProjectSelectMenu(workflow,command,client)
      available_projects = get_projects_for_member(command.author,workflow)
      available_project_options = create_project_options(available_projects)
      if len(available_projects) != 0:
        project_select_menu.placeholder = "Projects"
        project_select_menu.max_values = len(available_projects)
        project_select_menu.options = available_project_options
        view.add_item(project_select_menu)
        # Sending  message to channel.
        await channel.send(embed=embed,view=view,delete_after=300)
      else:
        embed = discord.Embed(color=discord.Color.blurple(),description="No projects to manage.")
        await channel.send(embed=embed,delete_after=300)
    else:
      # Sending private message.
      await command.author.send("You do not have the necessary role to manage projects.")