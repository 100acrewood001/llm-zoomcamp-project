# Annual Report Analyzer MVP

An intelligent document analysis system that uses Azure OpenAI to extract insights from financial documents, particularly annual reports.

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ installed on your system
- Azure OpenAI subscription with deployed models:
  - GPT-4 (or GPT-4o) for chat completion
  - text-embedding-ada-002 for embeddings
- Git (for cloning the repository)

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/100acrewood001/llm-zoomcamp-project.git
cd llm-zoomcamp-project

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment:
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Azure OpenAI Credentials

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** with your actual Azure OpenAI credentials:
   ```env
   # Replace with your actual Azure OpenAI resource details:
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-32-character-api-key-here
   AZURE_OPENAI_API_VERSION=2024-02-01
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
   ```

3. **How to get Azure OpenAI credentials:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to your Azure OpenAI resource
   - Go to "Keys and Endpoint" section
   - Copy the endpoint URL and one of the API keys
   - Ensure you have deployed both models (GPT-4 and text-embedding-ada-002)

### Step 3: Test Your Setup

```bash
# Test configuration (should show no errors if properly configured)
python -c "from src.utils.config import get_config; print('✅ Configuration loaded successfully')"

# Run the setup validation script
python setup.py
```

### Step 4: Run the Application

**Option A: Interactive CLI Mode**
```bash
python main.py
```

**Option B: API Server Mode**
```bash
python main.py --api
# Server will start at http://localhost:8000
# API documentation available at http://localhost:8000/docs
```

## 🎯 Getting Started - Your First Analysis

### Using Interactive Mode

1. **Start the application:**
   ```bash
   python main.py
   ```

2. **Upload your first document:**
   ```
   > upload path/to/your/annual_report.pdf
   ```

3. **Ask questions about your document:**
   ```
   > query What was the total revenue for 2024?
   > query What are the main risk factors mentioned?
   > query How did operating expenses change year over year?
   ```

4. **Check system status:**
   ```
   > stats      # View document and query statistics
   > health     # Check system health
   > list       # Show all uploaded documents
   > quit       # Exit the application
   ```

### Using API Mode

1. **Start the API server:**
   ```bash
   python main.py --api
   ```

2. **Upload a document via API:**
   ```bash
   curl -X POST "http://localhost:8000/documents/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/annual_report.pdf"
   ```

3. **Query your document:**
   ```bash
   curl -X POST "http://localhost:8000/documents/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What was the revenue growth in 2024?"}'
   ```

4. **Access interactive API documentation:**
   - Open your browser to: `http://localhost:8000/docs`
   - Test all endpoints directly from the browser interface

## 📋 Features & Capabilities

### 🎯 Core Features
- **📄 PDF Document Processing**: Extract and analyze text from annual reports with metadata preservation
- **🧠 Intelligent Chunking**: Smart text segmentation optimized for financial documents and tables
- **🔍 Vector Search**: FAISS-powered semantic search across document content
- **💬 AI-Powered Q&A**: Natural language queries with context-aware responses and citations
- **🌐 REST API**: Complete web API for integration with other systems
- **💻 Interactive CLI**: User-friendly command-line interface for document management

### 🏦 Financial Document Optimization
- **📊 Table Recognition**: Specialized chunking preserves financial table structures
- **⚠️ Risk Factor Analysis**: Automatic identification and categorization of risk factors
- **💰 Financial Metrics**: Revenue, profit, and performance data extraction with context
- **📖 Citation Support**: All answers include source document and page references
- **📈 Multi-Year Analysis**: Compare metrics across different reporting periods

### 🔧 Technical Features
- **⚡ Fast Vector Search**: In-memory FAISS index for sub-second query responses
- **🔄 Async Processing**: Non-blocking operations for better performance
- **📝 Structured Logging**: JSON-formatted logs with performance metrics
- **🛡️ Error Handling**: Comprehensive error handling with graceful degradation
- **⚙️ Configurable Settings**: Extensive configuration options via YAML and environment variables

## 💡 Usage Examples & Best Practices

### Example Questions You Can Ask

**Financial Performance:**
```
"What was the total revenue for 2024?"
"How did operating expenses change compared to last year?"
"What is the company's profit margin?"
"Show me the key financial highlights for this quarter."
```

**Risk Analysis:**
```
"What are the main risk factors mentioned in the report?"
"Are there any new regulatory risks identified?"
"What operational risks does the company face?"
"How has the risk profile changed from previous years?"
```

**Strategic Analysis:**
```
"What are the company's growth strategies?"
"Which business segments performed best?"
"What investments is the company making?"
"What are the management's outlook statements?"
```

**Comparative Analysis:**
```
"Compare this year's revenue to last year."
"How have margins improved over time?"
"What trends can you identify in the financial data?"
"Which metrics show the most significant changes?"
```

### Best Practices for Document Upload

**Optimal Document Types:**
- ✅ **Annual Reports (10-K, 10-Q)**: Full financial statements with comprehensive data
- ✅ **Earnings Reports**: Quarterly performance summaries
- ✅ **Financial Statements**: Balance sheets, income statements, cash flow
- ✅ **Investor Presentations**: Management discussion and analysis

**File Preparation Tips:**
- 📄 **File Size**: Keep under 50MB for optimal performance
- 📝 **Text Quality**: Ensure PDFs are text-based, not scanned images
- 🏷️ **File Names**: Use descriptive names (e.g., "AAPL_Annual_Report_2024.pdf")
- 📅 **Organization**: Group documents by company and year for easier management

### API Integration Examples

**Python Integration:**
```python
import requests

# Upload document
def upload_document(file_path):
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post('http://localhost:8000/documents/upload', files=files)
    return response.json()

# Query document
def query_document(question):
    data = {'query': question}
    response = requests.post('http://localhost:8000/documents/query', json=data)
    return response.json()

# Example usage
result = upload_document('annual_report_2024.pdf')
answer = query_document('What was the revenue growth?')
print(f"Answer: {answer['answer']}")
```

**JavaScript Integration:**
```javascript
// Upload document
async function uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8000/documents/upload', {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

// Query document
async function queryDocument(question) {
    const response = await fetch('http://localhost:8000/documents/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question })
    });
    return await response.json();
}
```

### Performance Optimization Tips

**For Large Documents:**
1. **Reduce chunk size** in configuration (500-750 characters)
2. **Increase overlap** for better context (150-250 characters)
3. **Process in batches** if uploading multiple documents
4. **Monitor memory usage** and restart if needed

**For Better Accuracy:**
1. **Use specific questions** rather than general queries
2. **Include relevant keywords** in your questions
3. **Reference specific sections** when possible
4. **Verify citations** in the source document

**For API Performance:**
1. **Use connection pooling** for multiple requests
2. **Implement retry logic** for failed requests
3. **Cache frequent queries** if appropriate
4. **Monitor response times** and adjust configuration
- Revenue and performance data extraction
- Contextual citation support

## 🏗️ Architecture

```
src/
├── api/              # FastAPI web application
├── azure/            # Azure OpenAI clients
├── extractors/       # Document text extraction
├── orchestrator/     # Main workflow coordination
├── rag/             # RAG pipeline components
└── utils/           # Configuration and utilities

config/              # Configuration files
tests/              # Unit and integration tests
```

## 📖 Usage

### Interactive Mode Commands
- `upload <file_path>`: Upload and process a PDF document
- `query <question>`: Ask questions about uploaded documents
- `list`: Show all uploaded documents
- `stats`: Display system statistics
- `health`: Check system health
- `quit`: Exit the application

### API Endpoints
- `GET /health`: System health check
- `POST /documents/upload`: Upload a document
- `POST /documents/query`: Query documents
- `GET /documents`: List all documents
- `GET /stats`: System statistics

### Example API Usage
```bash
# Upload a document
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@annual_report_2024.pdf"

# Query documents
curl -X POST "http://localhost:8000/documents/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the revenue growth in 2024?"}'
```

## 🧪 Testing Your Setup

### Validation Steps

1. **Test Configuration Loading:**
   ```bash
   python -c "from src.utils.config import get_config; print('✅ Configuration loaded successfully')"
   ```

