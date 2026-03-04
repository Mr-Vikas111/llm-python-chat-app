#!/bin/bash
# Setup and testing script for LangChain RAG system
# Run this to verify your installation and test the system

set -e

echo "================================"
echo "LangChain RAG System Setup"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}[1/5] Checking Python...${NC}"
if command -v python3 &> /dev/null; then
    python3 --version
    echo -e "${GREEN}✓ Python found${NC}"
else
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

# Check virtual environment
echo ""
echo -e "${YELLOW}[2/5] Checking virtual environment...${NC}"
if [ -d "env" ]; then
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
else
    echo -e "${RED}✗ Virtual environment not found (expected: ./env)${NC}"
    exit 1
fi

# Install dependencies
echo ""
echo -e "${YELLOW}[3/5] Installing dependencies...${NC}"
./env/bin/pip install -q -e . 2>/dev/null
./env/bin/pip install -q langchain-chroma 2>/dev/null
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Check imports
echo ""
echo -e "${YELLOW}[4/5] Validating imports...${NC}"
if ./env/bin/python -c "from rag_app.core.embeddings import get_embedding_model; from rag_app.core.vector_store import get_vector_store; print('✓ All modules loaded successfully')" 2>/dev/null; then
    echo -e "${GREEN}✓ Imports validated${NC}"
else
    echo -e "${RED}✗ Import validation failed${NC}"
    exit 1
fi

# Run tests
echo ""
echo -e "${YELLOW}[5/5] Running tests...${NC}"
if ./env/bin/python -m pytest tests/test_chunker.py -q 2>/dev/null; then
    echo -e "${GREEN}✓ Tests passed${NC}"
else
    echo -e "${RED}✗ Tests failed${NC}"
    exit 1
fi

# Final checks
echo ""
echo "================================"
echo -e "${GREEN}Setup Verification Complete!${NC}"
echo "================================"
echo ""

# Check environment file
if [ -f ".env" ]; then
    if grep -q "OPENAI_API_KEY" .env; then
        echo -e "${GREEN}✓ .env file configured${NC}"
    else
        echo -e "${YELLOW}⚠ OPENAI_API_KEY not in .env${NC}"
        echo "  Add it manually: OPENAI_API_KEY=sk-..."
    fi
else
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "  Create one with: cp .env.example .env"
fi

# Check data directory
if [ -d "data/raw" ]; then
    file_count=$(find data/raw -type f | wc -l)
    if [ "$file_count" -gt 0 ]; then
        echo -e "${GREEN}✓ Documents found in data/raw ($file_count files)${NC}"
    else
        echo -e "${YELLOW}⚠ No documents in data/raw${NC}"
        echo "  Add documents to data/raw/ and run: python scripts/ingest.py"
    fi
else
    mkdir -p data/raw
    echo -e "${YELLOW}⚠ Created data/raw directory${NC}"
    echo "  Add your documents there and run: python scripts/ingest.py"
fi

echo ""
echo "================================"
echo "Next Steps:"
echo "================================"
echo ""
echo "1. Add OPENAI_API_KEY to .env if not already done"
echo "2. Add your documents to data/raw/"
echo "3. Run: python scripts/ingest.py"
echo "4. Try a query: python scripts/query_cli.py 'your question'"
echo ""
echo "For more info, see:"
echo "  - LANGCHAIN_QUICKSTART.md (beginner guide)"
echo "  - LANGCHAIN_MIGRATION.md (detailed changes)"
echo "  - REFACTORING_SUMMARY.md (technical summary)"
echo ""
