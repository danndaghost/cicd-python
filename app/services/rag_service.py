#from config.settings import Settings
from pinecone import Pinecone
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as LangchainPinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from growml_documents import PDF

# config/settings.py
from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    INDEX_NAME = os.getenv("PINECONE_INDEX")


class RAGService:
    def __init__(self):
         # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=Settings.OPENAI_API_KEY)
        self.llm = OpenAI(temperature=0, openai_api_key=Settings.OPENAI_API_KEY)
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=Settings.PINECONE_API_KEY)

        # Initialize vector store
        self.vectorstore = LangchainPinecone.from_existing_index(
            index_name=Settings.INDEX_NAME,
            embedding=self.embeddings
        )

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
    
    def process_pdf(self, file_content):
        text = ""
        pdf = PDF(file_content)
        text = pdf.read_text()

        chunks = self.text_splitter.split_text(text)
        self.vectorstore.add_texts(chunks)

    def query_document(self, question: str):
        if not self.qa_chain:
            raise ValueError("Documento no cargado")
        return self.qa_chain.invoke(question)
