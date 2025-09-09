#!/usr/bin/env python3
"""
Google GenAI (Gemini) Integration for DominateAI
Uses the streamlined Google GenAI SDK for better performance
"""

import os
import json
import time
from typing import List, Dict, Optional
import subprocess

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError as e:
    GENAI_AVAILABLE = False
    print(f"Google GenAI SDK not available: {e}")

class GeminiManager:
    def __init__(self):
        self.available = False
        self.client = None
        
        if GENAI_AVAILABLE:
            try:
                # Try to initialize with Vertex AI
                self.client = genai.Client(
                    vertexai=True,
                    # API key from environment or use default credentials
                    api_key=os.environ.get("GOOGLE_CLOUD_API_KEY")
                )
                
                # Test connection
                self._test_connection()
                self.available = True
                print("✅ Gemini (Google GenAI) initialized with Vertex AI")
                
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")
                print("   Make sure GOOGLE_CLOUD_API_KEY is set or gcloud auth is configured")
                self.available = False
        else:
            print("❌ Google GenAI SDK not installed")
    
    def _test_connection(self):
        """Test if we can connect to Gemini"""
        try:
            # Quick test generation
            response = list(self.client.models.generate_content_stream(
                model="gemini-2.5-flash-lite",
                contents=[types.Content(
                    role="user",
                    parts=[types.Part.from_text("Say 'test' only")]
                )],
                config=types.GenerateContentConfig(max_output_tokens=10)
            ))
            
            if not response:
                raise Exception("No response from Gemini")
                
        except Exception as e:
            raise Exception(f"Connection test failed: {e}")
    
    def generate_code(self, description: str, language: str = "python", stream: bool = False) -> str:
        """Generate code using Gemini 2.5 Flash"""
        if not self.available:
            return f"# Gemini not available\n# Task: {description}"
        
        try:
            prompt = f"""Generate clean, production-ready {language} code for: {description}

Requirements:
- Include proper error handling
- Add clear, helpful comments
- Follow best practices for {language}
- Include example usage if applicable
- Make it modular and reusable

Please provide only the code without explanations:"""
            
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(prompt)]
            )]
            
            config = types.GenerateContentConfig(
                temperature=0.3,  # Lower for more consistent code
                top_p=0.95,
                max_output_tokens=4000,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
                ]
            )
            
            if stream:
                # Stream response for real-time display
                result = ""
                for chunk in self.client.models.generate_content_stream(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=config
                ):
                    if chunk.text:
                        result += chunk.text
                        print(chunk.text, end="", flush=True)
                return result
            else:
                # Get complete response
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=config
                )
                return response.text if response.text else f"# Code generation failed for: {description}"
                
        except Exception as e:
            return f"# Error generating code: {e}\n# Task: {description}"
    
    def chat(self, message: str, conversation_history: List[Dict] = None, stream: bool = False) -> str:
        """Chat with Gemini with conversation history"""
        if not self.available:
            return "Gemini not available for chat."
        
        try:
            # Build conversation contents
            contents = []
            
            # Add conversation history
            if conversation_history:
                for turn in conversation_history[-10:]:  # Last 10 turns
                    contents.append(types.Content(
                        role=turn.get('role', 'user'),
                        parts=[types.Part.from_text(turn.get('content', ''))]
                    ))
            
            # Add current message
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(message)]
            ))
            
            config = types.GenerateContentConfig(
                temperature=0.9,  # Higher for more creative responses
                top_p=0.95,
                max_output_tokens=2000,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
                ]
            )
            
            if stream:
                # Stream response for real-time chat
                result = ""
                for chunk in self.client.models.generate_content_stream(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=config
                ):
                    if chunk.text:
                        result += chunk.text
                        print(chunk.text, end="", flush=True)
                return result
            else:
                # Get complete response
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=config
                )
                return response.text if response.text else "I couldn't generate a response."
                
        except Exception as e:
            return f"Chat error: {e}"
    
    def analyze_code(self, code: str, task: str = "analyze", stream: bool = False) -> str:
        """Analyze code with specific tasks"""
        if not self.available:
            return "Gemini not available for code analysis."
        
        prompts = {
            "analyze": f"Analyze this code and provide detailed insights about its structure, logic, and potential improvements:\n\n```\n{code}\n```",
            "fix": f"Find bugs and security issues in this code, then provide the corrected version:\n\n```\n{code}\n```",
            "optimize": f"Optimize this code for better performance, readability, and efficiency:\n\n```\n{code}\n```",
            "explain": f"Explain what this code does in simple, clear terms:\n\n```\n{code}\n```",
            "review": f"Provide a comprehensive code review with specific suggestions for improvement:\n\n```\n{code}\n```",
            "document": f"Generate comprehensive documentation for this code including docstrings and comments:\n\n```\n{code}\n```"
        }
        
        prompt = prompts.get(task, prompts["analyze"])
        
        try:
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(prompt)]
            )]
            
            config = types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.95,
                max_output_tokens=3000,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
                ]
            )
            
            if stream:
                result = ""
                for chunk in self.client.models.generate_content_stream(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=config
                ):
                    if chunk.text:
                        result += chunk.text
                        print(chunk.text, end="", flush=True)
                return result
            else:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=contents,
                    config=config
                )
                return response.text if response.text else "Analysis failed."
                
        except Exception as e:
            return f"Analysis error: {e}"
    
    def generate_deployment_config(self, description: str, platform: str = "gcp") -> str:
        """Generate deployment configurations"""
        if not self.available:
            return f"# Gemini not available\n# Deployment for: {description}"
        
        try:
            prompt = f"""Generate deployment configuration for: {description}

Platform: {platform}
Requirements:
- Production-ready configuration
- Include necessary environment variables
- Add security best practices
- Include scaling settings
- Add monitoring/logging setup

Please provide complete configuration files:"""
            
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(prompt)]
            )]
            
            config = types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.95,
                max_output_tokens=3000,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF"),
                ]
            )
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=contents,
                config=config
            )
            
            return response.text if response.text else f"# Configuration generation failed for: {description}"
            
        except Exception as e:
            return f"# Error generating deployment config: {e}\n# Task: {description}"
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.available:
            return []
        
        try:
            # For now, return known models
            return [
                "gemini-2.5-flash-lite",
                "gemini-1.5-flash", 
                "gemini-1.5-pro"
            ]
        except Exception as e:
            print(f"Error getting models: {e}")
            return []
    
    def show_status(self) -> Dict:
        """Show Gemini status and configuration"""
        status = {
            'available': self.available,
            'sdk_installed': GENAI_AVAILABLE,
            'vertex_ai': True,  # We're using Vertex AI backend
            'models': self.get_available_models() if self.available else []
        }
        
        # Check authentication
        if os.environ.get("GOOGLE_CLOUD_API_KEY"):
            status['auth_method'] = 'API Key'
        else:
            status['auth_method'] = 'Default Credentials'
        
        return status


