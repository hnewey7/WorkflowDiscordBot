'''
Command script for Workflow Bot
@author: Harry New
1st Jan 2024
'''

from workflow import IndexOutOfRangeError,EmptyProjectListError

# Handling all commands.
def handle_command(command, workflow) -> str:
     # Getting components of command.
    main_command = command.split(" ",1)[0].lower()
    parameter_section = " " + command.split(" ",1)[1] if len(command.split(" ")) != 1 else ""

    parameters = extract_parameters(parameter_section)

    if main_command == "help":
        response = help_command()
    elif main_command == "show_projects":
        response = show_projects_command(workflow=workflow)
    elif main_command == "add_project":
        response = add_project_command(parameters,workflow=workflow)
    elif main_command == "del_project":
        response = del_project_command(parameters,workflow=workflow)
    else:
        response = "Please enter a valid command."

    return response



# Initial extraction of parameters.
def extract_parameters(content):
    # Splitting parameters.
    multiple_parameters = content.split(" -")[1:]

    parameter_dictionary = {}

    for parameter in multiple_parameters:
        parameter_components = parameter.split(' ', 1)
        parameter_dictionary[parameter_components[0]] = parameter_components[1]

    return parameter_dictionary


# Help command.
def help_command():
    response = ">>> ## Commands \n\n \
`!add_project -title [TITLE] -deadline (DEADLINE)` \n \
Adds new project to the workflow [requires -title]. \n\n \
`!del_project -index [INDEX]` \n \
Deletes project at specific index [requires -index]. \n\n \
`!help` \n \
Lists all available commands. \n\n \
`!show_projects` \n \
Displays all existing projects in workflow."

    return response



# Adding project command.
def add_project_command(parameters,workflow):
    try:
        title = parameters['title']
        deadline = parameters['deadline'] if 'deadline' in parameters.keys() else None
        workflow.add_project(title,deadline)
        response = f"New project (**{title}**) has been added, with deadline (**{parameters['deadline']}**)." if 'deadline' in parameters.keys() else f"New project (**{title}**)."
    except KeyError:
        response = 'Please include `-title` when adding projects.'

    return response



# Deleting project command.
def del_project_command(parameters,workflow):
    try:
        index = int(parameters['index'])
        workflow.del_project(index-1)
        response = f"Project (**Number {index}**) was deleted."
    except IndexOutOfRangeError:
        response = "Please enter a valid project index."
    except EmptyProjectListError:
        response = "No current existing projects."
    except KeyError:
        response = "Please include `-index` when deleting projects."

    return response



# Show existing projects command.
def show_projects_command(workflow):
    projects = workflow.projects

    if projects:
        response = ">>> # Existing Projects:\n"
        for index, project in enumerate(projects):
            if not project.deadline:
                response += f"### {index}. {project.title}\n"
            else:
                response += f"### {index}. {project.title} - Deadline ({project.deadline})\n"
    else:
        response = "No current existing projects, use `!add_project`."

    return response
