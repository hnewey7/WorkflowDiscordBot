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

    # Create new project with title and deadline.
    def add_project(self, title, deadline) -> None:
        new_project = Project(title, deadline, len(self.projects)+1)
        self.projects.append(new_project)

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
            
    # Add team.
    def add_team(self,title,role_id=None,manager_role_id=None):
        team = Team(title,role_id=role_id,manager_role_id=manager_role_id)
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
            
    # Get project from title.
    def get_project_from_title(self,title):
      for project in self.projects:
       if project.title == title:
          return project

class Project():

    def __init__(self,title,deadline,project_id) -> None:
        self.tasks = []
        self.title = title
        self.deadline = convert_deadline(deadline)
        self.id = project_id

    # Add task.
    def add_task(self,name,deadline) -> None:
        task = Task(name,deadline,len(self.tasks)+1)
        self.tasks.append(task)

    # Delete task
    def del_task(self,number) -> None:
        del self.tasks[number-1]

    # Edit deadline.
    def edit_deadline(self,deadline) -> None:
        self.deadline = convert_deadline(deadline)

    def get_unix_deadline(self) -> int:
        return round(self.deadline.timestamp())


class Task():

    def __init__(self,name,deadline,task_id) -> None:
        self.name = name
        self.deadline = convert_deadline(deadline)
        self.id = task_id
    
    def get_unix_deadline(self) -> int:
        return round(self.deadline.timestamp())

# - - - - - - - - - - - - - - - - - - - - - - - - - -

class Team():

    def __init__(self,title,role_id:None,manager_role_id:None) -> None:
        self.title = title
        self.role_id = role_id
        self.manager_role_id = manager_role_id
        self.projects = []

    # Adding project to teams.
    def add_project(self,project: Project):
        self.projects.append(project)

    # Deleting project to teams.
    def del_project(self,project: Project):
        self.projects.remove(project)

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