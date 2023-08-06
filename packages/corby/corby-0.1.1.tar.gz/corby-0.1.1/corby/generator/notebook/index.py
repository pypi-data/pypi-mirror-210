"""Creates a new notebook"""

import inquirer
from ..base import BaseGenerator

class NotebookGenerator(BaseGenerator):
    """Jupyter Notebook manager"""

    def get_templates(self):
        return {
            # pylint: disable=line-too-long
           'basic-langchain-notebook': 'https://github.com/JoseHervas/basic-langchain-notebook.git'
    }

    def get_generator_params(self, name):
        '''Returns the specific parameters for notebooks'''
        template_params = {'notebook_name': name}
        return template_params

    def create_notebook(self, name):
        '''Calls super.create() to generate a new notebook
        we may have custom logic here on the future'''
        return super().create(name)

def create_notebook():
    """Ask the user for the template and creates a new notebook"""
    questions = [
        inquirer.Text("name", message="Name of your notebook:"),
    ]
    answers = inquirer.prompt(questions)
    NotebookGenerator().create_notebook(answers['name'])
