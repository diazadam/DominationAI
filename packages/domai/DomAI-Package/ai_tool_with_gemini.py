#!/usr/bin/env python3
"""
AI Tool with Google Gemini Integration
Uses Google GenAI SDK for enhanced AI capabilities
"""

import os
import json
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Import integrations
from gemini_integration import GeminiManager
from gcp_deployer import GCPDeployer
from ai_tool_with_gcp import AIToolWithGCP

load_dotenv()

class AIToolWithGemini(AIToolWithGCP):
    def __init__(self):
        # Initialize parent class (GCP functionality)
        super().__init__()
        
        # Initialize Gemini
        self.gemini = GeminiManager()
        
        if self.gemini.available:
            print("✅ Gemini AI integrated")
        else:
            print("⚠️  Gemini not available - using fallback OpenAI")
    
    def generate_code_with_gpt(self, task_description):
        """Enhanced code generation with Gemini as primary, OpenAI as fallback"""
        
        if self.gemini.available:
            print("🧠 Generating code with Gemini...")
            return self.gemini.generate_code(task_description, stream=True)
        elif self.openai_client:
            print("🧠 Generating code with OpenAI...")
            return super().generate_code_with_gpt(task_description)
        else:
            return f"# No AI available for code generation\n# Task: {task_description}"
    
    def understand_command_with_gpt(self, command):
        """Enhanced command understanding with Gemini"""
        
        if self.gemini.available:
            try:
                analysis_prompt = f"""Analyze this command and classify it into one of these categories:
- deploy_website
- deploy_api  
- deploy_function
- create_webhook
- generate_code
- analyze_code
- open_website
- clone_repository
- chat_request
- system_command
- unknown

Command: "{command}"

Respond with just the category name and confidence (0-100):"""
                
                response = self.gemini.chat(analysis_prompt)
                
                # Parse response
                lines = response.strip().split('\n')
                category = lines[0].lower().replace('-', '_')
                
                return {"category": category, "command": command, "confidence": 90}
                
            except Exception as e:
                print(f"Command analysis failed: {e}")
        
        # Fallback to parent method
        return super().understand_command_with_gpt(command)
    
    def execute_task(self, task_description):
        """Enhanced task execution with Gemini integration"""
        
        # Get command understanding
        interpretation = self.understand_command_with_gpt(task_description)
        category = interpretation.get('category', 'unknown')
        
        print(f"🎯 Task: {category}")
        
        # Handle Gemini-specific commands
        if 'chat' in task_description.lower() or category == 'chat_request':
            self.handle_chat_request(task_description)
        elif 'analyze code' in task_description.lower() or category == 'analyze_code':
            self.handle_code_analysis(task_description)
        elif 'generate' in task_description.lower() and 'code' in task_description.lower():
            self.handle_code_generation(task_description)
        elif 'streaming' in task_description.lower() or 'stream' in task_description.lower():
            self.handle_streaming_request(task_description)
        else:
            # Fall back to parent class methods
            super().execute_task(task_description)
    
    def handle_chat_request(self, request):
        """Handle conversational requests with Gemini"""
        
        # Extract the actual question/message
        message = request.lower().replace('chat', '').replace('ask', '').strip()
        if message.startswith('about') or message.startswith('with'):
            message = message[5:].strip()
        
        if not message:
            message = "Hello! What can you help me with regarding automation and deployment?"
        
        print("\n💬 Gemini Response:")
        print("-" * 40)
        
        if self.gemini.available:
            response = self.gemini.chat(message, stream=True)
            print("\n" + "-" * 40)
        else:
            print("Chat not available - Gemini not configured")
    
    def handle_code_analysis(self, request):
        """Handle code analysis requests"""
        
        print("\n🔍 Code Analysis:")
        print("-" * 30)
        
        # Check if there's a file mentioned
        if '.py' in request or '.js' in request or '.html' in request:
            # Try to extract filename
            words = request.split()
            for word in words:
                if '.' in word and not word.startswith('http'):
                    filepath = Path(word)
                    if filepath.exists():
                        print(f"📁 Analyzing file: {filepath}")
                        code = filepath.read_text()
                        
                        # Determine analysis type
                        if 'fix' in request.lower():
                            task = 'fix'
                        elif 'optimize' in request.lower():
                            task = 'optimize'
                        elif 'explain' in request.lower():
                            task = 'explain'
                        elif 'review' in request.lower():
                            task = 'review'
                        else:
                            task = 'analyze'
                        
                        if self.gemini.available:
                            self.gemini.analyze_code(code, task, stream=True)
                        else:
                            print("Code analysis not available - Gemini not configured")
                        return
        
        print("Please specify a code file to analyze")
        print("Example: analyze code main.py")
    
    def handle_code_generation(self, request):
        """Handle code generation with streaming"""
        
        # Extract language if specified
        language = "python"  # default
        if 'javascript' in request.lower() or 'js' in request.lower():
            language = "javascript"
        elif 'html' in request.lower():
            language = "html"
        elif 'css' in request.lower():
            language = "css"
        elif 'bash' in request.lower() or 'shell' in request.lower():
            language = "bash"
        elif 'go' in request.lower():
            language = "go"
        elif 'rust' in request.lower():
            language = "rust"
        
        # Extract the task description
        task = request.lower()
        for prefix in ['generate code', 'write code', 'create code', 'code for']:
            task = task.replace(prefix, '').strip()
        
        print(f"\n💻 Generating {language} code:")
        print("-" * 40)
        
        if self.gemini.available:
            code = self.gemini.generate_code(task, language, stream=True)
            
            print("\n" + "-" * 40)
            
            # Save the generated code
            timestamp = int(time.time())
            extension_map = {
                'python': 'py',
                'javascript': 'js', 
                'html': 'html',
                'css': 'css',
                'bash': 'sh',
                'go': 'go',
                'rust': 'rs'
            }
            
            ext = extension_map.get(language, 'txt')
            filename = f"generated_{timestamp}.{ext}"
            
            # Clean code for saving (remove markdown formatting)
            clean_code = code
            if '```' in clean_code:
                parts = clean_code.split('```')
                if len(parts) >= 3:
                    clean_code = parts[1]
                    if clean_code.startswith(language):
                        clean_code = clean_code[len(language):].strip()
            
            with open(filename, 'w') as f:
                f.write(clean_code)
            
            print(f"💾 Code saved to: {filename}")
        else:
            print("Code generation not available - Gemini not configured")
    
    def handle_streaming_request(self, request):
        """Handle requests that specifically want streaming output"""
        
        print("\n🌊 Streaming Response:")
        print("-" * 30)
        
        if self.gemini.available:
            # Remove 'streaming' from request
            clean_request = request.replace('streaming', '').replace('stream', '').strip()
            self.gemini.chat(clean_request, stream=True)
            print("\n" + "-" * 30)
        else:
            print("Streaming not available - Gemini not configured")
    
    def show_enhanced_status(self):
        """Show enhanced status including Gemini"""
        print("🔍 DominateAI Enhanced Status:")
        print("=" * 50)
        
        # Base status
        super().show_status()
        
        # Gemini status
        if hasattr(self, 'gemini'):
            print("\n🧠 Gemini AI Status:")
            status = self.gemini.show_status()
            for key, value in status.items():
                if key == 'models' and isinstance(value, list):
                    print(f"  {key}: {', '.join(value) if value else 'None'}")
                else:
                    print(f"  {key}: {value}")
    
    def run(self):
        """Enhanced run method with Gemini features"""
        print("\n" + "="*70)
        print("🤖 DominateAI with Google Gemini Integration")
        print("="*70)
        
        # Show AI status
        if self.gemini.available:
            print("🧠 Gemini AI: ✅ Ready for advanced code generation and chat")
        elif self.openai_client:
            print("🧠 OpenAI: ✅ Available (Gemini fallback)")
        else:
            print("⚠️  AI: Limited capabilities - configure Gemini or OpenAI")
        
        print(f"☁️  Google Cloud: {self.gcp.project_id}")
        print("✅ Ready to code, deploy, and automate!")
        
        print("\n🧠 Enhanced AI Commands:")
        print("  • chat [message] - Chat with Gemini AI")
        print("  • generate code [description] - AI code generation with streaming")
        print("  • analyze code [file] - Deep code analysis")
        print("  • streaming [request] - Get streaming AI responses")
        
        print("\n🚀 Deployment Commands:")
        print("  • deploy website [description] - Static site to Cloud Storage")
        print("  • deploy api [description] - API to Cloud Run")
        print("  • deploy function [description] - Serverless Cloud Function")
        print("  • create webhook - Webhook endpoint")
        
        print("\n🔧 System Commands:")
        print("  • status - Show detailed system status")
        print("  • open [website] - Open in browser")
        print("  • clone [github-url] - Clone repository")
        print("  • quit - Exit DominateAI")
        
        print("\n💡 Examples:")
        print("  • chat about the best deployment strategy")
        print("  • generate code for a REST API with authentication") 
        print("  • analyze code main.py")
        print("  • deploy api for user management")
        
        print("\n" + "="*70 + "\n")
        
        while True:
            try:
                command = input("🤖 DomAI > ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif command.lower() in ['status', 'info']:
                    self.show_enhanced_status()
                elif command:
                    self.execute_task(command)
                    print()
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == '__main__':
    tool = AIToolWithGemini()
    tool.run()