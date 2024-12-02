import os
from typing import List, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class RAG:
    def __init__(
        self, 
        openai_api_key: str,
        llm_model: str = "gpt-3.5-turbo", 
        embedding_model: str = "text-embedding-ada-002",
        persist_directory: str = "./chroma_db"
    ):
        """
        Inicializa el sistema RAG con OpenAI.
        
        Args:
            openai_api_key: Tu API key de OpenAI
            llm_model: Modelo de lenguaje a utilizar (default: gpt-3.5-turbo)
            embedding_model: Modelo de embeddings (default: text-embedding-ada-002)
            persist_directory: Directorio para almacenar vector store
        """
        # Configurar API key
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # Inicializar modelo de lenguaje y embeddings
        self.llm_model = ChatOpenAI(
            api_key=openai_api_key, 
            model=llm_model, 
            temperature=0.1
        )
        self.embedding_function = OpenAIEmbeddings(
            api_key=openai_api_key,
            model=embedding_model
        )
        
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.retriever = None

    def load_documents(self, document_path: str):
        """
        Carga documentos, los divide y crea un vector store.
        
        Args:
            document_path: Ruta al archivo de texto
        """
        # Cargar documento
        loader = TextLoader(document_path, encoding='utf-8')
        documents = loader.load()
        
        # Dividir documentos
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=100
        )
        splits = text_splitter.split_documents(documents)
        
        # Crear vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embedding_function,
            persist_directory=self.persist_directory
        )
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": 4}  # 4 documentos más relevantes
        )

    def _create_chain(self, template: str):
        """
        Crea una cadena de procesamiento con un template específico.
        
        Args:
            template: Plantilla de prompt
        
        Returns:
            Cadena de procesamiento
        """
        prompt = PromptTemplate.from_template(template)
        chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm_model
            | StrOutputParser()
        )
        return chain

    def query(self, question: str) -> str:
        """
        Realiza una consulta sobre el documento.
        
        Args:
            question: Pregunta a realizar
        
        Returns:
            Respuesta generada
        """
        if not self.retriever:
            raise ValueError("Primero debe cargar un documento con load_documents()")
        
        chain = self._create_chain(
            template="""Basándote en el siguiente contexto:
            {context}
            
            Responde a la pregunta: {question}
            
            Si no puedes responder con la información proporcionada, 
            indica que no hay suficiente información."""
        )
        
        return chain.invoke(question)
    
    def document_summary(self) -> str:
        """
        Genera un resumen del documento cargado.
        
        Returns:
            Resumen del documento
        """
        if not self.retriever:
            raise ValueError("Primero debe cargar un documento con load_documents()")
        
        chain = self._create_chain(
            template="""Basándote en el siguiente contexto:
            {context}
            
            Genera un resumen conciso y preciso del documento.
            El resumen debe capturar los puntos principales y la esencia del texto."""
        )
        
        return chain.invoke("Resume el documento")
    
    def document_timeline(self) -> str:
        """
        Genera una línea temporal del documento.
        
        Returns:
            Línea temporal del documento
        """
        if not self.retriever:
            raise ValueError("Primero debe cargar un documento con load_documents()")
        
        chain = self._create_chain(
            template="""Basándote en el siguiente contexto:
            {context}
            
            Genera una línea temporal detallada de los eventos del documento.
            Organiza los eventos cronológicamente y proporciona contexto para cada uno."""
        )
        
        return chain.invoke("Genera una línea temporal de los eventos del documento")

# Ejemplo de uso

# Usar tu API key de OpenAI
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# Inicializar RAG
rag = RAG(
    openai_api_key=OPENAI_API_KEY,
    llm_model="gpt-3.5-turbo",  # Opcional: cambiar modelo
    embedding_model="text-embedding-ada-002"  # Opcional: cambiar modelo de embeddings
)

# Cargar documento
rag.load_documents("documento.txt")

# Obtener resumen
resumen = rag.document_summary()
print("Resumen:", resumen)

# Obtener línea temporal
linea_temporal = rag.document_timeline()
print("Línea Temporal:", linea_temporal)

# Hacer consulta
respuesta = rag.query("¿De qué se trata el documento?")
print("Respuesta:", respuesta)