2. **Run Unit Tests:**
   ```bash
   # Activate virtual environment first
   # On Windows: .\venv\Scripts\Activate.ps1
   # On macOS/Linux: source venv/bin/activate
   
   pytest tests/ -v
   ```

3. **Run Integration Tests (requires Azure OpenAI setup):**
   ```bash
   pytest tests/ -m integration -v
   ```

4. **Test with Sample Document:**
   - Download a sample annual report PDF
   - Use the interactive mode to upload and query it
   - Verify you get meaningful responses with citations

### Manual Testing Checklist

- [ ] Virtual environment activates without errors
- [ ] All dependencies install successfully
- [ ] Configuration loads without validation errors
- [ ] Application starts in interactive mode
- [ ] Application starts in API mode (port 8000)
- [ ] Can upload a PDF document
- [ ] Can query the uploaded document
- [ ] Receives answers with proper citations
- [ ] Health check returns "healthy" status

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

#### 1. Import Errors
**Problem:** `ImportError` or `ModuleNotFoundError`
```bash
# Solution: Ensure virtual environment is activated and dependencies are installed
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
```

#### 2. Pydantic Configuration Errors
**Problem:** `ValidationError` for Azure OpenAI settings
```bash
# Solution: Check your .env file has the correct format and values
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-32-character-key
```

#### 3. Azure OpenAI Connection Issues
**Problem:** Authentication or connection failures
- ✅ Verify endpoint URL format (must end with `.openai.azure.com/`)
- ✅ Check API key is valid and not expired
- ✅ Ensure deployment names match your Azure resource exactly
- ✅ Verify you have quota available for your deployments

#### 4. Memory Issues with Large PDFs
**Problem:** Out of memory errors with large documents
```yaml
# Solution: Reduce chunk size in config/config.yaml
rag:
  chunk_size: 500          # Reduced from 1000
  chunk_overlap: 100       # Reduced from 200
```

#### 5. Port Already in Use
**Problem:** `Address already in use` when starting API server
```bash
# Solution: Use a different port
python main.py --api --port 8001
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

1. **Edit `.env` file:**
   ```env
   LOG_LEVEL=DEBUG
   DEBUG=true
   ```

2. **Check logs directory:**
   ```bash
   # Logs are saved to ./logs/ directory
   ls -la logs/
   ```

### Getting Help

1. **Check the logs** in the `./logs/` directory for detailed error information
2. **Verify Azure OpenAI** deployments are active and have quota
3. **Test with smaller PDF files** first (< 10MB)
4. **Ensure Python 3.8+** is being used
5. **Try the automated setup script:** `python setup.py`

## ⚙️ Configuration Reference

### Environment Variables (`.env` file)

**Required Settings:**
```env
# Azure OpenAI - Required
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-32-character-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
```

**Optional Settings:**
```env
# Application Settings
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
DEBUG=false                       # Enable/disable debug mode
MAX_FILE_SIZE_MB=50              # Maximum PDF file size

# API Configuration
API_HOST=0.0.0.0                 # API server bind address
API_PORT=8000                    # API server port

# Performance Settings
MAX_CONCURRENT_REQUESTS=10        # Concurrent request limit
REQUEST_TIMEOUT_SECONDS=300       # Request timeout

# Azure Key Vault (Optional - for enhanced security)
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
```

### Application Configuration (`config/config.yaml`)

**Complete Configuration Options:**
```yaml
# RAG (Retrieval-Augmented Generation) Settings
rag:
  chunk_size: 1000              # Text chunk size in characters
  chunk_overlap: 200            # Overlap between chunks
  max_context_chunks: 5         # Max chunks to use for context
  similarity_threshold: 0.7     # Minimum similarity for results
  
# API Server Settings
api:
  host: "127.0.0.1"            # Server bind address
  port: 8000                   # Server port
  debug: false                 # Debug mode
  cors_origins: ["*"]          # CORS allowed origins
  
# Azure OpenAI Model Settings
azure_openai:
  chat_deployment_name: "gpt-4"              # Your GPT-4 deployment name
  embedding_deployment_name: "text-embedding-ada-002"  # Embedding model
  max_tokens: 4000                           # Max response tokens
  temperature: 0.1                           # Response creativity (0-1)
  top_p: 0.9                                # Nucleus sampling
  frequency_penalty: 0.0                    # Frequency penalty
  presence_penalty: 0.0                     # Presence penalty
  
# Document Processing Settings
document:
  max_file_size_mb: 50                      # Max file size
  supported_formats: ["pdf"]               # Supported formats
  text_extraction_method: "pymupdf"        # Extraction method
  
# Performance Settings
performance:
  batch_size: 16                           # Embedding batch size
  max_retries: 3                           # API retry attempts
  retry_delay: 1.0                         # Retry delay in seconds
  timeout: 30                              # Request timeout
  
# Logging Settings
logging:
  level: "INFO"                            # Log level
  format: "json"                           # Log format (json/text)
  file: "logs/app.log"                     # Log file path
  max_size_mb: 100                         # Max log file size
  backup_count: 5                          # Number of backup files
```

### Configuration Priority

Settings are loaded in this order (later overrides earlier):
1. Default values in code
2. `config/config.yaml` file
3. Environment variables from `.env` file
4. System environment variables
5. Command-line arguments (where applicable)

### Azure OpenAI Model Requirements

| Model Type | Recommended Deployment | Purpose | Required |
|------------|----------------------|---------|----------|
| Chat | `gpt-4` or `gpt-4o` | Answer generation | ✅ Yes |
| Chat Alternative | `gpt-35-turbo` | Cost-effective option | ⚠️ Alternative |
| Embeddings | `text-embedding-ada-002` | Document search | ✅ Yes |
| Embeddings Alternative | `text-embedding-3-small` | Newer model option | ⚠️ Alternative |

### Configuration Validation

Test your configuration:
```bash
# Basic configuration test
python -c "from src.utils.config import get_config; print('✅ Config loaded')"

# Full validation with Azure connection test
python -c "
from src.utils.config import get_config
config = get_config()
if config.validate_azure_config():
    print('✅ Azure OpenAI configuration is valid')
else:
    print('❌ Azure OpenAI configuration needs attention')
