import discord
import commands
from workflow import Workflow


async def receive_input(message) -> str:
    return message.content


def run_discord_bot():
    # Initialising bot.
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # Creating new workflow.
    workflow = Workflow()
    print("New workflow created.")


    @client.event
    async def on_ready():
        print(f'{client.user} is now running.')


    @client.event
    async def on_message(message):
        # Ignoring bot messages.
        if message.author == client.user:
            return
        
        # Message info.
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        print(f"{username} has said: '{user_message}' ({channel})")

        # Evaluating command.
        if user_message[0] == '!':
            print(f"{username} has requested command.")
            await message.channel.send(commands.handle_command(user_message[1:],workflow=workflow))

    client.run(TOKEN)