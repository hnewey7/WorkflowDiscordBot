'''
Module for managing storage to json.

Created on Monday 5th February 2024.
@author: Harry New

'''

import discord
import logging
import json
from workflow import Workflow

# - - - - - - - - - - - - - - - - - - -

global logger
logger = logging.getLogger()

# - - - - - - - - - - - - - - - - - - -

def save_to_json(workflows):
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
      serialized_project = project
      # Serializing tasks.
      serialized_tasks = []
      for task in project.tasks:
        try:
          serialized_tasks.append(vars(task))
        except:
          logger.info("Failed attempt to save to JSON, already serialized.")
          return
      serialized_project.tasks = serialized_tasks
      # Serializing DaysOfCode project.
      if project.__class__.__name__ == "DaysOfCode":
        for member in project.members:
          project.member_ids.append(member.id)
        del project.members
      # Adding project dictionary.
      projects_dictionary[project.id] = vars(serialized_project)
    

    for team in workflows[server_id].teams:
      # Adding team dictionary.
      teams_dictionary[team.name] = vars(team)


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
async def convert_from_json(workflow_json, client):
  # Creating workflow dictionary.
  workflows = {}

  for guild_id in workflow_json.keys():
    logger.info(f"Loading data for guild, {guild_id}.")
    guild = await client.fetch_guild(guild_id)
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
      project_deadline = f"{project_deadline['day']} {project_deadline['month']} {project_deadline['year']}" if project_deadline else None

      # Adding project if DaysOfCode.
      if project_title == "100 Days of Code":
        project = workflow.add_100days_project()
        for member_id in workflow_json[guild_id]['projects'][project_id]['member_ids']:
          project.members.append(await guild.fetch_member(member_id))
        for member_id in workflow_json[guild_id]['projects'][project_id]['progress'].keys():
          project.progress[int(member_id)] =workflow_json[guild_id]['projects'][project_id]['progress'][member_id]
        for member_id in workflow_json[guild_id]['projects'][project_id]['time_checked']:
          project.time_checked[int(member_id)] = workflow_json[guild_id]['projects'][project_id]['time_checked'][member_id]
      else:
        # Adding project. 
        project = workflow.add_project(project_title,project_deadline)
      project.team_ids = workflow_json[guild_id]['projects'][project_id]['team_ids']
      logger.info(f"Loading project, {project_title} ({project_deadline}).")

      # Adding tasks.
      for task in workflow_json[guild_id]['projects'][project_id]['tasks']:
        # Getting task details.
        task_name = task['name']
        task_deadline = task['deadline']
        task_deadline = f"{task_deadline['day']} {task_deadline['month']} {task_deadline['year']}" if task_deadline else None

        # Adding task.
        if project.__class__.__name__ != "DaysOfCode":
          new_task = project.add_task(task_name,task_deadline)

          # Adding attributes to task.
          new_task.member_ids = task['member_ids']
          new_task.description = task['description']
          new_task.status = task['status']
          new_task.priority = task['priority']
          new_task.archive = task['archive']
          new_task.logs = task['logs']

        logger.info(f"Loading task, {task_name} ({task_deadline}).")
    

    # Adding teams.
    for team_name in workflow_json[guild_id]['teams'].keys():
      # Getting team details.
      role_id = workflow_json[guild_id]['teams'][team_name]['role_id']
      manager_role_id = workflow_json[guild_id]['teams'][team_name]['manager_role_id']

      # Adding team.
      team = workflow.add_team(team_name,role_id=role_id,manager_role_id=manager_role_id)
      team.project_ids = workflow_json[guild_id]['teams'][team_name]['project_ids']
      logger.info(f"Loading team, {team_name}.")

    # Adding workflow to workflows.
    workflows[guild_id] = workflow
    logger.info("- - - - - - - - - - - - - - - - - - - - - -")

  logger.info("Data loading finished.")
  logger.info("- - - - - - - - - - - - - - - - - - - - - -")

  return workflows
