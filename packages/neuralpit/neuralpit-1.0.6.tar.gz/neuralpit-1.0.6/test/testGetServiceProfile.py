from neuralpit.services.api import NeuralPitAPIService
from neuralpit.services.convert import TikaConverterService
import os

def main():
   client = NeuralPitAPIService()
   service = client.getServiceProfile('DOC_CHAT')
   print(service)
   server_url = service['converter']['server_url']
   converter = TikaConverterService(server_url)
   fileName = 'manual.pdf'
   with open(fileName, mode='rb') as file: # b is important -> binary
      fileContent = file.read()
      fileText = converter.convertFileToString(fileContent)
      print(fileText[0])

if __name__ == "__main__":
    main()
