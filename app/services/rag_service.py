from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from pinecone import Index
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.settings import Settings

class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=Settings.OPENAI_API_KEY)
        self.llm = OpenAI(temperature=0, openai_api_key=Settings.OPENAI_API_KEY)
        
        self.index_name = Settings.INDEX_NAME
        self.pc = Index(index_name=self.index_name, api_key=Settings.PINECONE_API_KEY)
        self.vectorstore = None
        self.qa_chain = None

    def process_pdf(self, file_content):
        text = ""
        pdf_reader = pypdf.PdfReader(file_content)
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        chunks = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        ).split_text(text)
        
        self.vectorstore = Pinecone.from_existing_index(
            index_name=self.index_name,
            embedding=self.embeddings
        )
        self.vectorstore.add_texts(chunks)
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )

    def query_document(self, question: str) -> str:
        if not self.qa_chain:
            raise ValueError("Documento no cargado")
        return self.qa_chain.run(question)



