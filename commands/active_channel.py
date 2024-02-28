'''
Module for defining commands related to the active channel.

Created on Wednesday 24th January 2024.
@author: Harry.New

'''

import discord
import asyncio

from .misc import get_admin_role

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# VIEW CLASSES.


class WorkflowButtonView(discord.ui.View):

    def __init__(self,workflow,client):
        super().__init__()
        self.workflow = workflow
        self.client = client


    @discord.ui.button(label="Add Project", style=discord.ButtonStyle.primary)
    async def add_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending add project modal.
            await interaction.response.send_modal(AddProjectModal(workflow=self.workflow))
        else:
            # Sending private message.
            await interaction.response.send_message("You do not have the necessary role to add projects to the workflow.",ephemeral=True)


    @discord.ui.button(label="Edit Project", style=discord.ButtonStyle.primary)
    async def edit_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending edit project modal.
            await interaction.response.send_modal(EditProjectModal(workflow=self.workflow,client=self.client,user=interaction.user))
        else:
            # Sending private message.
            await interaction.response.send_message("You do not have the necessary role to edit projects in the workflow.",ephemeral=True)


    @discord.ui.button(label="Delete Project", style=discord.ButtonStyle.primary)
    async def del_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending delete project modal.
            await interaction.response.send_modal(DelProjectModal(workflow=self.workflow))
        else:
            # Sending private message.
            await interaction.response.send_message("You do not have the necessary role to delete projects in the workflow.",ephemeral=True)



