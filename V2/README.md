# AI Agent System - Document Generation & API Integration

A comprehensive AI-powered agent system that performs prompt-based tasks including web search, API integration, and professional PDF document generation with a focus on Australian liquidation documents.

## 🚀 Features

- **LLM Integration**: Secure OpenAI GPT-4.1 API integration with memory cleanup
- **Web Search**: Multi-engine search (Google, DuckDuckGo, Wikipedia) with fallback
- **PDF Generation**: Professional document generation with Australian legal templates
- **Document Validation**: AI-powered compliance checking and validation
- **Async Processing**: High-performance concurrent task execution
- **Security-First**: Zero-knowledge encryption principles with no persistent storage

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main.py       │    │   AI Agent      │    │   LLM Service   │
│   Entry Point   │───▶│   Orchestrator  │───▶│   (GPT-4.1)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
              ┌──────────┐ ┌────────┐ ┌─────────────┐
              │Web Search│ │PDF Gen │ │ Validation  │
              │ Service  │ │Service │ │ Pipeline    │
              └──────────┘ └────────┘ └─────────────┘
```

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Optional: SerpAPI key for enhanced Google search

## 🛠️ Installation

1. **Clone and setup:**
```bash
git clone <repository>
cd AI-agent
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
# Set environment variables or create .env file
export OPENAI_API_KEY="your_openai_api_key_here"
export SERPAPI_API_KEY="your_serpapi_key_here"  # Optional
```

## ⚡ Quick Start

### Basic Usage

```python
from agent.ai_agent import AIAgent
from agent.config import Config
import asyncio

async def main():
    config = Config()
    agent = AIAgent(config)
    
    prompt = """
    As a Liquidity tester generate 5 PDF documents for liquidity notification 
    as a lawyer for various organizations. Validate and generate various types 
    of documents for different customers.
    """
    
    result = await agent.process_prompt(prompt)
    print(f"Generated {result.generated_documents['total_generated']} documents")

asyncio.run(main())
```

### Command Line Usage

```bash
python main.py
```

## 📄 Document Types Supported

### Australian Liquidation Documents
- **Liquidation Resolution**: Voluntary liquidation resolutions
- **Creditor Notification**: Creditor notification letters
- **Liquidator Appointment Notice**: Official appointment documentation
- **Director Statement**: Director's statement as to affairs
- **Asset Realization Notice**: Asset sale notifications

### Document Features
- ✅ Australian Corporations Act 2001 compliance
- ✅ Professional legal formatting
- ✅ ASIC regulatory guidelines adherence
- ✅ Automatic validation and compliance checking
- ✅ Professional PDF generation with templates

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | - | ✅ |
| `OPENAI_MODEL` | Model to use | `gpt-4.1` | ❌ |
| `SERPAPI_API_KEY` | SerpAPI key for Google search | - | ❌ |
| `PDF_OUTPUT_DIR` | PDF output directory | `./output` | ❌ |
| `ENABLE_VALIDATION` | Enable document validation | `true` | ❌ |
| `MAX_CONCURRENT_TASKS` | Max concurrent tasks | `5` | ❌ |

### Example Configuration

```python
from agent.config import Config

config = Config()
print(config)  # Display configuration
config.validate_config()  # Validate required settings
```

## 🚀 Usage Examples

### Example 1: Liquidation Document Generation

```python
prompt = """
Generate liquidation documents for ABC Pty Ltd including:
- Liquidation resolution
- Creditor notification
- Director statement
Ensure Australian legal compliance.
"""

result = await agent.process_prompt(prompt)
```

### Example 2: Research + Document Generation

```python
prompt = """
Research current Australian liquidation procedures and generate 
a comprehensive liquidator appointment notice for XYZ Corporation.
Include recent regulatory updates.
"""

result = await agent.process_prompt(prompt)
# Result includes both search results and generated documents
```

### Example 3: Multiple Organizations

```python
prompt = """
Generate creditor notifications for the following companies:
1. Tech Solutions Pty Ltd
2. Manufacturing Corp Australia
3. Retail Enterprises Ltd
"""

result = await agent.process_prompt(prompt)
```

## 📊 Response Structure

```python
@dataclass
class AgentResponse:
    prompt: str                    # Original prompt
    analysis: Dict[str, Any]       # Prompt analysis
    search_results: Optional[Dict] # Web search results
    generated_documents: Optional[List] # Generated documents
    task_results: List[TaskResult] # Individual task results
    total_execution_time: float    # Total time taken
    success: bool                  # Overall success status
    error: Optional[str]           # Error message if failed
```

## 🔍 Web Search Capabilities

### Supported Search Engines
- **Google** (via SerpAPI - requires key)
- **DuckDuckGo** (free, no key required)
- **Wikipedia** (fallback search)

### Search Features
- Automatic engine fallback
- Concurrent multi-query search
- Relevance scoring
- Result consolidation

## 📄 PDF Generation

### Templates Available
- **Liquidation Template**: Australian liquidation documents
- **Legal Template**: General legal documents
- **General Template**: Standard business documents

### PDF Features
- Professional formatting
- Legal compliance
- Signature blocks
- Watermarks and headers
- Multi-page support

### Fallback Options
If ReportLab is unavailable, the system automatically falls back to formatted text documents.

## 🛡️ Security Features

- **No Persistent Storage**: API keys never stored permanently
- **Memory Cleanup**: Automatic cleanup of sensitive data
- **Secure Sessions**: HTTPS-only API communications
- **Error Handling**: Comprehensive error handling without data leakage
- **Zero-Knowledge**: No data retention between sessions

## 🧪 Testing

```bash
# Run basic tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=agent tests/

# Test specific functionality
python -m pytest tests/test_llm_client.py
```

## 📈 Performance Optimization

### Concurrent Processing
- Parallel document generation
- Concurrent web searches
- Async PDF creation
- Non-blocking operations

### Memory Management
- Automatic cleanup
- Session management
- Resource pooling
- Timeout handling

## 🐛 Troubleshooting

### Common Issues

**1. OpenAI API Key Issues**
```bash
Error: API request failed: 401
Solution: Verify OPENAI_API_KEY is correctly set
```

**2. PDF Generation Fails**
```bash
Error: ReportLab not available
Solution: pip install reportlab>=4.0.0
```

**3. Search Engine Failures**
```bash
Warning: All search engines failed
Solution: Check internet connection, try with SerpAPI key
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run agent with debug logging
result = await agent.process_prompt(prompt)
```

## 🔄 Development

### Project Structure
```
AI-agent/
├── agent/
│   ├── __init__.py
│   ├── ai_agent.py          # Main agent orchestrator
│   ├── config.py            # Configuration management
│   ├── llm_client.py        # LLM API integration
│   ├── web_search.py        # Web search service
│   └── pdf_generator.py     # PDF generation
├── templates/
│   └── liquidation_template.py # Document templates
├── output/                  # Generated documents
├── logs/                    # Log files
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Adding New Document Types

1. Create template in `templates/`
2. Add to `LiquidationTemplates` class
3. Update `get_template_by_type()` function
4. Test with validation pipeline

### Adding New Search Engines

1. Implement search method in `WebSearchService`
2. Add to `_search_engines` dictionary
3. Test fallback behavior

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check troubleshooting section
- Review configuration documentation

## 🎯 Roadmap

- [ ] Additional document templates
- [ ] Enhanced validation rules
- [ ] Database integration
- [ ] Web interface
- [ ] API endpoint exposure
- [ ] Multi-language support
- [ ] Advanced PDF styling

---

**Built with security and compliance in mind for professional legal document generation.** 