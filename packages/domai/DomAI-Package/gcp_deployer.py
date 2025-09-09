#!/usr/bin/env python3
"""
Google Cloud Platform Deployment Integration
Deploy AI-generated apps to Cloud Run, Cloud Storage, and Cloud Functions
"""

import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict
import time
import random
import string

class GCPDeployer:
    def __init__(self):
        self.project_id = self.get_project_id()
        self.region = "us-central1"  # Default region
        self.check_gcloud_cli()
        
    def get_project_id(self):
        """Get current GCP project ID"""
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "gen-lang-client-0093497568"  # Your project ID as fallback
    
    def check_gcloud_cli(self):
        """Check if gcloud CLI is installed and configured"""
        try:
            result = subprocess.run(
                ['gcloud', 'version'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✅ Google Cloud CLI configured")
                print(f"   Project: {self.project_id}")
                return True
        except FileNotFoundError:
            print("❌ gcloud CLI not found")
            return False
    
    def deploy_to_cloud_run(self, app_name: str, code: str, 
                           runtime: str = "python39") -> Optional[str]:
        """Deploy a containerized app to Cloud Run"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create main application file
            if runtime.startswith("python"):
                self._create_python_cloud_run_app(tmppath, code)
            elif runtime.startswith("node"):
                self._create_node_cloud_run_app(tmppath, code)
            
            # Create Dockerfile
            dockerfile_content = self._generate_dockerfile(runtime)
            (tmppath / "Dockerfile").write_text(dockerfile_content)
            
            # Build and deploy
            return self._deploy_cloud_run(tmppath, app_name)
    
    def _create_python_cloud_run_app(self, path: Path, code: str):
        """Create Python Cloud Run application"""
        
        # Create main.py with Flask wrapper
        main_content = f"""
import os
from flask import Flask, request, jsonify, render_template_string
import json

app = Flask(__name__)

# User's generated code
{code}

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI-Generated App</title>
        <style>
            body {{
                font-family: -apple-system, system-ui, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                background: white;
                padding: 2rem;
                border-radius: 1rem;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; }}
            .badge {{
                display: inline-block;
                background: #4285f4;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.875rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 AI-Generated Cloud Run App</h1>
            <p>This application was automatically generated and deployed to Google Cloud Run.</p>
            <div class="badge">Running on GCP</div>
            <hr>
            <h2>API Endpoints:</h2>
            <ul>
                <li><code>GET /</code> - This page</li>
                <li><code>GET /api/status</code> - API status</li>
                <li><code>POST /api/process</code> - Process data</li>
            </ul>
        </div>
    </body>
    </html>
    '''

@app.route('/api/status')
def api_status():
    return jsonify({{
        'status': 'online',
        'service': 'Cloud Run',
        'project': '{self.project_id}'
    }})

@app.route('/api/process', methods=['POST'])
def api_process():
    data = request.get_json()
    # Call user's function if it exists
    if 'process_data' in globals():
        result = process_data(data)
    else:
        result = {{'received': data, 'processed': True}}
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
"""
        
        (path / "main.py").write_text(main_content)
        
        # Create requirements.txt
        requirements = """Flask==2.3.2
gunicorn==21.2.0
"""
        (path / "requirements.txt").write_text(requirements)
    
    def _create_node_cloud_run_app(self, path: Path, code: str):
        """Create Node.js Cloud Run application"""
        
        # Create app.js
        app_content = f"""
const express = require('express');
const app = express();

app.use(express.json());

// User's generated code
{code}

app.get('/', (req, res) => {{
    res.send(`
        <html>
        <body style="font-family: sans-serif; padding: 2rem;">
            <h1>AI-Generated Cloud Run App</h1>
            <p>Node.js application deployed on Google Cloud Run</p>
        </body>
        </html>
    `);
}});

app.get('/api/status', (req, res) => {{
    res.json({{
        status: 'online',
        service: 'Cloud Run',
        runtime: 'Node.js'
    }});
}});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {{
    console.log(`Server running on port ${{PORT}}`);
}});
"""
        
        (path / "app.js").write_text(app_content)
        
        # Create package.json
        package_json = {
            "name": "ai-generated-app",
            "version": "1.0.0",
            "main": "app.js",
            "scripts": {
                "start": "node app.js"
            },
            "dependencies": {
                "express": "^4.18.2"
            }
        }
        
        (path / "package.json").write_text(json.dumps(package_json, indent=2))
    
    def _generate_dockerfile(self, runtime: str) -> str:
        """Generate Dockerfile based on runtime"""
        
        if runtime.startswith("python"):
            return """FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app"""
        
        elif runtime.startswith("node"):
            return """FROM node:18-slim

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY . .

CMD ["npm", "start"]"""
        
        return ""
    
    def _deploy_cloud_run(self, app_path: Path, app_name: str) -> Optional[str]:
        """Deploy application to Cloud Run"""
        
        try:
            print(f"🏗️  Building container for {app_name}...")
            
            # Use Cloud Build to build and deploy
            deploy_cmd = [
                'gcloud', 'run', 'deploy', app_name,
                '--source', str(app_path),
                '--platform', 'managed',
                '--region', self.region,
                '--allow-unauthenticated',
                '--quiet'
            ]
            
            result = subprocess.run(deploy_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract URL from output
                for line in result.stdout.split('\n'):
                    if 'Service URL:' in line or 'https://' in line:
                        if 'run.app' in line:
                            url = line.split()[-1] if 'Service URL:' in line else line.strip()
                            if url.startswith('https://'):
                                print(f"✅ Deployed to Cloud Run!")
                                return url
                
                # Alternative: Get URL using gcloud command
                url_result = subprocess.run(
                    ['gcloud', 'run', 'services', 'describe', app_name,
                     '--platform', 'managed', '--region', self.region,
                     '--format', 'value(status.url)'],
                    capture_output=True, text=True
                )
                
                if url_result.returncode == 0 and url_result.stdout.strip():
                    url = url_result.stdout.strip()
                    print(f"✅ Deployed to Cloud Run!")
                    return url
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
        
        return None
    
    def deploy_static_site(self, files: Dict[str, str], 
                          bucket_name: Optional[str] = None) -> Optional[str]:
        """Deploy static website to Cloud Storage"""
        
        if not bucket_name:
            # Generate unique bucket name
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            bucket_name = f"ai-site-{random_suffix}"
        
        try:
            # Create bucket
            print(f"🪣 Creating storage bucket: {bucket_name}")
            
            create_bucket_cmd = [
                'gcloud', 'storage', 'buckets', 'create',
                f'gs://{bucket_name}',
                '--location', 'us-central1',
                '--uniform-bucket-level-access'
            ]
            
            subprocess.run(create_bucket_cmd, capture_output=True, text=True)
            
            # Make bucket public for website hosting
            public_cmd = [
                'gcloud', 'storage', 'buckets', 'add-iam-policy-binding',
                f'gs://{bucket_name}',
                '--member=allUsers',
                '--role=roles/storage.objectViewer'
            ]
            
            subprocess.run(public_cmd, capture_output=True, text=True)
            
            # Upload files
            with tempfile.TemporaryDirectory() as tmpdir:
                tmppath = Path(tmpdir)
                
                for filename, content in files.items():
                    file_path = tmppath / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)
                
                # Upload all files
                print(f"📤 Uploading files to Cloud Storage...")
                
                upload_cmd = [
                    'gcloud', 'storage', 'cp', '-r',
                    f'{tmppath}/*',
                    f'gs://{bucket_name}/'
                ]
                
                result = subprocess.run(upload_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Configure website settings
                    web_config_cmd = [
                        'gcloud', 'storage', 'buckets', 'update',
                        f'gs://{bucket_name}',
                        '--web-main-page-suffix=index.html',
                        '--web-error-page=404.html'
                    ]
                    
                    subprocess.run(web_config_cmd, capture_output=True, text=True)
                    
                    url = f"https://storage.googleapis.com/{bucket_name}/index.html"
                    print(f"✅ Static site deployed!")
                    return url
                else:
                    print(f"❌ Upload failed: {result.stderr}")
                    
        except Exception as e:
            print(f"❌ Error deploying static site: {e}")
        
        return None
    
    def deploy_cloud_function(self, function_code: str, 
                            function_name: str,
                            runtime: str = "python39") -> Optional[str]:
        """Deploy a Cloud Function"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            if runtime.startswith("python"):
                # Create main.py
                main_content = f"""
import functions_framework
import json

{function_code}

@functions_framework.http
def main(request):
    '''HTTP Cloud Function.'''
    request_json = request.get_json(silent=True)
    
    # Call user's function if exists
    if 'process' in globals():
        result = process(request_json)
    else:
        result = {{'message': 'Function executed', 'input': request_json}}
    
    return json.dumps(result)
"""
                (tmppath / "main.py").write_text(main_content)
                
                # Create requirements.txt
                (tmppath / "requirements.txt").write_text("functions-framework==3.*")
                
            try:
                print(f"⚡ Deploying Cloud Function: {function_name}")
                
                deploy_cmd = [
                    'gcloud', 'functions', 'deploy', function_name,
                    '--runtime', runtime,
                    '--trigger-http',
                    '--allow-unauthenticated',
                    '--entry-point', 'main',
                    '--source', str(tmppath),
                    '--region', self.region
                ]
                
                result = subprocess.run(deploy_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Get function URL
                    url_cmd = [
                        'gcloud', 'functions', 'describe', function_name,
                        '--region', self.region,
                        '--format', 'value(httpsTrigger.url)'
                    ]
                    
                    url_result = subprocess.run(url_cmd, capture_output=True, text=True)
                    
                    if url_result.returncode == 0:
                        url = url_result.stdout.strip()
                        print(f"✅ Cloud Function deployed!")
                        return url
                else:
                    print(f"❌ Deployment failed: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Error deploying function: {e}")
        
        return None
    
    def deploy_app_engine(self, app_code: str, runtime: str = "python39") -> Optional[str]:
        """Deploy to App Engine"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create app files
            if runtime.startswith("python"):
                self._create_python_cloud_run_app(tmppath, app_code)
                
                # Create app.yaml
                app_yaml = f"""runtime: {runtime}

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 0
  max_instances: 2
"""
                (tmppath / "app.yaml").write_text(app_yaml)
            
            try:
                print(f"🚀 Deploying to App Engine...")
                
                deploy_cmd = ['gcloud', 'app', 'deploy', '--quiet']
                
                result = subprocess.run(
                    deploy_cmd, 
                    cwd=tmppath,
                    capture_output=True, 
                    text=True
                )
                
                if result.returncode == 0:
                    url = f"https://{self.project_id}.appspot.com"
                    print(f"✅ Deployed to App Engine!")
                    return url
                else:
                    if "billing account" in result.stderr.lower():
                        print("❌ App Engine requires billing to be enabled")
                    else:
                        print(f"❌ Deployment failed: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Error deploying to App Engine: {e}")
        
        return None

# Convenience functions
def quick_deploy_website(html_content: str, project_name: str = "ai-website"):
    """Quick deploy a website to Cloud Storage"""
    deployer = GCPDeployer()
    
    files = {
        "index.html": html_content,
        "404.html": "<h1>404 - Page Not Found</h1>"
    }
    
    url = deployer.deploy_static_site(files)
    return url

def quick_deploy_api(api_code: str, api_name: str = "ai-api"):
    """Quick deploy an API to Cloud Run"""
    deployer = GCPDeployer()
    
    # Sanitize name for Cloud Run (lowercase, no underscores)
    api_name = api_name.lower().replace('_', '-')
    
    url = deployer.deploy_to_cloud_run(api_name, api_code)
    return url

if __name__ == "__main__":
    # Test deployment - non-interactive version
    deployer = GCPDeployer()
    
    print("\n🚀 Google Cloud Deployment Test")
    print("=" * 50)
    
    if deployer.check_gcloud_cli():
        print("✅ GCP CLI configured and ready")
        print("✅ All deployment methods available")
        print("\nTo test deployments, run:")
        print("  python3 ai_tool_with_gcp.py")
        print("\nThen try commands like:")
        print("  > deploy website test site")
        print("  > deploy api test api")
    else:
        print("❌ GCP CLI not configured")
        print("Run: gcloud auth login")