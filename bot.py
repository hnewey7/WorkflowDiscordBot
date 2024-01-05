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
    async def button(ctx):
        view = discord.ui.View()
        button = discord.ui.Select(min_values=1,max_values=1,options=[discord.SelectOption(label="test")],disabled=False)
        view.add_item(button)
        await ctx.send(view=view)

    bot.run(TOKEN)