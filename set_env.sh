#!/bin/bash

# Bright Data API Environment Setup Script

echo "🌐 Setting up Bright Data API environment variables..."

# Instructions for setting up API keys
echo "⚠️  Please set your API keys as environment variables:"
echo ""
echo "For Bright Data API:"
echo "   export BRIGHT_DATA_API_KEY='your_bright_data_api_key_here'"
echo ""
echo "For OpenAI API (optional):"
echo "   export OPENAI_API_KEY='your_openai_api_key_here'"
echo ""

# Check if Bright Data API key is set
if [ -z "$BRIGHT_DATA_API_KEY" ]; then
    echo "❌ BRIGHT_DATA_API_KEY not set"
    echo "   Please set it with: export BRIGHT_DATA_API_KEY='your_api_key_here'"
    exit 1
else
    echo "✅ BRIGHT_DATA_API_KEY is set"
fi

# Check if OpenAI API key is set (optional)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set (optional for Bright Data testing)"
    echo "   Set it with: export OPENAI_API_KEY='your_api_key_here'"
else
    echo "✅ OPENAI_API_KEY is set"
fi

echo ""
echo "🔧 Environment ready for Bright Data API testing"
echo ""
echo "Next steps:"
echo "1. Run: python setup_bright_data.py    (quick setup test)"
echo "2. Run: python test_bright_data_debug.py    (comprehensive testing)"
echo "3. Or use the API in your own scripts" 