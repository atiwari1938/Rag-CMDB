from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import process as ingest
from src.embeddings import embed_documents
from src.retriever import retrieve, generate_response

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get absolute path to data directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TICKETS_PARQUET = os.path.join(DATA_DIR, 'tickets.parquet')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        query = data.get('query')
        
        if not query or not query.strip():
            return jsonify({'error': 'Query cannot be empty'}), 400

        # Ensure data is ingested and embedded
        if not os.path.exists(TICKETS_PARQUET):
            print(f"Running initial ingestion with force reprocess (tickets.parquet not found at {TICKETS_PARQUET})...")
            ingest(force_reprocess=True)
            embed_documents()

        # Retrieve similar tickets and generate response
        similar_tickets = retrieve(query)
        response = generate_response(query, similar_tickets)

        # Debug: Log what fields are in the tickets
        if similar_tickets:
            print(f"\n🔍 Returned {len(similar_tickets)} tickets/documents")
            
            # Find first non-document ticket
            first_ticket = None
            for ticket in similar_tickets:
                if ticket.get('document_type') != 'support_document':
                    first_ticket = ticket
                    break
            
            if first_ticket:
                print(f"\n📋 First TICKET fields:")
                print(f"ALL fields: {list(first_ticket.keys())}")
                # Check for number fields
                number_fields = [k for k in first_ticket.keys() if 'number' in k.lower() or 'num' in k.lower() or 'id' in k.lower()]
                print(f"Number/ID/Num fields found: {number_fields}")
                
                # Show all field values (first 50 chars each)
                print(f"\nAll field values:")
                for key, val in first_ticket.items():
                    if val is not None:
                        val_str = str(val)[:50]
                        print(f"  {key}: {val_str}")

        # Temporary debug: add field info to response
        debug_info = {}
        if similar_tickets:
            first_non_doc = next((t for t in similar_tickets if t.get('document_type') != 'support_document'), None)
            if first_non_doc:
                debug_info = {
                    'all_fields': list(first_non_doc.keys()),
                    'has_number': 'number' in first_non_doc,
                    'number_value': first_non_doc.get('number'),
                    'sample_ticket': {k: str(v)[:50] if v else None for k, v in list(first_non_doc.items())[:15]}
                }
        
        return jsonify({
            'response': response,
            'similar_tickets': similar_tickets,
            'debug': debug_info  # Temporary - will show in browser console
        })

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/api/documents', methods=['GET'])
def get_documents():
    try:
        # Get the base directory (one level up from src)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        incoming_dir = os.path.join(base_dir, 'data', 'incoming')
        documents = []
        
        print(f"Looking for documents in: {incoming_dir}")
        
        if os.path.exists(incoming_dir):
            for filename in os.listdir(incoming_dir):
                file_path = os.path.join(incoming_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    documents.append({
                        'id': filename,
                        'filename': filename,
                        'name': filename,
                        'uploaded_at': stat.st_mtime,
                        'size': stat.st_size
                    })
            print(f"Found {len(documents)} documents")
        else:
            print(f"Directory does not exist: {incoming_dir}")
        
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        print(f"Error getting documents: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Get the base directory (one level up from src)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        incoming_dir = os.path.join(base_dir, 'data', 'incoming')
        
        # Create directory if it doesn't exist
        os.makedirs(incoming_dir, exist_ok=True)
        print(f"Saving file to: {incoming_dir}")
        
        file_path = os.path.join(incoming_dir, file.filename)
        file.save(file_path)
        print(f"File saved successfully: {file_path}")
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'filename': file.filename
        })
    except Exception as e:
        print(f"Error uploading document: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    # Ensure the required files exist
    if not os.path.exists(TICKETS_PARQUET):
        print("Running initial data setup...")
        ingest()
        embed_documents()
    
    print("Starting API server...")
    app.run(port=5000, debug=True)

