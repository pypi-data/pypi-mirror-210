import os, inquirer, git, shutil
from jinja2 import Environment, FileSystemLoader

def replace_in_file(file_path, params):
    env = Environment(loader=FileSystemLoader(os.path.dirname(file_path)))
    template = env.get_template(os.path.basename(file_path))
    rendered_template = template.render(params=params)
    
    with open(file_path, 'w') as file:
        file.write(rendered_template)

def replace_in_folder(folder_path, params):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            replace_in_file(file_path, params)

def create_cli_chatbot(name):
    templates = {
        'basic-langchain-template': 'https://github.com/JoseHervas/basic-langchain-chatbot.git'
    }

    templates_names = list(templates.keys())
    templates_names.append("Other")

    questions = [
        inquirer.List("template", message="Select one of the available chatbot's templates:", choices=templates_names),
    ]

    answers = inquirer.prompt(questions)

    if (answers["template"] == "Other"):
        template_url_question = [
            inquirer.Text("template_url", message="Enter the URL of the template's repository:"),
        ]
        template_url_answers = inquirer.prompt(template_url_question)
        template_url = template_url_answers["template_url"]
        template_name = template_url.split("/")[-1].split(".")[0]
    else:
        template_url = templates[answers["template"]]
        template_name = answers["template"]

    # Clone the template
    git.Repo.clone_from(template_url, os.getcwd() + '/' + template_name)

    # Extract the skeleton
    shutil.move(os.getcwd() + '/' + template_name + '/skeleton', os.getcwd() + '/' + name)

    # Cleanup
    shutil.rmtree(os.getcwd() + '/' + template_name)

    # Replace template values
    replace_in_folder(os.getcwd() + '/' + name, {'chatbot_name': name})

    print("Yeepay 🎉, your chatbot is ready!")
    print("You can find it in the " + name + " folder")
