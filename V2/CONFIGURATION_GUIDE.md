# Configuration Guide 🔧

**Professional AI Agent System - Environment Configuration**

## Quick Setup

### 1. **Create Configuration File**
```bash
# Run the setup script
python setup_env.py

# Or manually copy the template
cp config_template.env .env
```

### 2. **Edit Your API Keys**
Open `.env` file and update:
```bash
# Required for full functionality
OPENAI_API_KEY=your_actual_openai_api_key_here

# Optional for enhanced web search
SERPAPI_API_KEY=your_actual_serpapi_key_here
```

### 3. **Test Configuration**
```bash
# Test the configuration
python -c "from agent.config import Config; print(Config())"

# Test PDF generation
python test_professional_pdf.py
```

## 📋 Configuration Categories

### 🔑 **API Keys (Required)**
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1
OPENAI_TEMPERATURE=0.3

# Search APIs (Optional)
SERPAPI_API_KEY=your_serpapi_key_here
```

### 🤖 **Agent Settings**
```bash
# Identity
AGENT_NAME=Professional Legal AI Agent
AGENT_VERSION=2.0.0

# Behavior
MAX_RETRIES=3
REQUEST_TIMEOUT=30
MEMORY_CLEANUP_ENABLED=true
```

### 📄 **Document Generation**
```bash
# PDF Settings
PDF_OUTPUT_DIR=output
PDF_PAGE_SIZE=A4
PDF_FONT_FAMILY=Helvetica
PDF_FONT_SIZE_BODY=10

# Quality Features
INCLUDE_FINANCIAL_SCHEDULES=true
INCLUDE_LEGAL_CLAUSES=true
FEDERAL_COURT_FORMATTING=true
```

### ⚖️ **Legal Framework**
```bash
# Australian Legal Settings
CORPORATIONS_ACT_YEAR=2001
JURISDICTION=Australia
COURT_TYPE=Federal Court of Australia

# Compliance
ASIC_COMPLIANCE_ENABLED=true
LIQUIDATOR_REGISTRATION_REQUIRED=true
```

### 💰 **Financial Calculations**
```bash
# Currency
CURRENCY_SYMBOL=AUD $
FINANCIAL_ROUNDING=2

# Asset Realization Factors
ASSET_REALIZATION_FACTOR_CASH=1.00
ASSET_REALIZATION_FACTOR_DEBTORS=0.80
ASSET_REALIZATION_FACTOR_INVENTORY=0.60
ASSET_REALIZATION_FACTOR_PLANT=0.40
```

### 🔍 **Search & Research**
```bash
# Search Configuration
SEARCH_MAX_RESULTS=10
SEARCH_ENGINES=google,duckduckgo,wikipedia

# Legal Research
LEGAL_RESEARCH_ENABLED=true
CURRENT_LAW_RESEARCH=true
```

### 📊 **Logging & Monitoring**
```bash
# Logging
LOG_LEVEL=INFO
LOG_FILE=professional_agent.log
CONSOLE_LOG_ENABLED=true

# Performance
PERFORMANCE_MONITORING=true
EXECUTION_TIME_TRACKING=true
```

### 🔒 **Security Settings**
```bash
# Data Protection
ZERO_PERSISTENT_STORAGE=true
MEMORY_CLEANUP_AFTER_USE=true
API_KEY_MASKING=true

# Network
VERIFY_SSL_CERTIFICATES=true
CONNECTION_TIMEOUT=30
```

## 🎯 **Professional Features**

### Document Types
```bash
# Enable/Disable Document Types
GENERATE_PROFESSIONAL_AFFIDAVIT=true
GENERATE_LIQUIDATION_RESOLUTION=true
GENERATE_CREDITOR_NOTIFICATION=true
GENERATE_DIRECTOR_STATEMENT=true
GENERATE_ASSET_REALIZATION_NOTICE=true
```

### Quality Assurance
```bash
FEDERAL_COURT_COMPLIANCE_CHECK=true
FINANCIAL_CALCULATION_VALIDATION=true
LEGAL_CLAUSE_VERIFICATION=true
PROFESSIONAL_FORMATTING_CHECK=true
```

### Customer Management
```bash
CUSTOMER_PROFILE_GENERATION=true
INDUSTRY_SPECIFIC_ANALYSIS=true
CONTACT_MANAGEMENT=true
SPECIAL_REQUIREMENTS_TRACKING=true
```

## 🛠️ **Development & Testing**

### Development Mode
```bash
# Enable for testing
DEVELOPMENT_MODE=true
DEBUG_MODE=true
TEST_MODE=true

