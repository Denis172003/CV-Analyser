#!/bin/bash

# AI Resume Analyzer - Quick Start Script
# One-command application launch with environment setup and dependency checks

set -e  # Exit on any error

echo "🤖 AI Resume Analyzer - Starting Application..."
echo "================================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    local python_cmd=$1
    local version=$($python_cmd --version 2>&1 | cut -d' ' -f2)
    local major=$(echo $version | cut -d'.' -f1)
    local minor=$(echo $version | cut -d'.' -f2)
    
    if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
        return 0
    else
        return 1
    fi
}

# Check if Python 3.8+ is installed
echo "🔍 Checking Python installation..."
PYTHON_CMD=""
if command_exists python3; then
    if check_python_version python3; then
        PYTHON_CMD="python3"
        echo "✅ Python 3 found: $(python3 --version)"
    else
        echo "❌ Python 3.8 or higher is required. Found: $(python3 --version)"
        exit 1
    fi
elif command_exists python; then
    if check_python_version python; then
        PYTHON_CMD="python"
        echo "✅ Python found: $(python --version)"
    else
        echo "❌ Python 3.8 or higher is required. Found: $(python --version)"
        exit 1
    fi
else
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    echo "   Visit: https://www.python.org/downloads/"
    exit 1
fi

# Check if pip is installed
echo "🔍 Checking pip installation..."
PIP_CMD=""
if command_exists pip3; then
    PIP_CMD="pip3"
    echo "✅ pip3 found: $(pip3 --version)"
elif command_exists pip; then
    PIP_CMD="pip"
    echo "✅ pip found: $(pip --version)"
else
    echo "❌ pip is not installed. Please install pip."
    echo "   Run: $PYTHON_CMD -m ensurepip --upgrade"
    exit 1
fi

# Check if Streamlit is installed
echo "🔍 Checking Streamlit installation..."
if ! command_exists streamlit; then
    echo "⚠️  Streamlit not found. Will install with dependencies."
fi

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please ensure you're in the AI Resume Analyzer directory."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing/updating dependencies..."
    echo "   This may take a few minutes on first run..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "🔧 Creating virtual environment..."
        $PYTHON_CMD -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Upgrade pip in virtual environment
    pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please check your Python environment."
        echo "   Try running: pip install --upgrade pip"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "❌ requirements.txt not found. Please ensure you're in the correct directory."
    exit 1
fi

# Check if .env file exists and validate API keys
echo "🔍 Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "📝 Created .env file from template."
        echo ""
        echo "⚠️  IMPORTANT: Please configure your API keys in .env file:"
        echo "   • OPENAI_API_KEY (Required for AI analysis)"
        echo "   • SUPABASE_URL and SUPABASE_KEY (Required for database)"
        echo "   • NUTRIENT_API_KEY (Optional for OCR fallback)"
        echo "   • GEMINI_API_KEY (Optional for advanced video generation)"
        echo ""
        echo "💡 You can get API keys from:"
        echo "   • OpenAI: https://platform.openai.com/api-keys"
        echo "   • Supabase: https://supabase.com/dashboard"
        echo "   • Nutrient: https://nutrient.io/sdk/web/"
        echo "   • Google AI: https://ai.google.dev/"
        echo ""
        read -p "Press Enter after you've configured your .env file..."
    else
        echo "❌ .env.template not found. Please create .env file manually."
        exit 1
    fi
fi

# Validate required API keys
source .env
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
    echo "❌ OPENAI_API_KEY is not configured in .env file."
    echo "   This is required for AI analysis functionality."
    exit 1
fi

# Check if session pooler is configured
if [ "$USE_SESSION_POOLER" = "true" ]; then
    # Check individual database parameters
    if [ -z "$SUPABASE_DB_HOST" ]; then
        echo "❌ SUPABASE_DB_HOST is not configured but USE_SESSION_POOLER=true"
        echo "   Please set SUPABASE_DB_HOST (e.g., aws-1-eu-north-1.pooler.supabase.com)"
        exit 1
    fi
    
    if [ -z "$SUPABASE_DB_USER" ]; then
        echo "❌ SUPABASE_DB_USER is not configured but USE_SESSION_POOLER=true"
        echo "   Please set SUPABASE_DB_USER (e.g., postgres.your_project_ref)"
        exit 1
    fi
    
    if [ -z "$SUPABASE_DB_PASSWORD" ]; then
        echo "❌ SUPABASE_DB_PASSWORD is not configured but session pooler is enabled"
        echo "   This is required for PostgreSQL pooler connections"
        exit 1
    fi
    
    echo "✅ Session pooler configuration detected (host: $SUPABASE_DB_HOST)"
else
    echo "❌ Session pooler is disabled but this application requires session pooler configuration."
    echo "   Please set USE_SESSION_POOLER=true and configure the required SUPABASE_DB_* variables."
    exit 1
fi

echo "✅ Environment configuration validated"

# Check if sample data exists
echo "🔍 Checking sample data..."
if [ ! -d "samples" ] || [ ! -f "samples/sample_resume_en.txt" ]; then
    echo "⚠️  Sample data not found. Some demo features may not work."
else
    echo "✅ Sample data found"
fi

# Final system check
echo "🔍 Running final system check..."
python -c "
import sys
print(f'✅ Python version: {sys.version}')

try:
    import streamlit
    print(f'✅ Streamlit version: {streamlit.__version__}')
except ImportError:
    print('❌ Streamlit not available')
    sys.exit(1)

try:
    import openai
    print(f'✅ OpenAI library available')
except ImportError:
    print('❌ OpenAI library not available')
    sys.exit(1)

try:
    import supabase
    print(f'✅ Supabase library available')
except ImportError:
    print('❌ Supabase library not available')
    sys.exit(1)

# Test database connection
try:
    from database import test_database_connection
    conn_info = test_database_connection()
    if conn_info['status'] == 'connected':
        print(f'✅ Database connection successful ({conn_info[\"connection_type\"]})')
    else:
        print(f'❌ Database connection failed: {conn_info.get(\"error\", \"Unknown error\")}')
        sys.exit(1)
except Exception as e:
    print(f'⚠️  Database connection test skipped: {str(e)}')

print('✅ All core dependencies available')
"

if [ $? -ne 0 ]; then
    echo "❌ System check failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "🎉 All checks passed! Starting application..."
echo "================================================"
echo "🚀 Starting Streamlit application..."
echo "📱 The app will open in your browser at http://localhost:8501"
echo "🛑 Press Ctrl+C to stop the application"
echo ""
echo "💡 Demo tip: Use sample files in the 'samples' directory for testing"
echo ""

# Start the Streamlit application with virtual environment
streamlit run app.py