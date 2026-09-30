import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DB_DIR = "./chroma_db"

def load_and_split_legal_pdf(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    full_text = "\n".join([p.page_content for p in pages])

    # Regex to split by Section numbers (e.g., "Section 302." or "302. ")
    # Adjust regex based on your bare act format
    raw_sections = re.split(r'\n(?=(?:Section\s+\d+|[0-9]{1,3}[A-Z]?\.\s+))', full_text)
    
    docs = []
    for section_text in raw_sections:
        cleaned = section_text.strip()
        if len(cleaned) > 40:  # ignore empty or header fragments
            # Extract section number for metadata
            match = re.search(r'(?:Section\s+|)([0-9]{1,3}[A-Z]?)', cleaned)
            sec_num = match.group(1) if match else "Unknown"
            
            docs.append(Document(
                page_content=cleaned,
                metadata={"source": "IPC", "section": sec_num}
            ))
    return docs

def build_vector_db():
    print("Loading documents...")
    docs = load_and_split_legal_pdf("data/ipc_bare_act.pdf")
    print(f"Total sections processed: {len(docs)}")

    print("Generating embeddings...")
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Store directly in ChromaDB persistent folder
    Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=DB_DIR
    )
    print("ChromaDB vector store successfully created!")

if __name__ == "__main__":
    build_vector_db()