import inquirer
from .cli import create_cli_chatbot

def create_chatbot():
    questions = [
        inquirer.Text("name", message="Name of your chatbot:"),
        inquirer.List("interface", message="Choose your chatbot's interface:", choices=["CLI"]),
    ]
    answers = inquirer.prompt(questions)
    if (answers["interface"] == "CLI"):
        create_cli_chatbot(answers["name"])

    

