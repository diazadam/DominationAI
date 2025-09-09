#!/usr/bin/env python3
"""
AI Tool with Vercel Integration
Generates and instantly deploys web apps, APIs, and automation endpoints
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import openai
from vercel_integration import VercelDeployer

# Import base AI tool functionality
from ai_tool_with_openai import AIToolWithOpenAI

load_dotenv()

class AIToolWithVercel(AIToolWithOpenAI):
    def __init__(self):
        super().__init__()
        self.vercel = VercelDeployer()
        
        # Add new task categories
        self.extended_tasks = [
            "deploy website",
            "create api",
            "build webapp",
            "deploy n8n webhook"
        ]
    
    def execute_task(self, task_description):
        """Extended task execution with Vercel deployment"""
        
        # Check for deployment tasks
        if any(keyword in task_description.lower() for keyword in ['deploy', 'host', 'publish']):
            self.handle_deployment(task_description)
        elif 'create api' in task_description.lower():
            self.create_and_deploy_api(task_description)
        elif 'build webapp' in task_description.lower():
            self.build_and_deploy_webapp(task_description)
        else:
            # Fall back to parent class implementation
            super().execute_task(task_description)
    
    def handle_deployment(self, task_description):
        """Handle deployment requests"""
        print("🚀 Preparing deployment...")
        
        if 'website' in task_description.lower() or 'landing' in task_description.lower():
            self.deploy_landing_page(task_description)
        elif 'api' in task_description.lower():
            self.create_and_deploy_api(task_description)
        elif 'webhook' in task_description.lower():
            self.deploy_webhook_endpoint(task_description)
        else:
            self.deploy_generated_project(task_description)
    
    def deploy_landing_page(self, description):
        """Generate and deploy a landing page"""
        print("🎨 Generating landing page...")
        
        if self.openai_client:
            try:
                # Generate HTML with GPT
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Generate a beautiful, modern HTML landing page. Include inline CSS and make it responsive."},
                        {"role": "user", "content": f"Create a landing page for: {description}"}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                html_content = response.choices[0].message.content
                
                # Extract HTML if wrapped in code blocks
                if '```html' in html_content:
                    html_content = html_content.split('```html')[1].split('```')[0]
                elif '```' in html_content:
                    html_content = html_content.split('```')[1].split('```')[0]
                
            except Exception as e:
                print(f"GPT generation failed: {e}")
                html_content = self.generate_fallback_html(description)
        else:
            html_content = self.generate_fallback_html(description)
        
        # Deploy to Vercel
        project_name = description.lower().replace(' ', '-')[:20]
        url = self.vercel.deploy_html(html_content, project_name)
        
        if url:
            print(f"\n✨ Website deployed successfully!")
            print(f"🌐 Live URL: {url}")
            print(f"📋 Share this link: {url}")
            
            # Open in browser
            import subprocess
            subprocess.run(['open', url])
        else:
            print("❌ Deployment failed. Try running 'vercel login' first")
    
    def generate_fallback_html(self, description):
        """Generate a fallback HTML template"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{description}</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(to bottom right, #4f46e5, #7c3aed);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: white;
            padding: 3rem;
            border-radius: 1rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            max-width: 42rem;
            margin: 1rem;
        }}
        h1 {{
            color: #1f2937;
            margin-bottom: 1rem;
        }}
        p {{
            color: #6b7280;
            line-height: 1.6;
        }}
        .cta {{
            display: inline-block;
            margin-top: 1.5rem;
            padding: 0.75rem 1.5rem;
            background: #4f46e5;
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: 600;
        }}
        .cta:hover {{
            background: #4338ca;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{description}</h1>
        <p>This website was automatically generated and deployed by AI in seconds.</p>
        <p>The AI Tool can create, deploy, and manage web applications instantly using natural language commands.</p>
        <a href="#" class="cta">Learn More</a>
    </div>
</body>
</html>
"""
    
    def create_and_deploy_api(self, description):
        """Generate and deploy an API endpoint"""
        print("⚡ Creating API endpoint...")
        
        # Generate API code
        if self.openai_client:
            code = self.generate_api_code(description)
        else:
            code = "def main():\n    return {'message': 'API endpoint active', 'description': '" + description + "'}"
        
        # Deploy as serverless function
        endpoint_name = "api_" + str(int(time.time()))
        url = self.vercel.deploy_api(code, endpoint_name)
        
        if url:
            api_url = f"{url}/api/{endpoint_name}"
            print(f"\n⚡ API deployed successfully!")
            print(f"🔗 Endpoint: {api_url}")
            print(f"\nTest with: curl {api_url}")
    
    def generate_api_code(self, description):
        """Generate API code using GPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate Python code for a serverless API function. Include a main() function that returns a dictionary."},
                    {"role": "user", "content": f"Create API code for: {description}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except:
            return "def main():\n    return {'status': 'ok'}"
    
    def build_and_deploy_webapp(self, description):
        """Build and deploy a full web application"""
        print("🏗️  Building web application...")
        
        # Generate multiple files for a complete app
        files = {}
        
        # Generate HTML
        files['index.html'] = self.generate_webapp_html(description)
        
        # Generate CSS
        files['styles.css'] = self.generate_webapp_css()
        
        # Generate JavaScript
        files['script.js'] = self.generate_webapp_js(description)
        
        # Deploy all files
        url = self.vercel.deploy_static_site(files)
        
        if url:
            print(f"\n🎉 Web app deployed successfully!")
            print(f"🌐 Live URL: {url}")
            import subprocess
            subprocess.run(['open', url])
    
    def generate_webapp_html(self, description):
        """Generate HTML for web app"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{description}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="app">
        <header>
            <h1>{description}</h1>
            <p>AI-Generated Interactive Web App</p>
        </header>
        <main>
            <div class="card">
                <h2>Interactive Features</h2>
                <button id="actionBtn">Click Me</button>
                <div id="output"></div>
            </div>
            <div class="card">
                <h2>Data Input</h2>
                <input type="text" id="userInput" placeholder="Enter something...">
                <button id="submitBtn">Submit</button>
                <div id="result"></div>
            </div>
        </main>
        <footer>
            <p>🤖 Generated & Deployed with AI + Vercel</p>
        </footer>
    </div>
    <script src="script.js"></script>
</body>
</html>
"""
    
    def generate_webapp_css(self):
        """Generate CSS for web app"""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

#app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

header {
    text-align: center;
    color: white;
    margin-bottom: 3rem;
}

header h1 {
    font-size: 3rem;
    margin-bottom: 0.5rem;
}

main {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.card {
    background: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.card h2 {
    color: #333;
    margin-bottom: 1rem;
}

button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-size: 1rem;
    cursor: pointer;
    transition: transform 0.2s;
}

button:hover {
    transform: translateY(-2px);
}

input {
    width: 100%;
    padding: 0.75rem;
    margin-bottom: 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 0.5rem;
    font-size: 1rem;
}

#output, #result {
    margin-top: 1rem;
    padding: 1rem;
    background: #f5f5f5;
    border-radius: 0.5rem;
    min-height: 50px;
}

footer {
    text-align: center;
    color: white;
    margin-top: 3rem;
}
"""
    
    def generate_webapp_js(self, description):
        """Generate JavaScript for web app"""
        return f"""
// AI-Generated Interactive JavaScript
console.log('Web app initialized: {description}');

let clickCount = 0;
const output = document.getElementById('output');
const result = document.getElementById('result');
const actionBtn = document.getElementById('actionBtn');
const submitBtn = document.getElementById('submitBtn');
const userInput = document.getElementById('userInput');

// Interactive button
actionBtn.addEventListener('click', () => {{
    clickCount++;
    output.innerHTML = `
        <p>Button clicked ${{clickCount}} times!</p>
        <p>Timestamp: ${{new Date().toLocaleTimeString()}}</p>
    `;
    output.style.background = `hsl(${{clickCount * 30}}, 70%, 95%)`;
}});

// Form submission
submitBtn.addEventListener('click', () => {{
    const value = userInput.value;
    if (value) {{
        result.innerHTML = `
            <p><strong>You entered:</strong> ${{value}}</p>
            <p><strong>Length:</strong> ${{value.length}} characters</p>
            <p><strong>Reversed:</strong> ${{value.split('').reverse().join('')}}</p>
        `;
        userInput.value = '';
    }} else {{
        result.innerHTML = '<p style="color: red;">Please enter some text!</p>';
    }}
}});

// Enter key support
userInput.addEventListener('keypress', (e) => {{
    if (e.key === 'Enter') {{
        submitBtn.click();
    }}
}});

// Add some animation on load
document.addEventListener('DOMContentLoaded', () => {{
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {{
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {{
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }}, index * 200);
    }});
}});
"""
    
    def deploy_webhook_endpoint(self, description):
        """Deploy a webhook endpoint for n8n"""
        print("🔗 Creating webhook endpoint...")
        
        # Generate webhook handler code
        webhook_code = """
def process_webhook(data):
    # Process incoming webhook data
    return {
        'status': 'success',
        'received': data,
        'timestamp': str(time.time()),
        'processed_by': 'AI-generated webhook handler'
    }
"""
        
        url = self.vercel.create_webhook_endpoint(webhook_code)
        
        if url:
            webhook_url = f"{url}/api/webhook"
            print(f"\n🔗 Webhook endpoint deployed!")
            print(f"📥 URL for n8n: {webhook_url}")
            print(f"\nUse this URL in your n8n webhook trigger node")
    
    def run(self):
        """Extended run method with Vercel features"""
        print("\n" + "="*60)
        print("🤖 AI Tool with Vercel Integration")
        print("="*60)
        
        if self.openai_client:
            print("✅ OpenAI API connected")
        else:
            print("⚠️  OpenAI API not configured")
        
        if self.vercel.check_vercel_cli():
            print("✅ Vercel CLI ready for deployments")
        else:
            print("⚠️  Vercel CLI not available")
        
        print("\n🚀 New Deployment Commands:")
        print("  • deploy website [description] - Create & deploy a website")
        print("  • create api [description] - Deploy serverless API")
        print("  • build webapp [description] - Deploy interactive web app")
        print("  • deploy webhook - Create webhook endpoint for n8n")
        
        print("\n💡 Regular Commands:")
        print("  • write code [description] - Generate code")
        print("  • open [website] - Open in browser")
        print("  • pull repo github.com/[user/repo] - Clone repository")
        print("  • quit - Exit")
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
    tool = AIToolWithVercel()
    tool.run()