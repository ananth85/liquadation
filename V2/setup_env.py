#!/usr/bin/env python3
"""
Environment Setup Script for Professional AI Agent System
Helps users create and configure their .env file from the template
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Setup environment configuration file"""
    print("🔧 PROFESSIONAL AI AGENT SYSTEM - ENVIRONMENT SETUP")
    print("=" * 60)
    
    # Check if .env already exists
    env_file = Path('.env')
    template_file = Path('config_template.env')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled.")
            return False
    
    # Check if template exists
    if not template_file.exists():
        print("❌ config_template.env not found!")
        print("Please ensure you have the configuration template file.")
        return False
    
    # Copy template to .env
    try:
        shutil.copy(template_file, env_file)
        print(f"✅ Created .env file from template")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False
    
    print("\n📝 CONFIGURATION SETUP")
    print("-" * 30)
    
    # Get API keys from user
    openai_key = input("Enter your OpenAI API key (required): ").strip()
    if openai_key:
        update_env_value('.env', 'OPENAI_API_KEY', openai_key)
        print("✅ OpenAI API key configured")
    else:
        print("⚠️  OpenAI API key not set - you'll need to add it manually to .env")
    
    serpapi_key = input("Enter your SerpAPI key (optional, press Enter to skip): ").strip()
    if serpapi_key:
        update_env_value('.env', 'SERPAPI_API_KEY', serpapi_key)
        print("✅ SerpAPI key configured")
    else:
        print("ℹ️  SerpAPI key not set - web search will use free engines only")
    
    # Ask about agent name
    agent_name = input("Enter agent name (press Enter for default): ").strip()
    if agent_name:
        update_env_value('.env', 'AGENT_NAME', agent_name)
        print(f"✅ Agent name set to: {agent_name}")
    
    # Ask about output directory
    output_dir = input("Enter PDF output directory (press Enter for 'output'): ").strip()
    if output_dir:
        update_env_value('.env', 'PDF_OUTPUT_DIR', output_dir)
        print(f"✅ Output directory set to: {output_dir}")
    
    print("\n🎯 SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Environment file created: .env")
    print("📄 Template preserved: config_template.env")
    
    print("\n📋 Next Steps:")
    print("1. Review and customize settings in .env file")
    print("2. Install dependencies: pip install -r requirements_professional.txt")
    print("3. Test the system: python test_professional_pdf.py")
    print("4. Generate documents: python main_professional.py")
    
    print("\n💡 Tips:")
    print("• Edit .env file to customize all settings")
    print("• Set DEVELOPMENT_MODE=true for testing")
    print("• Set DEBUG_MODE=true for detailed logging")
    print("• Configure asset realization factors for your jurisdiction")
    
    return True

def update_env_value(env_file: str, key: str, value: str):
    """Update a value in the .env file"""
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        if not updated:
            lines.append(f"{key}={value}\n")
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
    except Exception as e:
        print(f"⚠️  Warning: Could not update {key} in .env file: {e}")

def main():
    """Main setup function"""
    try:
        success = setup_environment()
        if success:
            print("\n🎉 Environment setup completed successfully!")
            print("The Professional AI Agent System is ready to use.")
        else:
            print("\n❌ Environment setup failed.")
            print("Please check the errors above and try again.")
    except KeyboardInterrupt:
        print("\n⏹️  Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")

if __name__ == "__main__":
    main() 