"
```

## 📊 System Requirements

- Python 3.8+
- Azure OpenAI subscription with:
  - GPT-4 deployment
  - text-embedding-ada-002 deployment
- 4GB+ RAM (for FAISS vector operations)
- 1GB+ disk space (for document storage and vectors)

## 🔧 Development

### Project Structure
```
llm-zoomcamp-project/
├── config/
│   ├── config.yaml           # Main configuration
│   └── .env.example         # Environment template
├── src/
│   ├── api/
│   │   └── fastapi_app.py   # FastAPI application
│   ├── azure/
│   │   ├── chat_client.py   # Chat completion client
│   │   └── embedding_client.py  # Embedding client
│   ├── extractors/
│   │   └── text_extractor.py    # PDF text extraction
│   ├── orchestrator/
│   │   └── mvp_orchestrator.py  # Main workflow
│   ├── rag/
│   │   ├── chunking_strategy.py # Text chunking
│   │   └── vector_store.py      # Vector database
│   └── utils/
│       ├── config.py        # Configuration management
│       └── logging_config.py    # Logging setup
├── tests/
│   └── test_mvp.py         # Test suite
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
├── setup.py               # Setup script
└── README.md              # This file
```

### Adding New Features
1. Follow the existing architecture patterns
2. Add configuration to `config.yaml` if needed
3. Include comprehensive error handling
4. Add tests in `tests/` directory
5. Update documentation

### Common Issues

#### Azure OpenAI Connection
- Verify endpoint URL format
- Check API key validity
- Ensure deployment names match your Azure resource

#### Import Errors
- Run `python setup.py` to install dependencies
- Activate virtual environment if using one
- Check Python version (3.8+ required)

#### Memory Issues
- Reduce `chunk_size` in configuration
- Process smaller documents
- Monitor system RAM usage

## 📝 Roadmap

### Phase 1: MVP Core ✅
- Basic document processing and Q&A
- Azure OpenAI integration
- Vector storage and retrieval
- REST API and CLI interface

### Phase 2: Enhanced Analytics (Planned)
- Advanced financial metrics extraction
- Comparative analysis across documents
- Export capabilities (PDF, Excel)
- Batch processing support

### Phase 3: Web Interface (Planned)
- React/Vue.js frontend
- Document visualization
- Interactive dashboards
- User management

### Phase 4: Enterprise Features (Planned)
- Multi-tenant support
- Advanced security features
- Audit logging
- Performance monitoring

## ❓ Frequently Asked Questions (FAQ)

### General Questions

**Q: What types of documents can I analyze?**
A: Currently, the system supports PDF documents, specifically optimized for:
- Annual Reports (10-K, 10-Q forms)
- Financial Statements
- Earnings Reports  
- Investor Presentations
- Any PDF containing structured financial information

**Q: What's the maximum file size I can upload?**
A: The default limit is 50MB, configurable via the `MAX_FILE_SIZE_MB` environment variable. For larger files, consider reducing the chunk size in the configuration.

**Q: How accurate are the AI responses?**
A: Accuracy depends on:
- Quality of the source document (text-based PDFs work best)
- Specificity of your questions
- Relevance of the content to your query
All responses include citations so you can verify information in the source document.

### Technical Questions

**Q: Which Azure OpenAI models do I need?**
A: You need two deployments:
- **GPT-4 or GPT-4o**: For generating responses
- **text-embedding-ada-002**: For document search
Both must be deployed in your Azure OpenAI resource.

**Q: Can I use other AI models besides Azure OpenAI?**
A: The current MVP is specifically built for Azure OpenAI. Support for other providers (OpenAI direct, Claude, etc.) would require code modifications.

**Q: How much does it cost to run?**
A: Costs depend on:
- Azure OpenAI usage (embeddings + chat completions)
- Document size and number of queries
- Typically $0.01-$0.10 per document for processing
- $0.001-$0.01 per query depending on complexity

**Q: Is my data secure?**
A: Yes, the system:
- Processes documents locally on your machine
- Only sends text chunks to Azure OpenAI for analysis
- Doesn't store data permanently (in-memory processing)
- Supports Azure Key Vault for credential management

### Setup & Configuration

**Q: I'm getting "ValidationError" for Azure OpenAI settings. What's wrong?**
A: Check your `.env` file:
1. Ensure `AZURE_OPENAI_ENDPOINT` ends with `.openai.azure.com/`
2. Verify your API key is exactly 32 characters
3. Confirm your deployment names match your Azure resource
4. Test with: `python -c "from src.utils.config import get_config; get_config()"`

**Q: The application starts but gives authentication errors. Help?**
A: Common authentication issues:
1. **API Key**: Ensure it's valid and not expired
2. **Endpoint**: Must be the exact URL from Azure Portal
3. **Deployments**: Model names must match your Azure deployments exactly
4. **Quota**: Check you have available quota in Azure Portal

**Q: How do I know if my virtual environment is set up correctly?**
A: Run these validation commands:
```bash
# Check virtual environment
which python  # Should show venv path

# Check package installation  
python -c "import openai, faiss, fastapi; print('✅ All packages installed')"

# Check configuration
python -c "from src.utils.config import get_config; print('✅ Configuration loaded')"
```

### Usage Questions

**Q: What's the best way to ask questions?**
A: For best results:
- ✅ **Be specific**: "What was revenue in Q4 2024?" vs "Tell me about revenue"
- ✅ **Use financial terms**: "operating margin", "EBITDA", "cash flow"
- ✅ **Reference time periods**: "2024", "last year", "this quarter"
- ✅ **Ask focused questions**: One concept per question

**Q: Why are my answers sometimes incomplete or wrong?**
A: Common issues:
- **Document quality**: Scanned PDFs work poorly, use text-based PDFs
- **Question clarity**: Vague questions get vague answers
- **Content availability**: Information might not be in the document
- **Context limits**: Very long documents may have relevant info excluded

**Q: Can I analyze multiple documents at once?**
A: The current MVP processes one document at a time. For multiple documents:
1. Upload and process each separately
2. Ask questions about each individually
3. Future versions will support multi-document analysis

### Performance & Troubleshooting

**Q: The system is slow. How can I speed it up?**
A: Performance optimization:
1. **Reduce chunk size**: Edit `config/config.yaml`, set `chunk_size: 500`
2. **Use smaller documents**: Under 10MB process faster
3. **Specific queries**: Focused questions return faster
4. **Check internet**: Azure OpenAI calls require good connectivity

**Q: I'm running out of memory. What can I do?**
A: Memory management:
1. **Reduce chunk size** in configuration
2. **Process smaller documents** (< 20MB)
3. **Restart the application** periodically
4. **Close other applications** to free RAM

**Q: The API server won't start - "port already in use"?**
A: Port conflicts:
```bash
# Use a different port
python main.py --api --port 8001

# Or kill the process using the port
netstat -ano | findstr :8000  # Find process ID
taskkill /PID <process_id> /F  # Kill on Windows
```

### Integration & Development

**Q: How do I integrate this with my existing application?**
A: Integration options:
1. **REST API**: Use the HTTP endpoints (`/documents/upload`, `/documents/query`)
2. **Python imports**: Import modules directly in Python applications  
3. **CLI wrapper**: Call the command-line interface from other programs

**Q: Can I customize the analysis for my specific industry?**
A: Yes, you can:
1. **Modify prompts**: Edit system prompts in the code
2. **Adjust chunking**: Configure chunk sizes for your document types
3. **Add business logic**: Extend the orchestrator for custom workflows
4. **Fine-tune responses**: Adjust temperature and other model parameters

**Q: How do I add support for other file formats?**
A: Currently only PDF is supported. To add other formats:
1. Create new extractor classes in `src/extractors/`
2. Update configuration to include new formats
3. Modify the upload validation logic
4. Test with your specific file types

### Future Development

**Q: What features are planned for future releases?**
A: Roadmap includes:
- **Phase 2**: Advanced financial calculations, multi-document comparison
- **Phase 3**: Web interface, visualization dashboards
- **Phase 4**: Enterprise features, user management, audit logging

**Q: Can I contribute to the project?**
A: Absolutely! Contributions are welcome:
1. Fork the repository
2. Create feature branches for new capabilities
3. Add tests for your changes
4. Submit pull requests with clear descriptions
5. Follow the existing code patterns and documentation standards

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. **Check this FAQ section** for common solutions
2. **Review the troubleshooting guide** above for technical issues  
3. **Test with sample documents** to isolate problems
4. **Verify Azure OpenAI configuration** using the validation commands
5. **Check the logs** in `./logs/` directory for detailed error information

**Getting More Help:**
- 📖 Review the complete documentation above
- 🔧 Run the setup validation: `python setup.py`
- 🧪 Test with small, simple documents first
- 📝 Enable debug logging: Set `LOG_LEVEL=DEBUG` in `.env`

---

**Note**: This is an MVP (Minimum Viable Product) focused on core functionality. Additional features and optimizations are planned for future phases.

---

## 🎯 **Key Improvements Over Basic RAG**

### **Financial Intelligence**
- 📊 **Table & Chart Extraction** - Parse financial statements, balance sheets, cash flows
- 🧮 **Financial Calculations** - Auto-compute ratios, YoY growth, margins with citations  
- 📈 **Multi-Year Analysis** - Compare metrics across reporting periods
- 🏛️ **Regulatory Structure** - Understand 10-K/10-Q sections, MD&A, risk factors

### **Advanced AI Stack**
- 🚀 **Azure OpenAI Integration** - GPT-4 for analysis, text-embedding-ada-002 for semantics
- 🔗 **LangChain RAG** - Hybrid retrieval (semantic + keyword), advanced chunking
- 🕸️ **LangGraph Orchestration** - Multi-agent workflow with specialized analysis agents
- 💾 **In-Memory Vector Store** - Fast FAISS-based similarity search

---

## 🏗️ **Enhanced System Architecture**

```mermaid
graph TD
    A[PDF Input] --> B[Document Processor Agent]
    B --> C[Text Extractor]
    B --> D[Table Parser]
    B --> E[Chart OCR]
    
    C --> F[Chunking Strategy]
    D --> G[Financial Data Normalizer]
    E --> H[Chart Data Extractor]
    
    F --> I[Azure OpenAI Embeddings]
    G --> I
    H --> I
    
    I --> J[FAISS Vector Store]
    
    K[User Query] --> L[Query Router Agent]
    L --> M{Query Type}
    
    M -->|Text Query| N[Semantic Search Agent]
    M -->|Financial Query| O[Financial Analysis Agent]
    M -->|Comparative Query| P[Multi-Year Comparison Agent]
    M -->|Risk Query| Q[Risk Analysis Agent]
    
    N --> R[Context Builder]
    O --> R
    P --> R  
    Q --> R
    
    R --> S[Azure OpenAI GPT-4]
    S --> T[Response Synthesizer Agent]
    T --> U[Final Answer + Citations]
    
    J --> N
    J --> O
    J --> P
    J --> Q
