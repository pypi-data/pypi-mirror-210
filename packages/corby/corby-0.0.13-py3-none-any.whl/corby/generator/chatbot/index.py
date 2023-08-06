"""Dispatches the action to the corresponding chatbot generator"""

import inquirer
from .cli import CliChatbotGenerator
from .telegram import TelegramChatbotGenerator

def create_chatbot():
    """Ask the user for the chatbot's name and interface and create it"""
    questions = [
        inquirer.Text("name", message="Name of your chatbot:"),
        inquirer.List(
            "interface", 
            message="Choose your chatbot's interface:",
            choices=["CLI", "Telegram"]
        ),
    ]
    answers = inquirer.prompt(questions)
    if answers["interface"] == "CLI":
        generator = CliChatbotGenerator()
        generator.create_cli_chatbot(answers["name"])
    elif answers["interface"] == "Telegram":
        generator = TelegramChatbotGenerator()
        generator.create_telegram_chatbot(answers["name"])
