'''
Main for Workflow Bot

Created on Monday 1st January 2024
@author: Harry New

'''

import discord
import logging
from datetime import datetime
import pathlib
import logging.config
import logging.handlers
import json

import commands
from workflow import Workflow
from json_storage import save_to_json,convert_from_json

# - - - - - - - - - - - - - - - - - - - - - - - 

def init_logging():
  global logger
  logger = logging.getLogger()

  # Setting up logger with config.
  config_file = pathlib.Path("logging_config.json")
  with open(config_file) as f_in:
    config = json.load(f_in)
  logging.config.dictConfig(config)

  # Adding logger to commands.
  commands.init_commands(logger)

  return logger


def init_client(token):
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")
    # Initialising and running client.
    client = discord.Client(intents=intents)
    tree = discord.app_commands.CommandTree(client)

    # Initialising events.
    init_events(client,tree)
    logger.info("Initialising events.")

    # Initialising commands.
    init_commands(client,tree)
    logger.info("Initialising commands.")

    logger.info("Running client.")
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")
    client.run(TOKEN,reconnect=True,log_handler=None)

    return client


def init_events(client,tree):
    global temp_client
    temp_client = client


    # On connect event.
    @client.event
    async def on_connect():
        # Initialising saved data.
        logger.info("Initialising saved data.")
        await init_saved(client)

        # Initialising active message looping.
        logger.info("Initialising message looping.")
        await init_message_looping(client)
        

    # On guild join event.
    @client.event
    async def on_guild_join(guild):
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")
        logger.info(f"Joined discord server ({guild.name}).")
        
        for role in await guild.fetch_roles():
            if role.name == "Workflow Manager":
                admin_role = role
                break
        else:
            # Creating "Workflow Manager" role.
            admin_role = await guild.create_role(name="Workflow Manager", colour=discord.Colour.teal())
            logger.info("Workflow Manager role has been created.")

        # Creating workflow for guild.
        new_workflow = Workflow()
        logger.info("Creating new workflow for server.")

        # Adding workflow to dictionary.
        workflows[str(guild.id)] = new_workflow
        logger.info("Adding workflow to workflows dictionary.")

    # On role update event.
    @client.event
    async def on_member_update(before, after):
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")
        logging.info("Member's role updated event.")
        # Getting workflow.
        guild = after.guild
        workflow = workflows[str(guild.id)]
        # Getting list of manager role ids.
        manager_ids = workflow.get_manager_role_ids()

        # Getting new role.
        for role in after.roles:
          if role not in before.roles:
            new_role = role

        # Check if manager role.
        try:
            if new_role.id in manager_ids:
                logging.info(f"Manager role updated, {new_role.name}")
                team = workflow.get_team_from_manager_id(new_role.id)
                # Getting team role.
                team_role = guild.get_role(team.role_id)

                # Adding normal team role.
                await after.add_roles(team_role)
                await team_role.edit(reason="Trigger guild role event.")
                logging.info(f"Adding member to standard team role, {team_role.name}")
        except:
            pass
        

    @client.event
    async def on_guild_role_delete(role):
      logger.info("- - - - - - - - - - - - - - - - - - - - - -")
      logging.info("Role deleted event.")
      # Getting workflow.
      guild = role.guild
      workflow = workflows[str(guild.id)]
      # Getting list of manager role ids.
      manager_ids = workflow.get_manager_role_ids()
      team_role_ids = workflow.get_role_ids()
      
      # Check if manager role.
      if role.id in manager_ids:
        logging.info(f"Manager role deleted, {role.name}")
        # Getting team and deleting.
        team = workflow.get_team_from_manager_id(role.id)
        logging.info(f"Deleting team, {team.name}")
        workflow.del_team(workflow.teams.index(team)+1)
        # Removing team member role.
        logging.info(f"Deleting team member role.")
        role = guild.get_role(team.role_id)
        await role.edit(reason="Trigger guild role event.")
        await role.delete()
      elif role.id in team_role_ids:
        logging.info(f"Team member role deleted, {role.name}")
        # Getting team and deleting.
        team = workflow.get_team_from_role_id(role.id)
        logging.info(f"Deleting team, {team.name}")
        workflow.del_team(workflow.teams.index(team)+1)
        # Removing team manager role.
        logging.info(f"Deleting team member role.")
        role = guild.get_role(team.manager_role_id)
        await role.edit(reason="Trigger guild role event.")
        await role.delete()
      else:
        pass

    # On guild remove event.
    @client.event
    async def on_guild_remove(guild):
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")
        logger.info(f"Removed discord server ({guild.name}).")

        # Removing guild from workflow.
        workflows.pop(guild.id)
        logger.info("Removing guild from workflows dictionary.")

    # On message event.
    @client.event
    async def on_message(message):
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")
        logger.info(f"Message sent in {message.guild.name} {message.channel.name}.")
        if len(message.content) > 0 and message.content[0] == "!":
            logger.info(f"Command requested in {message.guild.name} {message.channel.name}.")
            await commands.evaluate_command(message,temp_client,workflows[str(message.guild.id)],tree)

    # On disconnect event.
    @client.event
    async def on_disconnect():
      # Saving data to json.
      save_to_json(workflows)

    @client.event
    async def on_ready():
      logger.info("Starting command tree syncing.")
      await tree.sync()
      logger.info("Finished command tree syncing.")


def init_commands(client,tree):

  @tree.command(name="help",description="Provides a list of commands that can be used with the Workflow Bot.")
  async def help_command(interaction):
    logger.info("Requesting help command.")
    await commands.help_command(interaction,workflows[str(interaction.guild.id)])
  
  @tree.command(name="set_active_channel",description="Sets the current channel to the active channel and displays all existing projects in the workflow.")
  @discord.app_commands.checks.has_role("Workflow Manager")
  async def set_active_channel_command(interaction):
    logger.info("Requesting set active channel command.")
    await commands.set_active_channel_command(interaction,workflows[str(interaction.guild.id)],client)
  
  @set_active_channel_command.error
  async def on_set_active_channel_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
     if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("You do not have the necessary role to use this command.")
  
  @tree.command(name="disconnect",description="Disconnects the bot and saves data to JSON.")
  async def disconnect(interaction):
    logger.info("Requesting disconnect command.")
    await commands.disconnect_command(client)

async def init_saved(client):
    # Loading workflows dictionary.
    global workflows
    
    load_check = False

    try:
        # Loading json.
        json_file = open('server_workflows.json',)
        workflows_json = json.load(json_file)
        load_check = True
    except:
        # Creating new dictionary.
        workflows = {}

    if load_check:
        workflows = await convert_from_json(workflows_json, client)


async def init_message_looping(client):
    for guild_id in workflows.keys():
        if workflows[guild_id].active_message:
            await commands.restart_looping(client,workflows[guild_id],await client.fetch_guild(guild_id))

# - - - - - - - - - - - - - - - - - - - - - - - 

if __name__ == "__main__":

    global client 

    # Initialising logging.
    init_logging()

    # Initialising intents.
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True

    # Initialising client.
    client = init_client(TOKEN)



    