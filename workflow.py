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

    # Remove existing project.
    def del_project(self,index) -> None:
        if len(self.projects) <= 0:
            raise EmptyProjectListError
        elif index < 0 or index >= len(self.projects):
            raise IndexOutOfRangeError
        else:
            del self.projects[index]

    # Get project by title.
    def get_project_from_title(self,title):
        for project in self.projects:
            if title == project.title:
                return project


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

class IndexOutOfRangeError(Exception):
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