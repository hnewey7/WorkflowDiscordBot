import discord
import discord.ext.commands as commands
from workflow import Workflow


class ProjectButtonView(discord.ui.View):

    @discord.ui.button(label="Add Project", style=discord.ButtonStyle.success)
    async def add_project(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Please enter a project title:")

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        # Wait for title response and delete responses.
        title = await bot.wait_for('message', timeout=30, check=check)
        title_prompt = await interaction.original_response()
        await title.delete()
        await title_prompt.delete()

        await interaction.followup.send("Please enter a deadline for the project (%H:%M:%S %d-%m-%Y).")

        deadline = await bot.wait_for('message', timeout=30, check=check)



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
        # Creating content of message.
        content = '>>> # Existing Projects:\n'

        if len(workflow.projects) != 0:
            for project in workflow.projects:
                content += f'{workflow.projects.index(project)+1}. {project.title} - Deadline <t:{project.get_unit_deadline()}:R>\n' if project.deadline else \
                f'{workflow.projects.index(project)+1}. {project.title}\n'
        else:
            content += '### No existing projects.\n '

        # Creating UI at bottom of message.
        view = ProjectButtonView()

        await ctx.send(content=content,view=view,delete_after=300)

    bot.run(TOKEN)