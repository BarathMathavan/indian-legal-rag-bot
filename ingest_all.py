import os
import glob
import warnings
warnings.filterwarnings("ignore")

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# -------------------------------------------------------------
# If you copied PDFs to data folder, use r"./data"
# If you kept them in the old location, use r"C:\bbib\bot\datasets for model"
# -------------------------------------------------------------
DATA_DIR = r"./data/datasets for model"  # <-- Change this path if your PDFs are elsewhere
DB_DIR = r"./chroma_db"

def process_and_store_documents():
    print(f"[*] Looking for PDFs inside: {os.path.abspath(DATA_DIR)}")
    pdf_files = glob.glob(os.path.join(DATA_DIR, "*.pdf"))
    
    if not pdf_files:
        print(f"\n[X] ERROR: Found 0 PDFs in {DATA_DIR}!")
        print("[!] Please ensure your 31 PDF files are inside that folder and try again.")
        return

    print(f"[✓] Found {len(pdf_files)} PDF documents to process.\n")

    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", "Section ", "SECTION ", ". ", " "]
    )

    for i, pdf_path in enumerate(pdf_files, 1):
        file_name = os.path.basename(pdf_path)
        clean_title = (
            file_name.replace(".pdf", "")
                     .replace("(compressed)", "")
                     .replace("_", " ")
                     .strip()
        )

        try:
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()

            # Skip unreadable/scanned PDFs
            if not pages or len("".join([p.page_content for p in pages]).strip()) < 50:
                print(f"[{i}/{len(pdf_files)}] [!] Warning: Skipped {clean_title} (scanned image or empty)")
                continue

            chunks = text_splitter.split_documents(pages)

            for chunk in chunks:
                chunk.metadata["source_document"] = clean_title
                chunk.metadata["filename"] = file_name

            all_chunks.extend(chunks)
            print(f"[{i}/{len(pdf_files)}] [✓] Processed: {clean_title} ({len(chunks)} chunks)")

        except Exception as e:
            print(f"[{i}/{len(pdf_files)}] [X] Failed to load {file_name}: {e}")

    if not all_chunks:
        print("\n[!] No text chunks created. Exiting.")
        return

    print(f"\n[*] Total text chunks extracted: {len(all_chunks)}")
    print("[*] Generating embeddings and building ChromaDB (this may take 1-2 minutes)...")
    
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Automatically creates a fresh chroma_db folder
    Chroma.from_documents(
        documents=all_chunks,
        embedding=embedding_model,
        persist_directory=DB_DIR
    )

    print(f"\n[✓] SUCCESS: ChromaDB database created with all documents at '{DB_DIR}'!")

if __name__ == "__main__":
    process_and_store_documents()