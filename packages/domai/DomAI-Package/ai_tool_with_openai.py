#!/usr/bin/env python3
"""
AI Tool with OpenAI Integration
Securely uses OpenAI API for code generation and task understanding
"""

import os
import pyautogui
import time
import subprocess
import json
from pathlib import Path
from git import Repo
from transformers import pipeline
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

class AIToolWithOpenAI:
    def __init__(self):
        # Initialize OpenAI client with API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
            print("   Please create a .env file with your OpenAI API key")
            print("   Example: OPENAI_API_KEY=sk-...")
            self.openai_client = None
        else:
            self.openai_client = openai.OpenAI(api_key=api_key)
            print("✅ OpenAI API initialized")
        
        # Fallback NLP model for basic understanding
        self.nlp_model = pipeline('text-classification', 
                                 model='distilbert-base-uncased-finetuned-sst-2-english')
    
    def understand_command_with_gpt(self, command):
        """Use GPT to understand and classify the command"""
        if not self.openai_client:
            # Fallback to basic NLP
            return self.nlp_model(command)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a command classifier. Classify the user's command into one of these categories: open_website, write_code, clone_repository, build_pipeline, install_package, or unknown. Respond with just the category name."},
                    {"role": "user", "content": command}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            category = response.choices[0].message.content.strip().lower()
            return {"category": category, "command": command}
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {"category": "unknown", "command": command}
    
    def generate_code_with_gpt(self, task_description):
        """Generate actual code using GPT-4"""
        if not self.openai_client:
            # Fallback to template
            return f"# Generated code for: {task_description}\nprint('OpenAI API key not configured')"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert Python programmer. Generate clean, working Python code based on the user's description. Include proper error handling and comments."},
                    {"role": "user", "content": f"Write Python code to: {task_description}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Code generation error: {e}")
            return f"# Error generating code: {e}\nprint('Failed to generate code')"
    
    def execute_task(self, task_description):
        """Execute tasks based on description"""
        # Use GPT to understand the command
        interpretation = self.understand_command_with_gpt(task_description)
        category = interpretation.get('category', 'unknown')
        
        print(f"Interpreted as: {category}")
        
        if category == 'open_website' or 'open' in task_description.lower():
            self.open_website(task_description)
        elif category == 'write_code' or 'write code' in task_description.lower():
            self.write_code(task_description)
        elif category == 'clone_repository' or 'pull repo' in task_description.lower():
            self.pull_repo(task_description)
        elif category == 'build_pipeline' or 'n8n' in task_description.lower():
            self.build_n8n_pipeline(task_description)
        elif category == 'install_package' or 'install' in task_description.lower():
            self.install_package(task_description)
        else:
            print(f"Task not recognized: {task_description}")
            if self.openai_client:
                self.suggest_alternatives(task_description)
    
    def suggest_alternatives(self, task_description):
        """Use GPT to suggest how to handle unknown tasks"""
        if not self.openai_client:
            return
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Suggest how to handle this task in 1-2 sentences."},
                    {"role": "user", "content": task_description}
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            suggestion = response.choices[0].message.content
            print(f"💡 Suggestion: {suggestion}")
            
        except Exception as e:
            print(f"Could not generate suggestion: {e}")
    
    def open_website(self, task_description):
        """Open website based on task description"""
        # Common websites
        sites = {
            'canva': 'https://www.canva.com',
            'github': 'https://github.com',
            'google': 'https://www.google.com',
            'n8n': 'https://n8n.io',
            'openai': 'https://platform.openai.com'
        }
        
        for site, url in sites.items():
            if site in task_description.lower():
                subprocess.run(['open', '-a', 'Google Chrome', url])
                print(f"✅ Opened {site} at {url}")
                time.sleep(3)
                return
        
        # Try to extract URL from the command
        if 'http' in task_description:
            import re
            urls = re.findall(r'https?://[^\s]+', task_description)
            if urls:
                subprocess.run(['open', '-a', 'Google Chrome', urls[0]])
                print(f"✅ Opened {urls[0]}")
                return
        
        print("❌ Could not identify website to open")
    
    def write_code(self, task_description):
        """Generate and save code using GPT"""
        # Extract the actual coding task
        if 'write code' in task_description.lower():
            coding_task = task_description.lower().replace('write code', '').strip()
        else:
            coding_task = task_description
        
        print(f"Generating code for: {coding_task}")
        code = self.generate_code_with_gpt(coding_task)
        
        # Save the generated code
        timestamp = int(time.time())
        filename = f"generated_{timestamp}.py"
        
        with open(filename, 'w') as f:
            f.write(code)
        
        print(f"✅ Code saved to {filename}")
        print("\nGenerated code preview:")
        print("-" * 40)
        print(code[:500] + "..." if len(code) > 500 else code)
        print("-" * 40)
        
        return filename
    
    def pull_repo(self, task_description):
        """Clone a GitHub repository"""
        # Extract GitHub URL
        import re
        github_pattern = r'github\.com/[\w-]+/[\w-]+'
        matches = re.findall(github_pattern, task_description)
        
        if matches:
            repo_url = f"https://{matches[0]}"
            repo_name = repo_url.split('/')[-1]
            
            # Create extensions directory
            extensions_dir = Path("extensions")
            extensions_dir.mkdir(exist_ok=True)
            repo_path = extensions_dir / repo_name
            
            try:
                print(f"Cloning {repo_url}...")
                Repo.clone_from(repo_url, repo_path)
                print(f"✅ Repository cloned to {repo_path}")
                
                # Check for README
                readme_path = repo_path / "README.md"
                if readme_path.exists():
                    print("📄 Found README.md - reading first few lines:")
                    with open(readme_path, 'r') as f:
                        lines = f.readlines()[:5]
                        for line in lines:
                            print(f"   {line.rstrip()}")
                
            except Exception as e:
                print(f"❌ Error cloning repository: {e}")
        else:
            print("❌ No GitHub URL found in command")
    
    def build_n8n_pipeline(self, task_description):
        """Build an n8n workflow pipeline"""
        # Extract pipeline name
        pipeline_name = "ai_generated_workflow"
        if 'named' in task_description:
            words = task_description.split()
            if 'named' in words:
                idx = words.index('named')
                if idx + 1 < len(words):
                    pipeline_name = words[idx + 1].strip('.,!?')
        
        # Generate pipeline with GPT if available
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Generate a valid n8n workflow JSON. Include webhook trigger, data processing, and output nodes."},
                        {"role": "user", "content": f"Create n8n workflow: {task_description}"}
                    ],
                    temperature=0.5,
                    max_tokens=1500
                )
                
                pipeline_json = response.choices[0].message.content
                # Try to parse as JSON
                try:
                    pipeline = json.loads(pipeline_json)
                except:
                    # Fallback to basic pipeline
                    pipeline = self.create_basic_pipeline(pipeline_name)
            except:
                pipeline = self.create_basic_pipeline(pipeline_name)
        else:
            pipeline = self.create_basic_pipeline(pipeline_name)
        
        # Save pipeline
        filename = f"{pipeline_name}_workflow.json"
        with open(filename, 'w') as f:
            json.dump(pipeline, f, indent=2)
        
        print(f"✅ n8n workflow saved to {filename}")
        print(f"   Nodes: {len(pipeline.get('nodes', []))}")
        return filename
    
    def create_basic_pipeline(self, name):
        """Create a basic n8n pipeline structure"""
        return {
            "name": name,
            "nodes": [
                {
                    "parameters": {
                        "path": f"/{name}-webhook",
                        "options": {}
                    },
                    "id": "webhook",
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "jsCode": "// Process data here\nreturn items;"
                    },
                    "id": "code",
                    "name": "Process",
                    "type": "n8n-nodes-base.code",
                    "position": [450, 300]
                }
            ],
            "connections": {
                "Webhook": {
                    "main": [[{"node": "Process", "type": "main", "index": 0}]]
                }
            }
        }
    
    def install_package(self, task_description):
        """Install Python packages"""
        # Extract package name
        words = task_description.split()
        packages = []
        
        for i, word in enumerate(words):
            if word.lower() in ['install', 'add']:
                if i + 1 < len(words):
                    packages.append(words[i + 1])
        
        if not packages:
            print("❌ No package name found")
            return
        
        for package in packages:
            print(f"Installing {package}...")
            result = subprocess.run(
                ['pip', 'install', package],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully installed {package}")
            else:
                print(f"❌ Failed to install {package}")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
    
    def run(self):
        """Main interaction loop"""
        print("\n" + "="*60)
        print("🤖 AI Tool with OpenAI Integration")
        print("="*60)
        
        if self.openai_client:
            print("✅ OpenAI API connected - Full capabilities available")
        else:
            print("⚠️  Running in limited mode - Set OPENAI_API_KEY in .env file")
        
        print("\nAvailable commands:")
        print("  • open [website] - Open website in browser")
        print("  • write code [description] - Generate code with AI")
        print("  • pull repo github.com/[user/repo] - Clone repository")
        print("  • build n8n pipeline named [name] - Create workflow")
        print("  • install [package] - Install Python package")
        print("  • quit - Exit the tool")
        print("\n" + "="*60 + "\n")
        
        while True:
            try:
                command = input("🤖 > ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if command:
                    self.execute_task(command)
                    print()  # Add spacing between commands
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == '__main__':
    tool = AIToolWithOpenAI()
    tool.run()