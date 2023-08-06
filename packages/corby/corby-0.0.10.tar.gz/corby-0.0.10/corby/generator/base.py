"""Base class to be extended by each generator"""

import os
import shutil
from abc import ABC
from jinja2 import Environment, FileSystemLoader
import inquirer
import git

class BaseGenerator(ABC):
    '''Abstract class to be extended by each generator'''

    def replace_in_file(self, file_path, params):
        '''Replace the placeholders in a file with the given params'''
        env = Environment(loader=FileSystemLoader(os.path.dirname(file_path)))
        template = env.get_template(os.path.basename(file_path))
        rendered_template = template.render(params=params)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(rendered_template)

    def replace_in_folder(self, folder_path, params):
        '''Runs replace_in_file for each file in the given folder'''
        # pylint: disable=unused-variable
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.replace_in_file(file_path, params)

    def get_templates(self):
        '''Returns a dictionary with the available templates for the generator'''
        raise NotImplementedError

    def ask_template(self):
        '''Ask the user to select a template from the list returned by get_templates'''
        templates = self.get_templates()

        templates_names = list(templates.keys())
        templates_names.append("Other")

        questions = [
            inquirer.List(
                "template", 
                message="Select one of the available chatbot's templates:",
                choices=templates_names
            ),
        ]

        answers = inquirer.prompt(questions)

        if answers["template"] == "Other":
            template_url_question = [
                inquirer.Text(
                    "template_url", 
                    message="Enter the URL of the template's repository:"
                ),
            ]
            template_url_answers = inquirer.prompt(template_url_question)
            template_url = template_url_answers["template_url"]
            template_name = template_url.split("/")[-1].split(".")[0]
        else:
            template_url = templates[answers["template"]]
            template_name = answers["template"]

        return {
            "template_name": template_name,
            "template_url": template_url
        }

    def clone_template(self, template_url, template_name):
        '''Download a template from github and extract the skeleton'''

        # Clone the template
        git.Repo.clone_from(template_url, os.getcwd() + '/' + template_name)

        # Extract the skeleton
        shutil.move(
            os.getcwd() + '/' + template_name + '/skeleton', os.getcwd() + '/skeleton'
        )

    def cleanup(self, template_name):
        '''Removes the base folder from the template'''
        shutil.rmtree(os.getcwd() + '/' + template_name)
