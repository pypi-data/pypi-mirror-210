"""Web chatbot manager"""

from .base_chatbot import BaseChatbotGenerator

class WebChatbotGenerator(BaseChatbotGenerator):
    """Web chatbot manager"""

    def get_templates(self):
        return {
            # pylint: disable=line-too-long
           'langchain-web-chatbot': 'https://github.com/corby-templates/langchain-web-chatbot.git'
    }
