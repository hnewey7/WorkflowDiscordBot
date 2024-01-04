'''
Command script for Workflow Bot
@author: Harry New
1st Jan 2024
'''
from workflow import ProjectNotInListError, EmptyProjectListError, DatetimeConversionError

# Handling all commands.
def handle_command(command, workflow) -> str:
     # Getting components of command.
    main_command = command.split(" ",1)[0].lower()
    parameter_section = " " + command.split(" ",1)[1] if len(command.split(" ")) != 1 else ""

    first_parameter,parameters = extract_parameters(parameter_section)

    if main_command == "help":
        response = help_command()
    elif main_command == "show_projects":
        response = show_projects_command(workflow=workflow)
    elif main_command == "add_project":
        response = add_project_command(parameters,workflow=workflow)
    elif main_command == "del_project":
        response = del_project_command(first_parameter,parameters,workflow=workflow)
    elif main_command == "edit_project":
        response = edit_project_command(parameters,workflow=workflow)
    else:
        response = "Please enter a valid command."

    return response



# Initial extraction of parameters.
def extract_parameters(content):
    # Splitting parameters.
    multiple_parameters = content.split(" -")[1:]

    parameter_dictionary = {}

    for parameter in multiple_parameters:
        if parameter == multiple_parameters[0]:
            first_parameter = parameter.split(' ')[0]
        parameter_components = parameter.split(' ', 1)
        parameter_dictionary[parameter_components[0]] = parameter_components[1]

    return first_parameter,parameter_dictionary



# Help command.
def help_command():
    response = ">>> ## Commands \n\n \
`!add_project -title [TITLE] -deadline (00:00:00 01-01-2000)` \n \
Adds new project to the workflow [requires `-title`]. \n\n \
`!del_project [-title (TITLE) -index (INDEX)]` \n \
Deletes project from the workflow [requires either `-title` or `-index`]. \n\n \
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
        deadline = workflow.get_project_from_title(title).get_unix_deadline()
        response = f"New project (**{title}**) has been added, with deadline (**<t:{deadline}:R>**)." if 'deadline' in parameters.keys() else f"New project (**{title}**)."
    except KeyError:
        response = 'Please include `-title` when adding projects.'
    except DatetimeConversionError:
        response = "Please input `-deadline` in format '%H:%M:%S %d-%m-%Y'"

    return response



# Deleting project command.
def del_project_command(priority,parameters,workflow):
    try:
        if 'index' == priority:
            index = int(parameters['index'])
            deleted = workflow.del_project_by_index(index-1)
        elif 'title' == priority:
            title = parameters['title']
            deleted = workflow.del_project_by_title(title)
        response = f"Project (**{deleted.title}**) has been deleted."
    except ProjectNotInListError:
        response = "Please enter a valid project."
    except EmptyProjectListError:
        response = "No current existing projects."
    except KeyError:
        response = "Please include either `-index` or `-title` when deleting projects."

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
                response += f"### {index}. {project.title} - Deadline (<t:{project.get_unix_deadline()}:R>)\n"
    else:
        response = "No current existing projects, use `!add_project`."

    return response


# Edit project command.
def edit_project_command(parameters,workflow):
    pass
        
