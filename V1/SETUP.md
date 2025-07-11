# 🛠️ Liquidation Agent Setup Guide

This guide provides detailed, step-by-step instructions for setting up the Liquidation Documentation Generation Agent on different platforms.

## 📋 Pre-Installation Checklist

Before starting, ensure you have:

- [ ] **Python 3.10 or higher** installed
- [ ] **pip** package manager available
- [ ] **Command line access** (Terminal on macOS/Linux, PowerShell on Windows)
- [ ] **Internet connection** for downloading packages
- [ ] **500MB+ free disk space** for dependencies and generated files

### Check Your Python Version

```bash
python --version
# Should show: Python 3.10.x or higher

pip --version
# Should show: pip 23.x.x or similar
```

If Python is not installed, download from: https://www.python.org/downloads/

## 🖥️ Platform-Specific Setup

### Windows 10/11 Setup

#### Method 1: PowerShell Installation (Recommended)

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)"

2. **Create Project Directory**
   ```powershell
   # Navigate to your development folder
   cd C:\Users\%USERNAME%\Documents
   mkdir liquidation-agent
   cd liquidation-agent
   ```

3. **Create Virtual Environment**
   ```powershell
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   .\venv\Scripts\activate
   
   # Verify activation (prompt should show (venv))
   ```

4. **Install Core Dependencies**
   ```powershell
   # Upgrade pip first
   python -m pip install --upgrade pip
   
   # Install minimal required packages
   pip install pandas jinja2 faker click aiohttp pydantic python-dotenv reportlab
   
   # Optional: Install OpenAI for enhanced generation
   pip install openai
   ```

5. **Verify Installation**
   ```powershell
   # Check installed packages
   pip list
   
   # Should show all required packages
   ```

#### Method 2: Using requirements.txt (If Available)

```powershell
# If you have the full project with requirements.txt
pip install -r requirements.txt
```

#### Windows Troubleshooting

**Issue: WeasyPrint installation fails**
```powershell
# Skip WeasyPrint - ReportLab works better on Windows
pip install pandas jinja2 faker click aiohttp pydantic python-dotenv reportlab openai
```

**Issue: "pip is not recognized"**
```powershell
# Add Python to PATH, or use full path:
C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts\pip.exe install pandas
```

**Issue: Permission denied**
```powershell
# Run PowerShell as Administrator, or use user installation:
pip install --user pandas jinja2 faker click aiohttp reportlab
```

### macOS Setup

#### Prerequisites for macOS

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python** (if not using system Python)
   ```bash
   brew install python@3.11
   ```

#### Setup Steps

1. **Create Project Directory**
   ```bash
   # Navigate to your development folder
   cd ~/Documents
   mkdir liquidation-agent
   cd liquidation-agent
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Verify activation (prompt should show (venv))
   ```

3. **Install System Dependencies** (for WeasyPrint support)
   ```bash
   # Install required system libraries
   brew install pango libffi cairo pango gdk-pixbuf libxml2 libxslt
   ```

4. **Install Python Dependencies**
   ```bash
   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Install core packages
   pip install pandas jinja2 faker click aiohttp pydantic python-dotenv
   
   # Install PDF engines (try WeasyPrint first, fallback to ReportLab)
   pip install weasyprint reportlab
   
   # Optional: Enhanced AI generation
   pip install openai
   ```

5. **Verify Installation**
   ```bash
   python -c "import pandas, jinja2, faker, click, aiohttp; print('✅ Core packages installed')"
   python -c "import weasyprint; print('✅ WeasyPrint installed')" || echo "⚠️ WeasyPrint failed, using ReportLab"
   python -c "import reportlab; print('✅ ReportLab installed')"
   ```

### Linux (Ubuntu/Debian) Setup

#### Prerequisites

