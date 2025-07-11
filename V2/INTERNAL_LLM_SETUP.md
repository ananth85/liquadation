# Internal LLM Integration Guide

This guide explains how to configure and use internally hosted LLM models as an alternative or fallback to OpenAI APIs.

## Overview

The system now supports multiple LLM providers with automatic fallback:
- **OpenAI API** (primary, if configured)
- **Internal LLM** (self-hosted models like Llama, Mistral, etc.)
- **Automatic Fallback** (switches providers when primary fails)

## Configuration

### Environment Variables

Add these settings to your `.env` file:

```bash
# Internal LLM Configuration
INTERNAL_LLM_ENABLED=true
INTERNAL_LLM_API_BASE=http://localhost:8000/v1
INTERNAL_LLM_API_KEY=your_internal_llm_key_here
INTERNAL_LLM_MODEL=llama2-70b-chat
INTERNAL_LLM_MAX_TOKENS=4000
INTERNAL_LLM_TEMPERATURE=0.3
INTERNAL_LLM_TIMEOUT=60

# Provider Selection
PRIMARY_LLM_PROVIDER=openai          # or 'internal'
AUTO_FALLBACK_ENABLED=true
FALLBACK_RETRY_ATTEMPTS=2
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `INTERNAL_LLM_ENABLED` | Enable internal LLM support | `true` |
| `INTERNAL_LLM_API_BASE` | Base URL for internal LLM API | `http://localhost:8000/v1` |
| `INTERNAL_LLM_API_KEY` | API key for internal LLM | `your_internal_llm_key_here` |
| `INTERNAL_LLM_MODEL` | Model name to use | `llama2-70b-chat` |
| `INTERNAL_LLM_MAX_TOKENS` | Maximum tokens per request | `4000` |
| `INTERNAL_LLM_TEMPERATURE` | Response creativity (0.0-1.0) | `0.3` |
| `INTERNAL_LLM_TIMEOUT` | Request timeout in seconds | `60` |
| `PRIMARY_LLM_PROVIDER` | Primary provider ('openai' or 'internal') | `openai` |
| `AUTO_FALLBACK_ENABLED` | Enable automatic fallback | `true` |
| `FALLBACK_RETRY_ATTEMPTS` | Number of retry attempts | `2` |

## Use Cases

### 1. OpenAI with Internal Fallback
```bash
PRIMARY_LLM_PROVIDER=openai
AUTO_FALLBACK_ENABLED=true
```
- Uses OpenAI as primary
- Falls back to internal LLM if OpenAI fails

### 2. Internal LLM as Primary
```bash
PRIMARY_LLM_PROVIDER=internal
AUTO_FALLBACK_ENABLED=true
```
- Uses internal LLM as primary
- Falls back to OpenAI if internal LLM fails

### 3. Internal LLM Only
```bash
PRIMARY_LLM_PROVIDER=internal
AUTO_FALLBACK_ENABLED=false
OPENAI_API_KEY=not_configured
```
- Uses only internal LLM
- No fallback to external APIs

## Setting Up Internal LLM Servers

### Option 1: vLLM Server
```bash
# Install vLLM
pip install vllm

# Start server
python -m vllm.entrypoints.openai.api_server \
    --model microsoft/DialoGPT-large \
    --host 0.0.0.0 \
    --port 8000
```

### Option 2: Ollama with OpenAI API
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Run model
ollama run llama2:70b-chat

# Start OpenAI-compatible API server
ollama serve --host 0.0.0.0 --port 8000
```

### Option 3: Text Generation WebUI
```bash
# Clone repository
git clone https://github.com/oobabooga/text-generation-webui.git
cd text-generation-webui

# Install dependencies
pip install -r requirements.txt

# Start with OpenAI API extension
python server.py --extensions openai --api-port 8000
```

## Usage Examples

### Basic Usage
The system automatically handles provider selection and fallback:

```python
from agent.llm_client import LLMClient
from agent.config import Config

config = Config()

async with LLMClient(config) as client:
    response = await client.generate_response(
        prompt="Generate a legal document",
        max_tokens=1000
    )
    print(f"Response from {client.get_current_provider()}: {response.content}")
```

### Manual Provider Switching
```python
async with LLMClient(config) as client:
    # Check available providers
    providers = client.get_available_providers()
    print(f"Available: {providers}")
    
    # Switch provider manually
    success = await client.switch_provider('internal')
    if success:
        print("Switched to internal LLM")
    
    # Make request
    response = await client.generate_response("Hello world")
```

### Service Level Usage
```python
from agent.llm_client import LLMService

service = LLMService(config)

# Analyze prompt (automatically handles provider fallback)
analysis = await service.analyze_prompt("Generate liquidation documents")

# Generate document content
content = await service.generate_document_content(
    document_type="affidavit",
    context={"company": "Tech Corp"},
    organization="Legal Firm"
)
```

## Testing

Run the internal LLM test suite:

```bash
cd tests
python test_internal_llm.py
```

This tests:
- Provider detection and availability
- Manual provider switching
- Automatic fallback functionality
- Integration with LLM service

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Error: API request failed (internal): Connection refused
   ```
   - Check that internal LLM server is running
   - Verify `INTERNAL_LLM_API_BASE` URL is correct

2. **Authentication Failed**
   ```
   Error: API request failed (internal): 401 - Unauthorized
   ```
   - Check `INTERNAL_LLM_API_KEY` is correct
   - Some servers don't require API keys - try empty string

3. **Model Not Found**
   ```
   Error: Model 'llama2-70b-chat' not found
   ```
   - Verify model name matches server configuration
   - Check available models at `/v1/models` endpoint

4. **Timeout Issues**
   ```
   Error: Request timeout
   ```
   - Increase `INTERNAL_LLM_TIMEOUT` value
   - Check server performance and load

### Debug Mode

Enable debug logging to troubleshoot:

```bash
LOG_LEVEL=DEBUG
DEVELOPMENT_MODE=true
```

## Security Considerations

1. **API Keys**: Store internal LLM API keys securely
2. **Network**: Use HTTPS for production deployments
3. **Access Control**: Implement proper authentication on internal LLM servers
4. **Data Privacy**: Internal LLMs keep data on-premises
5. **Fallback Behavior**: Consider data sensitivity when enabling fallback to external APIs

## Benefits

- **Cost Control**: Reduce reliance on paid external APIs
- **Data Privacy**: Keep sensitive data on internal infrastructure
- **Reliability**: Fallback ensures system availability
- **Customization**: Use specialized models for legal document generation
- **Performance**: Lower latency with local deployment
- **Compliance**: Meet regulatory requirements for data handling 