'''
Workflow Object

Created on Tuesday 2nd January 2024
@author: Harry New

'''

from datetime import datetime

class Workflow():

    def __init__(self) -> None:
        # Storing projects in dictionary.
        self.projects = [Project('Test','07 01 2024')]

    # Create new project with title and deadline.
    def add_project(self, title, deadline) -> None:
        new_project = Project(title, deadline)
        self.projects.append(new_project)

    # Remove project with number.
    def del_project(self, number) -> None:
        del self.projects[number-1]

    # Edit project with number.
    def edit_project(self, number, new_title, new_deadline):
        project = self.projects[number-1]
        project.title = new_title
        project.deadline = convert_deadline(new_deadline)


class Project():

    def __init__(self,title,deadline) -> None:
        self.tasks = []
        self.title = title
        self.deadline = convert_deadline(deadline)


    def get_unix_deadline(self) -> int:
        return round(self.deadline.timestamp())


class DatetimeConversionError(Exception):
    "Raised when deadline input cannot be converted to a datetime object."
    pass


# Converting string input to datetime object.
def convert_deadline(deadline_input):
    try:
        deadline = datetime.strptime(deadline_input, "%d %m %Y")
    except:
        raise DatetimeConversionError

    return deadline