# Testing
TEST_OUTPUT_DIR=test_output
TEST_GENERATE_SAMPLE_DATA=true
```

### Demo Configuration
```bash
# Demo settings
DEMO_MODE=false
DEMO_ORGANIZATIONS=5
DEMO_DOCUMENTS_PER_ORG=5
DEMO_INCLUDE_RESEARCH=true
```

## 📏 **System Limits**

### Processing Limits
```bash
MAX_ORGANIZATIONS_PER_REQUEST=10
MAX_DOCUMENTS_PER_ORGANIZATION=10
MAX_DOCUMENT_SIZE_MB=50
MAX_PROCESSING_TIME_MINUTES=30
```

### Memory Management
```bash
MAX_MEMORY_USAGE_MB=2048
GARBAGE_COLLECTION_ENABLED=true
MEMORY_THRESHOLD_WARNING=1536
```

### File Management
```bash
MAX_OUTPUT_FILES=1000
AUTO_CLEANUP_OLD_FILES=true
FILE_RETENTION_DAYS=30
BACKUP_GENERATED_DOCUMENTS=false
```

## 📖 **Common Configurations**

### **Production Setup**
```bash
# Professional production environment
DEVELOPMENT_MODE=false
DEBUG_MODE=false
LOG_LEVEL=INFO
PERFORMANCE_MONITORING=true
FEDERAL_COURT_FORMATTING=true
ASIC_COMPLIANCE_ENABLED=true
ZERO_PERSISTENT_STORAGE=true
```

### **Development Setup**
```bash
# Development and testing
DEVELOPMENT_MODE=true
DEBUG_MODE=true
LOG_LEVEL=DEBUG
TEST_MODE=true
MOCK_API_RESPONSES=false
```

### **High Volume Setup**
```bash
# For processing many organizations
MAX_ORGANIZATIONS_PER_REQUEST=20
MAX_DOCUMENTS_PER_ORGANIZATION=15
MAX_MEMORY_USAGE_MB=4096
PERFORMANCE_MONITORING=true
```

### **Security Focused**
```bash
# Maximum security settings
ZERO_PERSISTENT_STORAGE=true
MEMORY_CLEANUP_AFTER_USE=true
API_KEY_MASKING=true
VERIFY_SSL_CERTIFICATES=true
SENSITIVE_DATA_ENCRYPTION=false  # Not implemented yet
```

## 🔧 **Configuration Validation**

The system automatically validates your configuration on startup:

```python
from agent.config import Config

config = Config()
is_valid = config.validate_config()

if is_valid:
    print("✅ Configuration is valid")
else:
    print("❌ Configuration has issues - check logs")
```

### **Common Validation Issues**
- Missing `OPENAI_API_KEY`
- Invalid directory permissions for `PDF_OUTPUT_DIR`
- Negative values for limits
- Invalid boolean values

## 💡 **Tips & Best Practices**

### **API Key Security**
- Never commit `.env` files to version control
- Use different API keys for development/production
- Rotate API keys regularly
- Monitor API usage and costs

### **Performance Optimization**
- Set appropriate memory limits for your system
- Enable garbage collection for long-running processes
- Monitor performance metrics
- Adjust timeout values based on your network

### **Legal Compliance**
- Keep asset realization factors current
- Review legal clauses regularly
- Ensure ASIC compliance settings are correct
- Update Corporations Act references as needed

### **Document Quality**
- Enable all quality assurance checks
- Use Federal Court formatting for official documents
- Include comprehensive financial schedules
- Validate all generated documents before use

## 🆘 **Troubleshooting**

### **Configuration Not Loading**
```bash
# Check if .env file exists
ls -la .env

# Verify file permissions
chmod 644 .env

# Test loading manually
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('AGENT_NAME'))"
```

### **API Key Issues**
```bash
# Test OpenAI connection
python -c "from agent.config import Config; from agent.llm_client import LLMService; c = Config(); print('API Key:', c._mask_key(c.openai_api_key))"
```

### **PDF Generation Problems**
```bash
# Check ReportLab installation
python -c "import reportlab; print('ReportLab version:', reportlab.Version)"

# Test directory permissions
python -c "from pathlib import Path; p = Path('output'); p.mkdir(exist_ok=True); (p / 'test').touch(); print('✅ Directory writable')"
```

### **Memory Issues**
```bash
# Monitor memory usage
MEMORY_USAGE_TRACKING=true
MEMORY_THRESHOLD_WARNING=1024
LOG_LEVEL=DEBUG
```

## 📞 **Getting Help**

1. **Check the logs**: Look in `professional_agent.log`
2. **Validate configuration**: Run `python -c "from agent.config import Config; Config().validate_config()"`
3. **Test individual components**: Use the test scripts
4. **Review this guide**: Ensure all required settings are configured

## 🔄 **Environment Management**

### **Multiple Environments**
```bash
# Development
cp config_template.env .env.dev
# Edit .env.dev for development settings

# Production  
cp config_template.env .env.prod
# Edit .env.prod for production settings

# Load specific environment
python -c "from dotenv import load_dotenv; load_dotenv('.env.prod')"
```

### **Environment Switching**
```bash
# Use environment variables to switch
export ENV_FILE=.env.prod
python main_professional.py
```

---

## ✅ **Configuration Checklist**

- [ ] Created `.env` file from template
- [ ] Set `OPENAI_API_KEY` with valid key
- [ ] Configured agent name and version
- [ ] Set appropriate PDF output directory
- [ ] Enabled required document types
- [ ] Configured legal framework settings
- [ ] Set financial calculation parameters
- [ ] Enabled appropriate logging level
- [ ] Tested configuration with validation
- [ ] Verified PDF generation works
- [ ] Reviewed security settings

**Ready to generate professional documents!** 🎉 