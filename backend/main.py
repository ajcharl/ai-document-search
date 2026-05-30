"""FastAPI entrypoint exposing /upload and /ask."""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.document_loader import load_text
from services.chunker import chunk_text
from services.embeddings import embed_texts
from services.vector_store import add_chunks
from services.rag import answer_question

app = FastAPI(title="RAG Document Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "ok", "service": "rag-documentsearch"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = load_text(file.filename, contents)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any text from the file.")

        chunks = chunk_text(text)
        if not chunks:
            raise HTTPException(status_code=400, detail="Document produced no chunks.")

        embeddings = embed_texts(chunks)
        stored = add_chunks(chunks, embeddings, source=file.filename)
        return {"message": f"Stored {stored} chunks from {file.filename}.", "chunks": stored}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {exc}")


@app.post("/ask")
def ask(req: AskRequest):
    question = (req.question or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        return answer_question(question)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {exc}")
