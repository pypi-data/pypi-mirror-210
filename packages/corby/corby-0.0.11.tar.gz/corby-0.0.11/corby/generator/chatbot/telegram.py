"""Telegram chatbot manager"""

import os
import inquirer
from ..base import BaseGenerator

class TelegramChatbotGenerator(BaseGenerator):
    """Telegram chatbot manager"""

    def get_templates(self):
        return {
        'telegram-langchain-chatbot': 'https://github.com/JoseHervas/telegram-langchain-chatbot.git'
    }

    def create_telegram_chatbot(self, name):
        """Generates a new Telegram chatbot"""
        app_path = os.getcwd() + '/' + name
        selected_template = self.ask_template()
        questions = [
                inquirer.List(
                    "token", 
                    message="Do you have a Telegram bot token?",
                    choices=["yes", "no"]
                ),
            ]
        answers = inquirer.prompt(questions)
        if answers["token"] == "yes":
            questions = [
                inquirer.Text("token", message="Enter your Telegram bot token:"),
            ]
            telegram_token = inquirer.prompt(questions)
        self.clone_template(selected_template["template_url"], selected_template["template_name"])
        os.rename(os.getcwd() + '/skeleton', app_path)
        self.cleanup(selected_template["template_name"])
        self.replace_in_folder(app_path, {'chatbot_name': name})
        if telegram_token:
            self.replace_in_folder(app_path, {'telegram_bot_token': answers["token"]})
        print("Yeepay 🎉, your chatbot is ready!")
        print("You can find it in the " + name + " folder")
