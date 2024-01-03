'''
Workflow Object
@author: Harry New
2nd Jan 2024
'''

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


class Project():

    def __init__(self,title,deadline) -> None:
        self.tasks = []
        self.title = title
        self.deadline = deadline


class EmptyProjectListError(Exception):
    "Raised when action performed on empty project list."
    pass

class IndexOutOfRangeError(Exception):
    "Raised when index out of range."
    pass