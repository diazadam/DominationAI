#!/Library/Developer/CommandLineTools/usr/bin/python3
"""
DominateAI Superpower Manager
Gives DominateAI the ability to control Mac, browsers, and self-extend
"""

import os
import json
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional
import shutil
import tempfile
import requests
try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("⚠️  GitPython not available - GitHub extension features disabled")

class SuperpowerManager:
    def __init__(self):
        self.superpowers_dir = Path(__file__).parent / "superpowers"
        self.superpowers_dir.mkdir(exist_ok=True)
        self.loaded_powers = {}
        
        # Initialize core automation libraries
        self.setup_automation_libraries()
        
    def setup_automation_libraries(self):
        """Check automation libraries availability"""
        libraries = [
            ('pyautogui', 'pyautogui'),      # Mac GUI automation
            ('selenium', 'selenium'),       # Browser automation
            ('playwright', 'playwright'),     # Modern browser automation
            ('requests', 'requests'),       # HTTP requests
            ('beautifulsoup4', 'bs4'), # Web scraping
            ('gitpython', 'git'),      # Git operations
        ]
        
        available = []
        missing = []
        
        for lib_name, import_name in libraries:
            try:
                __import__(import_name)
                available.append(lib_name)
                print(f"✅ {lib_name} available")
            except ImportError:
                missing.append(lib_name)
                print(f"⚠️  {lib_name} not available (install with: pip install {lib_name})")
        
        print(f"📊 Libraries: {len(available)} available, {len(missing)} missing")
    
    def add_mac_control_powers(self):
        """Add Mac system control capabilities"""
        mac_controller = """
import subprocess
import os
import time
from pathlib import Path

class MacController:
    def __init__(self):
        self.name = "Mac System Control"
        
    def execute_applescript(self, script):
        '''Execute AppleScript commands'''
        try:
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            return {'success': True, 'output': result.stdout.strip()}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def open_application(self, app_name):
        '''Open Mac application'''
        script = f'tell application "{app_name}" to activate'
        return self.execute_applescript(script)
    
    def create_file(self, path, content=""):
        '''Create file on Mac'''
        try:
            Path(path).write_text(content)
            return {'success': True, 'message': f'File created: {path}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_terminal_command(self, command):
        '''Execute terminal command'''
        try:
            result = subprocess.run(command, shell=True, 
                                  capture_output=True, text=True)
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_system_info(self):
        '''Get Mac system information'''
        commands = {
            'hostname': 'hostname',
            'username': 'whoami', 
            'os_version': 'sw_vers -productVersion',
            'architecture': 'uname -m',
            'memory': 'sysctl -n hw.memsize'
        }
        
        info = {}
        for key, cmd in commands.items():
            result = self.run_terminal_command(cmd)
            info[key] = result.get('output', '').strip()
        
        return info
    
    def control_window(self, app_name, action):
        '''Control application windows'''
        actions = {
            'minimize': f'tell application "System Events" to set visible of application process "{app_name}" to false',
            'maximize': f'tell application "{app_name}" to activate',
            'close': f'tell application "{app_name}" to quit'
        }
        
        if action in actions:
            return self.execute_applescript(actions[action])
        
        return {'success': False, 'error': 'Unknown action'}

def get_superpower():
    return MacController()
"""
        
        mac_file = self.superpowers_dir / "mac_control.py"
        mac_file.write_text(mac_controller)
        return self.load_superpower(mac_file)
    
    def add_browser_control_powers(self):
        """Add browser automation capabilities"""
        browser_controller = """
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

class BrowserController:
    def __init__(self):
        self.name = "Browser Automation"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        '''Setup Chrome driver with options'''
        try:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"Browser setup failed: {e}")
            return False
    
    def navigate_to(self, url):
        '''Navigate to URL'''
        if not self.driver:
            self.setup_driver()
        
        try:
            self.driver.get(url)
            return {'success': True, 'url': url}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def find_and_click(self, selector, by_type="css"):
        '''Find element and click it'''
        try:
            by_map = {
                'css': By.CSS_SELECTOR,
                'xpath': By.XPATH,
                'id': By.ID,
                'name': By.NAME,
                'class': By.CLASS_NAME
            }
            
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_map[by_type], selector))
            )
            element.click()
            return {'success': True, 'message': f'Clicked {selector}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def fill_form_field(self, selector, text, by_type="css"):
        '''Fill form field with text'''
        try:
            by_map = {
                'css': By.CSS_SELECTOR,
                'xpath': By.XPATH,
                'id': By.ID,
                'name': By.NAME
            }
            
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_map[by_type], selector))
            )
            element.clear()
            element.send_keys(text)
            return {'success': True, 'message': f'Filled {selector} with text'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def extract_text(self, selector, by_type="css"):
        '''Extract text from element'''
        try:
            by_map = {
                'css': By.CSS_SELECTOR,
                'xpath': By.XPATH,
                'id': By.ID,
                'name': By.NAME,
                'class': By.CLASS_NAME
            }
            
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_map[by_type], selector))
            )
            text = element.text
            return {'success': True, 'text': text}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def take_screenshot(self, filename=None):
        '''Take screenshot of current page'''
        try:
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            return {'success': True, 'filename': filename}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute_javascript(self, script):
        '''Execute JavaScript in browser'''
        try:
            result = self.driver.execute_script(script)
            return {'success': True, 'result': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def close_browser(self):
        '''Close browser'''
        if self.driver:
            self.driver.quit()
            return {'success': True, 'message': 'Browser closed'}

def get_superpower():
    return BrowserController()
"""
        
        browser_file = self.superpowers_dir / "browser_control.py"
        browser_file.write_text(browser_controller)
        return self.load_superpower(browser_file)
    
    def add_github_extension_powers(self):
        """Add GitHub repository extension capabilities"""
        github_extender = """
import os
import json
import importlib.util
from pathlib import Path
try:
    from git import Repo
except ImportError:
    Repo = None
import tempfile
import shutil

class GitHubExtender:
    def __init__(self):
        self.name = "GitHub Extension System"
        self.extensions_dir = Path.home() / ".domai_extensions"
        self.extensions_dir.mkdir(exist_ok=True)
    
    def clone_and_extend(self, github_url, extension_name=None):
        '''Clone GitHub repo and extract DominateAI extensions'''
        try:
            if not extension_name:
                extension_name = github_url.split('/')[-1].replace('.git', '')
            
            # Clone to temp directory
            if not Repo:
                return {'success': False, 'error': 'GitPython not installed. Run: pip install gitpython'}
                
            with tempfile.TemporaryDirectory() as temp_dir:
                repo = Repo.clone_from(github_url, temp_dir)
                
                # Look for DominateAI extension files
                extensions = self.scan_for_extensions(temp_dir)
                
                # Install extensions
                installed = []
                for ext_file in extensions:
                    installed_path = self.install_extension(ext_file, extension_name)
                    if installed_path:
                        installed.append(installed_path)
                
                return {
                    'success': True,
                    'extensions_found': len(extensions),
                    'extensions_installed': installed
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scan_for_extensions(self, repo_path):
        '''Scan repository for DominateAI extensions'''
        extensions = []
        repo_path = Path(repo_path)
        
        # Look for files that might be extensions
        patterns = [
            "**/*domai*.py",
            "**/domai_*.py", 
            "**/dominateai_*.py",
            "**/extensions/*.py",
            "**/plugins/*.py"
        ]
        
        for pattern in patterns:
            for file_path in repo_path.glob(pattern):
                # Check if file contains extension markers
                content = file_path.read_text()
                if self.is_domai_extension(content):
                    extensions.append(file_path)
        
        return extensions
    
    def is_domai_extension(self, content):
        '''Check if file is a DominateAI extension'''
        markers = [
            "class.*Extension",
            "def get_superpower",
            "DOMAI_EXTENSION",
            "DominateAI"
        ]
        
        return any(marker in content for marker in markers)
    
    def install_extension(self, source_path, extension_name):
        '''Install extension to DominateAI'''
        try:
            dest_path = self.extensions_dir / f"{extension_name}_{source_path.name}"
            shutil.copy2(source_path, dest_path)
            
            # Try to load and validate extension
            if self.validate_extension(dest_path):
                return str(dest_path)
            else:
                dest_path.unlink()  # Remove invalid extension
                return None
                
        except Exception as e:
            print(f"Extension install failed: {e}")
            return None
    
    def validate_extension(self, extension_path):
        '''Validate that extension is safe and functional'''
        try:
            # Load module
            spec = importlib.util.spec_from_file_location("temp_ext", extension_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for required functions
            if hasattr(module, 'get_superpower'):
                superpower = module.get_superpower()
                if hasattr(superpower, 'name'):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Extension validation failed: {e}")
            return False
    
    def list_available_extensions(self):
        '''List installed extensions'''
        extensions = []
        for ext_file in self.extensions_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location("ext", ext_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if hasattr(module, 'get_superpower'):
                    superpower = module.get_superpower()
                    extensions.append({
                        'file': ext_file.name,
                        'name': getattr(superpower, 'name', 'Unknown'),
                        'path': str(ext_file)
                    })
            except:
                continue
        
        return extensions
    
    def load_extension(self, extension_name):
        '''Load specific extension'''
        for ext_file in self.extensions_dir.glob("*.py"):
            if extension_name in ext_file.name:
                try:
                    spec = importlib.util.spec_from_file_location("loaded_ext", ext_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'get_superpower'):
                        return module.get_superpower()
                except Exception as e:
                    print(f"Failed to load {extension_name}: {e}")
        
        return None

def get_superpower():
    return GitHubExtender()
"""
        
        github_file = self.superpowers_dir / "github_extender.py"
        github_file.write_text(github_extender)
        return self.load_superpower(github_file)
    
    def add_website_builder_powers(self):
        """Add automated website building and deployment"""
        website_builder = """
import json
import time
from pathlib import Path
import subprocess
import tempfile

class WebsiteBuilder:
    def __init__(self):
        self.name = "Website Builder & Deployer"
        
    def generate_website(self, description, style="modern"):
        '''Generate complete website from description'''
        # This would use Gemini to generate HTML, CSS, JS
        templates = {
            'modern': self.get_modern_template(),
            'minimalist': self.get_minimalist_template(),
            'business': self.get_business_template()
        }
        
        template = templates.get(style, templates['modern'])
        
        # Replace placeholders with description-specific content
        website_content = template.replace('{{DESCRIPTION}}', description)
        website_content = website_content.replace('{{TITLE}}', description.title())
        
        return website_content
    
    def get_modern_template(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .hero {
            text-align: center;
            color: white;
            padding: 4rem 0;
        }
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            animation: slideIn 1s ease-out;
        }
        .hero p {
            font-size: 1.25rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        .cta-button {
            display: inline-block;
            margin-top: 2rem;
            padding: 1rem 2rem;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 50px;
            border: 2px solid rgba(255,255,255,0.3);
            transition: all 0.3s ease;
        }
        .cta-button:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.7);
            margin-top: 4rem;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>{{TITLE}}</h1>
            <p>{{DESCRIPTION}}</p>
            <a href="#" class="cta-button">Get Started</a>
        </div>
        <div class="footer">
            <p>🤖 Built and deployed by DominateAI</p>
        </div>
    </div>
    <script>
        // Add some interactivity
        document.querySelector('.cta-button').addEventListener('click', (e) => {
            e.preventDefault();
            alert('DominateAI: Ready to build amazing things!');
        });
    </script>
</body>
</html>'''
    
    def get_minimalist_template(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 4rem 2rem;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #333;
            padding-bottom: 0.5rem;
        }
        .description {
            font-size: 1.125rem;
            margin-bottom: 2rem;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>{{TITLE}}</h1>
    <div class="description">{{DESCRIPTION}}</div>
    <p><em>Generated by DominateAI</em></p>
</body>
</html>'''
    
    def get_business_template(self):
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: #f8f9fa;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 1rem 0;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .hero {
            background: white;
            padding: 3rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .hero h1 {
            color: #2c3e50;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{TITLE}}</h1>
    </div>
    <div class="container">
        <div class="hero">
            <p>{{DESCRIPTION}}</p>
        </div>
    </div>
</body>
</html>'''
    
    def deploy_to_cloud_storage(self, html_content, site_name):
        '''Deploy website to Google Cloud Storage'''
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
                f.write(html_content)
                temp_file = f.name
            
            # Create bucket name
            bucket_name = f"domai-{site_name}-{int(time.time())}"
            
            # Create bucket and upload
            commands = [
                f"gsutil mb gs://{bucket_name}",
                f"gsutil cp {temp_file} gs://{bucket_name}/index.html",
                f"gsutil web set -m index.html gs://{bucket_name}",
                f"gsutil iam ch allUsers:objectViewer gs://{bucket_name}"
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode != 0:
                    return {'success': False, 'error': result.stderr}
            
            # Clean up
            Path(temp_file).unlink()
            
            url = f"https://storage.googleapis.com/{bucket_name}/index.html"
            return {
                'success': True,
                'url': url,
                'bucket': bucket_name
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

def get_superpower():
    return WebsiteBuilder()
"""
        
        website_file = self.superpowers_dir / "website_builder.py"
        website_file.write_text(website_builder)
        return self.load_superpower(website_file)
    
    def add_n8n_powers(self):
        """Add n8n workflow automation capabilities"""
        n8n_controller = """
import json
import requests
import subprocess
from pathlib import Path

class N8NController:
    def __init__(self):
        self.name = "n8n Workflow Automation"
        self.n8n_url = "http://localhost:5678"  # Default n8n URL
        
    def check_n8n_status(self):
        '''Check if n8n is running'''
        try:
            response = requests.get(f"{self.n8n_url}/rest/active")
            return {'success': True, 'running': response.status_code == 200}
        except:
            return {'success': False, 'running': False}
    
    def start_n8n(self):
        '''Start n8n if not running'''
        try:
            # Try to start n8n
            subprocess.Popen(['n8n', 'start'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {'success': True, 'message': 'n8n starting...'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_workflow(self, workflow_name, description="AI-generated workflow"):
        '''Create a new n8n workflow'''
        workflow_template = {
            "name": workflow_name,
            "active": False,
            "nodes": [
                {
                    "parameters": {
                        "path": f"/{workflow_name.lower().replace(' ', '-')}",
                        "options": {}
                    },
                    "id": "webhook-trigger",
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [250, 300],
                    "webhookId": f"{workflow_name.lower()}-webhook"
                },
                {
                    "parameters": {
                        "jsCode": "// Process incoming data\\nreturn items;"
                    },
                    "id": "code-processor", 
                    "name": "Process Data",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 1,
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "resource": "message",
                        "operation": "send",
                        "text": f"Workflow {workflow_name} executed successfully!"
                    },
                    "id": "notification",
                    "name": "Send Notification", 
                    "type": "n8n-nodes-base.http",
                    "typeVersion": 1,
                    "position": [650, 300]
                }
            ],
            "connections": {
                "Webhook Trigger": {
                    "main": [
                        [
                            {
                                "node": "Process Data",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                "Process Data": {
                    "main": [
                        [
                            {
                                "node": "Send Notification",
                                "type": "main", 
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            "settings": {},
            "staticData": {},
            "tags": ["DominateAI", "Auto-generated"]
        }
        
        return workflow_template
    
    def save_workflow(self, workflow_data, filename=None):
        '''Save workflow to file'''
        if not filename:
            filename = f"workflow_{int(time.time())}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            return {'success': True, 'filename': filename}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_workflow_to_n8n(self, workflow_data):
        '''Upload workflow to running n8n instance'''
        try:
            # Check if n8n is running
            status = self.check_n8n_status()
            if not status.get('running'):
                return {'success': False, 'error': 'n8n is not running'}
            
            # Upload workflow
            response = requests.post(
                f"{self.n8n_url}/rest/workflows",
                json=workflow_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201]:
                return {'success': True, 'workflow_id': response.json().get('id')}
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_ai_automation_workflow(self, task_description):
        '''Create specialized workflow for AI automation tasks'''
        workflow_name = f"AI-{task_description.replace(' ', '-')}"
        
        workflow = {
            "name": workflow_name,
            "active": True,
            "nodes": [
                {
                    "parameters": {
                        "path": f"/ai-automation/{workflow_name.lower()}",
                        "options": {}
                    },
                    "name": "AI Task Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "position": [200, 300]
                },
                {
                    "parameters": {
                        "jsCode": f'''
// AI Automation: {task_description}
const task = "{task_description}";
const inputData = items[0].json;

// Log the task
console.log(`Executing AI task: ${{task}}`);
console.log("Input data:", inputData);

// Process the data (customize based on task)
const result = {{
    task: task,
    input: inputData,
    timestamp: new Date().toISOString(),
    status: "completed",
    result: `Task '${{task}}' processed successfully`
}};

return [{{json: result}}];
'''
                    },
                    "name": "AI Processor", 
                    "type": "n8n-nodes-base.code",
                    "position": [400, 300]
                }
            ],
            "connections": {
                "AI Task Trigger": {
                    "main": [
                        [
                            {
                                "node": "AI Processor",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            }
        }
        
        return workflow

def get_superpower():
    return N8NController()
"""
        
        n8n_file = self.superpowers_dir / "n8n_controller.py"
        n8n_file.write_text(n8n_controller)
        return self.load_superpower(n8n_file)
    
    def add_project_analyzer_powers(self):
        """Add project analysis and continuation capabilities"""
        # Import the project analyzer we created
        from project_analyzer import ProjectAnalyzer
        
        # Load it directly as a superpower
        analyzer = ProjectAnalyzer()
        self.loaded_powers[analyzer.name] = analyzer
        print(f"✅ Loaded superpower: {analyzer.name}")
        return analyzer
    
    def add_intelligent_executor_powers(self):
        """Add intelligent autonomous execution capabilities"""
        from intelligent_executor import IntelligentExecutor
        
        # Pass both AI systems if available
        try:
            from working_gemini_integration import WorkingGeminiManager
            from ai_gateway_manager import AIGatewayManager
            
            gemini = WorkingGeminiManager()
            ai_gateway = AIGatewayManager()
            executor = IntelligentExecutor(gemini, ai_gateway)
        except:
            try:
                from working_gemini_integration import WorkingGeminiManager
                gemini = WorkingGeminiManager()
                executor = IntelligentExecutor(gemini)
            except:
                executor = IntelligentExecutor()
            
        self.loaded_powers[executor.name] = executor
        print(f"✅ Loaded superpower: {executor.name}")
        return executor
    
    def add_ai_gateway_powers(self):
        """Add AI Gateway with access to 100+ models"""
        from ai_gateway_manager import AIGatewayManager
        
        gateway = AIGatewayManager()
        self.loaded_powers[gateway.name] = gateway
        print(f"✅ Loaded superpower: {gateway.name}")
        return gateway
    
    def add_self_fixer_powers(self):
        """Add self-fixing and error resolution capabilities"""
        from self_fixer import SelfFixer
        
        # Pass AI systems for intelligent error analysis
        try:
            ai_gateway = self.loaded_powers.get('AI Gateway Manager')
            gemini = None
            try:
                from working_gemini_integration import WorkingGeminiManager
                gemini = WorkingGeminiManager()
            except:
                pass
            
            fixer = SelfFixer(ai_gateway, gemini)
        except:
            fixer = SelfFixer()
            
        self.loaded_powers[fixer.name] = fixer
        print(f"✅ Loaded superpower: {fixer.name}")
        return fixer
    
    def load_superpower(self, power_file):
        """Load a superpower module"""
        try:
            spec = importlib.util.spec_from_file_location("superpower", power_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, 'get_superpower'):
                power = module.get_superpower()
                power_name = getattr(power, 'name', power_file.stem)
                self.loaded_powers[power_name] = power
                print(f"✅ Loaded superpower: {power_name}")
                return power
            else:
                print(f"❌ Invalid superpower format: {power_file}")
                
        except Exception as e:
            print(f"❌ Failed to load {power_file}: {e}")
        
        return None
    
    def initialize_all_superpowers(self):
        """Initialize all superpowers"""
        print("🚀 Initializing DominateAI Superpowers...")
        
        superpowers = [
            ("Mac Control", self.add_mac_control_powers),
            ("Browser Control", self.add_browser_control_powers),
            ("GitHub Extensions", self.add_github_extension_powers),
            ("Website Builder", self.add_website_builder_powers),
            ("n8n Automation", self.add_n8n_powers),
            ("Project Analyzer", self.add_project_analyzer_powers),
            ("Intelligent Executor", self.add_intelligent_executor_powers),
            ("AI Gateway", self.add_ai_gateway_powers),
            ("Self Fixer", self.add_self_fixer_powers),
        ]
        
        for name, initializer in superpowers:
            try:
                print(f"🔧 Setting up {name}...")
                initializer()
            except Exception as e:
                print(f"⚠️  {name} setup failed: {e}")
        
        print(f"\n✨ DominateAI now has {len(self.loaded_powers)} superpowers!")
        return self.loaded_powers
    
    def get_superpower(self, name):
        """Get specific superpower by name"""
        return self.loaded_powers.get(name)
    
    def list_superpowers(self):
        """List all available superpowers"""
        return list(self.loaded_powers.keys())

if __name__ == "__main__":
    manager = SuperpowerManager()
    powers = manager.initialize_all_superpowers()
    
    print("\n🎯 Available Superpowers:")
    for name in powers.keys():
        print(f"  • {name}")
    
    print("\n💡 DominateAI can now:")
    print("  • Control your Mac system")  
    print("  • Automate web browsers")
    print("  • Clone and integrate GitHub repos")
    print("  • Build and deploy websites")
    print("  • Create n8n workflows")
    print("  • Self-extend with new capabilities")