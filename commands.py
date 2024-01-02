'''
Command script for Workflow Bot
@author: Harry New
1st Jan 2024
'''

# Handling all commands.
def handle_command(command, workflow) -> str:
    # Initialising response.
    response = None

    # Getting components of command.
    lower_command = command.lower()
    main_command = lower_command.split(" ")[0]
    
    # Undertaking relevant command.
    if main_command == "add_project":
        # Defining parameters for command.
        required = ['title']
        valid = ['deadline']
        
        # Extracting parameters.
        required_inputs,valid_inputs = extract_parameters(required,valid,lower_command)
        print(required_inputs,valid_inputs)

        # Adding project depending on parameters.
        if len(required) == len(required_inputs) and not valid_inputs:
            title = required_inputs['title']
            add_project_command(workflow,title)
            response = f"New project (**{title}**) has been added."

        elif len(required) == len(required_inputs) and valid_inputs:
            title = required_inputs['title']
            deadline = valid_inputs['deadline']
            add_project_command(workflow,title,deadline)
            response = f"New project (**{title}**) has been added, with deadline (**{deadline}**)"

        else:
            response = f"Invalid use of {main_command}."

    return response



# Extract parameters.
def extract_parameters(required_parameters,valid_parameters,content):
    # Splitting parameters.
    parameter_components = content.split("-")[1:]
    print("Parameter components: " + str(parameter_components))

    # Storing parameters in dictionaries.
    required_inputs = dict.fromkeys(required_parameters)
    valid_inputs = {}

    # Checking required parameters.
    for required in required_parameters:
        for parameter in parameter_components:
            if required in parameter[:len(required)]:
                required_inputs[required] = parameter.split(' ',1)[1]
                break
    
    # Checking valid parameters.
    for valid in valid_parameters:
        for parameter in parameter_components:
            if valid in parameter[:len(valid)]:
                valid_inputs[valid] = parameter.split(' ',1)[1]
                break

    return required_inputs,valid_inputs



# Adding project command.
def add_project_command(workflow,title,deadline=None):
    workflow.add_project(title,deadline)