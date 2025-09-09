#!/Library/Developer/CommandLineTools/usr/bin/python3
"""
AI Gateway Manager for DomAI
Provides access to 100+ models through Vercel AI Gateway
"""

import os
from typing import Dict, List, Optional, Any
import json

class AIGatewayManager:
    def __init__(self):
        self.name = "AI Gateway Manager"
        self.api_key = "vck_3iKW9qXMeku6PNU6IvrnjcrQWnyCTpR74DoE95edEdaHYhcSbR3uVLpH"
        self.base_url = "https://ai-gateway.vercel.sh/v1"
        self.available_models = {
            # OpenAI Models (corrected names)
            'gpt-4': 'GPT-4 - Most capable OpenAI model',
            'gpt-4-turbo-preview': 'GPT-4 Turbo - Faster and cheaper GPT-4',
            'gpt-3.5-turbo': 'GPT-3.5 Turbo - Fast and efficient',
            
            # Anthropic Models (corrected names)
            'claude-3-opus-20240229': 'Claude 3 Opus - Most powerful Claude',
            'claude-3-sonnet-20240229': 'Claude 3 Sonnet - Balanced performance',
            'claude-3-haiku-20240307': 'Claude 3 Haiku - Fast and efficient',
            
            # Google Models
            'gemini-pro': 'Gemini Pro - Google\'s flagship model',
            'google/gemini-ultra': 'Gemini Ultra - Most capable Google model',
            
            # Meta Models
            'meta/llama-2-70b': 'Llama 2 70B - Open source large model',
            'meta/llama-2-13b': 'Llama 2 13B - Efficient open source model',
            
            # Cohere Models
            'cohere/command': 'Cohere Command - General purpose model',
            'cohere/command-r': 'Cohere Command R - Reasoning focused',
            
            # Mistral Models
            'mistral/mistral-large': 'Mistral Large - High performance model',
            'mistral/mistral-medium': 'Mistral Medium - Balanced model',
            
            # Specialized Models
            'openai/code-davinci': 'Code Davinci - Code generation specialist',
            'anthropic/claude-instant': 'Claude Instant - Fast responses',
        }
        
        self.setup_client()
    
    def setup_client(self):
        """Setup OpenAI client for AI Gateway"""
        try:
            from openai import OpenAI
            
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            print(f"✅ AI Gateway connected - Access to {len(self.available_models)} models")
            self.available = True
            
        except ImportError:
            print("⚠️  OpenAI package not found. Install with: pip install openai")
            self.available = False
            self.client = None
        except Exception as e:
            print(f"⚠️  AI Gateway setup failed: {e}")
            self.available = False
            self.client = None
    
    def chat_with_model(self, message: str, model: str = 'claude-3-sonnet-20240229', 
                       temperature: float = 0.7, max_tokens: int = 2000) -> Dict:
        """Chat with any available model through AI Gateway"""
        
        if not self.available or not self.client:
            return {
                'success': False,
                'error': 'AI Gateway not available'
            }
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        'role': 'user',
                        'content': message
                    }
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return {
                'success': True,
                'model': model,
                'response': response.choices[0].message.content,
                'usage': dict(response.usage) if response.usage else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': model
            }
    
    def get_best_model_for_task(self, task_type: str) -> str:
        """Recommend the best model for a specific task"""
        
        task_models = {
            'code': 'gpt-4',  # Great for code generation
            'creative': 'claude-3-opus-20240229',  # Best for creative writing
            'analysis': 'claude-3-sonnet-20240229',  # Excellent reasoning
            'fast': 'gpt-3.5-turbo',  # Quick responses
            'reasoning': 'claude-3-opus-20240229',  # Complex reasoning
            'conversation': 'claude-3-sonnet-20240229',  # Natural conversation
            'technical': 'gpt-4-turbo-preview',  # Technical documentation
            'general': 'claude-3-sonnet-20240229',  # Default choice
        }
        
        return task_models.get(task_type.lower(), 'claude-3-sonnet-20240229')
    
    def compare_models(self, message: str, models: List[str]) -> Dict:
        """Compare responses from multiple models"""
        
        results = {}
        
        for model in models:
            print(f"🤖 Testing {model}...")
            result = self.chat_with_model(message, model)
            results[model] = result
        
        return {
            'message': message,
            'models_tested': models,
            'results': results
        }
    
    def smart_chat(self, message: str, task_type: str = 'general', 
                   fallback_models: List[str] = None) -> Dict:
        """Intelligently choose model and handle failovers"""
        
        # Get best model for task
        primary_model = self.get_best_model_for_task(task_type)
        
        # Set fallback models if not provided
        if not fallback_models:
            fallback_models = [
                'claude-3-sonnet-20240229',
                'gpt-4-turbo-preview', 
                'gpt-3.5-turbo'
            ]
        
        # Try primary model first
        result = self.chat_with_model(message, primary_model)
        
        if result.get('success'):
            return result
        
        # Try fallback models
        for fallback_model in fallback_models:
            if fallback_model != primary_model:
                print(f"🔄 Trying fallback: {fallback_model}")
                result = self.chat_with_model(message, fallback_model)
                
                if result.get('success'):
                    result['fallback_used'] = fallback_model
                    return result
        
        return {
            'success': False,
            'error': 'All models failed',
            'attempted_models': [primary_model] + fallback_models
        }
    
    def generate_code_with_best_model(self, description: str, language: str = 'python') -> Dict:
        """Generate code using the best coding model"""
        
        coding_prompt = f"""
Generate complete, production-ready {language} code for: {description}

Requirements:
- Include proper error handling
- Add clear comments explaining the logic
- Follow {language} best practices and conventions
- Make the code modular and reusable
- Include example usage if applicable

Provide only the code, no explanations or markdown formatting.
"""
        
        # Use the best coding model
        return self.smart_chat(coding_prompt, task_type='code')
    
    def analyze_project_with_advanced_ai(self, project_context: Dict) -> Dict:
        """Use advanced AI models to analyze and plan project completion"""
        
        analysis_prompt = f"""
You are an expert software architect analyzing a project for completion.

Project Details:
- Name: {project_context.get('name', 'Unknown')}
- Type: {project_context.get('type', 'Unknown')}
- Technologies: {', '.join(project_context.get('technologies', []))}
- Files: {list(project_context.get('files', {}).keys())}

File Contents:
{json.dumps({k: v[:500] + '...' if len(v) > 500 else v for k, v in project_context.get('files', {}).items()}, indent=2)}

Provide a comprehensive analysis with:
1. Current state assessment
2. Missing components identification  
3. Implementation priority ranking
4. Detailed step-by-step completion plan
5. Quality improvement suggestions
6. Deployment recommendations

Be specific and actionable.
"""
        
        return self.smart_chat(analysis_prompt, task_type='analysis')
    
    def list_models(self) -> Dict[str, str]:
        """List all available models"""
        return self.available_models
    
    def get_model_info(self, model: str) -> str:
        """Get information about a specific model"""
        return self.available_models.get(model, "Model not found")

