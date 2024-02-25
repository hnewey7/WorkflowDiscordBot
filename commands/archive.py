'''
Module to handle displaying the project archive.

Created on Saturday 24th February 2024.
@author: Harry New

'''

import discord
import math
import asyncio

from .manage_task import ManagerIndividualTaskView

# - - - - - - - - - - - - - - - - -

class ArchiveButtonView(discord.ui.View):

  def __init__(self,project,guild,client,workflow,page_display):
    super().__init__()
    self.project = project
    self.guild = guild
    self.client = client
    self.workflow = workflow
    self.page_down_check = False
    self.page_up_check = False
    self.page_display = page_display
    self.close_check = False

  @discord.ui.button(label="Unarchive Task",style=discord.ButtonStyle.primary)
  async def unarchive_task(self,interaction:discord.Interaction,button:discord.Button):
    # Sending edit task modal.
    await interaction.response.send_modal(UnarchiveTaskModal(self.project,self.guild,self.client,self.workflow,interaction,self.page_display))

  @discord.ui.button(label="Edit Task",style=discord.ButtonStyle.primary)
  async def edit_task(self,interaction:discord.Interaction,button:discord.Button):
    # Sending edit task modal.
    await interaction.response.send_modal(EditTaskModal(self.project,self.guild,self.client,self.workflow,interaction,self.page_display))
  
  @discord.ui.button(label="Clear Task",style=discord.ButtonStyle.primary)
  async def clear_task(self,interaction:discord.Interaction,button:discord.Button):
    # Sending edit task modal.
    await interaction.response.send_modal(ClearTaskModal(self.project,self.guild,self.client,self.workflow,interaction,self.page_display))

  @discord.ui.button(label="Finish",style=discord.ButtonStyle.success)
  async def finish(self,interaction:discord.Interaction,button:discord.Button):
    self.close_check = True

  @discord.ui.button(label="Page Down",style=discord.ButtonStyle.primary,row=2)
  async def page_down(self,interaction:discord.Interaction,button:discord.Button):
    self.page_down_check = True
    await interaction.response.defer()

  @discord.ui.button(label="Page Up",style=discord.ButtonStyle.primary,row=2)
  async def page_up(self,interaction:discord.Interaction,button:discord.Button):
    self.page_up_check = True
    await interaction.response.defer()

# - - - - - - - - - - - - - - - - -

class UnarchiveTaskModal(discord.ui.Modal,title="Unarchive Task"):

  def __init__(self,project,guild,client,workflow,command,page_display):
    super().__init__()
    self.project = project
    self.guild = guild
    self.client = client
    self.workflow = workflow
    self.command = command
    self.page_display = page_display

  # Requires task number
  number_input = discord.ui.TextInput(label="Please enter a task number:",style=discord.TextStyle.short,placeholder="Task Number",required=True,max_length=2)

  async def on_submit(self, interaction: discord.Interaction):
    # Unarchiving task from project.
    count = 0
    for task in self.project.tasks:
      if task.archive:
        count += 1
      if count == int(self.number_input.value):
        task.archive = False
        await interaction.response.defer()


class EditTaskModal(discord.ui.Modal,title="Edit Task"):

  def __init__(self,project,guild,client,workflow,command,page_display):
    super().__init__()
    self.project = project
    self.guild = guild
    self.client = client
    self.workflow = workflow
    self.command = command
    self.page_display = page_display

  # Requires task number
  number_input = discord.ui.TextInput(label="Please enter a task number:",style=discord.TextStyle.short,placeholder="Task Number",required=True,max_length=2)

  async def on_submit(self, interaction: discord.Interaction):
    # Editing task from project.
    count = 0
    for task in self.project.tasks:
      if task.archive:
        count += 1
      if count == int(self.number_input.value):
        # Creating tasks.
        await send_edit_task_message(task,self.guild,self.client,self.workflow,self.command,interaction)


