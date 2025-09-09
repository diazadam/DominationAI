#!/Library/Developer/CommandLineTools/usr/bin/python3
"""
Intelligent Executor for DomAI
Makes DomAI autonomous and action-oriented like Claude
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

class IntelligentExecutor:
    def __init__(self, gemini_manager=None, ai_gateway=None):
        self.name = "Intelligent Executor"
        self.gemini = gemini_manager
        self.ai_gateway = ai_gateway
        self.current_project_path = None
        
    def analyze_and_implement_project(self, project_path: str, user_intent: str) -> Dict:
        """Analyze project and autonomously implement what's needed"""
        
        print(f"🧠 Analyzing project with full AI capabilities...")
        
        # Navigate to project
        original_cwd = os.getcwd()
        os.chdir(project_path)
        self.current_project_path = project_path
        
        try:
            # Get comprehensive project context
            context = self._gather_project_context(project_path)
            
            # Generate implementation plan
            plan = self._create_implementation_plan(context, user_intent)
            
            # Execute the plan autonomously
            results = self._execute_implementation_plan(plan, context)
            
            return {
                'success': True,
                'project_path': project_path,
                'context': context,
                'plan': plan,
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            os.chdir(original_cwd)
    
    def _gather_project_context(self, project_path: str) -> Dict:
        """Gather complete project context"""
        context = {
            'path': project_path,
            'name': os.path.basename(project_path),
            'files': {},
            'structure': [],
            'type': 'unknown',
            'technologies': []
        }
        
        # Read all relevant files
        for root, dirs, files in os.walk(project_path):
            # Skip deep nested directories and common ignore patterns
            level = root.replace(project_path, '').count(os.sep)
            if level >= 3:
                dirs[:] = []
                continue
                
            if any(ignore in root for ignore in ['.git', 'node_modules', '__pycache__']):
                dirs[:] = []
                continue
            
            for file in files:
                if self._should_read_file(file):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Limit content for analysis
                            if len(content) > 10000:
                                content = content[:10000] + "\n... [truncated]"
                            context['files'][rel_path] = content
                    except (UnicodeDecodeError, PermissionError):
                        context['files'][rel_path] = "[Could not read file]"
        
        # Determine project type and technologies
        context['type'] = self._determine_project_type(context['files'])
        context['technologies'] = self._identify_technologies(context['files'])
        
        return context
    
    def _should_read_file(self, filename: str) -> bool:
        """Determine if file should be read for analysis"""
        read_extensions = {'.html', '.css', '.js', '.py', '.json', '.md', '.txt', '.yml', '.yaml'}
        important_files = {'README.md', 'package.json', 'requirements.txt', 'index.html'}
        
        return (
            filename in important_files or
            any(filename.endswith(ext) for ext in read_extensions)
        ) and not filename.startswith('.')
    
    def _determine_project_type(self, files: Dict[str, str]) -> str:
        """Determine project type from files"""
        if 'package.json' in files:
            return 'javascript/node'
        elif any(f.endswith('.html') for f in files):
            return 'web/html'
        elif any(f.endswith('.py') for f in files):
            return 'python'
        else:
            return 'unknown'
    
    def _identify_technologies(self, files: Dict[str, str]) -> List[str]:
        """Identify technologies used in project"""
        tech = []
        
        if any(f.endswith('.html') for f in files):
            tech.append('HTML')
        if any(f.endswith('.css') for f in files):
            tech.append('CSS')
        if any(f.endswith('.js') for f in files):
            tech.append('JavaScript')
        if 'package.json' in files:
            tech.append('Node.js')
        if any(f.endswith('.py') for f in files):
            tech.append('Python')
            
        return tech
    
    def _create_implementation_plan(self, context: Dict, user_intent: str) -> Dict:
        """Create comprehensive implementation plan using AI"""
        
        # Prefer AI Gateway for better planning
        ai_system = self.ai_gateway if (self.ai_gateway and getattr(self.ai_gateway, 'available', False)) else self.gemini
        
        if not ai_system:
            return {'error': 'AI not available for planning'}
        
        planning_prompt = f"""
You are an expert software developer analyzing a project to implement missing features.

Project: {context['name']}
Type: {context['type']}
Technologies: {', '.join(context['technologies'])}
User Intent: {user_intent}

Existing Files:
{chr(10).join([f"- {filename}: {len(content)} chars" for filename, content in context['files'].items() if content != "[Could not read file]"])}

File Contents Preview:
{chr(10).join([f"=== {filename} ==={chr(10)}{content[:500]}{'...' if len(content) > 500 else ''}{chr(10)}" for filename, content in list(context['files'].items())[:3] if content != "[Could not read file]"])}

Based on this analysis, create a JSON implementation plan with this structure:
{{
  "assessment": "brief assessment of current state",
  "missing_components": ["list", "of", "missing", "files/features"],
  "implementation_steps": [
    {{
      "step": 1,
      "action": "create_file",
      "filename": "index.html",
      "description": "Create main game interface",
      "priority": "high"
    }},
    {{
      "step": 2,
      "action": "create_file", 
      "filename": "style.css",
      "description": "Add styling and animations",
      "priority": "high"
    }}
  ],
  "success_criteria": ["working game", "responsive design", "animations"]
}}

Provide ONLY the JSON response, no explanations.
"""
        
        try:
            if hasattr(ai_system, 'smart_chat'):  # AI Gateway
                result = ai_system.smart_chat(planning_prompt, task_type='analysis')
                plan_response = result.get('response', '') if result.get('success') else ''
            else:  # Gemini
                plan_response = ai_system.chat(planning_prompt, stream=False, concise=True)
            
            # Extract JSON from response
            import json
            
            # Find JSON in the response
            start = plan_response.find('{')
            end = plan_response.rfind('}') + 1
            
            if start != -1 and end > start:
                plan_json = plan_response[start:end]
                return json.loads(plan_json)
            else:
                return {'error': 'Could not parse AI response'}
                
        except Exception as e:
            return {'error': f'Planning failed: {str(e)}'}
    
    def _execute_implementation_plan(self, plan: Dict, context: Dict) -> List[Dict]:
        """Execute the implementation plan autonomously"""
        
        if 'error' in plan:
            return [{'step': 'planning', 'success': False, 'error': plan['error']}]
        
        results = []
        
        print(f"📋 Assessment: {plan.get('assessment', 'Unknown')}")
        print(f"⚙️  Executing {len(plan.get('implementation_steps', []))} implementation steps...")
        
        for step_data in plan.get('implementation_steps', []):
            step_num = step_data.get('step', 0)
            action = step_data.get('action', '')
            filename = step_data.get('filename', '')
            description = step_data.get('description', '')
            
            print(f"  {step_num}. {description}")
            
            if action == 'create_file':
                result = self._create_file_with_ai(filename, description, context)
                results.append({
                    'step': step_num,
                    'action': action,
                    'filename': filename,
                    'success': result.get('success', False),
                    'details': result
                })
            
        return results
    
    def _create_file_with_ai(self, filename: str, description: str, context: Dict) -> Dict:
        """Use AI to generate and create a specific file"""
        
        # Use the best available AI system
        ai_system = self.ai_gateway if (self.ai_gateway and getattr(self.ai_gateway, 'available', False)) else self.gemini
        
        if not ai_system:
            return {'success': False, 'error': 'AI not available'}
        
        # Determine file type for appropriate generation
        file_ext = filename.split('.')[-1] if '.' in filename else ''
        
        generation_prompt = f"""
Generate the complete content for {filename} for this FlipAI memory card game project.

Project Context:
- Name: {context['name']}
- Type: {context['type']} 
- Technologies: {', '.join(context['technologies'])}
- Existing files: {list(context['files'].keys())}

Task: {description}

Requirements for {filename}:
"""
        
        if file_ext == 'html':
            generation_prompt += """
- Create a complete HTML5 document
- Include proper DOCTYPE and meta tags
- Create card grid layout for memory game
- Include game controls (start, reset, score, timer)
- Link to external CSS and JS files
- Make it semantic and accessible
- Add game title "FlipAI Memory Game"
"""
        elif file_ext == 'css':
            generation_prompt += """
- Style the memory card game beautifully
- Implement card flip animations (3D transforms)
- Create responsive grid layout
- Add hover effects and transitions
- Style game controls and UI
- Use modern CSS features (flexbox/grid)
- Add color scheme and typography
- Include mobile-responsive design
"""
        elif file_ext == 'js':
            generation_prompt += """
- Implement complete memory card game logic
- Card shuffling and initialization
- Card flip animation handling
- Match detection and game state management
- Score tracking and timer functionality
- Win condition detection
- Reset game functionality
- Mobile touch support
"""
        
        generation_prompt += f"""

Provide ONLY the complete file content for {filename}, no explanations or markdown formatting.
"""
        
        try:
            # Use appropriate AI system for code generation
            if hasattr(ai_system, 'generate_code_with_best_model'):  # AI Gateway
                result = ai_system.generate_code_with_best_model(generation_prompt, file_ext or 'text')
                file_content = result.get('response', '') if result.get('success') else ''
            elif hasattr(ai_system, 'smart_chat'):  # AI Gateway fallback
                result = ai_system.smart_chat(generation_prompt, task_type='code')
                file_content = result.get('response', '') if result.get('success') else ''
            else:  # Gemini
                file_content = ai_system.chat(generation_prompt, stream=False)
            
            if not file_content:
                return {'success': False, 'error': 'No content generated'}
            
            # Clean up the response (remove any markdown formatting)
            if file_content.startswith('```'):
                lines = file_content.split('\n')
                if len(lines) > 2:
                    file_content = '\n'.join(lines[1:-1])
            
            # Write the file
            file_path = os.path.join(self.current_project_path, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            print(f"    ✅ Created {filename} ({len(file_content)} chars)")
            
            return {
                'success': True,
                'filename': filename,
                'path': file_path,
                'size': len(file_content)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def get_superpower():
    return IntelligentExecutor()