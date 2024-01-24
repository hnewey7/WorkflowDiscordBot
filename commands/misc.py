'''
Module for defining miscellaneous commands.

Created on Wednesday 24th January 2024.
@author: Harry New

'''

# Disconnect command.
async def disconnect_command(client):
    await client.close()

# Show workflow command.
async def show_workflow_command(workflow):
    logger.info("Requested workflow display.")
    print(workflow.projects)

# Show guild ids.
async def show_guild_command(command):
    logger.info("Requested guild id.")
    print(command.guild.id)