```

---

## 🧭 **Multi-Agent Workflow**

```python
# LangGraph Agent Flow
PDFs ──► Document Processor Agent ──► Chunking Strategy ──► Azure Embeddings ──► FAISS Store
                │                                                                    ▲
                ├── Table Parser ────────────────────────────────────────────────────┤
                ├── Chart OCR ───────────────────────────────────────────────────────┤
                └── Financial Data Normalizer ──────────────────────────────────────┤

User Query ──► Query Router Agent ──► Specialized Agents ──► Context Builder ──► GPT-4 ──► Response Synthesizer
                      │                       │
                      └── Financial Analysis  ├── Semantic Search
                          Multi-Year Compare  ├── Risk Analysis  
                          Regulatory Section  └── Citation Tracker
``` down a **modular, end-to-end pseudo‑code skeleton** for a simple RAG system focused on **PDF annual reports**, with **dummy data** and **stubs** for each step. You can treat this as a blueprint to implement in Python (or any language) in later iterations.

---

## 🧭 High-Level Flow

```
PDFs ──► Ingest (text per page) ──► Clean/Normalize ──► Chunk ──► Index (BM25)
                                  │                                    ▲
                                  └────────────► Metadata ─────────────┘

User Query ──► Retrieve (top‑k) ──► (optional) Rerank ──► Build Context ──► Answer
                                                            │
                                       Extractive (baseline)│ Generative (LLM optional)
                                                            │
                                                     Citations (file, page)
```

---

## 📁 **Optimized Project Structure**

```
annual_report_analyzer/
  ├── config/
  │   ├── settings.yaml                 # System configuration
  │   ├── azure_config.yaml             # Azure OpenAI settings  
  │   └── agent_prompts.yaml            # Agent-specific prompts
  │   
  ├── data/
  │   ├── pdfs/                         # Input annual reports
  │   ├── processed/                    # Processed chunks & metadata
  │   └── cache/                        # Embeddings & index cache
  │   
  ├── src/
  │   ├── agents/                       # LangGraph Agents
  │   │   ├── document_processor.py     # PDF → structured data
  │   │   ├── financial_analyzer.py     # Financial calculations
  │   │   ├── query_router.py           # Route queries to specialists
  │   │   ├── semantic_searcher.py      # Vector similarity search
  │   │   ├── risk_analyzer.py          # Risk factor extraction
  │   │   └── response_synthesizer.py   # Final answer generation
  │   │   
  │   ├── extractors/                   # Specialized Data Extraction
  │   │   ├── text_extractor.py         # Clean text extraction
  │   │   ├── table_parser.py           # Financial table parsing
  │   │   ├── chart_ocr.py              # Chart/graph data extraction
  │   │   └── financial_normalizer.py   # Standardize financial data
  │   │   
  │   ├── rag/                          # RAG Components
  │   │   ├── chunking_strategy.py      # Smart document chunking
  │   │   ├── vector_store.py           # FAISS vector operations
  │   │   ├── retrieval_engine.py       # Hybrid search (semantic + keyword)
  │   │   ├── reranker.py               # Context relevance ranking
  │   │   └── context_builder.py        # Multi-source context assembly
  │   │   
  │   ├── azure/                        # Azure OpenAI Integration
  │   │   ├── embedding_client.py       # text-embedding-ada-002
  │   │   ├── chat_client.py            # GPT-4 for analysis
  │   │   ├── credential_manager.py     # Managed Identity auth
  │   │   └── rate_limiter.py           # API quota management
  │   │   
  │   ├── financial/                    # Financial Intelligence
  │   │   ├── calculator.py             # YoY growth, ratios, margins
  │   │   ├── comparator.py             # Multi-year analysis
  │   │   ├── validator.py              # Data consistency checks
  │   │   └── formatter.py              # Financial data presentation
  │   │   
  │   ├── orchestrator/                 # LangGraph Orchestration
  │   │   ├── workflow_graph.py         # Agent coordination graph
  │   │   ├── state_manager.py          # Conversation state
  │   │   └── execution_engine.py       # Workflow execution
  │   │   
  │   └── utils/
  │       ├── logging_config.py         # Structured logging
  │       ├── metrics.py                # Performance monitoring
  │       └── validators.py             # Input validation
  │       
  ├── tests/
  │   ├── test_agents/                  # Agent unit tests
  │   ├── test_extractors/              # Extractor tests
  │   ├── test_financial/               # Financial calc tests
  │   └── integration/                  # End-to-end tests
  │   
  ├── notebooks/                        # Analysis & Development
  │   ├── data_exploration.ipynb        # PDF structure analysis
  │   ├── embedding_analysis.ipynb      # Vector space exploration  
  │   └── agent_testing.ipynb           # Agent behavior testing
  │   
  ├── api/
  │   ├── fastapi_app.py               # REST API endpoints
  │   ├── websocket_handler.py         # Real-time analysis
  │   └── middleware.py                # Auth, logging, CORS
  │   
  ├── deployment/
  │   ├── infra/                       # Azure infrastructure
  │   │   ├── main.bicep              # Azure resources
  │   │   └── parameters.json         # Deployment parameters
  │   ├── docker/
  │   │   └── Dockerfile              # Containerization
  │   └── azure.yaml                  # AZD configuration
  │   
  └── requirements.txt                 # Python dependencies
```

---

## ⚙️ **Core Technology Stack**

### **AI & ML Layer**
```yaml
Azure OpenAI:
  embedding_model: "text-embedding-ada-002"    # 1536 dimensions
  chat_model: "gpt-4"                          # Analysis & reasoning
  api_version: "2024-02-01"                    # Latest stable
  
LangChain Components:
  document_loaders: "PyMuPDFLoader, UnstructuredPDFLoader"
  text_splitters: "RecursiveCharacterTextSplitter, SemanticChunker"
  vectorstores: "FAISS (in-memory), Chroma (optional)"
  retrievers: "MultiQueryRetriever, EnsembleRetriever"
  agents: "CustomAgent, StructuredChatAgent"

LangGraph Orchestration:
  state_management: "TypedDict state graphs"
  agent_coordination: "Conditional routing & parallel execution"
  memory: "ConversationBufferWindowMemory"
```

### **Financial Processing**
```yaml
Document Processing:
  pdf_parsing: "PyMuPDF, pdfplumber, camelot-py"
  table_extraction: "tabula-py, pdfplumber"
  ocr_capability: "Azure AI Document Intelligence"
  
Financial Intelligence:
  calculation_engine: "pandas, numpy"
  data_validation: "Great Expectations"
  time_series: "pandas financial analysis"
```

### **Infrastructure & Deployment**
```yaml
Vector Storage:
  in_memory: "FAISS with pickle persistence"  # Fast startup
  scalable_option: "Azure AI Search"          # Production ready
  
API Framework:
  web_framework: "FastAPI"                    # High performance
  async_support: "asyncio, aiofiles"
  websocket: "Real-time analysis streaming"
  
Azure Services:
  compute: "Azure Container Apps"             # Serverless containers  
  storage: "Azure Blob Storage"               # Document storage
  security: "Azure Key Vault, Managed Identity"
  monitoring: "Azure Application Insights"
```

---

## 🔧 **Enhanced Configuration System**

### **settings.yaml**
```yaml
# System Configuration
app:
  name: "Annual Report Analyzer"
  version: "2.0.0"
  environment: "development"

# Document Processing
document_processing:
  max_file_size_mb: 50
  supported_formats: ["pdf"]
  extract_tables: true
  extract_charts: true
  ocr_enabled: true

