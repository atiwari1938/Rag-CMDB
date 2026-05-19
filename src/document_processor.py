"""
Document processor for multiple file formats (PDF, DOCX, XLSX, TXT)
Extracts text content and metadata from various document types
"""

import os
from datetime import datetime
from typing import List, Dict, Any
import hashlib

def get_file_hash(filepath: str) -> str:
    """Generate MD5 hash of file content"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        text = ""
        with open(filepath, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except ImportError:
        print("⚠️ PyPDF2 not installed. Install with: pip install PyPDF2")
        return ""
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
        return ""

def extract_text_from_docx(filepath: str) -> str:
    """Extract text from DOCX file"""
    try:
        from docx import Document
        doc = Document(filepath)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except ImportError:
        print("⚠️ python-docx not installed. Install with: pip install python-docx")
        return ""
    except Exception as e:
        print(f"Error reading DOCX {filepath}: {e}")
        return ""

def extract_text_from_txt(filepath: str) -> str:
    """Extract text from TXT file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(filepath, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading TXT {filepath}: {e}")
            return ""
    except Exception as e:
        print(f"Error reading TXT {filepath}: {e}")
        return ""

def extract_text_from_excel(filepath: str) -> str:
    """Extract text from Excel file"""
    try:
        import pandas as pd
        text_parts = []
        xlsx = pd.ExcelFile(filepath)
        
        for sheet_name in xlsx.sheet_names:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            # Convert all columns to string and concatenate
            for col in df.columns:
                text_parts.extend(df[col].astype(str).tolist())
        
        return "\n".join(filter(lambda x: x != 'nan', text_parts))
    except Exception as e:
        print(f"Error reading Excel {filepath}: {e}")
        return ""

def process_document(filepath: str) -> Dict[str, Any]:
    """
    Process a document and extract its content
    Returns a dictionary with document metadata and content
    """
    filename = os.path.basename(filepath)
    file_ext = os.path.splitext(filename)[1].lower()
    
    print(f"📄 Processing: {filename}")
    
    # Extract text based on file type
    text = ""
    if file_ext == '.pdf':
        text = extract_text_from_pdf(filepath)
    elif file_ext in ['.docx', '.doc']:
        text = extract_text_from_docx(filepath)
    elif file_ext == '.txt':
        text = extract_text_from_txt(filepath)
    elif file_ext in ['.xlsx', '.xls']:
        text = extract_text_from_excel(filepath)
    else:
        print(f"⚠️ Unsupported file type: {file_ext}")
        return None
    
    if not text or len(text.strip()) < 10:
        print(f"⚠️ No meaningful text extracted from {filename}")
        return None
    
    # Get file metadata
    stat = os.stat(filepath)
    file_hash = get_file_hash(filepath)
    
    document = {
        'filename': filename,
        'filepath': filepath,
        'file_type': file_ext,
        'file_hash': file_hash,
        'content': text,
        'file_size': stat.st_size,
        'modified_time': datetime.fromtimestamp(stat.st_mtime),
        'ingested_at': datetime.utcnow(),
        # For compatibility with existing ticket structure
        'number': filename,
        'short_description': f"Document: {filename}",
        'description': text[:500] + "..." if len(text) > 500 else text,
        'document_type': 'support_document'
    }
    
    print(f"✅ Extracted {len(text)} characters from {filename}")
    return document

def process_all_documents(directory: str) -> List[Dict[str, Any]]:
    """
    Process all supported documents in a directory
    Returns a list of document dictionaries
    Note: Excel files are excluded as they're processed as tickets in ingestion.py
    """
    supported_extensions = ['.pdf', '.docx', '.doc', '.txt']  # Removed .xlsx, .xls
    documents = []
    
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return documents
    
    files = [f for f in os.listdir(directory) 
             if os.path.isfile(os.path.join(directory, f)) 
             and os.path.splitext(f)[1].lower() in supported_extensions]
    
    print(f"\n📁 Found {len(files)} documents to process")
    print(f"Supported formats: {', '.join(supported_extensions)}\n")
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        doc = process_document(filepath)
        if doc:
            documents.append(doc)
    
    print(f"\n✅ Successfully processed {len(documents)} documents")
    return documents

if __name__ == "__main__":
    # Test the document processor
    import sys
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if os.path.exists(test_file):
            doc = process_document(test_file)
            if doc:
                print("\n" + "="*50)
                print("Document Info:")
                print(f"Filename: {doc['filename']}")
                print(f"Type: {doc['file_type']}")
                print(f"Size: {doc['file_size']} bytes")
                print(f"Content preview: {doc['content'][:200]}...")
        else:
            print(f"File not found: {test_file}")
    else:
        print("Usage: python document_processor.py <file_path>")
