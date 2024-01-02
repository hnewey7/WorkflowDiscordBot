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
    def del_project(self,project) -> None:
        self.projects.remove(project)


class Project():

    def __init__(self,title,deadline) -> None:
        self.tasks = []
        self.title = title
        self.deadline = deadline