# Chunking Strategy  
chunking:
  strategy: "semantic_adaptive"  # semantic_adaptive, recursive, fixed
  target_chunk_size: 1000
  chunk_overlap: 200
  min_chunk_size: 100
  semantic_similarity_threshold: 0.8

# Retrieval Configuration
retrieval:
  hybrid_search: true
  semantic_weight: 0.7
  keyword_weight: 0.3
  top_k_initial: 20
  top_k_final: 5
  reranking_enabled: true

# Financial Analysis
financial:
  currency_detection: true
  number_extraction: true
  ratio_calculations: ["ROE", "ROA", "debt_to_equity", "current_ratio"]
  yoy_analysis: true
  trend_detection: true
```

### **azure_config.yaml**
```yaml
# Azure OpenAI Configuration
azure_openai:
  endpoint: "${AZURE_OPENAI_ENDPOINT}"
  api_key: "${AZURE_OPENAI_API_KEY}"  # Use Managed Identity in production
  api_version: "2024-02-01"
  
  # Embedding Model
  embedding:
    deployment_name: "text-embedding-ada-002"
    model_name: "text-embedding-ada-002"
    chunk_size: 1000
    max_retries: 3
    timeout: 30
    
  # Chat Model  
  chat:
    deployment_name: "gpt-4"
    model_name: "gpt-4"
    max_tokens: 4000
    temperature: 0.1        # Low for factual analysis
    top_p: 0.9
    frequency_penalty: 0.0
    presence_penalty: 0.0

# Rate Limiting
rate_limits:
  requests_per_minute: 240
  tokens_per_minute: 40000
  concurrent_requests: 10
  backoff_factor: 2.0
```

---

## 🤖 **Multi-Agent System Design**

### **1. Document Processor Agent**
```python
class DocumentProcessorAgent:
    """Handles PDF ingestion and initial processing"""
    
    capabilities = [
        "PDF text extraction with layout preservation",
        "Financial table detection and parsing", 
        "Chart/graph OCR and data extraction",
        "Document structure analysis (sections, footnotes)",
        "Metadata extraction (filing date, company, period)"
    ]
    
    tools = [
        "PyMuPDF for text extraction",
        "pdfplumber for table parsing", 
        "Azure AI Document Intelligence for OCR",
        "Regular expressions for structure detection"
    ]
```

### **2. Financial Analysis Agent**
```python  
class FinancialAnalysisAgent:
    """Specialized in financial calculations and analysis"""
    
    capabilities = [
        "Automatic ratio calculations (ROE, ROA, margins)",
        "Year-over-year growth analysis",
        "Financial trend detection",
        "Cross-period comparisons",
        "Data consistency validation"
    ]
    
    financial_knowledge = [
        "GAAP accounting principles",
        "Financial statement relationships", 
        "Industry standard ratios",
        "Regulatory reporting requirements"
    ]
```

### **3. Query Router Agent**
```python
class QueryRouterAgent:
    """Intelligently routes queries to specialized agents"""
    
    routing_logic = {
        "financial_metrics": "FinancialAnalysisAgent",
        "risk_factors": "RiskAnalysisAgent", 
        "text_search": "SemanticSearchAgent",
        "multi_year_comparison": "ComparisonAgent",
        "regulatory_compliance": "ComplianceAgent"
    }
    
    query_classification = [
        "Entity extraction (companies, dates, metrics)",
        "Intent classification (search, calculate, compare)",
        "Complexity assessment (simple lookup vs. analysis)"
    ]
```

### **4. Response Synthesizer Agent**
```python
class ResponseSynthesizerAgent:
    """Combines multi-agent outputs into coherent responses"""
    
    synthesis_capabilities = [
        "Multi-source evidence integration",
        "Conflicting information resolution",
        "Citation formatting and validation", 
        "Confidence scoring",
        "Follow-up question suggestions"
    ]
```

---

## 🚀 **Implementation Architecture**

### **1. Azure OpenAI Integration**

```python
# src/azure/embedding_client.py
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import numpy as np
from typing import List, Dict

class AzureEmbeddingClient:
    """Secure Azure OpenAI embedding client with rate limiting"""
    
    def __init__(self, config: Dict):
        # Use Managed Identity for authentication
        credential = DefaultAzureCredential()
        
        self.client = AzureOpenAI(
            azure_endpoint=config["endpoint"],
            azure_ad_token_provider=credential.get_token("https://cognitiveservices.azure.com/.default"),
            api_version=config["api_version"]
        )
        
        self.deployment_name = config["embedding"]["deployment_name"]
        self.rate_limiter = RateLimiter(config["rate_limits"])
        
    async def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Get embeddings for text chunks with batching and retry logic"""
        embeddings = []
        
        # Process in batches to respect rate limits
        for batch in self._batch_texts(texts, batch_size=16):
            await self.rate_limiter.acquire()
            
            try:
                response = await self.client.embeddings.create(
                    input=batch,
                    model=self.deployment_name
                )
                
                batch_embeddings = [np.array(item.embedding) for item in response.data]
                embeddings.extend(batch_embeddings)
                
            except Exception as e:
                logger.error(f"Embedding error: {e}")
                # Implement exponential backoff retry
                embeddings.extend([np.zeros(1536)] * len(batch))
                
        return embeddings

# src/azure/chat_client.py  
class AzureChatClient:
    """GPT-4 client for financial analysis with structured outputs"""
    
    def __init__(self, config: Dict):
        credential = DefaultAzureCredential()
        
        self.client = AzureOpenAI(
            azure_endpoint=config["endpoint"],
            azure_ad_token_provider=credential.get_token("https://cognitiveservices.azure.com/.default"),
            api_version=config["api_version"]
        )
        
        self.deployment_name = config["chat"]["deployment_name"]
        self.default_params = config["chat"]
        
    async def analyze_financial_context(
        self, 
        context: str, 
        query: str,
        analysis_type: str = "general"
    ) -> Dict:
        """Analyze financial context with specialized prompts"""
        
        prompt = self._build_analysis_prompt(context, query, analysis_type)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": FINANCIAL_ANALYST_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.default_params["max_tokens"],
                temperature=self.default_params["temperature"],
                response_format={"type": "json_object"}  # Structured output
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Chat analysis error: {e}")
            return {"error": str(e), "fallback_response": True}
```

### **2. LangChain RAG Implementation**

```python
# src/rag/chunking_strategy.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import AzureOpenAIEmbeddings

class SmartChunkingStrategy:
    """Adaptive chunking based on document structure and semantics"""
    
    def __init__(self, azure_config: Dict):
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=azure_config["embedding"]["deployment_name"],
            azure_endpoint=azure_config["endpoint"],
            api_version=azure_config["api_version"]
        )
        
        # Different splitters for different content types
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        self.semantic_splitter = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=95
        )
        
    def chunk_financial_document(self, document: Document) -> List[Document]:
        """Smart chunking based on document section type"""
        
        sections = self._identify_sections(document.page_content)
        chunks = []
        
        for section_type, content in sections.items():
            if section_type == "financial_table":
                # Preserve table structure
                chunks.extend(self._chunk_table_content(content))
            elif section_type == "narrative_text":
                # Use semantic chunking for better context preservation
                chunks.extend(self.semantic_splitter.split_text(content))
            else:
                # Standard recursive chunking
                chunks.extend(self.text_splitter.split_text(content))
                
        return self._add_metadata(chunks, document)

# src/rag/vector_store.py
import faiss
import pickle
from pathlib import Path
from typing import List, Tuple

class FAISSVectorStore:
    """High-performance in-memory vector store with persistence"""
    
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner Product for cosine similarity
        self.documents = []
        self.metadata = []
        
    def add_documents(self, documents: List[Document], embeddings: List[np.ndarray]):
        """Add documents and their embeddings to the index"""
        
        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings_array)
        
        self.index.add(embeddings_array)
        self.documents.extend(documents)
        self.metadata.extend([doc.metadata for doc in documents])
        
    def similarity_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Document, float]]:
        """Semantic similarity search with scores"""
        
        query_vector = query_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_vector)
        
        scores, indices = self.index.search(query_vector, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid result
                results.append((self.documents[idx], float(score)))
                
        return results
        
    def save(self, path: str):
        """Persist vector store to disk"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, f"{path}/index.faiss")
        
        # Save documents and metadata
        with open(f"{path}/documents.pkl", "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "metadata": self.metadata
            }, f)
