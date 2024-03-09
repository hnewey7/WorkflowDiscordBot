'''
Module for handling types of project templates.

Created on Sunday 3rd March 2024.
@author: Harry New

'''


from typing import Any, Coroutine, List
import discord
import workflow
import logging
import time

# - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - -

class DaysOfCode(workflow.Project):

  def __init__(self, id) -> None:
    super().__init__("100 Days of Code", id, None)
    self.add_task("Complete 1 hour of coding each day for 100 days.",None)
    self.description = "The aim of this project is to jump start your coding journey with 100 days of consistent programming. Be sure to share your progress with others also embarking on the same journey."

    # List of members, progress and time dictionaries.
    self.members: list[discord.Member] = []
    self.member_ids: list = []
    self.progress: dict = {}
    self.time_checked: dict = {}

  def add_member(self,member) -> None:
    """ Adding members and initialising progress."""
    self.members.append(member)
    self.progress[member.id] = ["m"]
    self.time_checked[member.id] = time.time()

  def add_member_from_id(self,id,guild) -> None:
    """ Adding member from id."""
    self.members

  def get_progress_string(self,member) -> str:
    """ Producing string of member progress."""
    output: str = ""
    counter: int = 0
    total: int = 0
    individual_list: list[str] = []
    # Producing full output.
    for character in self.progress[member.id]:
      if character == "y":
        individual_list.append(":green_circle:")
        counter += 1
      elif character == "m":
        individual_list.append(":white_circle:")
      elif character == "n":
        individual_list.append(":red_circle:")
      total += 1

    # Condensing output.
    if len(self.progress[member.id]) > 10:
      output = "".join(individual_list[:5]) + "..." + "".join(individual_list[-5:]) + f" {counter}/{total}"
    else:
      output = "".join(individual_list) + f" {counter}/{total}"
    return output
  
  def get_top_progess(self,exclude=None) -> str:
    """ Producing string of top members."""
    output: str = ""
    member_score: dict = {}
    # Getting all members scores.
    for member in self.members:
      if member != exclude:
        count = 0
        for character in self.progress[member.id]:
          if character == "y":
            count += 1
        member_score[member] = count
    # Sorting and getting top members.
    sorted_score = dict(sorted(member_score.items(), key=lambda item: item[1], reverse=True))
    top_items_count = min(10, len(sorted_score))
    top_members =  dict(list(sorted_score.items())[:top_items_count])
    # Creating string output.
    for member in top_members.keys():
      output += f"- {member.mention} - {self.get_progress_string(member)}\n"
    return output

  def manage_progress(self,member,addition) -> None:
    """ To manage progress of an individual member."""
    self.progress[member.id][-1] = addition

  def display_message(self,active_member) -> discord.Embed:
    """ To display message specificaly for 100 days of code project."""
    embed = discord.Embed(color=discord.Color.dark_red(),title=self.name,description=self.description)
    
    # Creating field for members and progress.
    member_progress = ""
    if len(self.members) != 0:
      if active_member in self.members: 
        member_progress += f"- {active_member.mention} - {self.get_progress_string(active_member)}\n"
        member_progress += self.get_top_progess(active_member)
      else:
        member_progress += self.get_top_progess()
      embed.add_field(name="Members",value=member_progress,inline=False)
    else:
      embed.add_field(name="Members",value="No members",inline=False)

    return embed
  
  def get_manage_view(self) -> discord.ui.View:
    """ To get the view exclusive to the 100 days of code project."""
    view = DaysOfCodeManageView()
    return view
  
  def get_included_member_view(self,interaction) -> discord.ui.View:
    """ To get view for members already included in the project."""
    view = DaysOfCodeIncludedMemberView(self)

    if self.progress[interaction.user.id][-1] != "m":
      view.complete_day.disabled = True 
    return view
    
  def get_excluded_member_view(self) -> discord.ui.View:
    """ To get view for members not included in the project."""
    view = DaysOfCodeExcludedMemberView(self)
    return view

# - - - - - - - - - - - - - - - - -

class DaysOfCodeManageView(discord.ui.View):

  def __init__(self):
    super().__init__()
    self.close_check = False

  @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
  async def finish_edit(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.close_check = True


class DaysOfCodeIncludedMemberView(discord.ui.View):

  def __init__(self,project):
    super().__init__()
    self.close_check = False
    self.project = project

  @discord.ui.button(label="Complete Day",style=discord.ButtonStyle.primary)
  async def complete_day(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.project.manage_progress(interaction.user,"y")
    await interaction.response.defer()

  @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
  async def finish_edit(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.close_check = True


class DaysOfCodeExcludedMemberView(discord.ui.View):

  def __init__(self,project):
    super().__init__()
    self.close_check = False
    self.project = project

  @discord.ui.button(label="Join Project",style=discord.ButtonStyle.success)
  async def join_project(self,interaction:discord.Interaction,button:discord.ui.Button):
    self.project.add_member(interaction.user)
    await interaction.response.defer()

# - - - - - - - - - - - - - - - - -
  
class AddProjectModal(discord.ui.Modal,title="Add Project"):

  def __init__(self,workflow):
    super().__init__()
    self.workflow = workflow
  
  # Creating inputs.
  title_input = discord.ui.TextInput(label="Please enter a project title:",style=discord.TextStyle.short,required=True,max_length=100,placeholder="Title")
  deadline_input = discord.ui.TextInput(label="Please enter a project deadline:",style=discord.TextStyle.short,required=False,max_length=10,placeholder="dd mm yyyy")

  async def on_submit(self, interaction: discord.Interaction):
    # Creating project.
    self.workflow.add_project(self.title_input.value,self.deadline_input.value)
    # Sending update log in active channel.
    logger.info("Sending update log in active channel.")
    update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} added a project, `{self.title_input.value}`.")
    await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

    await interaction.response.defer()

# - - - - - - - - - - - - - - - - -
  
class TemplateSelectionMenu(discord.ui.Select):

  def __init__(self,workflow,initial_interaction) -> None:
    super().__init__()
    self.workflow = workflow
    self.initial_interaction = initial_interaction
  
  async def callback(self, interaction: discord.Interaction):
    if self.values[0] == "No template":
      await interaction.response.send_modal(AddProjectModal(self.workflow))
    elif self.values[0] == "100 Days of Code":
      project = self.workflow.add_100days_project()
      # Sending update log in active channel.
      logger.info("Sending update log in active channel.")
      update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} added a project, `{project.name}`.")
      await self.workflow.active_channel.send(embed=update_embed,delete_after=60)
    await self.initial_interaction.delete_original_response()

# - - - - - - - - - - - - - - - - -
  
async def get_template_selection(workflow,initial_interaction) -> discord.ui.Select:
  """ Getting a template selection menu."""

  # Checking if 100 days of code project already.
  days_of_code_check = False
  for project in workflow.projects:
    if project.__class__.__name__ == "DaysOfCode":
      days_of_code_check = True
  
  # Getting template options.
  if not days_of_code_check:
    template_options = [discord.SelectOption(label="No template"),
                        discord.SelectOption(label="100 Days of Code")]
  else:
    template_options = [discord.SelectOption(label="No template")]

  # Creating selection.
  template_selection = TemplateSelectionMenu(workflow,initial_interaction)
  template_selection.placeholder = "Template"
  template_selection.max_values = 1
  template_selection.options = template_options
  return template_selection

# - - - - - - - - - - - - - - - - -

if __name__ == "__main__":

  test = DaysOfCode(id=1)

  print(test.__class__.__name__)
