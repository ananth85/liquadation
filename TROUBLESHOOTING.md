# 🔧 Troubleshooting Guide

This guide helps resolve common issues when setting up and using the Liquidation Documentation Generation Agent.

## 🚨 Quick Diagnostics

### Run System Diagnostics

```bash
# Check system health
python main.py status

# Run complete system test
python test_system.py

# Check Python environment
python -c "import sys; print(f'Python: {sys.version}'); print(f'Path: {sys.executable}')"

# List installed packages
pip list | grep -E "(pandas|jinja2|faker|click|aiohttp|reportlab|weasyprint|openai)"
```

## 📦 Installation Issues

### Issue: `pip install` Fails with Permission Errors

**Symptoms:**
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   pip install pandas jinja2 faker click aiohttp reportlab
   ```

2. **User Installation**
   ```bash
   pip install --user pandas jinja2 faker click aiohttp reportlab
   ```

3. **Run as Administrator (Windows)**
   ```bash
   # Right-click PowerShell -> "Run as administrator"
   pip install pandas jinja2 faker click aiohttp reportlab
   ```

### Issue: WeasyPrint Installation Fails

**Symptoms:**
```
error: Microsoft Visual C++ 14.0 is required
Failed building wheel for weasyprint
```

**Solutions:**

1. **Skip WeasyPrint (Recommended for Windows)**
   ```bash
   pip install pandas jinja2 faker click aiohttp reportlab openai
   # System will use ReportLab for PDF generation
   ```

2. **Install System Dependencies**

   **Windows:**
   ```bash
   # Download and install GTK+ runtime:
   # https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
   
   # Or use conda:
   conda install -c conda-forge weasyprint
   ```

   **macOS:**
   ```bash
   brew install cairo pango gdk-pixbuf libxml2 libxslt libffi
   pip install weasyprint
   ```

   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
   pip install weasyprint
   ```

### Issue: Python Version Too Old

**Symptoms:**
```
SyntaxError: invalid syntax
TypeError: unsupported operand type(s) for |: 'type' and 'type'
```

**Solution:**
```bash
# Check Python version
python --version

# Need Python 3.10+, install newer version:
# Windows: Download from python.org
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11

# Create venv with specific version
python3.11 -m venv venv
```

### Issue: `No module named 'agents'`

**Symptoms:**
```bash
ModuleNotFoundError: No module named 'agents'
```

**Solutions:**

1. **Check Current Directory**
   ```bash
   pwd  # Should be in liquidation-agent directory
   ls   # Should see: agents/ main.py requirements.txt
   ```

2. **Verify agents Package**
   ```bash
   ls agents/
   # Should see: __init__.py base_agent.py supervisor_agent.py ...
   
   # If __init__.py is missing:
   touch agents/__init__.py
   ```

3. **Reinstall Project**
   ```bash
   # Ensure all Python files are in correct locations
   # agents/ folder should contain all agent .py files
   ```

## 🚀 Runtime Issues

### Issue: PDF Generation Fails

**Symptoms:**
```
Error: No PDF engines available
RuntimeError: PDF generation failed
```

**Diagnosis:**
```bash
python -c "
try:
    import reportlab
    print('✅ ReportLab available')
except ImportError:
    print('❌ ReportLab not installed')

try:
    import weasyprint
    print('✅ WeasyPrint available')
except ImportError:
    print('❌ WeasyPrint not installed')
"
```

**Solutions:**

1. **Install ReportLab**
   ```bash
   pip install reportlab
   ```

2. **Test PDF Engine**
   ```bash
   python -c "
   from reportlab.pdfgen import canvas
   from reportlab.lib.pagesizes import A4
   c = canvas.Canvas('test.pdf', pagesize=A4)
   c.drawString(100, 750, 'Test PDF')
   c.save()
   print('✅ ReportLab test successful')
   "
   ```

### Issue: Template Files Not Found

**Symptoms:**
```
TemplateNotFound: liquidation_resolution.j2
FileNotFoundError: [Errno 2] No such file or directory: 'templates/creditor_notice.j2'
```

**Solutions:**

1. **Check Templates Directory**
   ```bash
   ls templates/
   # Should see: .j2 template files
   ```

2. **Recreate Templates** (they auto-generate)
   ```bash
   # Remove templates directory
   rm -rf templates/
   
   # Run system - templates will be recreated
   python main.py status
   ```

3. **Manual Template Creation**
   ```bash
   mkdir -p templates
   # Templates will be auto-created on first run
   ```

### Issue: API Key Errors

**Symptoms:**
```
openai.error.AuthenticationError: Invalid API key
ABN lookup failed: API key invalid
```

**Solutions:**

1. **Check API Key Format**
   ```bash
   # OpenAI keys start with: sk-proj- or sk-
   # ABN keys are GUID format: 12345678-1234-1234-1234-123456789012
   ```

2. **System Works Without API Keys**
   ```bash
   # Remove or comment out API keys in .env
   # OPENAI_API_KEY=
   # ABN_API_KEY=
   
   # System will use synthetic data generation
   python main.py status
   # Should show "degraded" but functional
   ```

