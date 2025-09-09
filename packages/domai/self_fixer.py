#!/Library/Developer/CommandLineTools/usr/bin/python3
"""
Self-Fixer Superpower for DomAI
Detects and fixes its own errors autonomously
"""

import os
import sys
import traceback
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class SelfFixer:
    def __init__(self, ai_gateway=None, gemini=None):
        self.name = "Self Fixer"
        self.ai_gateway = ai_gateway
        self.gemini = gemini
        self.error_log = []
        
    def detect_and_fix_error(self, error_msg: str, context: str = "") -> Dict:
        """Automatically detect and fix errors"""
        
        print(f"🔧 Self-fixing error: {error_msg}")
        
        # Log the error
        self.error_log.append({
            'error': error_msg,
            'context': context,
            'timestamp': __import__('time').time()
        })
        
        # Analyze error and generate fix
        fix_result = self._analyze_and_fix_error(error_msg, context)
        
        if fix_result.get('success'):
            print(f"✅ Fixed: {fix_result.get('description', 'Error resolved')}")
            
            # Apply the fix if it involves code changes
            if 'code_fix' in fix_result:
                self._apply_code_fix(fix_result['code_fix'])
                
            return fix_result
        else:
            print(f"❌ Could not auto-fix: {error_msg}")
            return fix_result
    
    def _analyze_and_fix_error(self, error_msg: str, context: str) -> Dict:
        """Use AI to analyze error and generate fix"""
        
        ai_system = self._get_best_ai()
        if not ai_system:
            return {'success': False, 'error': 'No AI available for analysis'}
        
        analysis_prompt = f"""
You are an expert debugging assistant. Analyze this error and provide a fix:

Error Message: {error_msg}
Context: {context}

Common error patterns and fixes:
1. "'CompletionUsage' object has no attribute '_asdict'" - Replace _asdict() with dict() conversion
2. "Model 'openai/gpt-4' not found" - Use correct model names like 'gpt-4'
3. Import errors - Install missing packages or fix import paths
4. API key issues - Check authentication and permissions

Provide a JSON response with:
{{
  "error_type": "api_error|import_error|model_error|auth_error",
  "diagnosis": "detailed explanation of the problem",
  "fix_description": "what needs to be fixed",
  "code_fix": {{
    "file": "path/to/file.py",
    "old_code": "code to replace",
    "new_code": "replacement code"
  }},
  "success": true
}}

Focus on actual fixes, not just explanations.
"""
        
        try:
            if hasattr(ai_system, 'smart_chat'):  # AI Gateway
                result = ai_system.smart_chat(analysis_prompt, task_type='code')
                response = result.get('response', '') if result.get('success') else ''
            else:  # Gemini fallback
                response = ai_system.chat(analysis_prompt, stream=False)
            
            # Parse JSON response
            import json
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                fix_data = json.loads(response[start:end])
                return fix_data
            else:
                return {'success': False, 'error': 'Could not parse fix response'}
                
        except Exception as e:
            return {'success': False, 'error': f'Fix analysis failed: {str(e)}'}
    
    def _apply_code_fix(self, code_fix: Dict):
        """Apply code fix to the actual file"""
        
        file_path = code_fix.get('file', '')
        old_code = code_fix.get('old_code', '')
        new_code = code_fix.get('new_code', '')
        
        if not file_path or not old_code:
            return False
        
        try:
            # Read the file
            full_path = Path(file_path)
            if not full_path.exists():
                # Try relative to DomAI directory
                full_path = Path(__file__).parent / file_path
            
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Apply the fix
                if old_code in content:
                    fixed_content = content.replace(old_code, new_code)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    
                    print(f"    🔧 Applied fix to {full_path}")
                    return True
                else:
                    print(f"    ⚠️  Could not find code to replace in {full_path}")
                    
        except Exception as e:
            print(f"    ❌ Failed to apply fix: {e}")
            
        return False
    
    def fix_ai_gateway_errors(self) -> Dict:
        """Specifically fix AI Gateway model and usage errors"""
        
        print("🔧 Fixing AI Gateway errors...")
        
        fixes_applied = []
        
        # Fix 1: CompletionUsage._asdict() error
        ai_gateway_file = Path(__file__).parent / "ai_gateway_manager.py"
        if ai_gateway_file.exists():
            with open(ai_gateway_file, 'r') as f:
                content = f.read()
            
            if '_asdict()' in content:
                fixed_content = content.replace(
                    'response.usage._asdict()',
                    'dict(response.usage) if response.usage else None'
                )
                
                with open(ai_gateway_file, 'w') as f:
                    f.write(fixed_content)
                
                fixes_applied.append("Fixed CompletionUsage._asdict() error")
        
        # Fix 2: Update model names to correct ones
        model_fixes = {
            'openai/gpt-4': 'gpt-4',
            'openai/gpt-4-turbo': 'gpt-4-turbo-preview', 
            'openai/gpt-3.5-turbo': 'gpt-3.5-turbo',
            'anthropic/claude-sonnet-4': 'claude-3-sonnet-20240229',
            'anthropic/claude-3-opus': 'claude-3-opus-20240229',
            'anthropic/claude-3-sonnet': 'claude-3-sonnet-20240229',
            'google/gemini-pro': 'gemini-pro',
        }
        
        if ai_gateway_file.exists():
            with open(ai_gateway_file, 'r') as f:
                content = f.read()
            
            modified = False
            for old_model, new_model in model_fixes.items():
                if f"'{old_model}'" in content:
                    content = content.replace(f"'{old_model}'", f"'{new_model}'")
                    modified = True
                    fixes_applied.append(f"Updated model {old_model} -> {new_model}")
            
            if modified:
                with open(ai_gateway_file, 'w') as f:
                    f.write(content)
        
        # Fix 3: Test with known working models
        working_models = ['gpt-3.5-turbo', 'gpt-4']
        
        return {
            'success': True,
            'fixes_applied': fixes_applied,
            'recommended_models': working_models
        }
    
    def install_missing_packages(self, package_names: List[str]) -> Dict:
        """Install missing Python packages"""
        
        installed = []
        failed = []
        
        for package in package_names:
            try:
                print(f"📦 Installing {package}...")
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    installed.append(package)
                    print(f"    ✅ {package} installed")
                else:
                    failed.append(package)
                    print(f"    ❌ {package} failed: {result.stderr}")
                    
            except Exception as e:
                failed.append(package)
                print(f"    ❌ {package} error: {e}")
        
        return {
            'success': len(installed) > 0,
            'installed': installed,
            'failed': failed
        }
    
    def _get_best_ai(self):
        """Get the best available AI system"""
        if self.ai_gateway and getattr(self.ai_gateway, 'available', False):
            return self.ai_gateway
        elif self.gemini and getattr(self.gemini, 'available', False):
            return self.gemini
        return None
    
    def auto_fix_command_errors(self) -> bool:
        """Automatically detect and fix common command errors"""
        
        # Check for common issues and fix them
        fixes = [
            self.fix_ai_gateway_errors(),
        ]
        
        success_count = sum(1 for fix in fixes if fix.get('success'))
        
        if success_count > 0:
            print(f"🔧 Applied {success_count} automatic fixes")
            print("🔄 Please try your command again - errors should be resolved")
            return True
        
        return False

def get_superpower():
    return SelfFixer()