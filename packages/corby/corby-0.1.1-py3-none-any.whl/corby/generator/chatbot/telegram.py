"""Telegram chatbot manager"""

import inquirer
from .base_chatbot import BaseChatbotGenerator

class TelegramChatbotGenerator(BaseChatbotGenerator):
    """Telegram chatbot manager"""

    def get_templates(self):
        return {
            # pylint: disable=line-too-long
           'telegram-langchain-chatbot': 'https://github.com/corby-templates/langchain-telegram-chatbot.git'
    }

    def get_chatbot_params(self):
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
            return {'telegram_bot_token': telegram_token["token"]}
        return {}