```

### **3. LangGraph Agent Orchestration**

```python
# src/orchestrator/workflow_graph.py
from langgraph import StateGraph, CompiledGraph
from typing import Dict, Any, List
from typing_extensions import TypedDict

class AnalysisState(TypedDict):
    """Shared state across all agents"""
    query: str
    document_path: str
    processed_chunks: List[Document]
    retrieval_results: List[Tuple[Document, float]]
    financial_calculations: Dict[str, Any]
    risk_analysis: Dict[str, Any] 
    final_answer: str
    citations: List[Dict[str, Any]]
    confidence_score: float

class FinancialAnalysisWorkflow:
    """LangGraph orchestrator for multi-agent financial analysis"""
    
    def __init__(self, agents: Dict[str, Any], config: Dict):
        self.agents = agents
        self.config = config
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> CompiledGraph:
        """Define the agent coordination workflow"""
        
        workflow = StateGraph(AnalysisState)
        
        # Add agent nodes
        workflow.add_node("document_processor", self._process_document)
        workflow.add_node("query_router", self._route_query)
        workflow.add_node("semantic_search", self._semantic_search)
        workflow.add_node("financial_analyzer", self._financial_analysis)
        workflow.add_node("risk_analyzer", self._risk_analysis)  
        workflow.add_node("response_synthesizer", self._synthesize_response)
        
        # Define workflow edges
        workflow.add_edge("document_processor", "query_router")
        workflow.add_conditional_edges(
            "query_router",
            self._route_decision,
            {
                "financial": "financial_analyzer",
                "risk": "risk_analyzer", 
                "general": "semantic_search"
            }
        )
        
        # Parallel execution for comprehensive analysis
        workflow.add_edge("financial_analyzer", "response_synthesizer")
        workflow.add_edge("risk_analyzer", "response_synthesizer")
        workflow.add_edge("semantic_search", "response_synthesizer")
        
        # Set entry and exit points
        workflow.set_entry_point("document_processor")
        workflow.set_finish_point("response_synthesizer")
        
        return workflow.compile()
        
    async def analyze(self, query: str, document_path: str) -> Dict[str, Any]:
        """Execute the complete analysis workflow"""
        
        initial_state = AnalysisState(
            query=query,
            document_path=document_path,
            processed_chunks=[],
            retrieval_results=[],
            financial_calculations={},
            risk_analysis={},
            final_answer="",
            citations=[],
            confidence_score=0.0
        )
        
        # Execute workflow
        result = await self.workflow.ainvoke(initial_state)
        
        return {
            "answer": result["final_answer"],
            "citations": result["citations"],
            "confidence": result["confidence_score"],
            "supporting_data": {
                "financial_calculations": result["financial_calculations"],
                "risk_analysis": result["risk_analysis"]
            }
        }
```

---

## 📊 **Advanced Financial Intelligence**

### **Financial Calculator**
```python
# src/financial/calculator.py
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class FinancialCalculator:
    """Automated financial ratio and growth calculations"""
    
    def __init__(self):
        self.standard_ratios = {
            "profitability": ["ROE", "ROA", "gross_margin", "operating_margin", "net_margin"],
            "liquidity": ["current_ratio", "quick_ratio", "cash_ratio"],
            "leverage": ["debt_to_equity", "debt_to_assets", "interest_coverage"],
            "efficiency": ["asset_turnover", "inventory_turnover", "receivables_turnover"]
        }
    
    def calculate_yoy_growth(self, current: float, previous: float) -> Dict[str, float]:
        """Calculate year-over-year growth metrics"""
        if previous == 0:
            return {"growth_rate": float('inf'), "absolute_change": current}
            
        growth_rate = (current - previous) / previous
        absolute_change = current - previous
        
        return {
            "growth_rate": growth_rate,
            "growth_percentage": growth_rate * 100,
            "absolute_change": absolute_change,
            "current_value": current,
            "previous_value": previous
        }
    
    def calculate_financial_ratios(self, financial_data: Dict[str, float]) -> Dict[str, float]:
        """Calculate standard financial ratios from extracted data"""
        ratios = {}
        
        # Profitability ratios
        if "net_income" in financial_data and "shareholders_equity" in financial_data:
            ratios["ROE"] = financial_data["net_income"] / financial_data["shareholders_equity"]
            
        if "net_income" in financial_data and "total_assets" in financial_data:
            ratios["ROA"] = financial_data["net_income"] / financial_data["total_assets"]
            
        # Add more ratio calculations...
        
        return ratios

# src/financial/comparator.py  
class MultiYearComparator:
    """Compare financial metrics across multiple reporting periods"""
    
    def compare_annual_reports(self, reports: List[Dict]) -> Dict[str, Any]:
        """Compare key metrics across multiple annual reports"""
        
        comparison = {
            "revenue_trend": [],
            "profitability_trend": [],
            "growth_analysis": {},
            "key_changes": []
        }
        
        # Sort reports by year
        sorted_reports = sorted(reports, key=lambda x: x["year"])
        
        # Calculate trends
        for i in range(1, len(sorted_reports)):
            current = sorted_reports[i]
            previous = sorted_reports[i-1]
            
            # Revenue growth
            if "revenue" in current and "revenue" in previous:
                growth = self.calculator.calculate_yoy_growth(
                    current["revenue"], 
                    previous["revenue"]
                )
                comparison["revenue_trend"].append({
                    "year": current["year"],
                    "growth": growth
                })
        
        return comparison
```

---

## 🔄 **Development & Deployment Pipeline**

### **requirements.txt**
```txt
# Core AI/ML
langchain>=0.1.0
langchain-openai>=0.1.0
langgraph>=0.0.40
openai>=1.12.0
faiss-cpu>=1.8.0
numpy>=1.24.0
pandas>=2.0.0

# PDF Processing
PyMuPDF>=1.23.0
pdfplumber>=0.10.0
camelot-py[cv]>=0.11.0
tabula-py>=2.8.0

# Azure Integration
azure-identity>=1.15.0
azure-keyvault-secrets>=4.7.0
azure-ai-documentintelligence>=1.0.0b1

# Web Framework
fastapi>=0.104.0
uvicorn>=0.24.0
websockets>=12.0

# Data Processing
great-expectations>=0.18.0
pydantic>=2.5.0
python-multipart>=0.0.6

# Development & Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
isort>=5.12.0
```

### **Docker Support**
```dockerfile
# deployment/docker/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ✅ **Key Design Improvements & Comments**

### **🎯 Technical Excellence**
1. **Azure OpenAI Best Practices** - Managed Identity auth, rate limiting, retry logic
2. **Smart Chunking** - Semantic + structure-aware chunking for better context
3. **Multi-Agent Architecture** - Specialized agents for different analysis types
4. **Financial Intelligence** - Built-in calculations, ratio analysis, YoY comparisons
5. **Hybrid Retrieval** - Semantic (FAISS) + keyword search fusion

### **🔒 Security & Production Readiness**
1. **No hardcoded credentials** - Azure Managed Identity + Key Vault
2. **Rate limiting & error handling** - Robust API quota management  
3. **Input validation** - Comprehensive data validation pipeline
4. **Structured logging** - Azure Application Insights integration
5. **Container-ready** - Docker support for easy deployment

### **📈 Performance & Scalability**
1. **In-memory FAISS** - Fast vector similarity search
2. **Async operations** - Non-blocking I/O for better throughput
3. **Batch processing** - Efficient embedding generation
4. **Caching strategy** - Persist processed documents and embeddings
5. **Azure Container Apps** - Serverless auto-scaling

### **🛠️ Alternative Tech Stack Considerations**

**Vector Database Options:**
- **Current**: FAISS (in-memory) - Fast, simple, good for single PDF
- **Scale-up**: Azure AI Search - Production-grade, hybrid search, managed
- **Alternative**: Pinecone, Weaviate - Specialized vector databases