class ProjectButtonView(discord.ui.View):

    def __init__(self, project,user,workflow):
        super().__init__()
        self.project = project
        self.close_check = False
        self.user = user
        self.workflow = workflow


    @discord.ui.button(label="Change Title", style=discord.ButtonStyle.primary)
    async def change_title(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending edit title modal.
      await interaction.response.send_modal(EditTitleModal(project=self.project,workflow=self.workflow))


    @discord.ui.button(label="Change Deadline", style=discord.ButtonStyle.primary)
    async def change_deadline(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending edit deadline modal.
      await interaction.response.send_modal(EditDeadlineModal(project=self.project,workflow=self.workflow))

    
    @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
    async def finish_edit(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Indicating to close message.
      self.close_check = True


    @discord.ui.button(label="Add Task", style=discord.ButtonStyle.primary,row=2)
    async def add_task(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending add task modal.
      await interaction.response.send_modal(AddTaskModal(project=self.project,workflow=self.workflow))


    @discord.ui.button(label="Delete Task", style=discord.ButtonStyle.primary,row=2)
    async def del_task(self, interaction: discord.Interaction, button: discord.ui.Button):
      # Sending delete task modal.
      await interaction.response.send_modal(DelTaskModal(project=self.project,workflow=self.workflow))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# MODAL CLASSES.


class AddProjectModal(discord.ui.Modal,title="New Project"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow

    # Requires title and deadline for new project.
    title_input = discord.ui.TextInput(label="Please enter a project title: ",style=discord.TextStyle.short,placeholder="Title",required=True,max_length=100)
    deadline_input = discord.ui.TextInput(label="Please enter a deadline (dd mm yyyy):",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=True,max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        # Adds new project to workflow.
        self.workflow.add_project(self.title_input.value,self.deadline_input.value)

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} created a new project, {self.title_input.value}.")
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

        await interaction.response.defer()




class EditProjectModal(discord.ui.Modal,title="Edit Project"):

    def __init__(self,workflow,client,user):
        super().__init__()
        self.workflow = workflow
        self.client = client
        self.user = user

    # Requires project number to edit.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        initial_check = True

        while True:
            # Getting project.
            project = self.workflow.projects[int(self.number_input.value)-1]
            # Creating title.
            title = f"{project.name} - Deadline <t:{project.get_unix_deadline()}:R>" if project.deadline else f"{project.name}"
            # Creating task list.
            task_list = ""
            for team in project.get_teams_from_ids(self.workflow):
              task_list += f"{self.workflow.active_message.guild.get_role(team.role_id).mention} "
            if len(project.get_teams_from_ids(self.workflow)) != 0:
              task_list += "\n"
            if len(project.tasks) != 0:
                index = 0
                for task in project.tasks:
                  if not task.archive:
                    index += 1
                    task_members_mention = ""
                    task_status = ""
                    if task.status:
                      task_status += f"**`{task.status}`**"
                    for member_id in task.member_ids:
                        member = await self.workflow.active_message.guild.fetch_member(member_id)
                        task_members_mention += member.mention 
                    task_list += f'{index}. {task.name} - *Due <t:{task.get_unix_deadline()}:R>* {task_status} {task_members_mention}\n' if task.deadline and task.status != "COMPLETED" else \
                    f'{index}. {task.name} {task_status} {task_members_mention}\n'
            else:
                task_list += "No tasks."
            # Creating embed.
            embed = discord.Embed(color=discord.Color.blurple(),title=title,description=task_list)
            # Creating view.
            view = ProjectButtonView(project=project,user=self.user,workflow=self.workflow)
            if len(project.tasks) == 0:
                view.del_task.disabled = True
            # Checking if initial message.
            if initial_check:
                await interaction.response.send_message(embed=embed,view=view,delete_after=300,ephemeral=True)
                initial_check = False
                await self.client.wait_for('interaction')
            else:
                await interaction.edit_original_response(embed=embed,view=view)
                await self.client.wait_for('interaction')
            # Checking to close the message.
            await asyncio.sleep(1)
            if view.close_check:
                await interaction.delete_original_response()
                break



class DelProjectModal(discord.ui.Modal,title="Delete Project"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow
    
    # Required project number to delete.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        # Getting original title
        project_title = self.workflow.get_project_by_id(int(self.number_input.value)).name

        # Deleting project from workflow.
        self.workflow.del_project(int(self.number_input.value))

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} deleted a project, {project_title}.")
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

        await interaction.response.defer()




class AddTaskModal(discord.ui.Modal,title="Add Task"):

    def __init__(self,project,workflow):
        super().__init__()
        self.project = project
        self.workflow = workflow

    # Requires task name and deadline.
    task_input = discord.ui.TextInput(label="Please enter a task name:",style=discord.TextStyle.short,placeholder="Name",required=True,max_length=100)
    deadline_input =  discord.ui.TextInput(label="Please enter a task deadline (dd mm yyyy):",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=False,max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        # Checking if deadline entered.
        if self.deadline_input.value == "":
            new_task = self.project.add_task(self.task_input.value,None)
        else:
            # Adding task to project.
            new_task = self.project.add_task(self.task_input.value,self.deadline_input.value)

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        description = f"{interaction.user.mention} added task, ({new_task.name}), to {self.project.name}." if self.deadline_input.value == "" else f"{interaction.user.mention} added task, ({self.task_input.value} <t:{new_task.get_unix_deadline()}:R>), to {self.project.name}."
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=description)
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

        await interaction.response.defer()




class DelTaskModal(discord.ui.Modal,title="Delete Task"):

    def __init__(self,project,workflow):
        super().__init__()
        self.project = project
        self.workflow = workflow

    # Requires task number to delete.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Project Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        # Deleting task from project.
        count = 0
        for task in self.project.tasks:
          if not task.archive:
            count += 1
          if count == int(self.number_input.value):
            task_name = task.name
            self.project.tasks.remove(task)

            # Sending update log in active channel.
            logger.info("Sending update log in active channel.")
            update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} deleted task, ({task_name}), from {self.project.name}.")
            await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

            await interaction.response.defer()




class EditTitleModal(discord.ui.Modal, title="Edit Title"):
    
    def __init__(self,project,workflow):
        super().__init__()
        self.project = project
        self.workflow = workflow

    # Required new title of project.
    title_input = discord.ui.TextInput(label="Please enter a new project title:",style=discord.TextStyle.short,placeholder="Project Title",required=True,max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        # Getting original title.
        original_title = self.project.name

        # Changing title of project.
        self.project.name = self.title_input.value
        
        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} changed a project's title from {original_title} to {self.project.name}.")
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

        await interaction.response.defer()




class EditDeadlineModal(discord.ui.Modal, title="Edit Deadline"):

    def __init__(self,project,workflow):
        super().__init__()
        self.project = project
        self.workflow = workflow

    # Requires new deadline of project.
    deadline_input = discord.ui.TextInput(label="Please enter a new project deadline:",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=True,max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        # Changing deadline of project.
        self.project.edit_deadline(self.deadline_input.value)

        # Sending update log in active channel.
        logger.info("Sending update log in active channel.")
        update_embed = discord.Embed(colour=discord.Color.blurple(),description=f"{interaction.user.mention} changed {self.project.name}'s deadline to <t:{self.project.get_unix_deadline()}:R>.")
        await self.workflow.active_channel.send(embed=update_embed,delete_after=60)

        await interaction.response.defer()

# - - - - - - - - - - - - - - - - - - - - - - - - - -

# Init active_channel.
def init_active_channel(logging):
    # Initialising logger.
    global logger
    logger = logging


# Set projects command.
async def set_active_channel_command(interaction, workflow, client):
    # Getting channel and guild of command was sent in.
    channel = interaction.channel
    guild = interaction.guild

    # Updating projects channel in workflow.
    workflow.active_channel = channel

    # Getting workflow manager role.
    admin_role = await get_admin_role(guild)

    # Changing permissions for channel.
    await channel.set_permissions(guild.default_role,send_messages=False,add_reactions=False,manage_messages=False)
    await channel.set_permissions(admin_role,send_messages=True,add_reactions=False,manage_messages=True)
    logger.info(f"Setting {channel.name} to project channel in {guild.name}.")

    # Registering initial check.
    initial_check = True

    # Sending projects embed.
    while True:
        
        # Creating embed for message.
        embed = discord.Embed(color=discord.Color.blurple(),title="Existing Projects")

        # Creating content of message.
        if len(workflow.projects) != 0:
            for project in workflow.projects:
                # Creating field title.
                field_title = f'{workflow.projects.index(project)+1}. {project.name} - Deadline <t:{project.get_unix_deadline()}:R>' if project.deadline else \
                f'{workflow.projects.index(project)+1}. {project.name}'
                # Creating task list for field.
                task_list = ""
                for team in project.get_teams_from_ids(workflow):
                  task_list += f"{guild.get_role(team.role_id).mention} "
                if len(project.get_teams_from_ids(workflow)) != 0:
                  task_list += "\n"
                if len(project.tasks) != 0:
                    for task in project.tasks:
                      if not task.archive:
                        task_members_mention = ""
                        task_status = ""
                        if task.status:
                          task_status += f"**`{task.status}`**"
                        for member_id in task.member_ids:
                            member = await workflow.active_message.guild.fetch_member(member_id)
                            task_members_mention += member.mention 
                        task_list += f'- {task.name} - *Due <t:{task.get_unix_deadline()}:R>* {task_members_mention}\n' if task.deadline and task.status != "COMPLETED" else \
                    f'- {task.name} {task_status} {task_members_mention}\n'
                else:
                    task_list += "No tasks."
                embed.add_field(name=field_title,value=task_list,inline=False)
        else:
            embed.description = 'No existing projects.'

        # Creating UI at bottom of message.
        view = WorkflowButtonView(workflow=workflow,client=client)
        if len(workflow.projects) == 0:
            view.edit_project.disabled = True
            view.del_project.disabled = True

        # Updating message.
        if initial_check:
            await interaction.response.send_message(embed=embed,view=view)
            response = await interaction.original_response()
            workflow.active_message = response
            initial_check = False
            await client.wait_for('interaction')
        else:
            await interaction.edit_original_response(embed=embed,view=view)
            await client.wait_for('interaction')

           
# Restarting message looping.
async def restart_looping(client,workflow,guild):
    while True:
        # Creating embed for message.
        embed = discord.Embed(color=discord.Color.blurple(),title="Existing Projects")

        # Creating content of message.
        if len(workflow.projects) != 0:
            for project in workflow.projects:
                # Creating field title.
                field_title = f'{workflow.projects.index(project)+1}. {project.name} - Deadline <t:{project.get_unix_deadline()}:R>' if project.deadline  else \
                f'{workflow.projects.index(project)+1}. {project.name}'
                # Creating task list for field.
                task_list = ""
                for team in project.get_teams_from_ids(workflow):
                  task_list += f"{guild.get_role(team.role_id).mention} "
                if len(project.get_teams_from_ids(workflow)) != 0:
                  task_list += "\n"
                if len(project.tasks) != 0:
                    for task in project.tasks:
                      if not task.archive:
                        task_members_mention = ""
                        task_status = ""
                        if task.status:
                          task_status += f"**`{task.status}`**"
                        if len(task.member_ids) != 0:
                          for member_id in task.member_ids:
                            member = await workflow.active_message.guild.fetch_member(member_id)
                            task_members_mention += member.mention 
                        task_list += f'- {task.name} - *Due <t:{task.get_unix_deadline()}:R>* {task_members_mention}\n' if task.deadline and task.status != "COMPLETED" else \
                    f'- {task.name} {task_status} {task_members_mention}\n'
                else:
                    task_list += "No tasks."
                embed.add_field(name=field_title,value=task_list,inline=False)
        else:
            embed.description = 'No existing projects.'

        # Creating UI at bottom of message.
        view = WorkflowButtonView(workflow=workflow,client=client) 
        if len(workflow.projects) == 0:
            view.edit_project.disabled = True
            view.del_project.disabled = True

        # Updating message.
        await workflow.active_message.edit(embed=embed,view=view)
        await client.wait_for('interaction')