# Convenience functions for DomAI integration
def quick_generate_code(description: str, language: str = "python", stream: bool = False) -> str:
    """Quick code generation using Gemini"""
    gemini = GeminiManager()
    return gemini.generate_code(description, language, stream)

def quick_chat(message: str, stream: bool = False) -> str:
    """Quick chat with Gemini"""
    gemini = GeminiManager()
    return gemini.chat(message, stream=stream)

def quick_analyze_code(code: str, task: str = "analyze", stream: bool = False) -> str:
    """Quick code analysis"""
    gemini = GeminiManager()
    return gemini.analyze_code(code, task, stream)

if __name__ == "__main__":
    # Test Gemini integration
    print("🤖 Testing Gemini Integration")
    print("=" * 50)
    
    gemini = GeminiManager()
    
    if gemini.available:
        print("✅ Gemini is ready!")
        
        # Test code generation
        print("\n🧪 Testing code generation...")
        test_code = gemini.generate_code("create a function to validate email addresses with regex")
        print("Generated code preview:")
        print(test_code[:300] + "..." if len(test_code) > 300 else test_code)
        
        # Test chat
        print("\n💬 Testing chat...")
        response = gemini.chat("What makes DominateAI special?")
        print(f"Chat response: {response[:150]}...")
        
        # Show status
        print("\n📊 Status:")
        status = gemini.show_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
            
    else:
        print("❌ Gemini not available")
        print("Set up authentication:")
        print("  1. Set GOOGLE_CLOUD_API_KEY environment variable, OR")
        print("  2. Run: gcloud auth application-default login")