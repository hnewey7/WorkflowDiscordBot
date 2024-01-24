'''
Package for handling all commands.

Created on Wednesday 24th January 2024.
@author: Harry.New

'''

from .active_channel import set_active_channel_command, restart_looping
from .misc import disconnect_command, show_workflow_command, show_guild_command


# Initialising commands.
def init_commands(logging):
    # Initialising logger.
    global logger
    logger = logging


# Evaluating all discord commands.
async def evaluate_command(command, client, workflow):
    if "set_active_channel" == command.content[1:]:
        await set_active_channel_command(command, workflow, client)
    if "disconnect" == command.content[1:]:
        await disconnect_command(client)
    if "show_workflow" == command.content[1:]:
        await show_workflow_command(workflow)
    if "show_guild" == command.content[1:]:
        await show_guild_command(command)