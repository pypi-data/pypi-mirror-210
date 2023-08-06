#!/usr/bin/env python3
import argparse
from string import Template
from .generator.chatbot.index import create_chatbot
from .__init__ import __version__

# We'll include more features in the future
available_actions = ['new']

available_entities = ['chatbot', 'notebook']

parser = argparse.ArgumentParser(
    usage=Template('corby $available_actions {$available_entities} [options]').substitute(
        available_actions=' | '.join(available_actions), 
        available_entities=' | '.join(available_entities)
    )
)

parser.add_argument('action', choices=available_actions, help='Action to perform')
parser.add_argument('entity', choices=available_entities, help='Entity to work with')
parser.add_argument('-v','--version', action='version', version=corby.__version__, help='Show version')
parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')
args = parser.parse_args()

def main():
    if args.action:
        if args.action == 'new':
            if args.entity == 'notebook':
                print("Sorry, the notebook generator is not yet available 😥")
            elif args.entity == 'chatbot':
                create_chatbot()

if __name__ == "__main__":
    main()