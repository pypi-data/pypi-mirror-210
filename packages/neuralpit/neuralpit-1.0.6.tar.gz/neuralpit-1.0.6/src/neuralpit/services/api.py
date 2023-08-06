import requests
import toml
import pathlib
import os
import json
from requests.compat import urljoin
from neuralpit import Enviroment

class NeuralPitAPIService():

    def __init__(self) -> None:
        super().__init__()
        self.api_key = Enviroment.getApiKey()
        self.api_endpoint = Enviroment.getApiEndpoint()


    def getServiceProfile(self, service_code):
        get_url = urljoin(self.api_endpoint,'/serviceProfile')
        headers = {'x-api-key':self.api_key, 'Content-Type':'application/json'}
        get_call = requests.get(get_url, data=None, headers = headers, params = {'serviceCode': service_code})
        resp =  json.loads(get_call.content)
        if 'errorMessage' in resp:
            raise Exception("Invalid code ", service_code)
        return resp['body']
    
    def getUserProfile(self):
        get_url = urljoin(self.api_endpoint,'/userProfile')
        headers = {'x-api-key':self.api_key, 'Content-Type':'application/json'}
        get_call = requests.get(get_url, data=None, headers = headers)
        resp =  json.loads(get_call.content)
        if 'errorMessage' in resp:
            raise Exception("Invalid api key")
        return resp['body']