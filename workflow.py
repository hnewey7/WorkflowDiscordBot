'''
Workflow Object
@author: Harry New
2nd Jan 2024
'''

from datetime import datetime

class Workflow():

    def __init__(self) -> None:
        # Storing projects in dictionary.
        self.projects = []

    # Create new project from title and add to dictionary.
    def add_project(self, title, deadline) -> None:
        new_project = Project(title, deadline)
        self.projects.append(new_project)

    # Remove existing project by index.
    def del_project_by_index(self,index):
        if len(self.projects) <= 0:
            raise EmptyProjectListError
        elif index < 0 or index >= len(self.projects):
            raise ProjectNotInListError
        else:
            deleted_project = self.projects[index]
            del self.projects[index]
            return deleted_project

    # Remove existing project by title.
    def del_project_by_title(self,title):
        if len(self.projects) <= 0:
            raise EmptyProjectListError
        else:
            deleted_project = self.get_project_from_title(title)
            self.projects.remove(deleted_project)
            return deleted_project

    # Get project by title.
    def get_project_from_title(self,title):
        for project in self.projects:
            if title == project.title:
                return project
        else:
            raise ProjectNotInListError
        


class Project():

    def __init__(self,title,deadline) -> None:
        self.tasks = []
        self.title = title
        self.deadline = convert_deadline(deadline)

    def get_unix_deadline(self) -> int:
        return round(self.deadline.timestamp())


class EmptyProjectListError(Exception):
    "Raised when action performed on empty project list."
    pass

class ProjectNotInListError(Exception):
    "Raised when index out of range."
    pass

class DatetimeConversionError(Exception):
    "Raised when deadline input cannot be converted to a datetime object."
    pass


# Converting string input to datetime object.
def convert_deadline(deadline_input):
    try:
        deadline = datetime.strptime(deadline_input, "%H:%M:%S %d-%m-%Y")
    except:
        raise DatetimeConversionError

    return deadline