'''Base class for chatbot generators'''
from ..base import BaseGenerator

class BaseChatbotGenerator(BaseGenerator):
    '''Base class for chatbot generators'''
    def get_chatbot_params(self):
        '''Returns the specific questions required for each kind of chatbot'''
        raise NotImplementedError

    def get_generator_params(self, name):
        '''Returns the specific parameters for chatbots'''
        template_params = {'chatbot_name': name}
        if hasattr(self, 'get_chatbot_params'):
            chatbot_specific_params = self.get_chatbot_params()
            if bool(chatbot_specific_params):
                template_params.update(chatbot_specific_params)
        return template_params

    def create_chatbot(self, name):
        '''Calls super.create() to generate a new chatbot
        we may have custom logic here on the future'''
        return super().create(name)
