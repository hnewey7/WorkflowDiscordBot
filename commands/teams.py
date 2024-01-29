'''
Module for commands related to teams.

Created on Wednesday 24th January 2024.
@author: Harry New

'''

from typing import Optional
import discord
import logging
import asyncio

# - - - - - - - - - - - - - - - - - - - - - - - - - -

# VIEW CLASSES

class TeamsButtonView(discord.ui.View):

    def __init__(self,workflow,client):
        super().__init__()
        self.workflow = workflow
        self.client = client
    
    @discord.ui.button(label="Add Team", style=discord.ButtonStyle.primary)
    async def add_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await get_admin_role(interaction.guild) in interaction.user.roles:
            # Sending add team modal.
            await interaction.response.send_modal(AddTeamModal(self.workflow))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to add teams to the workflow.")

    @discord.ui.button(label="Edit Team", style=discord.ButtonStyle.primary)
    async def edit_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await get_admin_role(interaction.guild) in interaction.user.roles:
            # Sending add team modal.
            await interaction.response.send_modal(EditTeamModal(self.workflow))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to edit teams to the workflow.")


    @discord.ui.button(label="Delete Team", style=discord.ButtonStyle.primary)
    async def delete_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await get_admin_role(interaction.guild) in interaction.user.roles:
            # Sending delete team modal.
            await interaction.response.send_modal(DelTeamModal(self.workflow))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to delete teams from the workflow.")


class DisabledTeamsButtonView(discord.ui.View):

    def __init__(self,workflow,client):
        super().__init__()
        self.workflow = workflow
        self.client = client
    
    @discord.ui.button(label="Add Team", style=discord.ButtonStyle.primary)
    async def add_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await get_admin_role(interaction.guild) in interaction.user.roles:
            # Sending add team modal.
            await interaction.response.send_modal(AddTeamModal(self.workflow))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to add teams to the workflow.")

    @discord.ui.button(label="Edit Team", style=discord.ButtonStyle.primary,disabled=True)
    async def edit_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await get_admin_role(interaction.guild) in interaction.user.roles:
            # Sending add team modal.
            await interaction.response.send_modal(EditTeamModal(self.workflow))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to edit teams to the workflow.")

    @discord.ui.button(label="Delete Team", style=discord.ButtonStyle.primary,disabled=True)
    async def delete_team(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await get_admin_role(interaction.guild) in interaction.user.roles:
            # Sending delete team modal.
            await interaction.response.send_modal(DelTeamModal(self.workflow))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to delete teams from the workflow.")


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
        # Creating new role in guild.
        new_role = await interaction.guild.create_role(name=self.title_input.value,color=discord.Colour.random())
        logger.info(f"New role created for team ({new_role.name}).")
        # Updating role id for new team.
        self.workflow.teams[self.workflow.teams.index(new_team)].role_id = new_role.id
        logger.info("Updating role id of team.")
        await interaction.response.defer()


class EditTeamModal(discord.ui.Modal,title="Edit Team"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow

    # Required index.
    number_input = discord.ui.TextInput(label="Please enter a team number: ",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        initial_check = True

        while True:
            # Getting team.
            team = self.workflow.teams[int(self.number_input.value)-1]
            # Getting role for team.
            role = interaction.guild.get_role(team.role_id)
            # Creating member list.
            if len(role.members) != 0:
                member_list = ""
                for index,member in enumerate(role.members):
                    member_list += f'{index+1}. {member.name}'
            else:
                member_list = "No members."
            # Creating embed for message.
            embed = discord.Embed(color=discord.Color.blurple(),title=team.title,description=member_list)
            
            await interaction.response.send_message(embed=embed,delete_after=600)
            
               
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
        # Removing role from guild.
        await interaction.guild.get_role(deleted_team.role_id).delete()
        logger.info(f"Deleted role, {deleted_team.title}")
        await interaction.response.defer()


# - - - - - - - - - - - - - - - - - - - - - - - - - -

async def display_teams(command, workflow, client):
    global logger
    logger = logging.getLogger()

    # Getting guild.
    guild = command.guild
    
    if await get_admin_role(guild) in command.author.roles:
        logger.info("Command request approved.")
        initial_check = True
        # Sending teams embed.
        while True:
            # Creating embed for message.
            embed = discord.Embed(color=discord.Color.blurple(),title="Teams")  

            # Creating content of message.
            if len(workflow.teams) != 0:
                for team in workflow.teams:
                    # Getting roles from team's role id.
                    team_role = guild.get_role(team.role_id)
                    while True:
                        if team_role == None:
                            team_role = guild.get_role(team.role_id)
                            await asyncio.sleep(0.2)
                        else:
                            break
                    # Creating field title.
                    field_title = f'{workflow.teams.index(team)+1}. {team.title}'
                    # Creating task list for field.
                    if len(team_role.members) != 0:
                        member_list = ""
                        for member in team_role.members:
                            member_list += f'- {member.name} **Manager**\n' if member.id in team.manager_ids else \
                        f'- {member.name}\n'
                    else:
                        member_list = "No members."
                    embed.add_field(name=field_title,value=member_list,inline=False)
            else:
                embed.description = 'No existing teams.'
            
            # Creating button view.
            view = TeamsButtonView(workflow,client) if len(workflow.teams) != 0 else DisabledTeamsButtonView(workflow,client)

            # Updating message.
            if initial_check:
                message = await command.channel.send(embed=embed,view=view,delete_after=300)
                initial_check = False
                await client.wait_for('interaction')
            else:
                await message.edit(embed=embed,view=view,delete_after=300)
                await client.wait_for('interaction')

    else:
        logger.info("User does not have necessary permission.")
        command.author.send("You do not have the necessary role to use this command.")

async def get_admin_role(guild):
    # Getting workflow manager role.
    for role in await guild.fetch_roles():
        if role.name == "Workflow Manager":
            return role