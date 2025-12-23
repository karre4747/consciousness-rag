#!/bin/bash

echo "🧠 Evolve Consciousness Engine - Quick Start"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/main_simplified.py" ]; then
    echo "❌ Error: Please run this script from the consciousness-rag directory"
    exit 1
fi

echo "Step 1: Backing up current files..."
cd backend
[ -f main.py ] && cp main.py main_old.py && echo "  ✓ Backed up main.py"
[ -f tagging.py ] && cp tagging.py tagging_old.py && echo "  ✓ Backed up tagging.py"
[ -f static/index.html ] && cp static/index.html static/index_old.html && echo "  ✓ Backed up index.html"

echo ""
echo "Step 2: Installing simplified versions..."
cp main_simplified.py main.py && echo "  ✓ Installed main_simplified.py → main.py"
cp tagging_clean.py tagging.py && echo "  ✓ Installed tagging_clean.py → tagging.py"
cp static/index_simplified.html static/index.html && echo "  ✓ Installed index_simplified.html → index.html"

echo ""
echo "Step 3: Checking environment..."
if [ ! -f ".env" ]; then
    echo "  ⚠️  No .env file found. Creating template..."
    cat > .env << 'ENVEOF'
# Required API Keys
PINECONE_API_KEY=your_pinecone_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional Configuration
INDEX_NAME=consciousness-rag
CHUNK_SIZE=1800
CHUNK_OVERLAP=200
ENVEOF
    echo "  ✓ Created .env template - PLEASE UPDATE WITH YOUR API KEYS"
else
    echo "  ✓ .env file exists"
fi

echo ""
echo "Step 4: Checking Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3.11 -m venv venv
    echo "  ✓ Virtual environment created"
fi

echo ""
echo "Step 5: Installing dependencies..."
source venv/bin/activate
pip install -q fastapi uvicorn python-dotenv pinecone-client openai anthropic
echo "  ✓ Dependencies installed"

echo ""
echo "============================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Update .env file with your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: python main.py"
echo "  4. Open: http://localhost:8000"
echo ""
echo "For detailed instructions, see SIMPLIFIED_DEPLOYMENT.md"
echo "============================================"
