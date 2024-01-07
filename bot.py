'''
Bot Script for the Workflow Bot

Created on Monday 1st January 2024
@author: Harry New

'''

from typing import Optional
import discord
import discord.ext.commands as commands
from discord.interactions import Interaction
from discord.utils import MISSING
from workflow import Workflow


class AddProjectModal(discord.ui.Modal,title="New Project"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow

    # Getting inputs.
    title_input = discord.ui.TextInput(label="Please enter a project title: ",style=discord.TextStyle.short,placeholder="Title",required=True,max_length=100)
    date_input = discord.ui.TextInput(label="Please enter a deadline (dd mm yyyy):",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=True,max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        self.workflow.add_project(self.title_input.value,self.date_input.value)
        await interaction.response.defer()


class EditProjectModal(discord.ui.Modal,title="Edit Project"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow

    # Getting details about edit.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)
    title_input = discord.ui.TextInput(label="Please enter a new project title:",style=discord.TextStyle.short,placeholder="Title",required=False,max_length=100)
    date_input =  discord.ui.TextInput(label="Please enter a new deadline (dd mm yyyy):",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=False,max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        self.workflow.edit_project(int(self.number_input.value),self.title_input.value,self.date_input.value)
        await interaction.response.defer()


class DelProjectModal(discord.ui.Modal,title="Delete Project"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow
    
    # Getting project number.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        self.workflow.del_project(int(self.number_input.value))
        await interaction.response.defer()


class AddTaskModal(discord.ui.Modal,title="Add Task"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow

    # Getting task details.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Number",required=True,max_length=2)
    task_input = discord.ui.TextInput(label="Please enter a task name:",style=discord.TextStyle.short,placeholder="Name",required=True,max_length=100)
    date_input =  discord.ui.TextInput(label="Please enter a task deadline (dd mm yyyy):",style=discord.TextStyle.short,placeholder="dd mm yyyy",required=False,max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        project = workflow.projects[int(self.number_input.value)-1]
        project.add_task(self.task_input.value,self.date_input.value)
        await interaction.response.defer()


class DelTaskModal(discord.ui.Modal,title="Delete Task"):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow

    # Getting task number.
    number_input = discord.ui.TextInput(label="Please enter a project number:",style=discord.TextStyle.short,placeholder="Project Number",required=True,max_length=2)
    task_number = discord.ui.TextInput(label="Please enter a task number:",style=discord.TextStyle.short,placeholder="Task Number",required=True,max_length=2)

    async def on_submit(self, interaction: discord.Interaction):
        project = workflow.projects[int(self.number_input.value)-1]
        project.del_task(int(self.task_number.value))
        await interaction.response.defer()


class ProjectButtonView(discord.ui.View):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow


    @discord.ui.button(label="Add Project", style=discord.ButtonStyle.primary)
    async def add_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending title response.
        await interaction.response.send_modal(AddProjectModal(workflow=workflow))


    @discord.ui.button(label="Edit Project",style=discord.ButtonStyle.primary)
    async def edit_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending edit response.
        await interaction.response.send_modal(EditProjectModal(workflow=workflow))


    @discord.ui.button(label="Delete Project", style=discord.ButtonStyle.primary)
    async def del_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending number response.
        await interaction.response.send_modal(DelProjectModal(workflow=workflow))


    @discord.ui.button(label="Add Task", style=discord.ButtonStyle.secondary,row=2)
    async def add_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending number response.
        await interaction.response.send_modal(AddTaskModal(workflow=workflow))

    
    @discord.ui.button(label="Delete Task", style=discord.ButtonStyle.secondary,row=2)
    async def del_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending number response.
        await interaction.response.send_modal(DelTaskModal(workflow=workflow))


class DisabledProjectButtonView(discord.ui.View):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow 


    @discord.ui.button(label="Add Project", style=discord.ButtonStyle.primary)
    async def add_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending title response.
        await interaction.response.send_modal(AddProjectModal(workflow=workflow))


    @discord.ui.button(label="Edit Project",style=discord.ButtonStyle.primary, disabled=True)
    async def edit_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending edit response.
        await interaction.response.send_modal(EditProjectModal(workflow=workflow))


    @discord.ui.button(label="Delete Project", style=discord.ButtonStyle.primary,disabled=True)
    async def del_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending number response.
        await interaction.response.send_modal(DelProjectModal(workflow=workflow))

    @discord.ui.button(label="Add Task", style=discord.ButtonStyle.secondary,row=2,disabled=True)
    async def add_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending number response.
        await interaction.response.send_modal(AddTaskModal(workflow=workflow))

    
    @discord.ui.button(label="Delete Task", style=discord.ButtonStyle.secondary,row=2,disabled=True)
    async def del_task(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Sending number response.
        await interaction.response.send_modal(DelTaskModal(workflow=workflow))

    




def run_discord_bot():
    # Initialising bot.
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    intents.message_content = True
    
    global bot
    bot = commands.Bot(command_prefix="!", intents=intents)

    # Creating new workflow.
    global workflow
    workflow = Workflow()
    print("New workflow created.")

    @bot.command()
    async def projects(ctx):

        initial_check = True

        while True:
            # Creating embed for message.
            embed = discord.Embed(color=discord.Color.blurple(),title="Existing Projects")

            if len(workflow.projects) != 0:
                for project in workflow.projects:
                    # Creating field title.
                    field_title = f'{workflow.projects.index(project)+1}. {project.title} - Deadline <t:{project.get_unix_deadline()}:R>' if project.deadline else \
                    f'{workflow.projects.index(project)+1}. {project.title}'
                    # Creating task list for field.
                    if len(project.tasks) != 0:
                        task_list = ""
                        for task in project.tasks:
                            task_list += f'- {task.name} due <t:{task.get_unix_deadline()}:R>\n' if task.deadline else \
                        f'- {task.name}\n'
                    else:
                        task_list = "No tasks."
                    embed.add_field(name=field_title,value=task_list,inline=False)
            else:
                embed.description = 'No existing projects.'

            # Creating UI at bottom of message.
            if len(workflow.projects) != 0:
                view = ProjectButtonView(workflow=workflow)
            else:
                view = DisabledProjectButtonView(workflow=workflow)

            # Updating message.
            if initial_check:
                message = await ctx.send(embed=embed,view=view,delete_after=300)
                initial_check = False
                await bot.wait_for('interaction')
            else:
                await message.edit(embed=embed,view=view,delete_after=300)
                await bot.wait_for('interaction')

    bot.run(TOKEN)