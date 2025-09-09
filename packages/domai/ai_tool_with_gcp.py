#!/usr/bin/env python3
"""
AI Tool with Google Cloud Platform Integration
Deploy AI-generated apps instantly to GCP services
"""

import os
import json
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import openai
from gcp_deployer import GCPDeployer, quick_deploy_website, quick_deploy_api

# Import base AI tool functionality
from ai_tool_with_openai import AIToolWithOpenAI

load_dotenv()

class AIToolWithGCP(AIToolWithOpenAI):
    def __init__(self):
        super().__init__()
        self.gcp = GCPDeployer()
        print(f"☁️  Google Cloud Project: {self.gcp.project_id}")
        
    def execute_task(self, task_description):
        """Extended task execution with GCP deployment"""
        
        task_lower = task_description.lower()
        
        # GCP-specific deployments
        if 'deploy' in task_lower or 'host' in task_lower:
            if 'cloud run' in task_lower or 'api' in task_lower:
                self.deploy_to_cloud_run(task_description)
            elif 'static' in task_lower or 'website' in task_lower:
                self.deploy_static_site(task_description)
            elif 'function' in task_lower:
                self.deploy_cloud_function(task_description)
            else:
                self.smart_deploy(task_description)
        elif 'create webhook' in task_lower:
            self.create_webhook_endpoint(task_description)
        else:
            # Fall back to parent class implementation
            super().execute_task(task_description)
    
    def smart_deploy(self, description):
        """Intelligently choose deployment method based on content"""
        print("🤖 Analyzing deployment requirements...")
        
        if self.openai_client:
            # Use GPT to determine best deployment method
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Determine if this should be deployed as: static_site, api, or full_app. Respond with just one word."},
                        {"role": "user", "content": description}
                    ],
                    temperature=0.3,
                    max_tokens=10
                )
                
                deployment_type = response.choices[0].message.content.strip().lower()
                
                if 'static' in deployment_type:
                    self.deploy_static_site(description)
                elif 'api' in deployment_type:
                    self.deploy_to_cloud_run(description)
                else:
                    self.deploy_full_app(description)
                    
            except Exception as e:
                print(f"Auto-detection failed: {e}")
                self.deploy_static_site(description)  # Default to static
        else:
            self.deploy_static_site(description)  # Default to static
    
    def deploy_static_site(self, description):
        """Generate and deploy a static website to Cloud Storage"""
        print("🎨 Generating static website...")
        
        # Generate HTML content
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Generate a complete, beautiful HTML page with inline CSS and JavaScript. Make it modern and interactive."},
                        {"role": "user", "content": f"Create a website for: {description}"}
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
                
                html_content = response.choices[0].message.content
                
                # Clean up code blocks if present
                if '```html' in html_content:
                    html_content = html_content.split('```html')[1].split('```')[0]
                elif '```' in html_content:
                    html_content = html_content.split('```')[1].split('```')[0]
                    
            except Exception as e:
                print(f"GPT generation failed: {e}")
                html_content = self.generate_default_html(description)
        else:
            html_content = self.generate_default_html(description)
        
        # Create additional files for a complete website
        files = {
            "index.html": html_content,
            "404.html": self.generate_404_page(),
            "robots.txt": "User-agent: *\nAllow: /"
        }
        
        # Deploy to Cloud Storage
        print("☁️  Deploying to Google Cloud Storage...")
        url = self.gcp.deploy_static_site(files)
        
        if url:
            print(f"\n✨ Website deployed successfully!")
            print(f"🌐 Live URL: {url}")
            print(f"📋 Share this link: {url}")
            
            # Open in browser
            subprocess.run(['open', url])
        else:
            print("❌ Deployment failed. Check your GCP configuration.")
    
    def deploy_to_cloud_run(self, description):
        """Generate and deploy an API/app to Cloud Run"""
        print("⚡ Generating Cloud Run application...")
        
        # Generate Python code for the API
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Generate Python code for a Flask API. Include route handlers and data processing functions."},
                        {"role": "user", "content": f"Create an API for: {description}"}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                api_code = response.choices[0].message.content
                
                # Clean up code blocks
                if '```python' in api_code:
                    api_code = api_code.split('```python')[1].split('```')[0]
                elif '```' in api_code:
                    api_code = api_code.split('```')[1].split('```')[0]
                    
            except Exception as e:
                print(f"Code generation failed: {e}")
                api_code = self.generate_default_api_code(description)
        else:
            api_code = self.generate_default_api_code(description)
        
        # Deploy to Cloud Run
        app_name = f"ai-app-{int(time.time())}"
        print(f"☁️  Deploying to Cloud Run as '{app_name}'...")
        
        url = self.gcp.deploy_to_cloud_run(app_name, api_code)
        
        if url:
            print(f"\n🚀 API deployed successfully!")
            print(f"🔗 Service URL: {url}")
            print(f"\nTest your API:")
            print(f"  curl {url}/api/status")
            print(f"  curl -X POST {url}/api/process -H 'Content-Type: application/json' -d '{{}}'")
            
            # Open in browser
            subprocess.run(['open', url])
        else:
            print("❌ Deployment failed. Make sure Cloud Run API is enabled.")
    
    def deploy_cloud_function(self, description):
        """Deploy a serverless function to Cloud Functions"""
        print("⚡ Generating Cloud Function...")
        
        # Generate function code
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Generate a Python function that processes data. Include a 'process' function that takes a dict and returns a dict."},
                        {"role": "user", "content": f"Create a function for: {description}"}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                function_code = response.choices[0].message.content
                
                # Clean up code blocks
                if '```python' in function_code:
                    function_code = function_code.split('```python')[1].split('```')[0]
                elif '```' in function_code:
                    function_code = function_code.split('```')[1].split('```')[0]
                    
            except:
                function_code = "def process(data):\n    return {'result': 'processed', 'input': data}"
        else:
            function_code = "def process(data):\n    return {'result': 'processed', 'input': data}"
        
        # Deploy function
        function_name = f"ai-function-{int(time.time())}"
        print(f"☁️  Deploying Cloud Function '{function_name}'...")
        
        url = self.gcp.deploy_cloud_function(function_code, function_name)
        
        if url:
            print(f"\n⚡ Cloud Function deployed!")
            print(f"🔗 Endpoint: {url}")
            print(f"\nTest with:")
            print(f"  curl -X POST {url} -H 'Content-Type: application/json' -d '{{}}'")
        else:
            print("❌ Deployment failed. Cloud Functions might need to be enabled.")
    
    def deploy_full_app(self, description):
        """Deploy a full application with frontend and backend"""
        print("🏗️  Building full application...")
        
        # For now, deploy as Cloud Run app with UI
        self.deploy_to_cloud_run(f"full application with web UI for {description}")
    
    def create_webhook_endpoint(self, description):
        """Create a webhook endpoint for n8n or other automation tools"""
        print("🔗 Creating webhook endpoint on Cloud Run...")
        
        webhook_code = """
import json
from datetime import datetime

def process_webhook(data):
    '''Process incoming webhook data'''
    return {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'received_data': data,
        'message': 'Webhook processed successfully'
    }

def handle_n8n_webhook(data):
    '''Special handler for n8n webhooks'''
    if 'workflow' in data:
        return {
            'status': 'success',
            'workflow_id': data.get('workflow', {}).get('id'),
            'execution_time': datetime.now().isoformat()
        }
    return process_webhook(data)
"""
        
        app_name = f"webhook-{int(time.time())}"
        url = self.gcp.deploy_to_cloud_run(app_name, webhook_code)
        
        if url:
            webhook_url = f"{url}/api/process"
            print(f"\n🔗 Webhook endpoint ready!")
            print(f"📥 Webhook URL: {webhook_url}")
            print(f"\nUse this URL in:")
            print(f"  • n8n webhook trigger node")
            print(f"  • GitHub webhooks")
            print(f"  • Any automation platform")
    
    def generate_default_html(self, description):
        """Generate default HTML template"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{description} - Powered by Google Cloud</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #4285f4 0%, #34a853 50%, #fbbc04 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}
        .container {{
            background: white;
            padding: 3rem;
            border-radius: 1rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 800px;
            width: 100%;
            animation: slideIn 0.5s ease-out;
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        h1 {{
            color: #1a73e8;
            margin-bottom: 1rem;
            font-size: 2.5rem;
        }}
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: #f8f9fa;
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            font-size: 0.875rem;
            color: #5f6368;
            margin: 1rem 0;
        }}
        .gcp-logo {{
            width: 20px;
            height: 20px;
        }}
        p {{
            color: #5f6368;
            line-height: 1.6;
            margin: 1rem 0;
        }}
        .features {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .feature {{
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 0.5rem;
            text-align: center;
        }}
        .cta {{
            display: inline-block;
            background: #1a73e8;
            color: white;
            padding: 0.75rem 2rem;
            border-radius: 0.5rem;
            text-decoration: none;
            font-weight: 500;
            margin-top: 1rem;
            transition: background 0.3s;
        }}
        .cta:hover {{
            background: #1557b0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{description}</h1>
        <div class="badge">
            <span>☁️</span>
            <span>Deployed on Google Cloud Platform</span>
        </div>
        <p>This website was automatically generated by AI and deployed to Google Cloud Storage in seconds.</p>
        
        <div class="features">
            <div class="feature">
                <h3>🚀 Instant</h3>
                <p>Deployed in seconds</p>
            </div>
            <div class="feature">
                <h3>🌍 Global</h3>
                <p>Served from GCP CDN</p>
            </div>
            <div class="feature">
                <h3>🔒 Secure</h3>
                <p>HTTPS by default</p>
            </div>
        </div>
        
        <p>Built with AI-powered automation using Google Cloud Storage for static hosting.</p>
        
        <a href="#" class="cta">Get Started</a>
    </div>
    
    <script>
        // Add some interactivity
        document.querySelector('.cta').addEventListener('click', (e) => {{
            e.preventDefault();
            alert('This website was deployed to Google Cloud Platform!');
        }});
        
        // Animate features on load
        document.querySelectorAll('.feature').forEach((el, i) => {{
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            setTimeout(() => {{
                el.style.transition = 'all 0.5s ease';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }}, 100 * i);
        }});
    </script>
</body>
</html>"""
    
    def generate_404_page(self):
        """Generate 404 error page"""
        return """<!DOCTYPE html>
<html>
<head>
    <title>404 - Page Not Found</title>
    <style>
        body {
            font-family: 'Google Sans', sans-serif;
            background: linear-gradient(135deg, #4285f4, #ea4335);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
        }
        h1 { font-size: 5rem; margin: 0; }
        p { font-size: 1.5rem; }
        a {
            color: white;
            text-decoration: none;
            background: rgba(255,255,255,0.2);
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            display: inline-block;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <p>Page not found</p>
        <a href="/">Go Home</a>
    </div>
</body>
</html>"""
    
    def generate_default_api_code(self, description):
        """Generate default API code"""
        return f"""
# Auto-generated API for: {description}

def process_data(data):
    '''Process incoming data'''
    result = {{
        'status': 'success',
        'description': '{description}',
        'input': data,
        'timestamp': str(time.time())
    }}
    return result

def analyze_data(data):
    '''Analyze data and return insights'''
    return {{
        'item_count': len(data) if isinstance(data, list) else 1,
        'data_type': type(data).__name__,
        'analysis': 'Data received and processed'
    }}
"""
    
    def run(self):
        """Extended run method with GCP features"""
        print("\n" + "="*60)
        print("🤖 AI Tool with Google Cloud Platform")
        print("="*60)
        
        if self.openai_client:
            print("✅ OpenAI API connected")
        else:
            print("⚠️  OpenAI API not configured (limited generation)")
        
        print(f"☁️  GCP Project: {self.gcp.project_id}")
        print("✅ Ready to deploy to Google Cloud!")
        
        print("\n🚀 Google Cloud Deployment Commands:")
        print("  • deploy website [description] - Static site to Cloud Storage")
        print("  • deploy api [description] - API to Cloud Run")
        print("  • deploy function [description] - Serverless Cloud Function")
        print("  • create webhook - Webhook endpoint for automation")
        
        print("\n💡 Other Commands:")
        print("  • write code [description] - Generate code")
        print("  • open [website] - Open in browser")
        print("  • pull repo github.com/[user/repo] - Clone repository")
        print("  • quit - Exit")
        
        print("\n💰 Note: Cloud Run and Cloud Functions may incur charges")
        print("   Cloud Storage static hosting is very low cost")
        print("\n" + "="*60 + "\n")
        
        while True:
            try:
                command = input("🤖 > ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if command:
                    self.execute_task(command)
                    print()
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == '__main__':
    tool = AIToolWithGCP()
    tool.run()