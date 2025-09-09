#!/usr/bin/env python3
"""
Vercel Integration for AI Tool
Enables instant deployment of AI-generated code
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict

class VercelDeployer:
    def __init__(self):
        self.check_vercel_cli()
        
    def check_vercel_cli(self):
        """Check if Vercel CLI is installed"""
        try:
            result = subprocess.run(['vercel', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Vercel CLI found: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            print("❌ Vercel CLI not found. Install with: npm i -g vercel")
            return False
    
    def deploy_html(self, html_content: str, project_name: str = "ai-generated") -> Optional[str]:
        """Deploy HTML content to Vercel and return the URL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create index.html
            index_file = tmppath / "index.html"
            index_file.write_text(html_content)
            
            # Create vercel.json for configuration
            vercel_config = {
                "name": project_name,
                "version": 2,
                "public": True
            }
            
            config_file = tmppath / "vercel.json"
            config_file.write_text(json.dumps(vercel_config, indent=2))
            
            # Deploy to Vercel
            return self._deploy_directory(tmppath)
    
    def deploy_api(self, code: str, endpoint_name: str = "api") -> Optional[str]:
        """Deploy Python/Node.js API to Vercel serverless"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create api directory for serverless functions
            api_dir = tmppath / "api"
            api_dir.mkdir()
            
            # Create the API endpoint
            api_file = api_dir / f"{endpoint_name}.py"
            
            # Wrap code in Vercel serverless function format
            serverless_code = f"""
from http.server import BaseHTTPRequestHandler
import json

{code}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Call the generated function if it exists
        response = {{"message": "API endpoint active"}}
        if 'main' in globals():
            response['result'] = main()
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # Process POST data
        data = json.loads(post_data)
        response = {{"received": data}}
        
        self.wfile.write(json.dumps(response).encode())
        return
"""
            
            api_file.write_text(serverless_code)
            
            # Create requirements.txt if needed
            requirements = tmppath / "requirements.txt"
            requirements.write_text("")
            
            # Deploy to Vercel
            return self._deploy_directory(tmppath)
    
    def deploy_nextjs_app(self, app_description: str) -> Optional[str]:
        """Generate and deploy a Next.js application"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create a basic Next.js app structure
            # Create package.json
            package_json = {
                "name": "ai-generated-app",
                "version": "1.0.0",
                "scripts": {
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start"
                },
                "dependencies": {
                    "next": "latest",
                    "react": "latest",
                    "react-dom": "latest"
                }
            }
            
            (tmppath / "package.json").write_text(json.dumps(package_json, indent=2))
            
            # Create pages directory
            pages_dir = tmppath / "pages"
            pages_dir.mkdir()
            
            # Create index.js
            index_content = f"""
import {{ useState }} from 'react'

export default function Home() {{
  const [count, setCount] = useState(0)
  
  return (
    <div style={{{{ padding: '2rem', fontFamily: 'sans-serif' }}}}>
      <h1>AI-Generated App</h1>
      <p>Description: {app_description}</p>
      <div>
        <p>Count: {{count}}</p>
        <button onClick={{() => setCount(count + 1)}}>
          Increment
        </button>
      </div>
    </div>
  )
}}
"""
            
            (pages_dir / "index.js").write_text(index_content)
            
            # Deploy to Vercel
            return self._deploy_directory(tmppath)
    
    def deploy_static_site(self, files: Dict[str, str]) -> Optional[str]:
        """Deploy multiple static files as a website"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create all files
            for filename, content in files.items():
                file_path = tmppath / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
            
            # Deploy to Vercel
            return self._deploy_directory(tmppath)
    
    def _deploy_directory(self, directory: Path) -> Optional[str]:
        """Deploy a directory to Vercel"""
        try:
            # Run vercel deploy command
            result = subprocess.run(
                ['vercel', 'deploy', '--public', '--confirm', '--no-clipboard'],
                cwd=directory,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Extract URL from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if 'https://' in line:
                        url = line.strip()
                        if '.vercel.app' in url or 'vercel.sh' in url:
                            print(f"✅ Deployed to: {url}")
                            return url
                
                # Fallback: last line often contains the URL
                last_line = output_lines[-1].strip()
                if 'https://' in last_line:
                    print(f"✅ Deployed to: {last_line}")
                    return last_line
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
            return None
    
    def create_webhook_endpoint(self, webhook_handler_code: str) -> Optional[str]:
        """Create a webhook endpoint for n8n pipelines"""
        webhook_template = f"""
import json

{webhook_handler_code}

def handler(request, response):
    '''Vercel serverless function handler'''
    if request.method == 'POST':
        data = json.loads(request.body)
        result = process_webhook(data) if 'process_webhook' in globals() else {{'status': 'received'}}
        response.status = 200
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(result)
    
    return {{'message': 'Webhook endpoint ready'}}
"""
        
        return self.deploy_api(webhook_template, "webhook")


# Example usage functions
def generate_landing_page(description: str) -> str:
    """Generate a simple landing page HTML"""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{description}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: white;
            padding: 3rem;
            border-radius: 1rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            text-align: center;
        }}
        h1 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 2.5rem;
        }}
        p {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 2rem;
        }}
        .button {{
            display: inline-block;
            padding: 1rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 0.5rem;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        .button:hover {{
            transform: translateY(-2px);
        }}
        .ai-badge {{
            display: inline-block;
            background: #f0f0f0;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.85rem;
            color: #666;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{description}</h1>
        <p>This page was automatically generated and deployed by AI.</p>
        <a href="#" class="button">Get Started</a>
        <div class="ai-badge">🤖 AI-Generated • Deployed with Vercel</div>
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    # Test the deployer
    deployer = VercelDeployer()
    
    print("\n🚀 Vercel Deployment Test")
    print("=" * 50)
    
    # Test HTML deployment
    test_html = generate_landing_page("AI Tool Demo Page")
    url = deployer.deploy_html(test_html, "ai-tool-demo")
    
    if url:
        print(f"\n✅ Success! Your page is live at: {url}")
        print(f"   Open in browser: open {url}")
    else:
        print("\n❌ Deployment failed. Please run 'vercel login' first")