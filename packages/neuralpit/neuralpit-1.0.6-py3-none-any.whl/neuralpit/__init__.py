import os

class Enviroment:

    @staticmethod
    def getApiEndpoint():
        return os.environ.get('API_ENDPOINT')
    
    @staticmethod
    def getApiKey():
        return os.environ.get('API_KEY')