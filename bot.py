import discord
import discord.ext.commands as commands
from workflow import Workflow


def run_discord_bot():
    # Initialising bot.
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    intents.message_content = True
    
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
        view = discord.ui.View()
        add_project_button = discord.ui.Button(label="Add Project")
        del_project_button = discord.ui.Button(label="Delete Project")
        view.add_item(add_project_button)
        view.add_item(del_project_button)

        await ctx.send(content=content,view=view,delete_after=300)


    bot.run(TOKEN)