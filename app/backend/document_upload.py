"""
Document Upload Handler

This module handles document uploads and knowledge base creation for different document types.
"""

import os
from pathlib import Path
import shutil
from werkzeug.utils import secure_filename
from knowledge_base import create_knowledge_base

UPLOAD_FOLDER = "data/pdfs"
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """Ensure the upload directory exists."""
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

def handle_file_upload(file, recreate_kb=False):
    """
    Handle file upload and knowledge base creation.
    
    Args:
        file: FileStorage object from Flask
        recreate_kb: bool, whether to recreate the knowledge base
        
    Returns:
        dict: Response with status and message
    """
    if not file:
        return {"success": False, "message": "No file provided"}, 400
        
    if not allowed_file(file.filename):
        return {"success": False, "message": "File type not allowed. Only PDF files are supported."}, 400

    try:
        ensure_upload_dir()
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the uploaded file
        file.save(filepath)
        
        # Create/update knowledge base
        kb = create_knowledge_base(
            source=UPLOAD_FOLDER,
            recreate=recreate_kb
        )
        
        return {
            "success": True, 
            "message": f"File {filename} uploaded successfully and added to knowledge base",
            "filename": filename
        }, 200
        
    except Exception as e:
        return {"success": False, "message": f"Error processing upload: {str(e)}"}, 500

def handle_url_upload(url, recreate_kb=False):
    """
    Handle URL-based document addition to knowledge base.
    
    Args:
        url: str, URL of the PDF document
        recreate_kb: bool, whether to recreate the knowledge base
        
    Returns:
        dict: Response with status and message
    """
    if not url:
        return {"success": False, "message": "No URL provided"}, 400
        
    try:
        # Create/update knowledge base with URL
        kb = create_knowledge_base(
            source=url,
            recreate=recreate_kb
        )
        
        return {
            "success": True,
            "message": f"Document from URL added successfully to knowledge base",
            "url": url
        }, 200
        
    except Exception as e:
        return {"success": False, "message": f"Error processing URL: {str(e)}"}, 500