**LLM Framework Alternatives:**
- **Current**: LangChain + LangGraph - Rich ecosystem, good abstraction
- **Alternative**: Haystack - More control, pipeline-focused
- **Lightweight**: Direct OpenAI API calls - Less abstraction, more control

**Document Processing:**
- **Current**: PyMuPDF + pdfplumber - Good balance of speed/accuracy
- **Advanced**: Azure AI Document Intelligence - Superior table/form extraction
- **Alternative**: Unstructured.io - Better layout understanding

Would you like me to implement any specific component first or create the initial project structure?
    chunk_size: 1000
    max_retries: 3
    timeout: 30
    
  # Chat Model  
  chat:
    deployment_name: "gpt-4"
    model_name: "gpt-4"
    max_tokens: 4000
    temperature: 0.1        # Low for factual analysis
    top_p: 0.9
    frequency_penalty: 0.0
    presence_penalty: 0.0

# Rate Limiting
rate_limits:
  requests_per_minute: 240
  tokens_per_minute: 40000
  concurrent_requests: 10
  backoff_factor: 2.0
```

---

## 🤖 **Multi-Agent System Design**

### **1. Document Processor Agent**
```python
class DocumentProcessorAgent:
    """Handles PDF ingestion and initial processing"""
    
    capabilities = [
        "PDF text extraction with layout preservation",
        "Financial table detection and parsing", 
        "Chart/graph OCR and data extraction",
        "Document structure analysis (sections, footnotes)",
        "Metadata extraction (filing date, company, period)"
    ]
    
    tools = [
        "PyMuPDF for text extraction",
        "pdfplumber for table parsing", 
        "Azure AI Document Intelligence for OCR",
        "Regular expressions for structure detection"
    ]
```

### **2. Financial Analysis Agent**
```python  
class FinancialAnalysisAgent:
    """Specialized in financial calculations and analysis"""
    
    capabilities = [
        "Automatic ratio calculations (ROE, ROA, margins)",
        "Year-over-year growth analysis",
        "Financial trend detection",
        "Cross-period comparisons",
        "Data consistency validation"
    ]
    
    financial_knowledge = [
        "GAAP accounting principles",
        "Financial statement relationships", 
        "Industry standard ratios",
        "Regulatory reporting requirements"
    ]
```

### **3. Query Router Agent**
```python
class QueryRouterAgent:
    """Intelligently routes queries to specialized agents"""
    
    routing_logic = {
        "financial_metrics": "FinancialAnalysisAgent",
        "risk_factors": "RiskAnalysisAgent", 
        "text_search": "SemanticSearchAgent",
        "multi_year_comparison": "ComparisonAgent",
        "regulatory_compliance": "ComplianceAgent"
    }
    
    query_classification = [
        "Entity extraction (companies, dates, metrics)",
        "Intent classification (search, calculate, compare)",
        "Complexity assessment (simple lookup vs. analysis)"
    ]
```

### **4. Response Synthesizer Agent**
```python
class ResponseSynthesizerAgent:
    """Combines multi-agent outputs into coherent responses"""
    
    synthesis_capabilities = [
        "Multi-source evidence integration",
        "Conflicting information resolution",
        "Citation formatting and validation", 
        "Confidence scoring",
        "Follow-up question suggestions"
    ]
```

---

# 2) Ingestion (PDF → pages)

```pseudo
# rag/ingest.pseudo
function load_pdfs(pdf_folder: String) -> List[Page]:
  pages = []
  for each path in list_files(pdf_folder, pattern="*.pdf"):
    try:
      doc = open_pdf(path)  # PyMuPDF or similar
      for i in range(doc.num_pages):
        raw = doc.page(i).get_text("text")
        if raw is not empty:
          pages.append({ file: basename(path), page: i, text: raw })
      close_pdf(doc)
    catch e:
      log_warn("Failed: " + path + " err=" + e)
  return pages

# --- Dummy data example (simulate ingestion result) ---
DUMMY_PAGES = [
  { file: "ACME_2024_AR.pdf", page: 0,
    text: "ACME Corporation Annual Report 2024. Total revenue was $5.2 billion, up 8% YoY." },
  { file: "ACME_2024_AR.pdf", page: 1,
    text: "Risk factors include supply chain disruptions and FX volatility." },
  { file: "ACME_2023_AR.pdf", page: 0,
    text: "ACME Corporation Annual Report 2023. Total revenue was $4.8 billion." }
]
```

---

# 3) Preprocess (cleaning, normalization)

```pseudo
# rag/preprocess.pseudo
function normalize_whitespace(s: String) -> String:
  return replace_regex(s, pattern="\s+", by=" ").trim()

function preprocess_pages(pages: List[Page]) -> List[Page]:
  for each p in pages:
    p.text = normalize_whitespace(p.text)
  return pages

# --- Dummy transformation ---
# "ACME   2024.\nRevenue  $5.2B " -> "ACME 2024. Revenue $5.2B"
```

---

# 4) Chunking (sentences → chunks)

```pseudo
# rag/chunk.pseudo
function split_sentences(text: String) -> List[String]:
  # naive split on .?! followed by space
  return regex_split(text, "(?<=[.?!])\s+")

function make_chunks(pages: List[Page],
                     target_chars: Int,
                     overlap_chars: Int) -> List[Chunk]:
  chunks = []
  for each p in pages:
    sents = split_sentences(p.text)
    buf = ""
    for each s in sents:
      if length(buf + s) > target_chars and buf != "":
        chunks.append({
          id: hash(p.file + ":" + p.page + ":" + buf[:50]),
          file: p.file, page_start: p.page, page_end: p.page, text: buf.trim()
        })
        # overlap tail
        if overlap_chars > 0 and length(buf) > overlap_chars:
          buf = substring(buf, length(buf) - overlap_chars, overlap_chars) + " "
        else:
          buf = ""
      buf = buf + s + " "
    if buf.trim() != "":
      chunks.append({
        id: hash(p.file + ":" + p.page + ":" + buf[:50]),
        file: p.file, page_start: p.page, page_end: p.page, text: buf.trim()
      })
  return unique(chunks)  # dedupe by (file, page range, text prefix)

# --- Dummy chunks result ---
DUMMY_CHUNKS = [
  { id: "c1", file: "ACME_2024_AR.pdf", page_start: 1, page_end: 1,
    text: "Risk factors include supply chain disruptions and FX volatility." },
  { id: "c2", file: "ACME_2024_AR.pdf", page_start: 0, page_end: 0,
    text: "ACME Corporation Annual Report 2024. Total revenue was $5.2 billion, up 8% YoY." },
  { id: "c3", file: "ACME_2023_AR.pdf", page_start: 0, page_end: 0,
    text: "ACME Corporation Annual Report 2023. Total revenue was $4.8 billion." }
]
```

---

# 5) Index (Baseline: BM25 Sparse)

```pseudo
# rag/index.pseudo
function tokenize(text: String) -> List[String]:
  return regex_findall(text.lower(), "[a-z0-9]+(?:['-][a-z0-9]+)?")

class BM25Index:
  init(chunks: List[Chunk]):
    self.docs = [tokenize(c.text) for c in chunks]
    self.meta = chunks  # keep chunk association
    self.N = len(self.docs)
    self.doc_len = [len(d) for d in self.docs]
    self.avgdl = average(self.doc_len)
    self.df = compute_doc_frequency(self.docs)
    self.idf = compute_bm25_idf(self.N, self.df)
    self.k1 = 1.5
    self.b = 0.75

  function score(q_tokens: List[String], doc_id: Int) -> Float:
    tf = term_counts(self.docs[doc_id])
    dl = self.doc_len[doc_id]
    s = 0
    for t in q_tokens:
      if t not in tf: continue
      f = tf[t]
      idf = self.idf.get(t, 0)
      denom = f + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
      s += idf * (f * (self.k1 + 1)) / max(denom, 1e-9)
    return s

  function retrieve(query: String, top_k: Int) -> List[RetrievalResult]:
    q_tokens = tokenize(query)
    scored = []
    for i in range(self.N):
      s = self.score(q_tokens, i)
      if s > 0: scored.append({ chunk: self.meta[i], score: s })
    return sort_desc(scored, key=score)[:top_k]