1. **Update Package Manager**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install Python and Dependencies**
   ```bash
   # Install Python and pip
   sudo apt install python3 python3-pip python3-venv -y
   
   # Install system dependencies for WeasyPrint
   sudo apt install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 -y
   sudo apt install libffi-dev libxml2-dev libxslt-dev -y
   ```

#### Setup Steps

1. **Create Project Directory**
   ```bash
   # Navigate to your development folder
   cd ~/Documents
   mkdir liquidation-agent
   cd liquidation-agent
   ```

2. **Create Virtual Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Verify activation
   which python  # Should show path to venv/bin/python
   ```

3. **Install Python Dependencies**
   ```bash
   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Install all packages
   pip install pandas jinja2 faker click aiohttp pydantic python-dotenv
   pip install weasyprint reportlab openai
   ```

4. **Verify Installation**
   ```bash
   python -c "import weasyprint, reportlab; print('✅ PDF engines ready')"
   ```

## 🔧 Project Setup

### Download or Create Project Files

#### Option A: If You Have Project Files
```bash
# Copy all Python files to your project directory
# agents/ folder with all .py files
# main.py, test_system.py, requirements.txt
```

#### Option B: Create Files Manually
```bash
# Create directory structure
mkdir agents data templates output_pdfs

# Create agent package
touch agents/__init__.py

# Create template directory (templates will auto-generate)
mkdir -p templates
```

### Create Configuration File

Create a `.env` file in your project root:

```bash
# Create .env file
cat > .env << 'EOF'
# OpenAI API Configuration (Optional)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=

# ABN Lookup API Configuration (Optional) 
# Register for free at: https://abr.business.gov.au/Tools/WebServices
ABN_API_KEY=

# File Paths (Optional - uses defaults if not specified)
TEMPLATES_DIR=templates
OUTPUT_DIR=output_pdfs
DATA_DIR=data

# Logging Configuration (Optional)
LOG_LEVEL=INFO
LOG_FILE=liquidation_agent.log
EOF
```

### Test Your Setup

1. **Basic Import Test**
   ```bash
   python -c "
   try:
       import pandas, jinja2, faker, click, aiohttp
       print('✅ All core packages imported successfully')
   except ImportError as e:
       print(f'❌ Import error: {e}')
   "
   ```

2. **PDF Engine Test**
   ```bash
   python -c "
   pdf_engines = []
   try:
       import weasyprint
       pdf_engines.append('weasyprint')
   except ImportError:
       pass
   
   try:
       import reportlab
       pdf_engines.append('reportlab')
   except ImportError:
       pass
   
   if pdf_engines:
       print(f'✅ PDF engines available: {pdf_engines}')
   else:
       print('❌ No PDF engines available')
   "
   ```

3. **System Test** (if you have the complete project)
   ```bash
   # Run system tests
   python test_system.py
   
   # Check system status
   python main.py status
   ```

## 🔍 Validation Steps

### Verify Complete Installation

Run these commands to ensure everything is working:

```bash
# 1. Check Python packages
pip list | grep -E "(pandas|jinja2|faker|click|aiohttp|reportlab)"

# 2. Test imports
python -c "
import sys
print(f'Python version: {sys.version}')

packages = ['pandas', 'jinja2', 'faker', 'click', 'aiohttp', 'pydantic', 'reportlab']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg}')
    except ImportError:
        print(f'❌ {pkg} - NOT INSTALLED')
"

# 3. Check file structure
ls -la
echo "Expected: agents/ data/ templates/ main.py requirements.txt README.md"
```

### Expected Output
```
✅ pandas
✅ jinja2  
✅ faker
✅ click
✅ aiohttp
✅ pydantic
✅ reportlab
```

## 🚨 Common Setup Issues & Solutions

### Issue 1: Python Version Too Old
```bash
# Check version
python --version

# If < 3.10, install newer Python:
# Windows: Download from python.org
# macOS: brew install python@3.11  
# Linux: sudo apt install python3.11
```

### Issue 2: Virtual Environment Issues
```bash
# Deactivate current environment
deactivate