3. **Test API Keys**
   ```bash
   # Test OpenAI key
   python -c "
   import openai
   import os
   from dotenv import load_dotenv
   load_dotenv()
   
   client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
   try:
       response = client.chat.completions.create(
           model='gpt-3.5-turbo',
           messages=[{'role': 'user', 'content': 'test'}],
           max_tokens=5
       )
       print('✅ OpenAI API key valid')
   except Exception as e:
       print(f'❌ OpenAI API error: {e}')
   "
   ```

### Issue: Memory or Performance Problems

**Symptoms:**
```
MemoryError: Unable to allocate array
System becomes slow with large CSV files
```

**Solutions:**

1. **Reduce Batch Size**
   ```bash
   # Process smaller batches
   python main.py csv --batch-size 10 large_file.csv
   ```

2. **Monitor Memory Usage**
   ```bash
   # Windows
   tasklist | findstr python
   
   # macOS/Linux
   ps aux | grep python
   top -p $(pgrep python)
   ```

3. **Clean Up Regularly**
   ```bash
   # Clean old files
   python main.py cleanup --days 7
   
   # Restart Python process occasionally
   ```

## 🔍 Environment Issues

### Issue: Virtual Environment Problems

**Symptoms:**
```
command not found: python
pip: command not found
Wrong Python version in venv
```

**Solutions:**

1. **Recreate Virtual Environment**
   ```bash
   deactivate  # If in venv
   rm -rf venv
   python3 -m venv venv
   
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   python --version  # Verify correct version
   ```

2. **Check Virtual Environment Status**
   ```bash
   which python  # Should point to venv/bin/python
   echo $VIRTUAL_ENV  # Should show venv path
   ```

3. **Alternative Virtual Environment Tools**
   ```bash
   # Using conda
   conda create -n liquidation python=3.11
   conda activate liquidation
   
   # Using virtualenv
   pip install virtualenv
   virtualenv venv
   ```

### Issue: PATH and Environment Problems

**Symptoms:**
```
'python' is not recognized as an internal or external command
pip: command not found
```

**Solutions:**

1. **Windows PATH Issues**
   ```bash
   # Add Python to PATH manually
   # System Properties > Environment Variables > PATH
   # Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311\
   
   # Or use py launcher
   py -3.11 -m pip install pandas
   ```

2. **macOS/Linux PATH Issues**
   ```bash
   # Check Python installation
   which python3
   ls -la /usr/bin/python*
   
   # Use full path if needed
   /usr/bin/python3 -m pip install pandas
   ```

## 🔄 System Recovery

### Complete System Reset

If all else fails, perform a complete reset:

```bash
# 1. Backup any custom data
cp data/*.csv /backup/location/

# 2. Deactivate and remove virtual environment
deactivate
rm -rf venv

# 3. Remove generated files
rm -rf output_pdfs/ templates/ *.log

# 4. Recreate virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 5. Reinstall packages
pip install --upgrade pip
pip install pandas jinja2 faker click aiohttp pydantic python-dotenv reportlab

# 6. Test installation
python -c "import pandas, jinja2, faker, click, aiohttp, reportlab; print('✅ All packages working')"

# 7. Run system test
python test_system.py
```

### Verify System Health

```bash
# After reset, verify everything works:
python main.py status
# Should show all agents as healthy or degraded (without API keys)

python main.py prompt "test company liquidation"
# Should generate test documents

ls output_pdfs/
# Should show generated PDF files
```

## 📊 Debug Mode

### Enable Verbose Logging

```bash
# Run with debug flag
python main.py --debug status
python main.py --debug prompt "test"

# Check log file
tail -f liquidation_agent.log

# Or create .env file with:
# DEBUG_MODE=true
# LOG_LEVEL=DEBUG
```

### Manual Component Testing

```bash
# Test individual components
python -c "
from agents.supervisor_agent import SupervisorAgent
supervisor = SupervisorAgent()
print('✅ Supervisor agent created')

health = supervisor.get_health_status()
print(f'Health: {health}')
"

# Test PDF generation directly
python -c "
from agents.pdf_generation_agent import PDFGenerationAgent
pdf_agent = PDFGenerationAgent()
print('✅ PDF agent created')

capabilities = pdf_agent.get_capabilities()
print(f'Capabilities: {capabilities}')
"
```

## 🆘 Getting Help

### Information to Collect

When reporting issues, include:

```bash
# System information
echo "=== System Info ==="
uname -a  # Linux/macOS
# or
systeminfo | findstr /B "OS"  # Windows

echo "=== Python Info ==="
python --version
which python  # Linux/macOS
# or
where python  # Windows

echo "=== Package Info ==="
pip list

echo "=== System Status ==="
python main.py status

echo "=== Error Logs ==="
tail -20 liquidation_agent.log
```

### Support Checklist

- [ ] Python version (3.10+ required)
- [ ] Operating system and version
- [ ] Virtual environment status
- [ ] Complete error message
- [ ] Output of `python main.py status`
- [ ] Output of `pip list`
- [ ] Recent log entries

### Emergency Fallback

If nothing works, use minimal installation:

```bash
# Minimal working system
pip install pandas jinja2 faker click reportlab

# Test basic functionality
python -c "
import pandas as pd
import faker
from jinja2 import Template

fake = faker.Faker()
print(f'Company: {fake.company()}')
print('✅ Minimal system working')
"
```

---

**💡 Remember**: The system is designed to be resilient. Most issues can be resolved by ensuring proper Python environment setup and having at least ReportLab installed for PDF generation. API keys are optional - the system works fully with synthetic data. 