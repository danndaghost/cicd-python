from fastapi import APIRouter, HTTPException, UploadFile
from services.rag_service import RAGService
from models.schemas import Query
import io

router = APIRouter()
rag_service = RAGService()

@router.post("/upload")
async def upload_document(file: UploadFile):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Solo se aceptan archivos PDF")
    
    contents = await file.read()
    try:
        rag_service.process_pdf(io.BytesIO(contents))
        return {"message": "Documento procesado exitosamente"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/query")
async def query_document(query: Query):
    try:
        response = rag_service.query_document(query.question)
        return {"response": response}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))