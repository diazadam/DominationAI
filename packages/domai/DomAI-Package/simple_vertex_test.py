#!/usr/bin/env python3
"""
Simple test to get Vertex AI working with your setup
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_vertex_ai():
    """Test Vertex AI connection"""
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Get project from environment or gcloud
        project_id = "gen-lang-client-0093497568"  # Your project
        
        print(f"🔧 Initializing Vertex AI for project: {project_id}")
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location="us-central1")
        
        # Create model instance
        model = GenerativeModel("gemini-2.0-flash-exp")
        
        print("🧪 Testing Gemini generation...")
        
        # Test generation
        response = model.generate_content("Say 'Hello from DominateAI!' in a friendly way")
        
        if response and response.text:
            print("✅ SUCCESS!")
            print(f"🤖 Gemini Response: {response.text}")
            return True
        else:
            print("❌ No response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Check if it's an authentication error
        if "authentication" in str(e).lower() or "credentials" in str(e).lower():
            print("\n🔐 Authentication needed:")
            print("   Run: gcloud auth application-default login")
            print("   Or set up a service account key")
        
        return False

if __name__ == "__main__":
    print("🚀 DominateAI Vertex AI Test")
    print("=" * 40)
    
    success = test_vertex_ai()
    
    if success:
        print("\n✅ Vertex AI is ready for DominateAI!")
        print("🎯 You can now use Gemini models for:")
        print("   • Code generation")
        print("   • Chat interactions")
        print("   • Code analysis")
        print("   • Deployment automation")
    else:
        print("\n❌ Setup needed for Vertex AI")
        print("💡 Once authenticated, DominateAI will have full AI powers!")