# Document Processing Feature

## Overview
The system now supports multiple document formats beyond Excel files:
- **PDF** (.pdf)
- **Word Documents** (.docx, .doc)
- **Excel Files** (.xlsx, .xls)
- **Text Files** (.txt)

## Setup Instructions

### 1. Install Required Libraries

Run this command to install document processing libraries:

```powershell
pip install PyPDF2 python-docx
```

Or install all requirements:

```powershell
pip install -r requirements.txt
```

### 2. Add Documents

Simply place your support documents in the `data/incoming` folder:

```
data/incoming/
├── troubleshooting_guide.pdf
├── user_manual.docx
├── known_issues.txt
├── incident (3).xlsx
└── sc_req_item (1) 1.xlsx
```

### 3. Process Documents

The system automatically processes all documents when the backend starts. You can also manually trigger processing:

```powershell
cd src
python ingestion.py
python embeddings.py
```

## How It Works

1. **Document Detection**: System scans `data/incoming` for supported file types
2. **Text Extraction**: 
   - PDF: Extracts text from all pages
   - DOCX: Extracts text from all paragraphs
   - XLSX: Converts all cells to text
   - TXT: Reads file content directly
3. **Indexing**: Text content is converted to embeddings for semantic search
4. **Search**: When users query, the system searches across all documents (tickets + support docs)

## Supported Document Types

| Format | Extension | Library Used |
|--------|-----------|--------------|
| PDF    | .pdf      | PyPDF2       |
| Word   | .docx     | python-docx  |
| Excel  | .xlsx     | pandas       |
| Text   | .txt      | built-in     |

## Features

✅ **Automatic Processing**: New documents are processed on server restart  
✅ **Duplicate Detection**: Files are tracked by hash to avoid reprocessing  
✅ **Mixed Content**: Search works across tickets and support documents  
✅ **File Metadata**: Tracks filename, size, modification date  
✅ **Error Handling**: Gracefully handles corrupted or unsupported files  

## Example Use Cases

### 1. Troubleshooting Guides
Add PDF troubleshooting guides:
```
data/incoming/network_troubleshooting.pdf
data/incoming/vpn_setup_guide.pdf
```

### 2. Knowledge Base Articles
Add Word documents with solutions:
```
data/incoming/common_issues.docx
data/incoming/best_practices.docx
```

### 3. Configuration Files
Add text files with configs:
```
data/incoming/server_config.txt
data/incoming/deployment_steps.txt
```

## Testing

Test a single document:
```powershell
python src/document_processor.py "data/incoming/your_document.pdf"
```

## Troubleshooting

### Issue: PDF text extraction fails
**Solution**: Some PDFs are image-based. Consider using OCR (pytesseract) for those.

### Issue: DOCX not processing
**Solution**: Ensure python-docx is installed: `pip install python-docx`

### Issue: Documents not appearing in search
**Solution**: Restart the backend server to trigger reindexing.

## API Impact

The `/api/documents` endpoint now shows all file types:
```json
{
  "success": true,
  "documents": [
    {
      "id": "troubleshooting.pdf",
      "filename": "troubleshooting.pdf",
      "size": 524288,
      "uploaded_at": 1699459200
    }
  ]
}
```
