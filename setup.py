#!/usr/bin/env python3
"""
Setup script for Annual Report Analyzer MVP.
This script helps set up the development environment and validates the installation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(text):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(step_num, text):
    """Print formatted step."""
    print(f"\n[{step_num}] {text}")

def run_command(command, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_python_version():
    """Check if Python version is suitable."""
    print_step(1, "Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected.")
    return True

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    print_step(2, "Setting up virtual environment...")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists.")
        return True
    
    success, stdout, stderr = run_command(f"{sys.executable} -m venv .venv")
    if success:
        print("✅ Virtual environment created successfully.")
        return True
    else:
        print(f"❌ Failed to create virtual environment: {stderr}")
        return False

def get_pip_command():
    """Get the appropriate pip command for the current platform."""
    if sys.platform == "win32":
        return ".venv\\Scripts\\pip"
    else:
        return ".venv/bin/pip"

def install_dependencies():
    """Install required dependencies."""
    print_step(3, "Installing dependencies...")
    
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    print("Upgrading pip...")
    success, stdout, stderr = run_command(f"{pip_cmd} install --upgrade pip")
    if not success:
        print(f"⚠️  Warning: Could not upgrade pip: {stderr}")
    
    # Install requirements
    print("Installing requirements...")
    success, stdout, stderr = run_command(f"{pip_cmd} install -r requirements.txt")
    if success:
        print("✅ Dependencies installed successfully.")
        return True
    else:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False

def check_environment_file():
    """Check if .env file exists and help create it."""
    print_step(4, "Checking environment configuration...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file exists.")
        # Warn user if endpoint is not set or is malformed
        with open(env_file, "r") as f:
            env_content = f.read()
        if "AZURE_OPENAI_ENDPOINT" not in env_content or "your-endpoint-url" in env_content:
            print("⚠️  Please ensure AZURE_OPENAI_ENDPOINT is set and valid in your .env file.")
        return True
    
    if env_example.exists():
        print("📋 .env file not found. Creating from template...")
        shutil.copy(env_example, env_file)
        print("✅ .env file created from template.")
        print("\n⚠️  IMPORTANT: Please edit .env file with your Azure OpenAI credentials:")
        print("   - AZURE_OPENAI_ENDPOINT (must be a valid URL, e.g. https://<resource>.openai.azure.com)")
        print("   - AZURE_OPENAI_API_KEY")
        print("   - AZURE_OPENAI_API_VERSION")
        return False  # Need manual configuration
    else:
        print("❌ Neither .env nor .env.example found.")
        return False

def test_installation():
    """Test the installation by importing key modules."""
    print_step(5, "Testing installation...")
    
    # Test basic imports
    test_modules = [
        ("openai", "Azure OpenAI client"),
        ("fastapi", "FastAPI web framework"),
        ("faiss", "FAISS vector database"),
        ("fitz", "PyMuPDF document processing"),
        ("langchain", "LangChain text processing"),
        ("pydantic", "Data validation"),
    ]
    
    all_passed = True
    for module, description in test_modules:
        try:
            __import__(module)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - Import failed")
            all_passed = False
    
    return all_passed

def run_basic_validation():
    """Run basic validation of the configuration."""
    print_step(6, "Running basic validation...")
    
    try:
        # Try to import and validate configuration
        sys.path.insert(0, "src")
        from src.utils.config import Config
        
        config = Config()
        print("✅ Configuration file loads successfully")
        
        if config.validate_azure_config():
            print("✅ Azure OpenAI configuration is valid")
        else:
            print("⚠️  Azure OpenAI configuration needs to be completed in .env file")
        
        return True
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False

def show_next_steps():
    """Show next steps to the user."""
    print_header("NEXT STEPS")
    
    print("\n1. Configure your Azure OpenAI credentials:")
    print("   - Edit the .env file with your Azure OpenAI endpoint and API key")
    print("   - Get credentials from Azure Portal > Azure OpenAI resource")
    
    print("\n2. Test the MVP system:")
    print("   - Interactive mode: python main.py")
    print("   - API server mode: python main.py --api")
    
    print("\n3. Upload a test PDF document:")
    print("   - Use the 'upload' command in interactive mode")
    print("   - Or use the REST API: POST /documents/upload")
    
    print("\n4. Query your documents:")
    print("   - Use the 'query' command in interactive mode")
    print("   - Or use the REST API: POST /documents/query")
    
    print("\n5. Run tests (optional):")
    print("   - Unit tests: pytest tests/")
    print("   - Integration tests: pytest tests/ -m integration")

def main():
    """Main setup function."""
    print_header("Annual Report Analyzer MVP Setup")
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Run setup steps
    steps_passed = 0
    total_steps = 6
    
    if check_python_version():
        steps_passed += 1
    else:
        print("\n❌ Setup failed: Python version requirement not met.")
        return False
    
    if create_virtual_environment():
        steps_passed += 1
    else:
        print("\n❌ Setup failed: Could not create virtual environment.")
        return False
    
    if install_dependencies():
        steps_passed += 1
    else:
        print("\n❌ Setup failed: Could not install dependencies.")
        return False
    
    env_configured = check_environment_file()
    if env_configured:
        steps_passed += 1
    
    if test_installation():
        steps_passed += 1
    else:
        print("\n⚠️  Some dependencies may not be properly installed.")
    
    if run_basic_validation():
        steps_passed += 1
    else:
        print("\n⚠️  Configuration validation had issues.")
    
    # Summary
    print_header("SETUP SUMMARY")
    print(f"\nCompleted {steps_passed}/{total_steps} setup steps.")
    
    if steps_passed >= 5:
        print("✅ Setup completed successfully!")
        if not env_configured:
            print("⚠️  Don't forget to configure your .env file with Azure OpenAI credentials.")
    else:
        print("⚠️  Setup completed with issues. Please review the errors above.")
    
    show_next_steps()
    return steps_passed >= 5

if __name__ == "__main__":
    main()
