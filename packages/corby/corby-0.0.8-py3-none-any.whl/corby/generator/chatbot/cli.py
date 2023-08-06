"""CLI chatbot manager"""

import os
from ..base import BaseGenerator

class CliChatbotGenerator(BaseGenerator):
    """CLI chatbot manager"""

    def get_templates(self):
        return {
        'basic-langchain-template': 'https://github.com/JoseHervas/basic-langchain-chatbot.git'
    }

    def create_cli_chatbot(self, name):
        """Generates a new CLI chatbot"""
        selected_template = self.ask_template()
        self.clone_template(selected_template["template_url"], selected_template["template_name"])
        self.cleanup(selected_template["template_name"])
        self.replace_in_folder(os.getcwd() + '/' + name, {'chatbot_name': name})
        print("Yeepay 🎉, your chatbot is ready!")
        print("You can find it in the " + name + " folder")
