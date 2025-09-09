
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
