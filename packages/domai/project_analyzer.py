#!/Library/Developer/CommandLineTools/usr/bin/python3
"""
Project Analyzer Superpower for DomAI
Finds, analyzes, and continues development on existing projects
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

class ProjectAnalyzer:
    def __init__(self):
        self.name = "Project Analyzer"
        
    def find_project(self, project_name: str, search_paths: List[str] = None) -> List[str]:
        """Find project directories by name"""
        if not search_paths:
            search_paths = [
                str(Path.home()),
                str(Path.home() / "Desktop"),
                str(Path.home() / "Documents"),
                str(Path.home() / "Projects"),
                "/Users/adammach"  # Your user directory
            ]
        
        found_projects = []
        project_name_lower = project_name.lower()
        
        for search_path in search_paths:
            try:
                for root, dirs, files in os.walk(search_path):
                    # Check if directory name matches project
                    for dir_name in dirs:
                        if project_name_lower in dir_name.lower():
                            full_path = os.path.join(root, dir_name)
                            # Check if it looks like a code project
                            if self.is_code_project(full_path):
                                found_projects.append(full_path)
                    
                    # Don't go too deep to avoid performance issues
                    if root.count(os.sep) - search_path.count(os.sep) > 3:
                        dirs.clear()
                        
            except (PermissionError, FileNotFoundError):
                continue
        
        return found_projects
    
    def is_code_project(self, path: str) -> bool:
        """Check if directory contains code project indicators"""
        indicators = [
            'package.json',
            'requirements.txt',
            'Cargo.toml', 
            'pom.xml',
            'build.gradle',
            '.git',
            'src/',
            'index.html',
            'main.py',
            'app.py',
            'index.js'
        ]
        
        for indicator in indicators:
            if os.path.exists(os.path.join(path, indicator)):
                return True
        return False
    
    def analyze_project_structure(self, project_path: str) -> Dict:
        """Analyze project structure and identify key files"""
        analysis = {
            'path': project_path,
            'name': os.path.basename(project_path),
            'type': 'unknown',
            'key_files': [],
            'structure': {},
            'technologies': [],
            'completeness': 'unknown'
        }
        
        # Identify project type
        if os.path.exists(os.path.join(project_path, 'package.json')):
            analysis['type'] = 'node/javascript'
            analysis['technologies'].append('Node.js')
            
        if os.path.exists(os.path.join(project_path, 'requirements.txt')):
            analysis['type'] = 'python'
            analysis['technologies'].append('Python')
            
        if os.path.exists(os.path.join(project_path, 'index.html')):
            analysis['technologies'].append('HTML/CSS/JS')
            
        # Find key files
        important_files = [
            'README.md', 'package.json', 'requirements.txt',
            'index.html', 'index.js', 'main.py', 'app.py',
            'style.css', 'script.js'
        ]
        
        for file in important_files:
            file_path = os.path.join(project_path, file)
            if os.path.exists(file_path):
                analysis['key_files'].append(file)
        
        # Basic structure mapping
        try:
            for item in os.listdir(project_path):
                item_path = os.path.join(project_path, item)
                if os.path.isdir(item_path):
                    analysis['structure'][item] = 'directory'
                else:
                    analysis['structure'][item] = 'file'
        except PermissionError:
            pass
            
        return analysis
    
    def read_key_files(self, project_path: str, max_files: int = 10) -> Dict[str, str]:
        """Read content of key project files"""
        files_content = {}
        
        # Priority files to read
        priority_files = [
            'README.md',
            'package.json', 
            'index.html',
            'index.js',
            'main.py',
            'app.py',
            'style.css'
        ]
        
        files_read = 0
        for filename in priority_files:
            if files_read >= max_files:
                break
                
            file_path = os.path.join(project_path, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Limit content length for analysis
                        if len(content) > 5000:
                            content = content[:5000] + "\n... [truncated]"
                        files_content[filename] = content
                        files_read += 1
                except (UnicodeDecodeError, PermissionError):
                    files_content[filename] = "[Could not read file]"
        
        return files_content
    
    def assess_completeness(self, project_analysis: Dict, files_content: Dict[str, str]) -> str:
        """Assess how complete the project appears to be"""
        completeness_indicators = {
            'has_readme': 'README.md' in files_content,
            'has_main_file': any(f in files_content for f in ['index.html', 'index.js', 'main.py', 'app.py']),
            'has_package_config': any(f in files_content for f in ['package.json', 'requirements.txt']),
            'has_styling': 'style.css' in files_content or 'styles' in str(files_content),
            'has_javascript': any('.js' in f for f in files_content.keys()) or 'script' in str(files_content)
        }
        
        score = sum(completeness_indicators.values())
        total = len(completeness_indicators)
        
        if score >= total * 0.8:
            return "mostly_complete"
        elif score >= total * 0.6:
            return "partially_complete" 
        elif score >= total * 0.3:
            return "early_stage"
        else:
            return "minimal"
    
    def generate_completion_plan(self, project_analysis: Dict, files_content: Dict[str, str]) -> List[str]:
        """Generate a plan to complete the project"""
        plan = []
        
        # Check what's missing
        if 'README.md' not in files_content:
            plan.append("Create comprehensive README.md with project description and setup instructions")
            
        if project_analysis['type'] == 'node/javascript':
            if 'package.json' not in files_content:
                plan.append("Create package.json with dependencies and scripts")
            if 'index.html' not in files_content:
                plan.append("Create main HTML file")
            if not any('.css' in f for f in files_content.keys()):
                plan.append("Add CSS styling for better UI/UX")
                
        elif project_analysis['type'] == 'python':
            if 'requirements.txt' not in files_content:
                plan.append("Create requirements.txt with dependencies")
            if not any(f in files_content for f in ['main.py', 'app.py']):
                plan.append("Create main Python application file")
                
        # Check for common missing elements
        if 'FlipAI' in project_analysis['name'] or 'flip' in project_analysis['name'].lower():
            plan.append("Implement card flipping animation logic")
            plan.append("Add game state management")
            plan.append("Create scoring and timer functionality")
            plan.append("Implement responsive design for mobile")
            plan.append("Add sound effects and visual feedback")
            
        if not plan:
            plan.append("Project appears complete - review for optimizations and deployment")
            
        return plan

def get_superpower():
    return ProjectAnalyzer()

if __name__ == "__main__":
    analyzer = ProjectAnalyzer()
    
    # Test finding FlipAI project
    print("🔍 Searching for FlipAI project...")
    projects = analyzer.find_project("flipai")
    
    if projects:
        print(f"📁 Found {len(projects)} potential FlipAI projects:")
        for project in projects:
            print(f"  • {project}")
            
        # Analyze the first one found
        analysis = analyzer.analyze_project_structure(projects[0])
        files = analyzer.read_key_files(projects[0])
        completeness = analyzer.assess_completeness(analysis, files)
        plan = analyzer.generate_completion_plan(analysis, files)
        
        print(f"\n📊 Analysis of {analysis['name']}:")
        print(f"  Type: {analysis['type']}")
        print(f"  Technologies: {', '.join(analysis['technologies'])}")
        print(f"  Key files: {', '.join(analysis['key_files'])}")
        print(f"  Completeness: {completeness}")
        
        print(f"\n✅ Completion Plan:")
        for i, task in enumerate(plan, 1):
            print(f"  {i}. {task}")
    else:
        print("❌ No FlipAI projects found")