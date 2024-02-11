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
from .misc import get_admin_role, get_team_manager_roles

# - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - -
'''
class ManageProjectsView(discord.ui.View):

  def __init__(self, workflow,command,client):
    super().__init__()
    self.workflow= workflow
    self.command = command
    self.guild = command.guild
    self.client = client

  def get_team_selection(self,role_selection):
    team_selection = []
    # Getting team selection.
    for role in role_selection:
      if " Manager" not in role.name:
        team = self.workflow.get_team_from_role_id(role.id)
      else:
        team = self.workflow.get_team_from_manager_id(role.id)
      # Adding team to selection.
      if team not in team_selection:
        team_selection.append(team)
    return team_selection

  @discord.ui.select(cls=discord.ui.RoleSelect,placeholder="Team",max_values=25)
  async def select_team(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
    async_tasks = []
    async_tasks.append(asyncio.create_task(self.proceed_task()))
    for team in self.get_team_selection(select.values):
      async_tasks.append(asyncio.create_task(self.send_team_message(team)))
    await asyncio.wait(async_tasks,return_when=asyncio.FIRST_COMPLETED)
    await interaction.response.defer()
  
  async def proceed_task(self):
    pass

  async def send_team_message(self,team):
    standard_role = self.guild.get_role(team.role_id)
    initial_check = True
    while True:
      # Creating individual teams message.
      embed = discord.Embed(color=standard_role.colour,title=team.name)
      # Adding current projects to message.
      if len(team.projects) != 0:
        description = ""
        for project in team.projects:
          description += f'{team.projects.index(project)+1}. {project.name} - Deadline <t:{project.get_unix_deadline()}:R>\n' if project.deadline else \
        f'{team.projects.index(project)+1}. {project.name}\n'
      else:
        description = "No projects."
      embed.add_field(name="Current Projects:",value=description,inline=False)
      # Creating view to add projects.
      view = IndividualTeamView(self.workflow,team,self.client,standard_role)

      # Toggling buttons.
      available_projects = get_project_selection(self.workflow,team,True)
      if len(available_projects) == 0:
        view.assign_project.disabled = True
      
      available_projects = get_project_selection(self.workflow,team,False)
      if len(available_projects) == 0:
        view.remove_project.disabled = True
      
      if initial_check:
        message = await self.command.channel.send(embed=embed,view=view,delete_after=300)
        initial_check = False
        await self.client.wait_for("interaction")
      else:
        await message.edit(embed=embed,view=view,delete_after=300)
        await self.client.wait_for("interaction")
    

class IndividualTeamView(discord.ui.View):

  def __init__(self,workflow,team,client,role):
    super().__init__()
    self.workflow = workflow
    self.team = team
    self.client = client
    self.role = role
  
  def create_select_menu(self,menu_type: bool):
    # Creating select menu.
    available_projects = get_project_selection(self.workflow,self.team,menu_type)
    project_select = ProjectSelectMenu(self.workflow,self.team,menu_type)
    project_select.placeholder = "Projects"
    project_select.max_values = len(available_projects)
    project_select.options = available_projects
    return project_select

  @discord.ui.button(label="Assign Project",style=discord.ButtonStyle.primary)
  async def assign_project(self,interaction: discord.Interaction,button: discord.ui.Button):
    view = discord.ui.View()
    # Creating embed.
    embed = discord.Embed(color=self.role.colour,description=f"Select a project to assign to {self.role.name}:")
    # Creating select menu.
    select_menu = self.create_select_menu(True)
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()

  @discord.ui.button(label="Remove Project",style=discord.ButtonStyle.primary)
  async def remove_project(self,interaction: discord.Interaction,button: discord.ui.Button):
    view = discord.ui.View()
    # Creating embed.
    embed = discord.Embed(color=self.role.colour,description=f"Select a project to remove from {self.role.name}:")
    # Creating select menu.
    select_menu = self.create_select_menu(False)
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()


class ProjectSelectMenu(discord.ui.Select):

  def __init__(self,workflow,team,menu_type):
    super().__init__()
    self.workflow = workflow
    self.team = team
    self.menu_type = menu_type

  async def callback(self, interaction: discord.Interaction):
    for project_title in self.values:
      project = self.workflow.get_project_from_title(project_title)
      if self.menu_type:
        self.team.add_project(project)
        logger.info(f"Assigned {project.name} to {self.team.name}")
      else:
        self.team.del_project(project)
        logger.info(f"Removed {project.name} from {self.team.name}")
    await interaction.response.defer()


# - - - - - - - - - - - - - - - - - -
    
def get_project_selection(workflow,team,menu_type):
    project_selection = []
    # Creating project option.
    if menu_type:
      for project in workflow.projects:
        if project not in team.projects:
          project_option = discord.SelectOption(label=project.name)
          project_selection.append(project_option)
    else:
      for project in team.projects:
        project_option = discord.SelectOption(label=project.name)
        project_selection.append(project_option)
    return project_selection

'''

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
    while True:
      description = ""
      # Creating project message.
      embed = discord.Embed(color=discord.Color.blurple(),title=project.name + f" - due <t:{project.get_unix_deadline()}:R>" ,description=description)
      # Adding status to message.
      status = "**`Pending`**"
      embed.add_field(name="Status:",value=status,inline=True)
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
          task_members_mention = ""
          task_status = ""
          if task.complete:
            task_status += "**`COMPLETED`**"
          for member_id in task.member_ids:
            member = await self.workflow.active_message.guild.fetch_member(member_id)
            task_members_mention += member.mention 
          task_list += f'{project.tasks.index(task)+1}. {task.name} Due <t:{task.get_unix_deadline()}:R> {task_members_mention}\n' if task.deadline else \
          f'{project.tasks.index(task)+1}. {task.name} {task_status} {task_members_mention}\n'
      else:
        task_list += "No tasks."
      embed.add_field(name="Tasks:",value=task_list,inline=False)

      # Creating buttons view.
      view = IndividualProjectView(project,self.workflow,self.client)

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
        

class IndividualProjectView(discord.ui.View):

  def __init__(self,project,workflow,client):
    super().__init__()
    self.project = project
    self.workflow = workflow
    self.client = client
    self.close_check = False

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
    await interaction.response.defer()

  @discord.ui.button(label="Change Priority",style=discord.ButtonStyle.primary)
  async def change_priority(self,interaction:discord.Interaction,button:discord.ui.Button):
    await interaction.response.defer()

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

  def create_team_menu(self,menu_type:bool):
    # Getting available teams.
    available_teams = get_team_selection(self.project,self.workflow,menu_type)
    member_select = TeamSelectMenu(self.workflow,self.project,menu_type)
    member_select.placeholder = "Teams"
    member_select.max_values = len(available_teams)
    member_select.options = available_teams
    return member_select
  

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
      print(team)
      if team not in project.get_teams_from_ids(workflow):
        available_teams.append(team)
    # Selecting from assigned teams.
    else:
      for team in project.get_teams_from_ids(workflow):
        available_teams.append(team)

  # Converting to select options.
  options = []
  print(available_teams)
  for team in available_teams:
    option = discord.SelectOption(label=team.name)
    options.append(option)
  return options

# - - - - - - - - - - - - - - - - - -

async def manage_projects(command,client,workflow):
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
  else:
    # Sending private message.
    await command.user.send("You do not have the necessary role to manage projects.")