# Remove old environment
rm -rf venv

# Create new environment with specific Python version
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### Issue 3: Package Installation Failures
```bash
# Clear pip cache
pip cache purge

# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install packages one by one to isolate issues
pip install pandas
pip install jinja2
# ... etc
```

### Issue 4: WeasyPrint Installation Failures

**Windows:**
```bash
# Skip WeasyPrint entirely
pip install pandas jinja2 faker click aiohttp reportlab

# Or try with conda
conda install -c conda-forge weasyprint
```

**macOS:**
```bash
# Install system dependencies first
brew install cairo pango gdk-pixbuf libxml2 libxslt libffi

# Then install WeasyPrint
pip install weasyprint
```

**Linux:**
```bash
# Install system dependencies
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Then install WeasyPrint
pip install weasyprint
```

### Issue 5: Permission Errors
```bash
# Use user installation
pip install --user package_name

# Or fix permissions (Linux/macOS)
sudo chown -R $USER:$USER ~/.local/

# Windows: Run PowerShell as Administrator
```

## 🧪 Testing Your Installation

### Quick Test Script

Create `test_install.py`:

```python
#!/usr/bin/env python3
"""Quick installation test script"""

def test_imports():
    """Test all required imports"""
    try:
        import pandas as pd
        import jinja2
        import faker
        import click
        import aiohttp
        import pydantic
        print("✅ All core packages imported successfully")
        
        # Test PDF engines
        pdf_engines = []
        try:
            import weasyprint
            pdf_engines.append("weasyprint")
        except ImportError:
            pass
            
        try:
            import reportlab
            pdf_engines.append("reportlab")
        except ImportError:
            pass
            
        if pdf_engines:
            print(f"✅ PDF engines available: {', '.join(pdf_engines)}")
        else:
            print("❌ No PDF engines available - install reportlab or weasyprint")
            
        # Test optional packages
        try:
            import openai
            print("✅ OpenAI package available")
        except ImportError:
            print("ℹ️ OpenAI package not installed (optional)")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality"""
    try:
        import pandas as pd
        import faker
        
        # Test pandas
        df = pd.DataFrame({'test': [1, 2, 3]})
        assert len(df) == 3
        
        # Test faker
        fake = faker.Faker()
        company = fake.company()
        assert isinstance(company, str)
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Liquidation Agent Installation")
    print("=" * 50)
    
    success = True
    success &= test_imports()
    success &= test_basic_functionality()
    
    print("=" * 50)
    if success:
        print("🎉 Installation test completed successfully!")
        print("You can now run: python main.py status")
    else:
        print("❌ Installation test failed. Check errors above.")
        print("Refer to troubleshooting section in SETUP.md")
```

Run the test:
```bash
python test_install.py
```

## 🎯 Next Steps

After successful installation:

1. **Run System Tests**
   ```bash
   python test_system.py
   ```

2. **Check System Status**
   ```bash
   python main.py status
   ```

3. **Generate Your First Document**
   ```bash
   python main.py prompt "Generate liquidation docs for a test company"
   ```

4. **Explore Features**
   ```bash
   python main.py --help
   python main.py templates
   python main.py generate --help
   ```

## 📞 Getting Help

If you encounter issues:

1. **Check the main README.md** for troubleshooting
2. **Run the system diagnostic**: `python main.py status`  
3. **Review log files**: Check `liquidation_agent.log`
4. **Test individual components**: Use `test_install.py`

### Support Checklist

When reporting issues, include:
- [ ] Operating system and version
- [ ] Python version (`python --version`)
- [ ] Virtual environment status
- [ ] Complete error message
- [ ] Output of `pip list`
- [ ] Output of `python main.py status`

---

**🎉 Congratulations!** Once setup is complete, you'll have a fully functional liquidation document generation system ready for testing and training scenarios. 