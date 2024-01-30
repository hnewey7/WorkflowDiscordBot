'''
Main for Workflow Bot

Created on Monday 1st January 2024
@author: Harry New

'''

import discord
import logging
from datetime import datetime
import json

import commands
from workflow import Workflow, Project

# - - - - - - - - - - - - - - - - - - - - - - - 

def init_logging():
    # Creating log file name.
    start_time = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
    log_file_name = "logs\\" + start_time + ".log"
    
    # Creating logger.
    global logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Creating console handler.
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)

    # Creating file handler.
    file_logger = logging.FileHandler(log_file_name)
    file_logger.setLevel(logging.INFO)

    # Creating formatter.
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:   %(message)s","%Y-%m-%d %H:%M:%S")
    file_logger.setFormatter(formatter)
    console_logger.setFormatter(formatter)

    # Adding to logger.
    logger.addHandler(file_logger)
    logger.addHandler(console_logger)

    # Adding logger to commands.
    commands.init_commands(logger)

    return logger


def init_client(token):
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")
    # Initialising and running client.
    client = discord.Client(intents=intents)

    # Initialising events.
    init_events(client)
    logger.info("Initialising events.")

    logger.info("Running client.")
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")
    client.run(TOKEN,reconnect=True,log_handler=None)

    return client


def init_events(client):
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
        workflows[guild.id] = new_workflow
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
            await commands.evaluate_command(message,temp_client,workflows[str(message.guild.id)])

    # On disconnect event.
    @client.event
    async def on_disconnect():
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")
        logging.info("Saving workflows as json file.")

        # Creating new structure for storing as json.
        workflows_json = {}

        for server_id in workflows.keys():
            # Creating dictionary to store guild details.
            guild_dictionary = {}

            # Creating dictionary to store all projects.
            projects_dictionary = {}

            # Adding active channel name to dictionary.
            guild_dictionary['active_channel'] = workflows[server_id].active_channel.id
            guild_dictionary['active_message'] = workflows[server_id].active_message.id

            for project in workflows[server_id].projects:
                # Creating project dictionary.
                project_dictionary = {}

                # Creating task dictionary.
                task_dictionary = {}

                for task in project.tasks:
                    # Creating individual task.
                    individual_task = {}

                    # Adding task details.
                    individual_task['name'] = task.name
                    individual_task['deadline'] = task.deadline.strftime("%d %m %Y") if task.deadline else None

                    # Adding individual task to task dictionary.
                    task_dictionary[task.id] = individual_task
                
                # Adding project details.
                project_dictionary['tasks'] = task_dictionary
                project_dictionary['name'] = project.title
                project_dictionary['deadline'] = project.deadline.strftime("%d %m %Y") if project.deadline else None

                # Adding project dictionary.
                projects_dictionary[project.id] = project_dictionary
            
            # Adding projects dictionary.
            guild_dictionary['projects'] = projects_dictionary

            # Adding guild dictionary
            workflows_json[server_id] = guild_dictionary


        with open("server_workflows.json", "w") as outfile: 
            json.dump(workflows_json, outfile)
        logging.info("All data saved.")
        logging.info("Disconnecting from client.")
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")


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
        workflows = await convert_json(workflows_json, client)


async def init_message_looping(client):
    for guild_id in workflows.keys():
        if workflows[guild_id].active_message:
            await commands.restart_looping(client,workflows[guild_id])

# - - - - - - - - - - - - - - - - - - - - - - - 

# Converting json into workflows dictionary.    
async def convert_json(workflow_json, client):
    # Creating workflow dictionary.
    workflows = {}

    for guild_id in workflow_json.keys():
        logger.info(f"Loading data for guild, {guild_id}.")
        # Creating new workflow.
        workflow = Workflow()

        # Setting active channel.
        try:
            workflow.active_channel = await (await client.fetch_guild(guild_id)).fetch_channel(workflow_json[guild_id]['active_channel'])
            logger.info("Active channel successfully fetched.")
        except:
            workflow.active_channel = None
            logger.info("Active channel unsuccessfully fetched.")

        # Setting active message
        try:
            workflow.active_message = await workflow.active_channel.fetch_message(workflow_json[guild_id]['active_message'])
            logger.info("Active message successfully fetched.")
        except:
            workflow.active_message = None
            logger.info("Active message unsuccessfully fetched.")
        
        # Adding projects.
        for project_id in workflow_json[guild_id]['projects'].keys():
            # Getting project details.
            project_title = workflow_json[guild_id]['projects'][project_id]['name']
            project_deadline = workflow_json[guild_id]['projects'][project_id]['deadline']

            # Adding project.
            workflow.add_project(project_title,project_deadline)
            logger.info(f"Loading project, {project_title} ({project_deadline}).")

            # Adding tasks.
            for task in workflow_json[guild_id]['projects'][project_id]['tasks'].keys():
                # Getting task details.
                task_name = workflow_json[guild_id]['projects'][project_id]['tasks'][task]['name']
                task_deadline = workflow_json[guild_id]['projects'][project_id]['tasks'][task]['deadline']

                # Adding task.
                workflow.get_project_by_id(project_id).add_task(task_name,task_deadline)
                logger.info(f"Loading task, {task_name} ({task_deadline}).")
    
        # Adding workflow to workflows.
        workflows[guild_id] = workflow

    logger.info("- - - - - - - - - - - - - - - - - - - - - -")
    logger.info("Data loading finished.")
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")

    return workflows

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



    