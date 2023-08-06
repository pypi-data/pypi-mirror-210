import requests
import toml
import pathlib
import os
import json

class NeuralPitAPIService():

    def __init__(self, api_key) -> None:
        super().__init__()
        self.api_key = api_key
        config_path = os.path.join(pathlib.Path(__file__).parent.parent.parent,"config.toml")
        config = toml.load(config_path)
        self.api_endpoint =  config['endpoint']['api']

    def getServiceProfile(self, service_code):
        get_url = self.api_endpoint + '/serviceProfile'
        headers = {'x-api-key':self.api_key, 'Content-Type':'application/json'}
        get_call = requests.get(get_url, data=None, headers = headers, params = {'serviceCode': service_code})
        resp =  json.loads(get_call.content)
        if 'errorMessage' in resp:
            raise Exception("Invalid code ", service_code)
        return resp['body']
    
    def getUserProfile(self):
        get_url = self.api_endpoint + '/userProfile'
        headers = {'x-api-key':self.api_key, 'Content-Type':'application/json'}
        get_call = requests.get(get_url, data=None, headers = headers)
        resp =  json.loads(get_call.content)
        if 'errorMessage' in resp:
            raise Exception("Invalid api key")
        return resp['body']