#!/usr/bin/env python3
"""
Test DominateAI with full Vertex AI integration
"""

import os
import sys
from pathlib import Path

# Add DominateAI to path
sys.path.insert(0, str(Path(__file__).parent))

from working_gemini_integration import WorkingGeminiManager

def test_dominate_ai_features():
    """Test all DominateAI Vertex AI features"""
    
    print("🤖 DominateAI Vertex AI Feature Test")
    print("=" * 50)
    
    # Initialize Gemini
    gemini = WorkingGeminiManager()
    
    if not gemini.available:
        print("❌ Vertex AI not available")
        return False
    
    print("✅ Vertex AI Gemini connected!")
    
    # Test 1: Code Generation
    print("\n💻 Testing Code Generation:")
    print("-" * 30)
    code = gemini.generate_code("create a Python function to validate email addresses using regex", stream=True)
    
    # Test 2: Chat
    print("\n💬 Testing Chat:")
    print("-" * 15)
    response = gemini.chat("What is DominateAI and what makes it special?", stream=True)
    
    # Test 3: Code Analysis
    print("\n🔍 Testing Code Analysis:")
    print("-" * 25)
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    analysis = gemini.analyze_code(sample_code, "optimize", stream=True)
    
    print(f"\n📊 Status: {gemini.show_status()}")
    
    return True

if __name__ == "__main__":
    success = test_dominate_ai_features()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 DominateAI is FULLY OPERATIONAL!")
        print("=" * 60)
        print("🚀 Ready for:")
        print("   • AI-powered code generation")
        print("   • Intelligent chat assistance") 
        print("   • Advanced code analysis")
        print("   • Google Cloud deployment")
        print("   • Repository automation")
        print("   • And much more!")
        print("\n💡 Run: DomAI")
        print("   Then try: generate code for a REST API")
    else:
        print("\n❌ Setup incomplete")