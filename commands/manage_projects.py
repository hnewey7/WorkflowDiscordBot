'''
Module related to the !manage_projects command.

Created on Saturday 3rd February 2024.
@author: Harry New

'''

import discord
import asyncio
import logging
from .misc import get_admin_role

# - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - -

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
          description += f'{team.projects.index(project)+1}. {project.title} - Deadline <t:{project.get_unix_deadline()}:R>\n' if project.deadline else \
        f'{team.projects.index(project)+1}. {project.title}\n'
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
        logger.info(f"Assigned {project.title} to {self.team.name}")
      else:
        self.team.del_project(project)
        logger.info(f"Removed {project.title} from {self.team.name}")
    await interaction.response.defer()


# - - - - - - - - - - - - - - - - - -
    
def get_project_selection(workflow,team,menu_type):
    project_selection = []
    # Creating project option.
    if menu_type:
      for project in workflow.projects:
        if project not in team.projects:
          project_option = discord.SelectOption(label=project.title)
          project_selection.append(project_option)
    else:
      for project in team.projects:
        project_option = discord.SelectOption(label=project.title)
        project_selection.append(project_option)
    return project_selection

# - - - - - - - - - - - - - - - - - -

async def manage_projects(command,client,workflow):
  if await get_admin_role(command.guild) in command.author.roles:
    logger.info("Command request approved.")
    channel = command.channel
    # Creating embed and view.
    embed = discord.Embed(color=discord.Color.blurple(),description="Please select a role to manage their projects:")
    view = ManageProjectsView(workflow,command,client)
    # Sending  message to channel.
    await channel.send(embed=embed,view=view,delete_after=300)
  else:
    # Sending private message.
    await command.user.send("You do not have the necessary role to manage projects.")