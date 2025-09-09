# enhanced_ai_tool.py
# Enhanced version with better NLP and LLM integration

import pyautogui
import time
import subprocess
import os
import json
import importlib.util
from git import Repo
from transformers import pipeline
from pathlib import Path

class EnhancedAITool:
    def __init__(self):
        # Use a zero-shot classification model for better command understanding
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        self.task_labels = [
            "open website",
            "write code",
            "clone repository",
            "build pipeline",
            "install tool",
            "execute script"
        ]
        self.loaded_extensions = {}
        
    def understand_command(self, command):
        """Better command interpretation using zero-shot classification"""
        result = self.classifier(command, candidate_labels=self.task_labels)
        return {
            'task': result['labels'][0],
            'confidence': result['scores'][0],
            'command': command
        }
    
    def execute_task(self, interpretation):
        """Execute task based on interpretation"""
        task = interpretation['task']
        command = interpretation['command']
        
        print(f"Executing: {task} (confidence: {interpretation['confidence']:.2f})")
        
        if task == "open website":
            self.open_website(command)
        elif task == "write code":
            self.write_code(command)
        elif task == "clone repository":
            self.clone_and_extend(command)
        elif task == "build pipeline":
            self.build_n8n_pipeline(command)
        elif task == "install tool":
            self.install_extension(command)
        elif task == "execute script":
            self.execute_extension(command)
        else:
            print(f"Task '{task}' not fully implemented yet")
    
    def open_website(self, command):
        """Open website based on command"""
        sites = {
            'canva': 'https://www.canva.com',
            'github': 'https://github.com',
            'n8n': 'https://n8n.io'
        }
        
        for site, url in sites.items():
            if site in command.lower():
                subprocess.run(['open', '-a', 'Google Chrome', url])
                print(f"Opened {site} at {url}")
                return
        
        print("Website not recognized. Add it to the sites dictionary.")
    
    def write_code(self, command):
        """Generate and write code based on description"""
        # Extract the code description
        desc = command.replace("write code", "").strip()
        
        # For now, create a template. In production, use OpenAI/Anthropic API
        code = f'''#!/usr/bin/env python3
"""
Generated code for: {desc}
"""

def main():
    # TODO: Implement {desc}
    print("Implementing: {desc}")
    pass

if __name__ == "__main__":
    main()
'''
        
        filename = f"generated_{int(time.time())}.py"
        with open(filename, 'w') as f:
            f.write(code)
        print(f"Code written to {filename}")
        return filename
    
    def clone_and_extend(self, command):
        """Clone repository and auto-load extensions"""
        # Extract GitHub URL
        if 'github.com/' in command:
            start = command.find('github.com/')
            url_part = command[start:]
            repo_url = f"https://{url_part.split()[0]}"
            
            # Extract repo name for directory
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            extensions_dir = Path("extensions")
            extensions_dir.mkdir(exist_ok=True)
            repo_path = extensions_dir / repo_name
            
            try:
                print(f"Cloning {repo_url}...")
                Repo.clone_from(repo_url, repo_path)
                print(f"Repository cloned to {repo_path}")
                
                # Auto-detect and load Python extensions
                self.scan_and_load_extensions(repo_path)
                
            except Exception as e:
                print(f"Error cloning repository: {e}")
    
    def scan_and_load_extensions(self, repo_path):
        """Scan cloned repo for loadable extensions"""
        # Look for Python files that might be extensions
        for py_file in repo_path.rglob("*.py"):
            if py_file.name.startswith("extension_") or py_file.name.endswith("_tool.py"):
                self.load_extension(py_file)
    
    def load_extension(self, module_path):
        """Dynamically load a Python extension"""
        try:
            module_name = module_path.stem
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Store the loaded module
            self.loaded_extensions[module_name] = module
            print(f"✓ Loaded extension: {module_name}")
            
            # Register new capabilities if the module has them
            if hasattr(module, 'register_capabilities'):
                new_tasks = module.register_capabilities()
                self.task_labels.extend(new_tasks)
                print(f"  Added capabilities: {new_tasks}")
                
        except Exception as e:
            print(f"Failed to load {module_path}: {e}")
    
    def build_n8n_pipeline(self, command):
        """Build n8n pipeline with more sophisticated generation"""
        # Extract pipeline name
        pipeline_name = "automation_pipeline"
        if 'named' in command:
            parts = command.split('named')
            if len(parts) > 1:
                pipeline_name = parts[1].strip().split()[0]
        
        # Create a more complex pipeline
        pipeline = {
            "name": pipeline_name,
            "nodes": [
                {
                    "parameters": {
                        "path": f"{pipeline_name}-webhook",
                        "options": {}
                    },
                    "id": "webhook_trigger",
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "jsCode": "// Process incoming data\nreturn items;"
                    },
                    "id": "code_processor",
                    "name": "Process Data",
                    "type": "n8n-nodes-base.code",
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "resource": "message",
                        "operation": "send"
                    },
                    "id": "slack_notifier",
                    "name": "Send Notification",
                    "type": "n8n-nodes-base.slack",
                    "position": [650, 300]
                }
            ],
            "connections": {
                "Webhook Trigger": {
                    "main": [[{"node": "Process Data", "type": "main", "index": 0}]]
                },
                "Process Data": {
                    "main": [[{"node": "Send Notification", "type": "main", "index": 0}]]
                }
            }
        }
        
        filename = f"{pipeline_name}_pipeline.json"
        with open(filename, 'w') as f:
            json.dump(pipeline, f, indent=2)
        print(f"✓ n8n pipeline created: {filename}")
        print(f"  Contains {len(pipeline['nodes'])} nodes")
        return filename
    
    def install_extension(self, command):
        """Install new tools/packages based on command"""
        # Extract package name
        if 'install' in command:
            package = command.split('install')[-1].strip()
            if package:
                print(f"Installing {package}...")
                result = subprocess.run(
                    ['pip', 'install', package],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"✓ Successfully installed {package}")
                else:
                    print(f"✗ Failed to install {package}: {result.stderr}")
    
    def execute_extension(self, command):
        """Execute loaded extensions"""
        for name, module in self.loaded_extensions.items():
            if name in command:
                if hasattr(module, 'execute'):
                    result = module.execute(command)
                    print(f"Extension {name} result: {result}")
                    return
        print("No matching extension found for execution")
    
    def run(self):
        """Main interaction loop"""
        print("🤖 Enhanced AI Tool Ready!")
        print("=" * 50)
        print("Capabilities:")
        for task in self.task_labels:
            print(f"  • {task}")
        print("\nType 'quit' to exit\n")
        
        while True:
            try:
                command = input("Command > ").strip()
                if command.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                if command:
                    interpretation = self.understand_command(command)
                    self.execute_task(interpretation)
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    tool = EnhancedAITool()
    tool.run()