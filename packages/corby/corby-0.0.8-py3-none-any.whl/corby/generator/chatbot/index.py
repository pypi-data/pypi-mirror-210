"""Dispatches the action to the corresponding chatbot generator"""

import inquirer
from .cli import CliChatbotGenerator

def create_chatbot():
    """Ask the user for the chatbot's name and interface and create it"""
    questions = [
        inquirer.Text("name", message="Name of your chatbot:"),
        inquirer.List("interface", message="Choose your chatbot's interface:", choices=["CLI"]),
    ]
    answers = inquirer.prompt(questions)
    if answers["interface"] == "CLI":
        generator = CliChatbotGenerator()
        generator.create_cli_chatbot(answers["name"])
