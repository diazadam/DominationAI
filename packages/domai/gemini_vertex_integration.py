#!/usr/bin/env python3
"""
Vertex AI Gemini Integration for DominateAI
Uses Google's Vertex AI for Gemini models
"""

import os
import json
import time
from typing import List, Dict, Optional
import subprocess

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

class VertexGeminiManager:
    def __init__(self):
        self.available = False
        self.client = None
        self.project_id = self._get_project_id()
        
        # Try Vertex AI first (preferred for production)
        if VERTEX_AVAILABLE and self.project_id:
            try:
                vertexai.init(project=self.project_id, location="us-central1")
                self.model = GenerativeModel("gemini-1.5-flash")
                self.available = True
                self.backend = "vertex"
                print("✅ Vertex AI Gemini initialized")
                return
            except Exception as e:
                print(f"⚠️  Vertex AI failed: {e}")
        
        # Fallback to GenAI SDK
        if GENAI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    self.available = True
                    self.backend = "genai"
                    print("✅ Google GenAI initialized")
                    return
                except Exception as e:
                    print(f"⚠️  GenAI failed: {e}")
        
        print("❌ No Gemini backend available")
        print("Setup options:")
        print("  1. Use Vertex AI: gcloud auth application-default login")
        print("  2. Use GenAI: Set GOOGLE_API_KEY environment variable")
    
    def _get_project_id(self):
        """Get current GCP project ID"""
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def generate_code(self, description: str, language: str = "python") -> str:
        """Generate code using Gemini"""
        if not self.available:
            return f"# Gemini not available\n# Task: {description}"
        
        try:
            prompt = f"""Generate clean, production-ready {language} code for: {description}

Requirements:
- Include proper error handling
- Add clear, helpful comments
- Follow {language} best practices
- Include example usage if applicable
- Make it modular and reusable

Provide only the code without explanations:"""
            
            response = self.model.generate_content(prompt)
            return response.text if response.text else f"# Code generation failed for: {description}"
            
        except Exception as e:
            return f"# Error generating code: {e}\n# Task: {description}"
    
    def chat(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Chat with Gemini"""
        if not self.available:
            return "Gemini not available for chat."
        
        try:
            # For now, simple single-turn chat
            # TODO: Implement conversation history
            response = self.model.generate_content(message)
            return response.text if response.text else "I couldn't generate a response."
            
        except Exception as e:
            return f"Chat error: {e}"
    
    def analyze_code(self, code: str, task: str = "analyze") -> str:
        """Analyze code using Gemini"""
        if not self.available:
            return "Gemini not available for code analysis."
        
        prompts = {
            "analyze": f"Analyze this code and provide detailed insights:\n\n```\n{code}\n```",
            "fix": f"Find bugs and issues in this code, then provide the corrected version:\n\n```\n{code}\n```",
            "optimize": f"Optimize this code for better performance and efficiency:\n\n```\n{code}\n```",
            "explain": f"Explain what this code does in simple terms:\n\n```\n{code}\n```",
            "review": f"Provide a comprehensive code review with suggestions:\n\n```\n{code}\n```"
        }
        
        prompt = prompts.get(task, prompts["analyze"])
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response.text else "Analysis failed."
            
        except Exception as e:
            return f"Analysis error: {e}"
    
    def show_status(self) -> Dict:
        """Show Gemini status"""
        return {
            'available': self.available,
            'backend': getattr(self, 'backend', 'none'),
            'project_id': self.project_id,
            'vertex_available': VERTEX_AVAILABLE,
            'genai_available': GENAI_AVAILABLE
        }


# Convenience functions
def quick_generate_code(description: str, language: str = "python") -> str:
    """Quick code generation"""
    gemini = VertexGeminiManager()
    return gemini.generate_code(description, language)

def quick_chat(message: str) -> str:
    """Quick chat with Gemini"""
    gemini = VertexGeminiManager()
    return gemini.chat(message)

def quick_analyze_code(code: str, task: str = "analyze") -> str:
    """Quick code analysis"""
    gemini = VertexGeminiManager()
    return gemini.analyze_code(code, task)

if __name__ == "__main__":
    # Test the integration
    print("🤖 Testing Vertex AI Gemini Integration")
    print("=" * 50)
    
    gemini = VertexGeminiManager()
    
    if gemini.available:
        print(f"✅ Gemini ready with {gemini.backend} backend!")
        
        # Test code generation
        print("\n🧪 Testing code generation...")
        code = gemini.generate_code("create a function to validate email addresses")
        print("Generated code preview:")
        print(code[:200] + "..." if len(code) > 200 else code)
        
        # Test chat
        print("\n💬 Testing chat...")
        response = gemini.chat("What is DominateAI?")
        print(f"Response: {response[:100]}...")
        
    else:
        print("❌ Gemini not available")
        
    # Show status
    status = gemini.show_status()
    print(f"\n📊 Status: {status}")