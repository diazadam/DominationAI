#!/usr/bin/env python3
"""
Working Gemini Integration for DominateAI
Uses proper Vertex AI authentication with service account
"""

import os
import json
import time
from typing import List, Dict, Optional
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part, Content
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False

class WorkingGeminiManager:
    def __init__(self):
        self.available = False
        self.model = None
        self.project_id = self._get_project_id()
        
        if VERTEX_AVAILABLE and self.project_id:
            try:
                # Initialize Vertex AI
                vertexai.init(project=self.project_id, location="us-central1")
                self.model = GenerativeModel("gemini-2.0-flash-exp")
                
                # Test with a simple generation
                test_response = self.model.generate_content("Test")
                if test_response and test_response.text:
                    self.available = True
                    print("✅ Vertex AI Gemini initialized and tested successfully!")
                else:
                    print("⚠️  Vertex AI initialized but test failed")
                    
            except Exception as e:
                print(f"⚠️  Vertex AI initialization failed: {e}")
                print("💡 Make sure you have proper authentication:")
                print("   gcloud auth application-default login")
        else:
            print("❌ Vertex AI SDK not available")
    
    def _get_project_id(self):
        """Get current GCP project ID"""
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True, text=True
            )
            project_id = result.stdout.strip() if result.returncode == 0 else None
            if project_id:
                print(f"📊 Using GCP Project: {project_id}")
            return project_id
        except:
            return None
    
    def generate_code(self, description: str, language: str = "python", stream: bool = False) -> str:
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

Provide only the code:"""
            
            if stream:
                print("🧠 Generating code with Gemini...")
                result = ""
                for chunk in self.model.generate_content(prompt, stream=True):
                    if chunk.text:
                        result += chunk.text
                        print(chunk.text, end="", flush=True)
                print()  # New line after streaming
                return result
            else:
                response = self.model.generate_content(prompt)
                return response.text if response and response.text else f"# Code generation failed"
                
        except Exception as e:
            return f"# Error generating code: {e}\n# Task: {description}"
    
    def chat(self, message: str, stream: bool = False, concise: bool = False) -> str:
        """Chat with Gemini"""
        if not self.available:
            return "Gemini not available for chat."
        
        try:
            # Add instruction for concise responses when streaming
            if concise:
                message = f"Please provide a concise, direct response (1-2 sentences max): {message}"
            
            if stream:
                result = ""
                for chunk in self.model.generate_content(message, stream=True):
                    if chunk.text:
                        result += chunk.text
                        print(chunk.text, end="", flush=True)
                        
                        # Add interrupt handling for long responses
                        if len(result) > 500 and not concise:
                            try:
                                # Check if user wants to stop (non-blocking)
                                import select
                                import sys
                                if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                                    user_input = sys.stdin.read(1)
                                    if user_input == '\x1b':  # ESC key
                                        print("\n⏹️  Stopped")
                                        return result
                            except:
                                pass  # Skip interrupt handling if not supported
                
                print()  # New line after streaming
                return result
            else:
                response = self.model.generate_content(message)
                return response.text if response and response.text else "I couldn't generate a response."
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopped")
            return "Response interrupted by user"
        except Exception as e:
            return f"Chat error: {e}"
    
    def analyze_code(self, code: str, task: str = "analyze", stream: bool = False) -> str:
        """Analyze code with Gemini"""
        if not self.available:
            return "Gemini not available for code analysis."
        
        prompts = {
            "analyze": f"Analyze this code and provide detailed insights:\n\n```\n{code}\n```",
            "fix": f"Find bugs and issues, then provide the corrected version:\n\n```\n{code}\n```", 
            "optimize": f"Optimize this code for better performance:\n\n```\n{code}\n```",
            "explain": f"Explain what this code does in simple terms:\n\n```\n{code}\n```",
            "review": f"Provide a comprehensive code review:\n\n```\n{code}\n```"
        }
        
        prompt = prompts.get(task, prompts["analyze"])
        
        try:
            if stream:
                print(f"🔍 {task.title()} with Gemini:")
                print("-" * 40)
                result = ""
                for chunk in self.model.generate_content(prompt, stream=True):
                    if chunk.text:
                        result += chunk.text
                        print(chunk.text, end="", flush=True)
                print("\n" + "-" * 40)
                return result
            else:
                response = self.model.generate_content(prompt)
                return response.text if response and response.text else "Analysis failed."
                
        except Exception as e:
            return f"Analysis error: {e}"
    
    def show_status(self) -> Dict:
        """Show Gemini status"""
        return {
            'available': self.available,
            'backend': 'vertex_ai',
            'project_id': self.project_id,
            'location': 'us-central1',
            'model': 'gemini-1.5-flash',
            'vertex_sdk': VERTEX_AVAILABLE
        }


# Convenience functions for DomAI
def quick_generate_code(description: str, language: str = "python") -> str:
    """Quick code generation"""
    gemini = WorkingGeminiManager()
    return gemini.generate_code(description, language)

def quick_chat(message: str) -> str:
    """Quick chat"""
    gemini = WorkingGeminiManager()
    return gemini.chat(message)

def quick_analyze_code(code: str, task: str = "analyze") -> str:
    """Quick code analysis"""
    gemini = WorkingGeminiManager()
    return gemini.analyze_code(code, task)

if __name__ == "__main__":
    print("🤖 Testing Working Gemini Integration")
    print("=" * 50)
    
    gemini = WorkingGeminiManager()
    
    if gemini.available:
        print("✅ Gemini is working!")
        
        # Test code generation
        print("\n🧪 Testing code generation...")
        code = gemini.generate_code("create a function to validate email addresses", "python", stream=True)
        
        # Test chat
        print("\n💬 Testing chat...")
        response = gemini.chat("What is the purpose of DominateAI?", stream=True)
        
        # Show status
        print(f"\n📊 Status: {gemini.show_status()}")
        
    else:
        print("❌ Gemini not working")
        print("Run: gcloud auth application-default login")