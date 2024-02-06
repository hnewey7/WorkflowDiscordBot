'''
Module for managing storage to json.

Created on Monday 5th February 2024.
@author: Harry New

'''

import logging
import json
from workflow import Workflow

# - - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - - -

def save_to_json(workflows):
  logger.info("- - - - - - - - - - - - - - - - - - - - - -")
  logging.info("Saving workflows as json file.")

  # Creating new structure for storing as json.
  workflows_json = {}

  for server_id in workflows.keys():
    # Creating dictionary to store guild details.
    guild_dictionary = {}

    # Creating dictionary to store all projects.
    projects_dictionary = {}

    # Creating dictionary to store all teams.
    teams_dictionary = {}

    # Adding active channel name to dictionary.
    guild_dictionary['active_channel'] = workflows[server_id].active_channel.id if workflows[server_id].active_channel else None
    guild_dictionary['active_message'] = workflows[server_id].active_message.id if workflows[server_id].active_message else None


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
      project_dictionary['teams'] = project.get_team_ids()

      # Adding project dictionary.
      projects_dictionary[project.id] = project_dictionary
    

    for team in workflows[server_id].teams:
      # Creating team dictionary.
      team_dictionary = {}

      # Adding team details.
      team_dictionary['role_id'] = team.role_id
      team_dictionary['manager_role_id'] = team.manager_role_id
      team_dictionary['projects'] = team.get_project_ids()

      # Adding team dictionary.
      teams_dictionary[team.name] = team_dictionary


    # Adding dictionaries to guild dictionary.
    guild_dictionary['projects'] = projects_dictionary
    guild_dictionary['teams'] = teams_dictionary

    # Adding guild dictionary
    workflows_json[server_id] = guild_dictionary


  with open("server_workflows.json", "w") as outfile: 
      json.dump(workflows_json, outfile)
  logging.info("All data saved.")
  logging.info("Disconnecting from client.")
  logger.info("- - - - - - - - - - - - - - - - - - - - - -")


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
    

    # Adding teams.
    for team_name in workflow_json[guild_id]['teams'].keys():
      # Getting team details.
      role_id = workflow_json[guild_id]['teams'][team_name]['role_id']
      manager_role_id = workflow_json[guild_id]['teams'][team_name]['manager_role_id']

      # Adding team.
      workflow.add_team(team_name,role_id=role_id,manager_role_id=manager_role_id)
      logger.info(f"Loading team, {team_name}.")


    # Loading teams to all projects.
    for project_id in workflow_json[guild_id]['projects'].keys():
      project = workflow.get_project_by_id(project_id)
      project.load_teams(workflow,workflow_json[guild_id]['projects'][project_id]['teams'])

    # Loading projects to all teams.
    for team_name in workflow_json[guild_id]['teams'].keys():
      team = workflow.get_team_from_name(team_name)
      team.load_projects(workflow,workflow_json[guild_id]['teams'][team_name]['projects'])


    # Adding workflow to workflows.
    workflows[guild_id] = workflow

  logger.info("- - - - - - - - - - - - - - - - - - - - - -")
  logger.info("Data loading finished.")
  logger.info("- - - - - - - - - - - - - - - - - - - - - -")

  return workflows
