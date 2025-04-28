import os
import json
import hashlib
import pymupdf
import pandas as pd
import pymupdf4llm
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import dotenv
from parse_tabular import parse_excel, parse_csv
dotenv.load_dotenv()
DATA_FOLDER = "../../data"  # Folder where documents are stored

class Vectorizer:
    def __init__(self):
        model = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2", model_kwargs = {"device": os.getenv("DEVICE","cpu")})

        self.vector_store = PGVector(
            embeddings=model,
            collection_name=os.getenv("COLLECTION_NAME","my_docs"),
            connection=os.getenv("POSTGRES_CONNECTION_STRING",),
            use_jsonb=True,
        )
    def convert_text(self, text, metadata=None):
        doc = []
        i=0
        if metadata is not None:
            for page in text:
                doc.append(Document(page_content=page,metadata=metadata[i]))
                i+=1
        else:
            for page in text:
                doc.append(Document(page_content=page))
        return doc
    def embed_text(self, text, metadata=None):
        return self.vector_store.add_documents(self.convert_text(text, metadata = metadata))

def load_existing_hashes(file_path):
    """Load existing hashes from a JSON file."""
    if os.path.exists(file_path+".md5"):
        with open(file_path+".md5", "r") as f:
            return f.read()
    return None

def generate_md5(file_path):
    """Generate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extract_text_pagewise(pdf_path):
    """Extract text from a PDF file page by page."""
    doc = pymupdf.open(pdf_path)
    pages_text = []
    metadata = []
    for i in range(doc.page_count):
        page_md = pymupdf4llm.to_markdown(doc, pages=[i])
        pages_text.append(page_md)
        metadata.append({
            "page_number": i+1, 
            "file_name": pdf_path.split("\\")[-1],
            "file_type": "pdf",
            "total_pages": doc.page_count
        })
    return pages_text, metadata

def process_tabular_file(file_path, file_name):
    """Process tabular files (Excel and CSV) and return text chunks with metadata."""
    file_ext = os.path.splitext(file_name)[1].lower()
    
    if file_ext in ['.xls', '.xlsx']:
        chunks = parse_excel(file_path)
        file_type = "excel"
    elif file_ext == '.csv':
        chunks = parse_csv(file_path)
        file_type = "csv"
    else:
        return None, None
    
    text_chunks = []
    metadata_chunks = []
    
    for i, chunk in enumerate(chunks):
        # Convert chunk to string representation
        chunk_text = json.dumps(chunk, indent=2)
        text_chunks.append(chunk_text)
        metadata_chunks.append({
            "chunk_number": i+1,
            "file_name": file_name,
            "file_type": file_type,
            "total_chunks": len(chunks)
        })
    
    return text_chunks, metadata_chunks

def process_files():
    """Check files, process new or updated ones, and save extracted text."""
    client = Vectorizer()
    supported_extensions = ['.pdf', '.xls', '.xlsx', '.csv']
    
    for file_name in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, file_name)
        
        # Skip if not a file or not a supported extension
        if not os.path.isfile(file_path):
            continue
            
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in supported_extensions:
            print(f"Skipping unsupported file type: {file_name}")
            continue
            
        # Check if file has changed
        existing_hashes = load_existing_hashes(file_path)
        new_md5 = generate_md5(file_path)
        
        if existing_hashes is None or existing_hashes != new_md5:
            print(f"Processing: {file_name}")
            
            try:
                # Process based on file type
                if file_ext == '.pdf':
                    text, metadata = extract_text_pagewise(file_path)
                elif file_ext == '.md5':
                    continue
                else:  # Excel or CSV
                    text, metadata = process_tabular_file(file_path, file_name)
                
                if text and metadata:
                    client.embed_text(text, metadata=metadata)
                    with open(file_path+".md5", "w") as f:
                        f.write(new_md5)
                    print(f"Successfully processed: {file_name}")
                else:
                    print(f"Failed to process: {file_name}")
                    
            except Exception as e:
                print(f"Error processing {file_name}: {e}")
        else:
            print(f"Skipping (No Changes): {file_name}")

if __name__ == "__main__":
    process_files()
  