class ClearTaskModal(discord.ui.Modal,title="Clear Task"):

  def __init__(self,project,guild,client,workflow,command,page_display):
    super().__init__()
    self.project = project
    self.guild = guild
    self.client = client
    self.workflow = workflow
    self.command = command
    self.page_display = page_display

  # Requires task number
  number_input = discord.ui.TextInput(label="Please enter a task number:",style=discord.TextStyle.short,placeholder="Task Number",required=True,max_length=2)

  async def on_submit(self, interaction: discord.Interaction):
    # Unarchiving task from project.
    count = 0
    for task in self.project.tasks:
      if task.archive:
        count += 1
      if count == int(self.number_input.value):
        self.project.tasks.remove(task)
        await interaction.response.defer()

# - - - - - - - - - - - - - - - - -
    
async def send_edit_task_message(task,guild,client,workflow,command,interaction):
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

    view = ManagerIndividualTaskView(task,guild,client,workflow,command.user)

    # Toggling buttons.
    available_members = get_member_selection(task,workflow,guild,True)
    if len(available_members) == 0:
      view.assign_member.disabled = True

    available_members = get_member_selection(task,workflow,guild,False)
    if len(available_members) == 0:
      view.remove_member.disabled = True

    if initial_check:
      await interaction.response.send_message(embed=embed,view=view,delete_after=300,ephemeral=True)
      initial_check = False
      await client.wait_for("interaction")
    else:
      await interaction.edit_original_response(embed=embed,view=view)
      await client.wait_for("interaction")

    await asyncio.sleep(0.5)

    # Checking to close message.
    if view.close_check:
      await interaction.delete_original_response()
      break


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

# - - - - - - - - - - - - - - - - -

async def send_archive_display(interaction: discord.Interaction,project,guild,client,workflow):
  initial_check = True
  page_display = 1
  fields_per_embed = 27
  while True:
  
    # Calculating number of archive tasks.
    archive_counter = 0
    for task in project.tasks:
      if task.archive:
        archive_counter += 1

    # Calculating total number of pages.
    total_pages = math.ceil(archive_counter/(fields_per_embed-2))

    if total_pages == 0:
      await interaction.delete_original_response()

    if page_display > total_pages:
      page_display = total_pages

    if len(project.tasks) != 0:
      # Creating archive message.
      embed = discord.Embed(color=discord.Color.blurple(),title=f"Archived Tasks ({page_display}/{total_pages})")

      counter = (page_display-1) * (fields_per_embed - 2)

      for index, task in enumerate(project.tasks):
        if index < (page_display * fields_per_embed) and index >= (page_display-1)*fields_per_embed:
          if task.archive:
            counter += 1
            task_members_mention = ""
            task_status = ""
            if task.status:
              task_status += f"**`{task.status}`**"
            for member_id in task.member_ids:
              member = await guild.fetch_member(member_id)
              task_members_mention += member.mention 
            task_list = f'{counter}. {task.name} Due <t:{task.get_unix_deadline()}:R>' if task.deadline and task.status != "COMPLETED" else \
            f'{counter}. {task.name} {task_status}\n'

            embed.add_field(name=task_list,value=task_members_mention,inline=False)
    else:
      task_list = "No tasks."
      embed = discord.Embed(color=discord.Color.blurple(),title=f"Archived Tasks ({page_display}/{total_pages})",description=task_list)

    view = ArchiveButtonView(project,guild,client,workflow,page_display)

    if page_display == total_pages:
      view.page_up.disabled = True
    if page_display == 1:
      view.page_down.disabled = True

    if initial_check:
      await interaction.response.send_message(embed=embed,view=view,delete_after=300,ephemeral=True)
      initial_check = False
      await client.wait_for("interaction")
    else:
      await interaction.edit_original_response(embed=embed,view=view)
      await client.wait_for("interaction")
    
    await asyncio.sleep(0.5)

    if view.page_up_check:
      page_display += 1
    if view.page_down_check:
      page_display -= 1
    
    if view.close_check:
      await interaction.delete_original_response()
    
    
    