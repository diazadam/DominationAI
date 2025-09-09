#!/Library/Developer/CommandLineTools/usr/bin/python3
"""
Vercel Deployment Integration for DomAI
Deploy websites and applications directly to Vercel
"""

import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict
import time

class VercelDeployer:
    def __init__(self):
        self.check_vercel_cli()
        
    def check_vercel_cli(self):
        """Check if Vercel CLI is installed and authenticated"""
        try:
            result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ Vercel CLI available (v{version})")
                self.available = self.check_auth()
                return self.available
        except FileNotFoundError:
            print("❌ Vercel CLI not found. Install with: npm i -g vercel")
            self.available = False
            return False
            
    def check_auth(self):
        """Check if user is authenticated with Vercel"""
        try:
            result = subprocess.run(['vercel', 'whoami'], capture_output=True, text=True)
            if result.returncode == 0:
                username = result.stdout.strip()
                print(f"✅ Authenticated as: {username}")
                return True
            else:
                print("⚠️  Not authenticated with Vercel CLI")
                print("💡 To use Vercel deployment, run: vercel login")
                return False
        except:
            print("⚠️  Could not check Vercel authentication")
            return False
    
    def deploy_website(self, html_content: str, site_name: str = None) -> Dict:
        """Deploy a static website to Vercel"""
        if not getattr(self, 'available', False):
            return {
                'success': False,
                'error': 'Vercel CLI not available or not authenticated. Run: vercel login'
            }
            
        if not site_name:
            site_name = f"domai-site-{int(time.time())}"
        
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Write HTML file
                index_file = temp_path / "index.html"
                index_file.write_text(html_content)
                
                # Create vercel.json for configuration
                vercel_config = {
                    "name": site_name,
                    "version": 2
                }
                
                vercel_file = temp_path / "vercel.json"
                vercel_file.write_text(json.dumps(vercel_config, indent=2))
                
                # Deploy to Vercel
                print(f"🚀 Deploying {site_name} to Vercel...")
                result = subprocess.run(
                    ['vercel', '--prod', '--yes'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Extract URL from output
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'https://' in line and 'vercel.app' in line:
                            url = line.strip()
                            return {
                                'success': True,
                                'url': url,
                                'name': site_name,
                                'platform': 'vercel'
                            }
                    
                    return {
                        'success': True,
                        'message': 'Deployed to Vercel successfully',
                        'name': site_name,
                        'platform': 'vercel'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.stderr or 'Deployment failed'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def deploy_nextjs_app(self, app_code: str, app_name: str = None) -> Dict:
        """Deploy a Next.js application to Vercel"""
        if not app_name:
            app_name = f"domai-app-{int(time.time())}"
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create package.json
                package_json = {
                    "name": app_name,
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
                
                (temp_path / "package.json").write_text(json.dumps(package_json, indent=2))
                
                # Create pages directory and index.js
                pages_dir = temp_path / "pages"
                pages_dir.mkdir()
                
                (pages_dir / "index.js").write_text(app_code)
                
                # Deploy to Vercel
                print(f"🚀 Deploying {app_name} Next.js app to Vercel...")
                result = subprocess.run(
                    ['vercel', '--prod', '--yes'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Extract URL from output
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'https://' in line and 'vercel.app' in line:
                            url = line.strip()
                            return {
                                'success': True,
                                'url': url,
                                'name': app_name,
                                'type': 'nextjs',
                                'platform': 'vercel'
                            }
                    
                    return {
                        'success': True,
                        'message': 'Next.js app deployed successfully',
                        'name': app_name,
                        'platform': 'vercel'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.stderr or 'Next.js deployment failed'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def deploy_api(self, api_code: str, api_name: str = None) -> Dict:
        """Deploy a serverless API to Vercel"""
        if not api_name:
            api_name = f"domai-api-{int(time.time())}"
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create package.json for API
                package_json = {
                    "name": api_name,
                    "version": "1.0.0",
                    "dependencies": {}
                }
                
                (temp_path / "package.json").write_text(json.dumps(package_json, indent=2))
                
                # Create api directory and handler
                api_dir = temp_path / "api"
                api_dir.mkdir()
                
                (api_dir / "index.js").write_text(api_code)
                
                # Deploy to Vercel
                print(f"🚀 Deploying {api_name} API to Vercel...")
                result = subprocess.run(
                    ['vercel', '--prod', '--yes'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Extract URL from output
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'https://' in line and 'vercel.app' in line:
                            url = line.strip()
                            return {
                                'success': True,
                                'url': f"{url}/api",
                                'name': api_name,
                                'type': 'api',
                                'platform': 'vercel'
                            }
                    
                    return {
                        'success': True,
                        'message': 'API deployed successfully',
                        'name': api_name,
                        'platform': 'vercel'
                    }
                else:
                    return {
                        'success': False,
                        'error': result.stderr or 'API deployment failed'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_deployments(self) -> Dict:
        """List all Vercel deployments"""
        try:
            result = subprocess.run(
                ['vercel', 'list'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'deployments': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to list deployments'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def quick_deploy_website(html_content: str, site_name: str = None) -> Dict:
    """Quick function to deploy a website to Vercel"""
    deployer = VercelDeployer()
    return deployer.deploy_website(html_content, site_name)

def quick_deploy_api(api_code: str, api_name: str = None) -> Dict:
    """Quick function to deploy an API to Vercel"""
    deployer = VercelDeployer()
    return deployer.deploy_api(api_code, api_name)

if __name__ == "__main__":
    print("🌐 Testing Vercel Deployment Integration")
    print("=" * 50)
    
    deployer = VercelDeployer()
    
    # Test with simple HTML
    test_html = """<!DOCTYPE html>
<html>
<head>
    <title>DomAI Test Site</title>
</head>
<body>
    <h1>🤖 Hello from DomAI!</h1>
    <p>This site was deployed automatically by DomAI to Vercel.</p>
</body>
</html>"""
    
    result = deployer.deploy_website(test_html, "domai-test")
    print(f"📊 Deployment result: {result}")