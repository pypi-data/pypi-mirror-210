"""CLI chatbot manager"""

import os
from ..base import BaseGenerator

class CliChatbotGenerator(BaseGenerator):
    """CLI chatbot manager"""

    def get_templates(self):
        return {
        'basic-langchain-template': 'https://github.com/JoseHervas/basic-langchain-chatbot.git',
        'langchain-chatbot-tools': 'https://github.com/JoseHervas/langchain-chatbot-tools'
    }

    def create_cli_chatbot(self, name):
        """Generates a new CLI chatbot"""
        app_path = os.getcwd() + '/' + name
        selected_template = self.ask_template()
        self.clone_template(selected_template["template_url"], selected_template["template_name"])
        template_params = {'chatbot_name': name}
        template_custom_inputs = self.ask_template_inputs(selected_template["template_name"])
        if bool(template_custom_inputs):
            template_params.update(template_custom_inputs)
        self.replace_in_folder(
            selected_template["template_name"] + '/skeleton',
            template_params
        )
        self.extract_skeleton(selected_template["template_name"])
        os.rename(os.getcwd() + '/skeleton', app_path)
        self.cleanup(selected_template["template_name"])
        print("Yeepay 🎉, your chatbot is ready!")
        print("You can find it in the " + name + " folder")
