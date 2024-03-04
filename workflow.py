'''
Workflow Object

Created on Tuesday 2nd January 2024
@author: Harry New

'''

from datetime import datetime

import templates

# - - - - - - - - - - - - - - - - - - - - - - - - - -

class Workflow():

  def __init__(self) -> None:
    self.projects = []
    self.teams = []
    self.active_channel = None
    self.active_message = None

  #   -   -   -   -   -   -   -   -   -   -   -   -   -
  # Project specific methods.

  # Create new project with title and deadline.
  def add_project(self, title, deadline: str=None) -> None:
    new_project = Project(title, len(self.projects)+1,deadline)
    self.projects.append(new_project)
    return new_project
  
  # Adding 100 days of code project.
  def add_100days_project(self) -> None:
    new_project = templates.DaysOfCode(len(self.projects)+1)
    self.projects.append(new_project)
    return new_project

  # Remove project with number.
  def del_project(self, number) -> None:
    project = self.projects[number-1]
    # Getting teams assigned to project.
    team_ids = project.team_ids
    for team_id in team_ids:
      team = self.get_team_from_id(team_id)
      team.project_ids.remove(project.id)
    # Removing project.
    del self.projects[number-1]

  # Edit project with number.
  def edit_project(self, number, name, deadline):
    project = self.projects[number-1]
    project.name = name
    project.deadline = convert_deadline(deadline)

  # Get project names.
  def get_project_names(self):
    project_names = []
    for project in self.projects:
      project_names.append(project.name)
    return project_names

  # Get project from id.
  def get_project_by_id(self, id_number):
    for project in self.projects:
      if int(project.id) == int(id_number):
        return project
  
  # Get project from title.
  def get_project_from_name(self,name):
    for project in self.projects:
      if project.name == name:
        return project

  #   -   -   -   -   -   -   -   -   -   -   -   -   -
  # Team specific methods.

  # Add team.
  def add_team(self,title,role_id=None,manager_role_id=None):
    team = Team(title,role_id=role_id,manager_role_id=manager_role_id,id=len(self.teams)+1)
    self.teams.append(team)
    return team

  # Delete team.
  def del_team(self,number):
    team = self.teams[int(number)-1]
    # Getting projects assigned to team.
    for project_id in team.project_ids:
      project = self.get_project_by_id(project_id)
      project.team_ids.remove(team.id)
    # Removing team.
    return self.teams.pop(int(number)-1)
  
  # Get manager role ids.
  def get_manager_role_ids(self):
    manager_ids = []
    for team in self.teams:
      manager_ids.append(team.manager_role_id)
    return manager_ids

  # Get team role ids.
  def get_role_ids(self):
    role_ids = []
    for team in self.teams:
      role_ids.append(team.role_id)
    return role_ids
  
  # Get team from role id.
  def get_team_from_role_id(self,role_id):
    for team in self.teams:
      if team.role_id == role_id:
        return team

  # Get team from manager id.
  def get_team_from_manager_id(self,manager_id):
    for team in self.teams:
      if team.manager_role_id == manager_id:
        return team
  
  # Get team from id.
  def get_team_from_id(self,id):
    for team in self.teams:
      if team.id == id:
        return team
      
  # Get team from name.
  def get_team_from_name(self,name):
    for team in self.teams:
      if team.name == name:
        return team
    

class Project():

  def __init__(self,name,id,deadline: str = None) -> None:
    self.name = name
    self.id = id
    self.deadline = convert_deadline(deadline) if deadline else None
    self.tasks = []
    self.team_ids = []
    self.description = None
    self.status = "PENDING"
    self.priority = None

  # Add task.
  def add_task(self,name,deadline) -> None:
    task = Task(name,deadline,len(self.tasks)+1,self.id)
    self.tasks.append(task)
    return task

  # Delete task
  def del_task(self,number) -> None:
    del self.tasks[number-1]

  # Edit deadline.
  def edit_deadline(self,deadline) -> None:
    self.deadline = convert_deadline(deadline)

  # Getting deadline in unix.
  def get_unix_deadline(self) -> int:
    deadline = datetime(year=self.deadline['year'],month=self.deadline['month'],day=self.deadline['day'])
    return round(deadline.timestamp())
  
  # Adding team to project.
  def add_team(self,team):
    self.team_ids.append(team.id)
    team.project_ids.append(self.id)

  # Removing team from project.
  def remove_team(self,team):
    self.team_ids.remove(team.id)
    team.project_ids.remove(self.id)

  # Getting teams from ids.
  def get_teams_from_ids(self,workflow):
    teams = []
    for team_id in self.team_ids:
      team = workflow.get_team_from_id(team_id)
      teams.append(team)
    return teams

  def change_description(self,description):
      self.description = description

  def change_status(self,status):
    self.status = status

  def change_priority(self,priority):
    self.priority = priority



class Task():

    def __init__(self,name,deadline,task_id,project_id) -> None:
        self.name = name
        self.id = task_id
        self.deadline = convert_deadline(deadline)
        self.project = project_id
        self.member_ids = []
        self.description = None
        self.status = "PENDING"
        self.priority = None
        self.archive = False
        self.logs = {}
    
    def assign_member(self,member):
      self.member_ids.append(member.id)

    def add_log(self,author,comment):
      current_datetime = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
      log_info = [comment,author.id]
      self.logs[current_datetime] = log_info

    def remove_log(self,datetime):
      del self.logs[datetime]

    def get_members(self,guild):
      members = []
      for member_id in self.member_ids:
        members.append(guild.get_member(member_id))
      return members
    
    def change_description(self,description):
      self.description = description

    def change_status(self,status):
      self.status = status

    def change_priority(self,priority):
      self.priority = priority

    def get_unix_deadline(self) -> int:
      deadline = datetime(year=self.deadline['year'],month=self.deadline['month'],day=self.deadline['day'])
      return round(deadline.timestamp())

# - - - - - - - - - - - - - - - - - - - - - - - - - -

class Team():

  def __init__(self,name,role_id:None,manager_role_id:None,id) -> None:
    self.name = name
    self.id = id
    self.role_id = role_id
    self.manager_role_id = manager_role_id
    self.project_ids = []

  # Adding project to teams.
  def add_project(self,project: Project):
    project.team_ids.append(self.id)
    self.project_ids.append(project.id)

  # Deleting project to teams.
  def del_project(self,project: Project):
    project.team_ids.remove(self.id)
    self.project_ids.remove(project.id)

  # Getting projects from ids..
  def get_projects_from_ids(self,workflow):
    projects = []
    for project_id in self.project_ids:
      project = workflow.get_project_by_id(project_id)
      projects.append(project)
    return projects

# - - - - - - - - - - - - - - - - - - - - - - - - - -

class DatetimeConversionError(Exception):
    "Raised when deadline input cannot be converted to a datetime object."
    pass

# - - - - - - - - - - - - - - - - - - - - - - - - - -

# Converting string input to datetime object.
def convert_deadline(deadline_input):
    try:
        if deadline_input == None:
            deadline = None
        else:
            deadline = datetime.strptime(deadline_input, "%d %m %Y")
            deadline = {
              'day': deadline.day,
              'month': deadline.month,
              'year': deadline.year
            }
    except:
        raise DatetimeConversionError

    return deadline