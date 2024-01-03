'''
Command script for Workflow Bot
@author: Harry New
1st Jan 2024
'''

# Handling all commands.
def handle_command(command, workflow) -> str:
     # Getting components of command.
    main_command = command.split(" ",1)[0].lower()
    parameter_section = " " + command.split(" ",1)[1] if len(command.split(" ")) != 1 else ""
    
    parameters = extract_parameters(parameter_section)

    if main_command == "add_project":
        response = add_project_command(parameters,workflow=workflow)
    elif main_command == "show_projects":
        response = show_projects_command(workflow=workflow)

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



# Adding project command.
def add_project_command(parameters,workflow):
    try:
        title = parameters['title']
        deadline = parameters['deadline'] if 'deadline' in parameters.keys() else None
        response = f"New project (**{title}**) has been added, with deadline (**{parameters['deadline']}**)." if 'deadline' in parameters.keys() else f"New project (**{title}**)."
        workflow.add_project(title,deadline)
    except KeyError:
        response = 'Please include -title when adding projects.'

    return response



# Show existing projects command.
def show_projects_command(workflow):
    projects = workflow.projects

    if projects:
        response = "**Existing Projects:**\n"
        for index, project in enumerate(projects):
            if not project.deadline:
                response += f"{index}. {project.title}\n"
            else:
                response += f"{index}. {project.title} - Deadline ({project.deadline})\n"
    else:
        response = "No current existing projects, use !add_project."

    return response
