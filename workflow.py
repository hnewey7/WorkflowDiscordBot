'''
Workflow Object

Created on Tuesday 2nd January 2024
@author: Harry New

'''

from datetime import datetime

# - - - - - - - - - - - - - - - - - - - - - - - - - -

class Workflow():

  def __init__(self) -> None:
    # Storing projects in dictionary.
    self.projects = []
    # Active projects channel and message.
    self.active_channel = None
    self.active_message = None
    # Storing teams.
    self.teams = []

  #   -   -   -   -   -   -   -   -   -   -   -   -   -
  # Project specific methods.

  # Create new project with title and deadline.
  def add_project(self, title, deadline) -> None:
    new_project = Project(title, deadline, len(self.projects)+1)
    self.projects.append(new_project)
    return new_project

  # Remove project with number.
  def del_project(self, number) -> None:
    del self.projects[number-1]

  # Edit project with number.
  def edit_project(self, number, new_title, new_deadline):
    project = self.projects[number-1]
    project.title = new_title
    project.deadline = convert_deadline(new_deadline)

  # Get project titles.
  def get_project_titles(self):
    project_titles = []
    for project in self.projects:
      project_titles.append(project.title)
    return project_titles

  # Get project from id.
  def get_project_by_id(self, id_number):
    for project in self.projects:
      if int(project.id) == int(id_number):
        return project
  
  # Get project from title.
  def get_project_from_title(self,title):
    for project in self.projects:
      if project.title == title:
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
    return self.teams.pop(int(number)-1)
  
  # Get manager role ids.
  def get_manager_role_ids(self):
    manager_ids = []
    for team in self.teams:
      manager_ids.append(team.manager_role_id)
    return manager_ids
  
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

  def __init__(self,title,deadline,project_id) -> None:
    self.tasks = []
    self.title = title
    self.deadline = convert_deadline(deadline)
    self.id = project_id
    self.teams = []

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

  def get_unix_deadline(self) -> int:
    return round(self.deadline.timestamp())
  
  # Getting team ids.
  def get_team_ids(self):
    team_ids = []
    for team in self.teams:
      team_ids.append(team.id)
    return team_ids
  
  # Loading teams.
  def load_teams(self,workflow,team_ids):
    for team_id in team_ids:
      team = workflow.get_team_from_id(team_id)
      self.teams.append(team)


class Task():

    def __init__(self,name,deadline,task_id,project_id) -> None:
        self.name = name
        self.deadline = convert_deadline(deadline)
        self.id = task_id
        self.project = project_id
        self.member_ids = []
        self.description = None
        self.complete = False
        self.priority = None
    
    def assign_member(self,member):
      self.member_ids.append(member.id)

    def get_members(self,guild):
      members = []
      for member_id in self.member_ids:
        members.append(guild.get_member(member_id))
      return members
    
    def change_description(self,description):
      self.description = description

    def change_status(self,status):
      if status == "COMPLETED":
        self.complete = True
      else:
        self.complete = False

    def change_priority(self,priority):
      self.priority = priority

    def get_unix_deadline(self) -> int:
        return round(self.deadline.timestamp())

# - - - - - - - - - - - - - - - - - - - - - - - - - -

class Team():

  def __init__(self,name,role_id:None,manager_role_id:None,id) -> None:
    self.name = name
    self.role_id = role_id
    self.manager_role_id = manager_role_id
    self.projects = []
    self.id = id

  # Adding project to teams.
  def add_project(self,project: Project):
    project.teams.append(self)
    self.projects.append(project)

  # Deleting project to teams.
  def del_project(self,project: Project):
    project.teams.remove(self)
    self.projects.remove(project)

  # Getting project ids.
  def get_project_ids(self):
    project_ids = []
    for project in self.projects:
      project_ids.append(project.id)
    return project_ids
  
  # Load projects.
  def load_projects(self,workflow,project_ids):
    for project_id in project_ids:
      project = workflow.get_project_by_id(project_id)
      self.projects.append(project)

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
    except:
        raise DatetimeConversionError

    return deadline