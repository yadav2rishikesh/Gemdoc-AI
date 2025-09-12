"""
backend/main.py
FastAPI backend for GEMDOC AI.

Endpoints:
- POST /upload/  -> accept PDF/DOCX file, extract text, chunk, embed, build & persist FAISS index
- POST /ask/     -> accept user query, retrieve top_k chunks, call LLM (Gemini) and return answer
- GET  /status/  -> basic status (index present, number of chunks)
"""

import os
import json
import shutil
from typing import Tuple

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import PyPDF2
import docx
from sentence_transformers import SentenceTransformer
import faiss

# Use google-generativeai for Gemini
import google.generativeai as genai

# -------------------------
# Configuration (env vars)
# -------------------------
DATA_DIR = "knowledge_db"
INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.json")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")             # Put your key in env
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")  # change if needed

# -------------------------
# FastAPI init
# -------------------------
app = FastAPI(title="GEMDOC AI - Backend")

# Allow local frontend during development - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Load embedding model
# -------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory variables (will be loaded from disk if present)
index = None
chunks = []

# Configure Gemini if key provided
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# -------------------------
# Helper functions
# -------------------------
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def save_index_and_chunks(idx: faiss.IndexFlatL2, chunks_list: list):
    """Persist FAISS index and chunks JSON to disk."""
    ensure_data_dir()
    faiss.write_index(idx, INDEX_PATH)
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks_list, f, ensure_ascii=False)

def load_index_and_chunks() -> Tuple[faiss.IndexFlatL2, list]:
    """Load FAISS index and chunks from disk if available."""
    if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
        idx = faiss.read_index(INDEX_PATH)
        with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
            ch = json.load(f)
        return idx, ch
    return None, []

def extract_text_from_pdf(path: str) -> str:
    """Extract text from every page of a PDF."""
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_docx(path: str) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def chunk_text(text: str, chunk_size: int = 400) -> list:
    """Split text into word-based chunks (default 400 words)."""
    words = text.split()
    chunks_local = [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size) if words[i:i+chunk_size]]
    return chunks_local

# -------------------------
# Load persisted index on startup if present
# -------------------------
index, chunks = load_index_and_chunks()
if index is not None:
    print(f"[startup] Loaded persisted index with {len(chunks)} chunks.")
else:
    print("[startup] No persisted index found. Upload a document to create one.")

# -------------------------
# API Models
# -------------------------
class UploadResponse(BaseModel):
    message: str
    chunks: int

class AskResponse(BaseModel):
    answer: str

# -------------------------
# Endpoints
# -------------------------
@app.post("/upload/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF or DOCX file.
    Steps:
      - save tmp file
      - extract text
      - split into chunks
      - compute embeddings & build FAISS index
      - persist index + chunks to disk
    """
    global index, chunks

    # save uploaded temp file
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # extract text based on extension
    fname = file.filename.lower()
    if fname.endswith(".pdf"):
        text = extract_text_from_pdf(temp_path)
    elif fname.endswith(".docx"):
        text = extract_text_from_docx(temp_path)
    else:
        os.remove(temp_path)
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or DOCX.")

    os.remove(temp_path)

    # chunking
    chunks = chunk_text(text, chunk_size=400)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text extracted from document. Please upload a text-based PDF or DOCX (not scanned).")

    # embeddings + build FAISS
    embeddings = embedder.encode(chunks, convert_to_numpy=True)
    dim = embeddings.shape[1]
    idx = faiss.IndexFlatL2(dim)
    idx.add(embeddings)

    # persist to disk
    save_index_and_chunks(idx, chunks)

    # update in-memory index
    index = idx

    return {"message": "Document processed and indexed successfully.", "chunks": len(chunks)}

@app.post("/ask/", response_model=AskResponse)
async def ask_question(query: str = Form(...), top_k: int = Form(3)):
    """
    Accepts a query (form field) and returns an answer.
    Workflow:
      - semantic search via FAISS (top_k)
      - build prompt with retrieved context
      - call Gemini if configured; otherwise return the context directly
    """
    global index, chunks

    if index is None or not chunks:
        return {"answer": "No indexed document found. Please upload a document first."}

    # encode query & search
    qvec = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(qvec, top_k)
    retrieved = [chunks[i] for i in I[0] if i < len(chunks)]
    context = "\n\n".join(retrieved)

    # strict extraction prompt
    prompt = f"""
You are an information extraction assistant.
Rules:
- Use ONLY the information from the context.
- Do NOT copy the entire context.
- Extract ONLY what is explicitly asked in the question.
- If multiple items are asked (like skills, projects), return them as a short comma-separated list.
- If the answer is not in the context, reply: 'Not found in document.'

Context:
{context}

Question:
{query}

Answer:
"""

    # fallback if Gemini key not set
    if not GEMINI_API_KEY:
        return {"answer": context}

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        answer = response.text.strip() if response and response.text else "No answer found."
    except Exception as e:
        answer = f"Gemini error: {str(e)}"

    return {"answer": answer}

@app.get("/status/")
async def status():
    """Return whether an index exists and how many chunks."""
    global index, chunks
    return {"has_index": index is not None, "chunks": len(chunks)}
