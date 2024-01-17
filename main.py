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
from workflow import Workflow

# - - - - - - - - - - - - - - - - - - - - - - - 

def init_saved():
    # Loading workflows dictionary.
    global workflows

    try:
        # Loading json.
        json_file = open('server_workflows.json',)
        workflows_json = json.load(json_file)
        workflows = convert_json(workflows_json)
    except:
        # Creating new dictionary.
        workflows = {}

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
    # Initialising and running client.
    client = discord.Client(intents=intents)

    # Initialising events.
    init_events(client)
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")
    logger.info("Initialising events.")
    logger.info("Running client.")
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")
    client.run(TOKEN,reconnect=True,log_handler=None)

    return client


def init_events(client):
    global temp_client
    temp_client = client

    # On guild join event.
    @client.event
    async def on_guild_join(guild):
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")
        logger.info(f"Joined discord server ({guild.name}).")

        # Creating "Workflow Manager" role.
        await guild.create_role(name="Workflow Manager", colour=discord.Colour.teal())
        logger.info("Workflow Manager role has been created.")

        # Creating workflow for guild.
        new_workflow = Workflow()
        logger.info("Creating new workflow for server.")

        # Adding workflow to dictionary.
        workflows[guild.id] = new_workflow
        logger.info("Adding workflow to workflows dictionary.")


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
                    individual_task['deadline'] = task.deadline.strftime("%d %m %Y")

                    # Adding individual task to task dictionary.
                    task_dictionary[task.id] = individual_task
                
                # Adding project details.
                project_dictionary['tasks'] = task_dictionary
                project_dictionary['name'] = project.title
                project_dictionary['deadline'] = project.deadline.strftime("%d %m %Y")

                # Adding project dictionary.
                guild_dictionary[project.id] = project_dictionary
            
            # Adding guild dictionary
            workflows_json[server_id] = guild_dictionary


        with open("server_workflows.json", "w") as outfile: 
            json.dump(workflows_json, outfile)
        logging.info("All data saved.")
        logging.info("Disconnecting from client.")
        logger.info("- - - - - - - - - - - - - - - - - - - - - -")

# - - - - - - - - - - - - - - - - - - - - - - - 

# Converting json into workflows dictionary.    
def convert_json(workflow_json):
    # Creating workflow dictionary.
    workflows = {}

    for guild_id in workflow_json.keys():
        # Creating new workflow.
        workflow = Workflow()
        
        # Adding projects.
        for project_id in workflow_json[guild_id].keys():
            # Getting project details.
            project_title = workflow_json[guild_id][project_id]['name']
            project_deadline = workflow_json[guild_id][project_id]['deadline']

            # Adding project.
            workflow.add_project(project_title,project_deadline)

            # Adding tasks.
            for task in workflow_json[guild_id][project_id]['tasks'].keys():
                # Getting task details.
                task_name = workflow_json[guild_id][project_id]['tasks'][task].name
                task_deadline = workflow_json[guild_id][project_id]['tasks'][task].deadline

                # Adding task.
                workflow.get_project_by_id(project_id).add_task(task_name,task_deadline)
    
        # Adding workflow to workflows.
        workflows[guild_id] = workflow

    return workflows

# - - - - - - - - - - - - - - - - - - - - - - - 

if __name__ == "__main__":

    global client 

    # Initialising saved data.
    init_saved()

    # Initialising logging.
    init_logging()

    # Initialising intents.
    TOKEN = 'MTE5MTQ0NzQ5OTM4NzQzNzEwOA.GgSomy.bK3obSpCL8KdShCpJss8zyw3DOFcb5saIL785g'
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True

    # Initialising client.
    client = init_client(TOKEN)



    