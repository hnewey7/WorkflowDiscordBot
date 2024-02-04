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
            await interaction.user.send("You do not have the necessary role to add projects to the workflow.")


    @discord.ui.button(label="Edit Project", style=discord.ButtonStyle.primary)
    async def edit_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending edit project modal.
            await interaction.response.send_modal(EditProjectModal(workflow=self.workflow,client=self.client))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to edit projects in the workflow.")


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
            await interaction.user.send("You do not have the necessary role to delete projects in the workflow.")



class ProjectButtonView(discord.ui.View):

    def __init__(self, project):
        super().__init__()
        self.project = project
        self.close_check = False


    @discord.ui.button(label="Change Title", style=discord.ButtonStyle.primary)
    async def change_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending edit title modal.
            await interaction.response.send_modal(EditTitleModal(project=self.project))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to the change title of a project.")


    @discord.ui.button(label="Change Deadline", style=discord.ButtonStyle.primary)
    async def change_deadline(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending edit deadline modal.
            await interaction.response.send_modal(EditDeadlineModal(project=self.project))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to the change deadline of a project.")

    
    @discord.ui.button(label="Finish Edit",style=discord.ButtonStyle.success)
    async def finish_edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Indicating to close message.
            self.close_check = True
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to finish the edit on the project.")


    @discord.ui.button(label="Add Task", style=discord.ButtonStyle.primary,row=2)
    async def add_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending add task modal.
            await interaction.response.send_modal(AddTaskModal(project=self.project))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to add tasks to the project.")


    @discord.ui.button(label="Delete Task", style=discord.ButtonStyle.primary,row=2)
    async def del_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Getting admin role.
        admin_role = await get_admin_role(interaction.guild)
        # Checking if user is admin role.
        if admin_role in interaction.user.roles:
            # Sending delete task modal.
            await interaction.response.send_modal(DelTaskModal(project=self.project))
        else:
            # Sending private message.
            await interaction.user.send("You do not have the necessary role to delete tasks from the project.")


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
        await interaction.response.defer()




class EditProjectModal(discord.ui.Modal,title="Edit Project"):

    def __init__(self,workflow,client):
        super().__init__()
        self.workflow = workflow
        self.client = client

    # Requires project number to edit.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        initial_check = True

        while True:
            # Getting project.
            project = self.workflow.projects[int(self.number_input.value)-1]
            # Creating title.
            title = f"{project.title} - Deadline <t:{project.get_unix_deadline()}:R>" if project.deadline else f"{project.title}"
            # Creating task list.
            if len(project.tasks) != 0:
                task_list = ""
                for task in project.tasks:
                    task_list += f'{project.tasks.index(task)+1}. {task.name}, due <t:{task.get_unix_deadline()}:R>\n' if task.deadline else \
                    f'{project.tasks.index(task)+1}. {task.name}\n'
            else:
                task_list = "No tasks."
            # Creating embed.
            embed = discord.Embed(color=discord.Color.blurple(),title=title,description=task_list)
            # Creating view.
            view = ProjectButtonView(project=project)
            if len(project.tasks) == 0:
                view.del_task.disabled = True
            # Checking if initial message.
            if initial_check:
                await interaction.response.send_message(embed=embed,view=view,delete_after=600)
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
        # Deleting project from workflow.
        self.workflow.del_project(int(self.number_input.value))
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
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Project Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        # Deleting task from project.
        self.project.del_task(int(self.task_number.value))
        await interaction.response.defer()




class EditTitleModal(discord.ui.Modal, title="Edit Title"):
    
    def __init__(self,project):
        super().__init__()
        self.project = project

    # Required new title of project.
    title_input = discord.ui.TextInput(label="Please enter a new project title:",style=discord.TextStyle.short,placeholder="Project Title",required=True,max_length=100)

    async def on_submit(self, interaction: discord.Interaction):
        # Changing title of project.
        self.project.title = self.title_input.value
        await interaction.response.defer()




class EditDeadlineModal(discord.ui.Modal, title="Edit Deadline"):

    def __init__(self,project):
        super().__init__()
        self.project = project

    # Requires new deadline of project.
    deadline_input = discord.ui.TextInput(label="Please enter a new project deadline:",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=True,max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        # Changing deadline of project.
        self.project.edit_deadline(self.deadline_input.value)
        await interaction.response.defer()

# - - - - - - - - - - - - - - - - - - - - - - - - - -

# Init active_channel.
def init_active_channel(logging):
    # Initialising logger.
    global logger
    logger = logging


# Set projects command.
async def set_active_channel_command(command, workflow, client):
    # Deleting user message.
    await command.delete()

    # Getting channel and guild of command was sent in.
    channel = command.channel
    guild = command.guild

    # Updating projects channel in workflow.
    workflow.active_channel = command.channel

    # Getting workflow manager role.
    admin_role = await get_admin_role(guild)

    # Changing permissions for channel.
    await channel.set_permissions(command.guild.default_role,send_messages=False,add_reactions=False,manage_messages=False)
    await channel.set_permissions(admin_role,send_messages=True,add_reactions=False,manage_messages=True)
    logger.info(f"Setting {channel.name} to project channel in {command.guild.name}.")

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
                field_title = f'{workflow.projects.index(project)+1}. {project.title} - Deadline <t:{project.get_unix_deadline()}:R>' if project.deadline else \
                f'{workflow.projects.index(project)+1}. {project.title}'
                # Creating task list for field.
                task_list = ""
                for team in project.teams:
                  task_list += f"{guild.get_role(team.role_id).mention} "
                if len(project.teams) != 0:
                  task_list += "\n"
                if len(project.tasks) != 0:
                    for task in project.tasks:
                        task_list += f'- {task.name} due <t:{task.get_unix_deadline()}:R>\n' if task.deadline else \
                    f'- {task.name}\n'
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
            message = await command.channel.send(embed=embed,view=view)
            workflow.active_message = message
            initial_check = False
            await client.wait_for('interaction')
        else:
            await message.edit(embed=embed,view=view)
            await client.wait_for('interaction')

           
# Restarting message looping.
async def restart_looping(client,workflow):
    while True:
        # Creating embed for message.
        embed = discord.Embed(color=discord.Color.blurple(),title="Existing Projects")

        # Creating content of message.
        if len(workflow.projects) != 0:
            for project in workflow.projects:
                # Creating field title.
                field_title = f'{workflow.projects.index(project)+1}. {project.title} - Deadline <t:{project.get_unix_deadline()}:R>' if project.deadline else \
                f'{workflow.projects.index(project)+1}. {project.title}'
                # Creating task list for field.
                task_list = ""
                for team in project.teams:
                  task_list += f"{workflow.active_message.guild.get_role(team.role_id).mention} "
                if len(project.teams) != 0:
                  task_list += "\n"
                if len(project.tasks) != 0:
                    for task in project.tasks:
                        task_list += f'- {task.name} due <t:{task.get_unix_deadline()}:R>\n' if task.deadline else \
                    f'- {task.name}\n'
                else:
                    task_list = "No tasks."
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
