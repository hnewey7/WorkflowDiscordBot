'''
Module for handling log message.

Created on Sunday 25th February 2024.
@author: Harry New

'''

import discord
import math
import asyncio
import logging

# - - - - - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - -

class LogButtonView(discord.ui.View):

  def __init__(self,task,guild,client,workflow,page_display,fields_per_embed):
    super().__init__()
    self.task = task
    self.guild = guild
    self.client = client
    self.workflow = workflow
    self.page_down_check = False
    self.page_up_check = False
    self.page_display = page_display
    self.fields_per_embed = fields_per_embed
    self.close_check = False

  def create_log_menu(self,user):
    log_select = LogSelectMenu(self.task,user)
    log_select.placeholder = "Status"
    log_select.max_values = 1

    # Getting options.
    options = get_log_selection(self.task,user,True)
    log_select.options = options[(self.page_display-1)*self.fields_per_embed:self.page_display*self.fields_per_embed]
    return log_select

  @discord.ui.button(label="Add Log", style=discord.ButtonStyle.primary)
  async def add_log(self,interaction:discord.Interaction,button:discord.Button):
    # Sending log modal.
    await interaction.response.send_modal(AddLogModal(self.task))

  @discord.ui.button(label="Remove Log", style=discord.ButtonStyle.primary)
  async def remove_log(self,interaction:discord.Interaction,button:discord.Button):
    view = discord.ui.View()
    # Creating embed.
    embed = discord.Embed(color=discord.Color.blurple(),description=f"Select a log to remove from the task:")
    # Creating select menu.
    select_menu = self.create_log_menu(interaction.user)
    view.add_item(select_menu)
    # Sending message.
    await interaction.response.send_message(embed=embed,view=view,ephemeral=True)
    # Deleting message after interaction.
    await self.client.wait_for("interaction")
    await interaction.delete_original_response()

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


class LogSelectMenu(discord.ui.Select):

  def __init__(self,task,user):
    super().__init__()
    self.task = task
    self.user = user
  
  async def callback(self, interaction: discord.Interaction):
    # Setting deleting selected log.
    self.task.remove_log(self.values[0])
    logger.info(f"Deleted log {self.values[0]} from {self.task.name}.")
    await interaction.response.defer()


# - - - - - - - - - - - - - - -


class AddLogModal(discord.ui.Modal,title="Add Log"):

  def __init__(self,task):
    super().__init__()
    self.task = task 
  
  # Requires description input.
  description_input = discord.ui.TextInput(label="Please enter a log comment:",style=discord.TextStyle.long,placeholder="Comment",required=True)

  async def on_submit(self, interaction: discord.Interaction):
    # Add log.
    self.task.add_log(interaction.user,self.description_input.value)
    await interaction.response.defer()

# - - - - - - - - - - - - - - -

def get_log_selection(task,author,manager_check):
  log_dates = task.logs.keys()
  options = []
  for date in log_dates:
    if manager_check:
      option = discord.SelectOption(label=date)
      options.append(option)
    else:
      if task.logs[date][1] == author.id:
        option = discord.SelectOption(label=date)
        options.append(option)
  return options

# - - - - - - - - - - - - - - -

async def send_log_message(interaction: discord.Interaction,task,client,guild,workflow):
  initial_check = True
  page_display = 1
  fields_per_embed = 25
  while True:

    # Calculating total number of pages.
    total_pages = math.ceil(len(task.logs.keys())/(fields_per_embed))

    if page_display > total_pages and page_display != 1:
      page_display = total_pages

    if len(task.logs.keys()) != 0:
      # Creating archive message.
      embed = discord.Embed(color=discord.Color.blurple(),title=f"Logs ({page_display}/{total_pages})")

      for index, log_date in enumerate(task.logs.keys()):
        if index < (page_display * fields_per_embed) and index >= (page_display-1)*fields_per_embed:
          log_author = guild.get_member(task.logs[log_date][1])
          embed.add_field(name=f"`{log_date}`",value=f"{log_author.mention} {task.logs[log_date][0]}",inline=False)
    else:
      log_list = "No logs."
      embed = discord.Embed(color=discord.Color.blurple(),title=f"Logs (1/1)",description=log_list)

    view = LogButtonView(task,guild,client,workflow,page_display,fields_per_embed=fields_per_embed)

    if page_display >= total_pages:
      view.page_up.disabled = True
    if page_display == 1:
      view.page_down.disabled = True
    if len(task.logs.keys()) == 0:
      view.remove_log.disabled = True

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
    