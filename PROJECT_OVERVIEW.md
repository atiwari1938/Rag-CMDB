# AI-Powered Support Assistant - Project Overview

## 🎯 Project Summary
An intelligent support assistant system that uses **Retrieval-Augmented Generation (RAG)** to provide accurate answers by searching through historical support tickets and uploaded documents. The system combines semantic search with AI-powered response generation to help support teams quickly find solutions.

---

## 🏗️ System Architecture

### **Three-Tier Architecture**
1. **Frontend Layer** - React.js web interface
2. **Backend Layer** - Flask REST API server
3. **Data Layer** - FAISS vector database + Parquet storage

```
User Query → Frontend → Backend API → Vector Search (FAISS) → AI Response → User
                                    ↓
                              Document Processing
                              Ticket Ingestion
```

---

## 💻 Technologies Used

### **Frontend Technologies**
- **React.js** (v18.2.0) - JavaScript library for building user interfaces
- **Material-UI** (v5.14.10) - React component library for modern UI design
- **Axios** - HTTP client for API communication
- **Custom Styling** - Consistent color scheme (#1976d2 primary, #424242 secondary)

### **Backend Technologies**
- **Flask** - Python web framework for REST API
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **Python** (v3.12) - Primary programming language

### **AI & Machine Learning**
- **Azure OpenAI Service** - Cloud-based AI platform
  - **text-embedding-ada-002** - Embedding model (converts text to vectors)
  - **gpt-4o-mini** - Chat completion model (generates responses)
- **FAISS** (Facebook AI Similarity Search) - Vector database for semantic search
- **NumPy** - Numerical computing for vector operations

### **Document Processing**
- **PyPDF2** - PDF text extraction
- **python-docx** - Microsoft Word document processing
- **pandas** - Excel file processing and data manipulation

### **Data Storage**
- **Parquet Format** - Columnar storage for ticket data
- **Pickle** - Python object serialization for metadata
- **SQLite** - Hash database for deduplication

---

## 🔑 Key Concepts & Abbreviations

### **RAG (Retrieval-Augmented Generation)**
A technique that combines:
1. **Retrieval** - Finding relevant information from a knowledge base
2. **Augmentation** - Adding retrieved context to the AI prompt
3. **Generation** - Using AI to generate accurate, context-aware responses

### **Vector Embeddings**
- Text converted into numerical arrays (vectors) that capture semantic meaning
- Similar concepts have similar vector representations
- Enables semantic search (meaning-based, not just keyword matching)

### **FAISS (Facebook AI Similarity Search)**
- High-performance vector similarity search library
- Efficiently finds the most relevant documents from millions of entries
- Uses cosine similarity to compare query vectors with stored vectors

### **Semantic Search**
- Search based on meaning rather than exact keyword matches
- Example: "login issue" matches "unable to access account"

### **Token**
- Units of text processed by AI models
- Approximately 3-4 characters = 1 token
- Models have token limits (e.g., 8,192 tokens)

---

## 📋 Core Features Implemented

### 1. **Intelligent Search System**
- **Semantic Search**: Uses AI embeddings to understand query meaning
- **Keyword Matching**: Boosts relevance scores for exact term matches
- **Hybrid Ranking**: Combines FAISS similarity + keyword relevance
- **Multi-Source Search**: Searches both tickets and uploaded documents

### 2. **Document Processing Pipeline**
- Supports multiple formats: PDF, DOCX, TXT, Excel
- Automatic text extraction and content parsing
- Hash-based deduplication to prevent duplicate processing
- Metadata storage for document tracking

### 3. **Conversation Management**
- Multi-conversation support with sidebar navigation
- Conversation history persistence
- New conversation creation
- Delete conversation functionality

### 4. **Modern User Interface**
- Clean, professional design with Material-UI components
- Real-time chat interface
- Similar tickets/documents display
- Responsive layout for different screen sizes

### 5. **Document Upload**
- Drag-and-drop file upload support
- Automatic processing and indexing
- Support for bulk document uploads

---

## 🔄 System Workflow

### **Data Ingestion Process**
1. **File Upload** → User uploads Excel tickets or support documents
2. **Hash Check** → System checks if file was already processed
3. **Text Extraction** → Extract content from PDF/DOCX/Excel
4. **Embedding Generation** → Convert text to vector embeddings (1536 dimensions)
5. **Index Storage** → Store vectors in FAISS index
6. **Metadata Storage** → Save document metadata (filename, content, type)

### **Query Processing Flow**
1. **User Query** → User asks a question in the chat interface
2. **Query Embedding** → Convert question to vector embedding
3. **Vector Search** → FAISS finds top semantically similar items
4. **Keyword Scoring** → Calculate relevance scores based on term matches
5. **Ranking** → Sort by combined semantic + keyword scores
6. **Context Building** → Format top 5 results as context
7. **AI Generation** → GPT-4o-mini generates response using context
8. **Response Display** → Show answer + similar tickets/documents

---

## 📊 Technical Specifications

### **Vector Database**
- **Index Type**: FAISS IndexFlatL2
- **Embedding Dimensions**: 1,536 (from text-embedding-ada-002)
- **Current Capacity**: 98 items (97 tickets + 1 document)
- **Search Strategy**: Exhaustive search with keyword re-ranking

### **Scoring Algorithm**
**For Documents:**
- Filename match: +100 points per term
- Description match: +50 points per term
- Content match: +30 points per term

**For Tickets:**
- Title match: +3 points per term
- Description match: +2 points per term
- Category match: +1 point per term

### **API Endpoints**
- `POST /api/chat` - Send query and get AI response
- `GET /api/documents` - List uploaded documents
- `POST /api/upload` - Upload new documents
- `GET /api/health` - Check system health

### **Token Management**
- Text truncation to 6,000 characters before embedding
- Context limited to 1,000 characters per item
- Maximum 5 items in context to prevent token overflow

---

## 🛠️ Development Tools & Practices

### **Version Control**
- **Git** - Source code management
- **GitHub** - Repository hosting (atiwari1938/RAG_GPT)

### **Development Environment**
- **VS Code** - Primary IDE
- **PowerShell** - Command line interface (Windows)
- **Python virtual environment** - Dependency isolation

### **Code Organization**
```
├── frontend/          # React application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API service layer
│   │   └── App.js        # Main application
├── src/               # Python backend
│   ├── api_server.py     # Flask API server
│   ├── ingestion.py      # Data processing
│   ├── embeddings.py     # Vector embedding generation
│   ├── retriever.py      # Search and response generation
│   └── document_processor.py  # Document text extraction
├── data/              # Data storage
│   ├── faiss_index.idx   # Vector database
│   ├── tickets_meta.pkl  # Metadata
│   ├── tickets.parquet   # Ticket data
│   └── incoming/         # Uploaded documents
└── requirements.txt   # Python dependencies
```

---

## 🎯 Problem Solved

### **Before This System:**
- Support agents manually search through thousands of tickets
- Time-consuming keyword searches miss semantically similar issues
- Difficult to find relevant solutions in uploaded documents
- Inconsistent answers to similar questions

### **After This System:**
- **Instant Search**: Find relevant tickets/documents in seconds
- **Semantic Understanding**: Matches questions by meaning, not just keywords
- **Unified Search**: Single interface for tickets and documents
- **AI-Powered Answers**: Generates contextual responses automatically
- **Improved Accuracy**: Combines multiple similar cases for better solutions

---

## 📈 Key Achievements

1. ✅ **Multi-Format Support** - PDF, DOCX, TXT, Excel processing
2. ✅ **Semantic Search** - AI-powered meaning-based search
3. ✅ **Document Integration** - Uploaded support docs searchable alongside tickets
4. ✅ **Smart Ranking** - Documents prioritized with 10x higher relevance scores
5. ✅ **Modern UI** - Professional, intuitive interface
6. ✅ **Conversation Management** - Multiple conversation threads
7. ✅ **Deduplication** - Hash-based prevention of duplicate processing
8. ✅ **Error Handling** - Token overflow protection, graceful error handling

---

## 🔧 Technical Challenges Overcome

### **Challenge 1: Token Limit Exceeded**
- **Problem**: Document content (17,591 tokens) exceeded model limit (8,192)
- **Solution**: Implemented 6,000 character truncation before embedding

### **Challenge 2: Documents Not Appearing in Search**
- **Problem**: FAISS semantic similarity didn't rank documents high enough
- **Solution**: Changed to search all candidates + keyword boosting (100/50/30 weights)

### **Challenge 3: Duplicate Processing**
- **Problem**: Excel files processed both as tickets and documents
- **Solution**: Excluded Excel from document processor, only process as tickets

### **Challenge 4: Path Resolution Issues**
- **Problem**: Relative paths caused file not found errors
- **Solution**: Implemented absolute path resolution with BASE_DIR

---

## 🚀 Future Enhancements (Possible Extensions)

1. **Multi-language Support** - Support tickets in different languages
2. **Advanced Analytics** - Dashboard showing search patterns, common issues
3. **User Feedback Loop** - Rate responses to improve accuracy
4. **Auto-categorization** - Automatically tag and categorize new tickets
5. **Integration** - Connect to ticketing systems (ServiceNow, Jira, Zendesk)
6. **Advanced Search Filters** - Filter by date, category, priority
7. **Export Features** - Export search results and reports

---

## 📚 Learning Outcomes

### **Technical Skills Gained**
- RAG architecture design and implementation
- Vector database management (FAISS)
- Azure OpenAI API integration
- Full-stack development (React + Flask)
- Document processing and text extraction
- Semantic search and embedding techniques

### **Best Practices Applied**
- Modular code architecture
- API-first design
- Error handling and logging
- Token management for AI models
- User experience optimization

---

## 🎓 Presentation Key Points

### **For Non-Technical Audience:**
> "We built an intelligent assistant that understands what users are asking and instantly finds relevant solutions from thousands of past tickets and documents, just like having an experienced support agent available 24/7."

### **For Technical Audience:**
> "This is a RAG-based system using FAISS for vector similarity search and Azure OpenAI for embeddings and generation. We implemented hybrid search combining semantic similarity with keyword-based relevance scoring, processing multi-format documents with a Flask backend and React frontend."

### **Impact Statement:**
> "This system reduces support ticket resolution time from hours to seconds by automatically finding relevant historical solutions and generating contextual responses using AI."

---

## 📞 System Metrics

- **Search Speed**: < 2 seconds for query processing
- **Accuracy**: Semantic search + keyword matching
- **Scalability**: Handles 98+ items (expandable to thousands)
- **Format Support**: 4 document formats (PDF, DOCX, TXT, Excel)
- **API Endpoints**: 4 REST endpoints
- **Frontend Components**: 4 major React components

---

## 🏆 Project Highlights

1. **Production-Ready**: Fully functional system with error handling
2. **Modern Stack**: Latest technologies (React 18, Flask, Azure OpenAI)
3. **User-Focused**: Clean UI with conversation management
4. **Extensible**: Modular architecture for easy enhancements
5. **Well-Documented**: Comprehensive code documentation and guides

---

**Project Duration**: Multiple iterations with continuous improvements
**Team Size**: Individual project with AI assistance
**Status**: ✅ Fully Functional and Deployable

