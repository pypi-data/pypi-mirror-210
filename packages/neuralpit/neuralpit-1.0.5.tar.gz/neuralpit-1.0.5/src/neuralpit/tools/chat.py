import time
from io import BytesIO
from typing import Any, Dict, List

import openai
from langchain.chains import RetrievalQAWithSourcesChain
from langchain import OpenAI
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS

from neuralpit.services.api import NeuralPitAPIService
from neuralpit.services.convert import TikaConverterService, LocalConverterService
from neuralpit.services.document import DocumentService


class ChatWithDocument():

    def __init__(self, api_key) -> None:
        super().__init__()
        self.api_key = api_key
        self.api_client =  NeuralPitAPIService(api_key=api_key)
        self.service_profile = None
        self.user_profile = None

    def getOpenAIKey(self)->str:
        if not self.user_profile:
            self.user_profile = self.api_client.getUserProfile()
        return self.user_profile['openai_key']
    
    def getConverter(self)->str:
        if not self.service_profile:
            self.service_profile = self.api_client.getServiceProfile('DOC_CHAT')
        converter_profile = self.service_profile['converter']
        tika_server_url=converter_profile['server_url'] if converter_profile['name'] =='TIKA' else None
        converter = TikaConverterService(api_key=self.api_key, tika_server_url=tika_server_url) if tika_server_url else LocalConverterService()
        return converter

    def addFile(self,file_content):
        converter = self.getConverter()
        pages = converter.convertFileToString(file_content)
        index = self.indexContent(pages)
        self.buildAgentExecutor(index)

    def indexContent(self, pages):
        docuemtn_service = DocumentService()
        docs = docuemtn_service.textToDocs(pages)
        embeddings = OpenAIEmbeddings(openai_api_key=self.getOpenAIKey())
        # Indexing
        index = FAISS.from_documents(docs, embeddings)
        return index

    def buildAgentExecutor(self, index):
        self.chain = RetrievalQAWithSourcesChain.from_chain_type(OpenAI(temperature=0, openai_api_key=self.getOpenAIKey()), chain_type="stuff", retriever=index.as_retriever())

    def response(self, question):
        resp = self.chain({"question": question}, return_only_outputs=True)
        return resp