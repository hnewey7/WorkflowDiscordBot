'''
Module for commands related to teams.

Created on Wednesday 24th January 2024.
@author: Harry New

'''

import discord
import logging
import asyncio

from .misc import get_admin_role

# - - - - - - - - - - - - - - - - - - - - - - - - - -

# VIEW CLASSES

class TeamsButtonView(discord.ui.View):

    def __init__(self,workflow,client):
        super().__init__()
        self.workflow = workflow
        self.client = client
        self.close_check = False
    
    @discord.ui.button(label="Add Team", style=discord.ButtonStyle.primary)
    async def add_team(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending add team modal.
      await interaction.response.send_modal(AddTeamModal(self.workflow))

    @discord.ui.button(label="Edit Team", style=discord.ButtonStyle.primary)
    async def edit_team(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending add team modal.
      await interaction.response.send_modal(EditTeamModal(self.workflow,self.client))

    @discord.ui.button(label="Delete Team", style=discord.ButtonStyle.primary)
    async def delete_team(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending delete team modal.
      await interaction.response.send_modal(DelTeamModal(self.workflow))

    @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
    async def finish_edit(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Indicating to close message.
      self.close_check = True


class IndividualTeamButtonView(discord.ui.View):
    
    def __init__(self,workflow,team,role,manager_role,guild,client):
        super().__init__()
        self.workflow = workflow
        self.team = team
        self.role = role
        self.manager_role = manager_role
        self.close_check = False
        self.guild = guild
        self.client = client
    
    async def create_member_menu(self,menu_type:bool):
      # Getting available members.
      available_members = await get_member_selection(self.team,self.guild,menu_type)
      member_select = MemberSelectMenu(self.guild,self.team,menu_type,self.workflow)
      member_select.placeholder = "Members"
      member_select.max_values = len(available_members)
      member_select.options = available_members
      return member_select

    @discord.ui.button(label="Assign Member", style=discord.ButtonStyle.primary)
    async def assign_member(self,interaction:discord.Interaction,button:discord.ui.Button):
      view = discord.ui.View()
      # Creating embed.
      embed = discord.Embed(color=discord.Color.blurple(),description=f"Select a member to assign to the team:")
      # Creating select menu.
      select_menu = await self.create_member_menu(True)
      view.add_item(select_menu)
      # Sending message.
      await interaction.response.send_message(embed=embed,view=view,ephemeral=True)
      # Deleting message after interaction.
      await self.client.wait_for("interaction")
      await interaction.delete_original_response()

    @discord.ui.button(label="Remove Member", style=discord.ButtonStyle.primary)
    async def remove_member(self,interaction:discord.Interaction,button:discord.ui.Button):
      view = discord.ui.View()
      # Creating embed.
      embed = discord.Embed(color=discord.Color.blurple(),description=f"Select a member to remove from the team:")
      # Creating select menu.
      select_menu = await self.create_member_menu(False)
      view.add_item(select_menu)
      # Sending message.
      await interaction.response.send_message(embed=embed,view=view,ephemeral=True)
      # Deleting message after interaction.
      await self.client.wait_for("interaction")
      await interaction.delete_original_response()

    @discord.ui.button(label="Change Title", style=discord.ButtonStyle.primary)
    async def change_title(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending add team modal.
      await interaction.response.send_modal(ChangeTitleModal(self.workflow,self.team,self.role,self.manager_role))

    @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
    async def finish_edit(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Indicating to close message.
      self.close_check = True

# - - - - - - - - - - - - - - - - - - - - - - - - - -

class MemberSelectMenu(discord.ui.Select):

  def __init__(self,guild,team,menu_type,workflow):
    super().__init__()
    self.guild = guild
    self.team = team
    self.menu_type = menu_type
    self.workflow = workflow

  async def callback(self, interaction: discord.Interaction):
    for member_title in self.values:
      member = self.guild.get_member_named(member_title)
      if self.menu_type:
        await member.add_roles(self.guild.get_role(self.team.role_id))
        logger.info(f"Assigned {member.name} to ({self.team.name})")

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")  
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} assigned {member.mention} to {self.guild.get_role(self.team.role_id).mention}.")
        await interaction.response.send_message(embed=update_embed,delete_after=3)
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)
      else:
        await member.remove_roles(self.guild.get_role(self.team.role_id))
        logger.info(f"Removed {member.name} from ({self.team.name})")

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")  
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} removed {member.mention} from {self.guild.get_role(self.team.role_id).mention}.")
        await interaction.response.send_message(embed=update_embed,delete_after=3)
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)


# - - - - - - - - - - - - - - - - - - - - - - - - - -
            
# MODAL CLASSES
            
class AddTeamModal(discord.ui.Modal,title="New Team"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow
    
    # Requires title for new team.
    title_input = discord.ui.TextInput(label="Please enter a team title: ",style=discord.TextStyle.short,placeholder="Title",required=True,max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        # Adds new team to workflow.
        new_team = self.workflow.add_team(self.title_input.value)
        logger.info(f"New team created in workflow.")

        # Managing colours of roles.
        team_colour = discord.Color.random()
        rgb = team_colour.to_rgb()
        new_rgb = []
        for channel in rgb:
            new_value = channel - 20
            if new_value < 0:
                new_value = 0
            new_rgb.append(new_value)
        manager_colour = discord.Color.from_rgb(new_rgb[0],new_rgb[1],new_rgb[2])

        # Creating new role in guild.
        new_role = await interaction.guild.create_role(name=self.title_input.value,color=team_colour,hoist=True)
        logger.info(f"New role created for team ({new_role.name}).")
        # Creating new manager role in guild.
        manager_role =  await interaction.guild.create_role(name=self.title_input.value + " Manager",color=manager_colour)
        logger.info(f"New manager role created for team ({manager_role.name}).")
        # Changing role positions.
        new_role.position = manager_role.position - 1
        # Updating role id for new team.
        self.workflow.teams[self.workflow.teams.index(new_team)].role_id = new_role.id
        self.workflow.teams[self.workflow.teams.index(new_team)].manager_role_id = manager_role.id
        logger.info("Updating role id of team.")

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} created a new team, `{new_role.mention}`.")
        await interaction.channel.send(embed=update_embed,delete_after=3)
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

        await interaction.response.defer()


class EditTeamModal(discord.ui.Modal,title="Edit Team"):

    def __init__(self,workflow,client):
        super().__init__()
        self.workflow = workflow
        self.client = client 

    # Required index.
    number_input = discord.ui.TextInput(label="Please enter a team number: ",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        initial_check = True

        while True:
            # Getting team.
            team = self.workflow.teams[int(self.number_input.value)-1]
            # Getting role for team.
            role = interaction.guild.get_role(team.role_id)
            manager_role = interaction.guild.get_role(team.manager_role_id)
            # Creating member list.
            team_starter = f"**{role.mention}**\n"
            member_list = ""
            manager_list = ""
            if len(role.members) != 0:
                for index,member in enumerate(role.members):
                  if member not in manager_role.members:
                    member_list += f'{index+1}. {member.name}\n'
                  else:
                    manager_list = f'{index+1}. {member.name} - **Manager**\n'
            else:
                member_list += "No members."
            # Creating embed for message.
            embed = discord.Embed(color=role.color,description=(team_starter+manager_list+member_list))

            # Creating view for message.
            view = IndividualTeamButtonView(self.workflow,team,role,manager_role,interaction.guild,self.client)

            # Toggling buttons.
            if len(await get_member_selection(team,interaction.guild,True)) == 0:
              view.assign_member.disabled = True
            if len(await get_member_selection(team,interaction.guild,False)) == 0:
              view.remove_member.disabled = True

            if initial_check:
                await interaction.response.send_message(embed=embed,view=view,delete_after=300,ephemeral=True)
                initial_check = False
                # Waiting for either interaction or role update.
                interaction_task = asyncio.create_task(self.client.wait_for('interaction'))
                role_task = asyncio.create_task(self.client.wait_for('member_update'))
                guild_task = asyncio.create_task(self.client.wait_for('guild_role_update'))
                await asyncio.wait([interaction_task,role_task,guild_task],return_when=asyncio.FIRST_COMPLETED)
            else:
                # Waiting for either interaction or role update.
                await interaction.edit_original_response(embed=embed,view=view)
                interaction_task = asyncio.create_task(self.client.wait_for('interaction'))
                role_task = asyncio.create_task(self.client.wait_for('member_update'))
                guild_task = asyncio.create_task(self.client.wait_for('guild_role_update'))
                await asyncio.wait([interaction_task,role_task,guild_task],return_when=asyncio.FIRST_COMPLETED)

            # Waiting to check whether to close edit.
            await asyncio.sleep(1)
            if view.close_check:
                await interaction.delete_original_response()
                break


               
class DelTeamModal(discord.ui.Modal,title="Delete Team"):
    
    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow
    
    # Required index.
    index_input = discord.ui.TextInput(label="Please enter a team number: ",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        # Deleting team from workflow.
        deleted_team = self.workflow.del_team(self.index_input.value)
        logger.info("Deleted team from workflow.")

        # Removing team role from guild.
        try:
          await interaction.guild.get_role(deleted_team.role_id).delete()
          logger.info(f"Deleted role, {deleted_team.name}")
        except:
          logger.info(f"Role could not be deleted, {deleted_team.name}")
        
        # Removing team manager role from guild.
        try:
          await interaction.guild.get_role(deleted_team.manager_role_id).delete()
          logger.info(f"Deleted manager role, {deleted_team.name}")
        except:
          logger.info(f"Role could not be deleted, {deleted_team.name}")

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} deleted a team, `{deleted_team.name}`.")
        await interaction.channel.send(embed=update_embed,delete_after=3)
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

        await interaction.response.defer()


class ChangeTitleModal(discord.ui.Modal,title="Change Title"):
    
    def __init__(self,workflow,team,role,manager_role):
        super().__init__()
        self.workflow = workflow
        self.team = team
        self.role = role
        self.manager_role = manager_role
    
    # Required title.
    title_input = discord.ui.TextInput(label="Please enter a new title:",style=discord.TextStyle.short,placeholder="Title",required=True,max_length=100)

    async def on_submit(self,interaction: discord.Interaction):
        # Getting original title.
        original_title = self.workflow.teams[self.workflow.teams.index(self.team)].name
        # Changing title of team.
        self.workflow.teams[self.workflow.teams.index(self.team)].name = self.title_input.value
        # Changing title of role.
        await self.role.edit(name=self.title_input.value)
        await self.manager_role.edit(name=self.title_input.value + " Manager")

        logging.info("Changing title of role.")

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} changed the title of `{original_title}` to `{self.workflow.teams[self.workflow.teams.index(self.team)].name}`.")
        await interaction.channel.send(embed=update_embed,delete_after=3)
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)
        
        await interaction.response.defer()

# - - - - - - - - - - - - - - - - - - - - - - - - - -

async def get_member_selection(team,guild,menu_type):
  # Getting members.
  member_selection = []
  if menu_type:
    async for member in guild.fetch_members():
      if guild.get_role(team.role_id) not in member.roles:
        member_selection.append(member)
  else:
    async for member in guild.fetch_members():
      if guild.get_role(team.role_id) in member.roles:
        member_selection.append(member)
 
  # Creating discord options.
  member_selection_options = []
  for member in member_selection:
    option = discord.SelectOption(label=member.name)
    member_selection_options.append(option)

  return member_selection_options

# - - - - - - - - - - - - - - - - - - - - - - - - - -

async def display_teams(interaction, workflow, client):
    global logger
    logger = logging.getLogger()

    # Getting guild.
    guild = interaction.guild
    
    logger.info("Command request approved.")
    initial_check = True
    # Sending teams embed.
    while True:
        try:
            # Creating embed for message.
            embed = discord.Embed(color=discord.Color.blurple(),title="Teams")  

            # Creating content of message.
            if len(workflow.teams) != 0:
                for team in workflow.teams:
                    # Getting roles from team's role id.
                    team_role = guild.get_role(team.role_id)
                    manager_role = guild.get_role(team.manager_role_id)
                    attempt = 0
                    while True:
                        if team_role == None and attempt < 5:
                            team_role = guild.get_role(team.role_id)
                            manager_role = guild.get_role(team.manager_role_id)
                            attempt += 1
                            await asyncio.sleep(0.2)
                        else:
                            break
                    
                    if team_role:
                      # Creating task list for field.
                      team_starter = f"**{workflow.teams.index(team)+1}.{team_role.mention}**\n"
                      member_list = ""
                      manager_list = ""
                      if len(team_role.members) != 0:
                          for member in team_role.members:
                            if member not in manager_role.members:
                              member_list += f'- {member.name}\n'
                            else:
                              manager_list += f'- {member.name} - **Manager**\n'
                      else:
                          member_list += "No members."
                    else:
                      team_starter = f"**{workflow.teams.index(team)+1}.{team.name}**\n"
                      manager_list = ""
                      member_list = "No members."

                    embed.add_field(name="",value=(team_starter+manager_list+member_list),inline=False)

            else:
                embed.description = 'No existing teams.'
            
            # Creating button view.
            view = TeamsButtonView(workflow,client)
            if len(workflow.teams) == 0:  
                view.edit_team.disabled = True
                view.delete_team.disabled = True

            # Updating message.
            if initial_check:
                await interaction.response.send_message(embed=embed,view=view,delete_after=300,ephemeral=True)
                initial_check = False
                # Waiting for either interaction or role update.
                interaction_task = asyncio.create_task(client.wait_for('interaction'))
                member_task = asyncio.create_task(client.wait_for('member_update'))
                role_task = asyncio.create_task(client.wait_for('guild_role_delete'))
                await asyncio.wait([interaction_task,member_task,role_task],return_when=asyncio.FIRST_COMPLETED)
                await asyncio.sleep(1)
            else:
                # Waiting for either interaction or role update.
                await interaction.edit_original_response(embed=embed,view=view)
                interaction_task = asyncio.create_task(client.wait_for('interaction'))
                member_task = asyncio.create_task(client.wait_for('member_update'))
                role_task = asyncio.create_task(client.wait_for('guild_role_delete'))
                await asyncio.wait([interaction_task,member_task,role_task],return_when=asyncio.FIRST_COMPLETED)
                await asyncio.sleep(1)

            if view.close_check:
              await interaction.delete_original_response()
              break

        except Exception as e:
          print(e)