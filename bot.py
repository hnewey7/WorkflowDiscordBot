'''
Bot Script for the Workflow Bot

Created on Monday 1st January 2024
@author: Harry New

'''

import discord
import discord.ext.commands as commands
from workflow import Workflow, DatetimeConversionError


class ProjectButtonView(discord.ui.View):

    def __init__(self,workflow):
        super().__init__()
        self.workflow = workflow


    @discord.ui.button(label="Add Project", style=discord.ButtonStyle.success)
    async def add_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check for correct user and channel.
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        # Storing all messages.
        message_objects = []

        try:
            # Sending title response.
            await interaction.response.send_message("**Please enter a project title:**")
            message_objects.append(await interaction.original_response())
            title = await bot.wait_for('message', timeout=30, check=check)
            message_objects.append(title)

            # Sending deadline response.
            deadline_prompt = await interaction.followup.send("**Please enter a deadline for the project (%H:%M:%S %d-%m-%Y):**")
            message_objects.append(deadline_prompt)
            deadline = await bot.wait_for('message', timeout=30, check=check)
            message_objects.append(deadline)

            while True:
                try:
                    # Adding project to workflow.
                    self.workflow.add_project(title.content,deadline.content)
                    break
                except DatetimeConversionError:
                    # Prompting user to input correct format.
                    deadline_error = await interaction.followup.send("**Invalid deadline, please try again.**")
                    message_objects.append(deadline_error)
                    deadline_error_response = await bot.wait_for('message', timeout=30, check=check)
                    deadline = deadline_error_response
                    message_objects.append(deadline_error_response)
        except TimeoutError:
            pass
        
        # Deleting all messages.
        for message in message_objects:
            await message.delete()


    @discord.ui.button(label="Delete Project", style=discord.ButtonStyle.danger)
    async def del_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check for correct user and channel.
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        # Storing all messages.
        message_objects = []

        try:
             # Sending number response.
            await interaction.response.send_message("**Please enter a project number: **")
            message_objects.append(await interaction.original_response())
            number = await bot.wait_for('message', timeout=30, check=check)
            message_objects.append(number)

            while True:
                try:
                    # Deleting projects from the workflow.
                    self.workflow.del_project(int(number.content))
                    break
                except:
                    # Prompting user to re-enter a valid project number
                    error_message = await interaction.followup.send("**Invalid project number, please try again.**")
                    message_objects.append(error_message)
                    error_response = await bot.wait_for('message',timeout=30,check=check)
                    number = error_response
                    message_objects.append(error_response)

        except TimeoutError:
            pass

        # Deleting all messages.
        for message in message_objects:
            await message.delete()




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
            # Creating content of message.
            content = '>>> # Existing Projects:\n'

            if len(workflow.projects) != 0:
                for project in workflow.projects:
                    content += f'### {workflow.projects.index(project)+1}. {project.title} - Deadline <t:{project.get_unix_deadline()}:R>\n' if project.deadline else \
                    f'{workflow.projects.index(project)+1}. {project.title}\n'
            else:
                content += '### No existing projects.\n '

            # Creating UI at bottom of message.
            view = ProjectButtonView(workflow=workflow)

            # Updating message.
            if initial_check:
                message = await ctx.send(content=content,view=view,delete_after=300)
                initial_check = False
                await bot.wait_for('message_delete')
            else:
                await message.edit(content=content,view=view,delete_after=300)
                await bot.wait_for('message_delete')

    bot.run(TOKEN)