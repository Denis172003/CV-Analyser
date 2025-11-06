#!/usr/bin/env python3
"""
Setup script for AI Resume Analyzer
Helps users quickly set up the application with all dependencies and configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header():
    """Print welcome header."""
    print("=" * 60)
    print("🤖 AI Resume Analyzer - Setup Script")
    print("=" * 60)
    print("This script will help you set up the AI Resume Analyzer application.")
    print()

def check_python_version():
    """Check if Python version is compatible."""
    print("📋 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again.")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} is compatible.")
    print()

def check_system_dependencies():
    """Check for required system dependencies."""
    print("🔧 Checking system dependencies...")
    
    dependencies = {
        'ffmpeg': 'FFmpeg (required for video generation)',
        'git': 'Git (required for version control)'
    }
    
    missing = []
    for cmd, description in dependencies.items():
        if not shutil.which(cmd):
            missing.append(f"  - {cmd}: {description}")
    
    if missing:
        print("⚠️  Missing system dependencies:")
        for dep in missing:
            print(dep)
        print()
        print("Please install the missing dependencies:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg git")
        print("  macOS: brew install ffmpeg git")
        print("  Windows: Download from official websites")
        print()
        
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    else:
        print("✅ All system dependencies are available.")
    
    print()

def create_virtual_environment():
    """Create and activate virtual environment."""
    print("🐍 Setting up virtual environment...")
    
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists.")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment.")
        print("   Please create it manually: python -m venv .venv")
        sys.exit(1)
    
    print()
    print("📝 To activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source .venv/bin/activate")
    print()

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    # Determine pip command
    pip_cmd = "pip"
    if os.name != 'nt':  # Unix/Linux/macOS
        venv_pip = Path(".venv/bin/pip")
        if venv_pip.exists():
            pip_cmd = str(venv_pip)
    else:  # Windows
        venv_pip = Path(".venv/Scripts/pip.exe")
        if venv_pip.exists():
            pip_cmd = str(venv_pip)
    
    try:
        # Upgrade pip first
        subprocess.run([pip_cmd, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Dependencies installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        print("   Please install manually: pip install -r requirements.txt")
        sys.exit(1)
    
    print()

def setup_environment_file():
    """Set up environment variables file."""
    print("🔐 Setting up environment variables...")
    
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    if env_file.exists():
        print("✅ .env file already exists.")
        return
    
    if not template_file.exists():
        print("❌ .env.template file not found.")
        return
    
    # Copy template to .env
    shutil.copy(template_file, env_file)
    print("✅ Created .env file from template.")
    
    print()
    print("🔑 Please edit the .env file with your API keys:")
    print("   - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys")
    print("   - SUPABASE_URL: Get from your Supabase project dashboard")
    print("   - SUPABASE_KEY: Get from your Supabase project dashboard")
    print("   - Optional: NUTRIENT_API_KEY, GEMINI_API_KEY")
    print()

def setup_database():
    """Set up database."""
    print("🗄️  Setting up database...")
    
    response = input("Do you want to initialize the database now? (y/N): ").lower()
    if response == 'y':
        try:
            subprocess.run([sys.executable, "setup_database.py"], check=True)
            print("✅ Database initialized successfully.")
        except subprocess.CalledProcessError:
            print("❌ Database initialization failed.")
            print("   Please run manually: python setup_database.py")
    else:
        print("⏭️  Skipping database setup.")
        print("   Run later: python setup_database.py")
    
    print()

def create_directories():
    """Create necessary directories."""
    print("📁 Creating necessary directories...")
    
    directories = ["temp", "logs", "samples"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created successfully.")
    print()

def run_tests():
    """Run tests to verify installation."""
    print("🧪 Running tests to verify installation...")
    
    response = input("Do you want to run tests now? (y/N): ").lower()
    if response == 'y':
        try:
            subprocess.run([sys.executable, "-m", "pytest", "--tb=short"], check=True)
            print("✅ All tests passed!")
        except subprocess.CalledProcessError:
            print("⚠️  Some tests failed. This might be due to missing API keys.")
            print("   The application should still work with proper configuration.")
    else:
        print("⏭️  Skipping tests.")
        print("   Run later: python -m pytest")
    
    print()

def print_next_steps():
    """Print next steps for the user."""
    print("🎉 Setup completed!")
    print()
    print("📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Activate virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source .venv/bin/activate")
    print("3. Initialize database: python setup_database.py")
    print("4. Run the application: streamlit run app.py")
    print("5. Open http://localhost:8501 in your browser")
    print()
    print("📚 For more information:")
    print("   - README.md: Complete documentation")
    print("   - DEPLOYMENT.md: Deployment options")
    print("   - CONTRIBUTING.md: How to contribute")
    print()
    print("🆘 Need help?")
    print("   - GitHub Issues: https://github.com/Denis172003/CV-Analyser/issues")
    print("   - Documentation: Check README.md")
    print()

def main():
    """Main setup function."""
    try:
        print_header()
        check_python_version()
        check_system_dependencies()
        create_virtual_environment()
        install_dependencies()
        setup_environment_file()
        create_directories()
        setup_database()
        run_tests()
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()