# --- Dummy BM25 outcome for query "What was revenue in 2024?" ---
DUMMY_RETRIEVAL = [
  { chunk: DUMMY_CHUNKS[1], score: 3.21 },  # mentions "2024" + "revenue"
  { chunk: DUMMY_CHUNKS[2], score: 1.85 }   # 2023 revenue (context)
]
```

> *We’ll add embeddings/hybrid search in a later iteration.*

---

# 6) (Optional) Reranker

```pseudo
# rag/rerank.pseudo
# Stub that could use lexical + lightweight semantic signals
function rerank(results: List[RetrievalResult], query: String) -> List[RetrievalResult]:
  # baseline: return as-is
  return results

# --- Dummy ---
DUMMY_RERANKED = DUMMY_RETRIEVAL
```

---

# 7) Context Builder (for LLM or extractive)

```pseudo
# rag/context.pseudo
function build_context(results: List[RetrievalResult], max_chars: Int = 6000) -> String:
  buf = ""
  for r in results:
    snippet = "[" + r.chunk.file + " p." + (r.chunk.page_start + 1) + "]\n" +
              r.chunk.text + "\n\n"
    if length(buf) + length(snippet) > max_chars: break
    buf = buf + snippet
  return buf

# --- Dummy context ---
DUMMY_CONTEXT = """
[ACME_2024_AR.pdf p.1]
ACME Corporation Annual Report 2024. Total revenue was $5.2 billion, up 8% YoY.

[ACME_2023_AR.pdf p.1]
ACME Corporation Annual Report 2023. Total revenue was $4.8 billion.
"""
```

---

# 8) Answerers

### 8a) Extractive (baseline, no LLM)

```pseudo
# rag/answer.pseudo
function extractive_answer(query: String,
                           results: List[RetrievalResult],
                           max_sentences: Int = 3) -> Answer:
  q_tokens = set(tokenize(query))
  candidates = []
  for r in results:
    sents = split_sentences(r.chunk.text)
    for s in sents:
      t = set(tokenize(s))
      if size(t) == 0: continue
      overlap = size(q_tokens ∩ t) / max(size(q_tokens ∪ t), 1)
      if overlap > 0:
        candidates.append({ sent: s, overlap: overlap, chunk: r.chunk })
  sorted_cands = sort_desc(candidates, key=overlap)[:max_sentences]
  if empty(sorted_cands):
    return { text: "Not found in context. Try rephrasing.",
             citations: [] }
  # format with citations
  lines = []
  cites = []
  for c in sorted_cands:
    lines.append("- " + c.sent + " (Source: " + c.chunk.file +
                 ", p." + (c.chunk.page_start + 1) + ")")
    cites.append({ file: c.chunk.file, page: c.chunk.page_start + 1 })
  return { text: join(lines, "\n"), citations: unique(cites) }

# --- Dummy extractive answer for query "What was revenue in 2024?" ---
DUMMY_EXTRACTIVE_ANSWER = {
  text: "- Total revenue was $5.2 billion, up 8% YoY. (Source: ACME_2024_AR.pdf, p.1)",
  citations: [{ file: "ACME_2024_AR.pdf", page: 1 }]
}
```

### 8b) Generative (LLM-ready prompt)

```pseudo
# rag/answer.pseudo
GEN_PROMPT = """
You are a financial analysis assistant. Answer strictly using the provided context.
If the answer is not present, say you don't know. Cite as (filename, p.X).

# Question
{QUESTION}

# Context
{CONTEXT}

# Instructions
- Be concise and numeric when possible (currency and units).
- Include citations inline.
"""

function build_llm_prompt(query: String, context: String) -> String:
  return replace(GEN_PROMPT, {
    "{QUESTION}": query,
    "{CONTEXT}": context
  })

# --- Dummy prompt snippet ---
DUMMY_PROMPT = build_llm_prompt(
  "What was revenue in 2024?",
  DUMMY_CONTEXT
)
```

---

# 9) Retriever (wrapper)

```pseudo
# rag/retrieve.pseudo
class Retriever:
  init(index): self.index = index
  function topk(query: String, k: Int) -> List[RetrievalResult]:
    return self.index.retrieve(query, top_k=k)

# --- Dummy wiring ---
DUMMY_INDEX = BM25Index(DUMMY_CHUNKS)
DUMMY_RETRIEVER = Retriever(DUMMY_INDEX)
```

---

# 10) Orchestrator (end-to-end)

```pseudo
# rag/orchestrator.pseudo
class RAGSystem:
  init(config):
    self.config = config
    pages = load_pdfs(config.PDF_FOLDER)
    pages = preprocess_pages(pages)
    self.chunks = make_chunks(
      pages,
      config.CHUNK_TARGET_CHARS,
      config.CHUNK_OVERLAP_CHARS
    )
    self.index = BM25Index(self.chunks)
    self.retriever = Retriever(self.index)

  function answer(query: String) -> Answer:
    results = self.retriever.topk(query, self.config.RETRIEVAL_TOP_K)
    results = rerank(results, query)  # no-op baseline

    if self.config.MODE == "extractive":
      return extractive_answer(query, results)
    else:
      ctx = build_context(results)
      prompt = build_llm_prompt(query, ctx)
      # send to LLM (out of scope for pseudo)
      llm_text = call_llm(prompt)  # TODO
      cits = [{file: r.chunk.file, page: r.chunk.page_start + 1} for r in results]
      return { text: llm_text, citations: cits }

# --- Dummy run ---
RAG = RAGSystem(CONFIG)
ANSWER = RAG.answer("What was revenue in 2024?")
# -> should resemble DUMMY_EXTRACTIVE_ANSWER
```

---

# 11) Persistence / Cache (stubs)

```pseudo
# rag/index.pseudo (continued)
function persist_chunks(chunks: List[Chunk], path: String):
  write_json(path, chunks)

function load_chunks(path: String) -> List[Chunk]:
  if file_exists(path): return read_json(path)
  else: return []

# TODO: cache tokenized docs, DF/IDF if needed
```

---

# 12) Evaluation Stubs

```pseudo
# rag/eval.pseudo
# Simple accuracy-like check against known answers
type QAItem = { query: String, must_contain: List[String] }

function evaluate(rag: RAGSystem, dataset: List[QAItem]) -> Dict:
  hits = 0
  for each item in dataset:
    ans = rag.answer(item.query)
    txt = lowercase(ans.text)
    ok = all(lowercase(key) in txt for key in item.must_contain)
    if ok: hits += 1
  return { total: len(dataset), correct: hits, accuracy: hits / len(dataset) }

# --- Dummy eval set ---
EVAL_SET = [
  { query: "What was revenue in 2024?", must_contain: ["$5.2", "2024"] },
  { query: "List one risk factor.", must_contain: ["risk", "supply"] }
]
```

---

# 13) Simple CLI / API (stub)

```pseudo
# api/app.pseudo
function main():
  rag = RAGSystem(CONFIG)
  print("Ready. Type your question (exit to quit).")
  while True:
    q = read_stdin("> ")
    if q in ["exit", "quit", ""]: break
    ans = rag.answer(q)
    print("\n=== Answer ===")
    print(ans.text)
    print("\n=== Citations ===")
    for c in ans.citations:
      print("- " + c.file + " p." + c.page)
    print("\n")
```

---

## ✅ What You Now Have
- Clear **module boundaries** and **data structures**.
- **Pseudo-code** for each step (ingestion → normalization → chunking → indexing → retrieval → context → answering → orchestration).
- **Dummy data** to visualize outputs at each stage.
- Hooks for **LLM**, **reranking**, **caching**, and **evaluation**.

---

## 🔜 Suggested Next Enhancements (pick one and I’ll draft the code)

1. **Hybrid Retrieval**: BM25 + embeddings with late-fusion scoring.
2. **Table Parsing**: Detect/parse financial tables (revenues, margins) for precise numeric QA.
3. **Computation Layer**: Auto compute YoY growth, margins, CAGR with source-backed numbers.
4. **Persistence**: Save/load index and chunks to skip reprocessing.
5. **UI**: Minimal Streamlit app with answers and page-level citations.

Which one would you like to implement first? I can convert the relevant pseudo‑code into runnable Python next.