def get_superpower():
    return AIGatewayManager()

if __name__ == "__main__":
    print("🚀 Testing AI Gateway Manager")
    print("=" * 50)
    
    gateway = AIGatewayManager()
    
    if gateway.available:
        # Test basic chat
        print("\n🧪 Testing Claude Sonnet 4:")
        result = gateway.chat_with_model(
            "Explain quantum computing in one sentence.",
            model='claude-3-sonnet-20240229'
        )
        
        if result.get('success'):
            print(f"✅ Response: {result['response']}")
            print(f"📊 Usage: {result.get('usage', 'N/A')}")
        else:
            print(f"❌ Error: {result.get('error')}")
        
        # Test smart chat with task type
        print("\n🧪 Testing Smart Chat for Code Generation:")
        code_result = gateway.smart_chat(
            "Create a Python function to calculate fibonacci numbers",
            task_type='code'
        )
        
        if code_result.get('success'):
            print(f"✅ Model used: {code_result['model']}")
            print(f"Code generated: {len(code_result['response'])} characters")
        
        # Show available models
        print(f"\n📋 Available models: {len(gateway.available_models)}")
        for model, description in list(gateway.available_models.items())[:5]:
            print(f"  • {model}: {description}")
        print("  ... and many more!")
        
    else:
        print("❌ AI Gateway not available")