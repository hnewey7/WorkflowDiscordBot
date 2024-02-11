'''
Package for handling all commands.

Created on Wednesday 24th January 2024.
@author: Harry.New

'''

from .active_channel import restart_looping,set_active_channel_command, init_active_channel
from .teams import display_teams    
from .manage_projects import manage_projects
from .manage_task import manage_tasks
from .misc import help_command,disconnect_command, show_workflow_command, show_guild_command, delete_roles_command


# Initialising commands.
def init_commands(logging):
    # Initialising logger.
    global logger
    logger = logging
    # Initialising active channel.
    init_active_channel(logger)


# Evaluating all discord commands.
async def evaluate_command(command, client, workflow):
    if "help" == command.content[1:]:
        logger.info("Requesting help command.")
        await help_command(command,client,workflow)
        await command.delete()
    if "set_active_channel" == command.content[1:]:
        logger.info("Requesting set active channel.")
        await set_active_channel_command(command, workflow, client)
        await command.delete()
    if "manage_projects" == command.content[1:]:
        logger.info("Requesting manage projects.")
        await manage_projects(command,client,workflow)
        await command.delete()
    if "manage_tasks" == command.content[1:]:
        logger.info("Requesting manage tasks.")
        await manage_tasks(command,client,workflow)
        await command.delete()
    if "teams" == command.content[1:]:
        logger.info("Requesting teams.")
        await display_teams(command,workflow,client)
        await command.delete()
    if "disconnect" == command.content[1:]:
        logger.info("Requesting disconnect.")
        await disconnect_command(client)
        await command.delete()
    if "show_workflow" == command.content[1:]:
        logger.info("Requesting show workflow.")
        await show_workflow_command(workflow)
        await command.delete()
    if "show_guild" == command.content[1:]:
        logger.info("Requesting show guild.")
        await show_guild_command(command)
        await command.delete()
    if "delete_roles" == command.content[1:]:
        logger.info("Requesting deleting all roles.")
        await delete_roles_command(command)
        await command.delete()

