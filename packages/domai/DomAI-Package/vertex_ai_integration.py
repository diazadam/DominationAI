#!/usr/bin/env python3
"""
Vertex AI Integration for DominateAI
Provides access to Google's Vertex AI models and ML platform
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
import subprocess

try:
    import vertexai
    from google.cloud import aiplatform
    from vertexai.generative_models import GenerativeModel, ChatSession, Part
    from vertexai.language_models import TextGenerationModel, ChatModel
    VERTEX_AI_AVAILABLE = True
except ImportError as e:
    VERTEX_AI_AVAILABLE = False
    print(f"Vertex AI SDK not available: {e}")

class VertexAIManager:
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        self.project_id = project_id or self._get_project_id()
        self.location = location
        
        if VERTEX_AI_AVAILABLE and self.project_id:
            try:
                # Initialize Vertex AI
                vertexai.init(project=self.project_id, location=self.location)
                aiplatform.init(project=self.project_id, location=self.location)
                print(f"✅ Vertex AI initialized for project: {self.project_id}")
                self.available = True
            except Exception as e:
                print(f"⚠️  Vertex AI initialization failed: {e}")
                self.available = False
        else:
            self.available = False
    
    def _get_project_id(self):
        """Get current GCP project ID"""
        try:
            result = subprocess.run(
                ['gcloud', 'config', 'get-value', 'project'],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def generate_code_with_gemini(self, description: str, language: str = "python") -> str:
        """Generate code using Gemini Pro"""
        if not self.available:
            return f"# Vertex AI not available\n# {description}"
        
        try:
            model = GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
Generate clean, working {language} code for: {description}

Requirements:
- Include proper error handling
- Add clear comments
- Follow best practices
- Make it production-ready
- Include example usage if applicable

Code:
"""
            
            response = model.generate_content(prompt)
            
            if response.text:
                return response.text
            else:
                return f"# Code generation failed for: {description}"
                
        except Exception as e:
            return f"# Error generating code: {e}\n# {description}"
    
    def chat_with_gemini(self, message: str, conversation_history: List[Dict] = None) -> str:
        """Chat with Gemini Pro model"""
        if not self.available:
            return "Vertex AI not available for chat."
        
        try:
            model = GenerativeModel("gemini-1.5-flash")
            
            # Start chat session
            if conversation_history:
                # Convert history to Vertex AI format
                chat = model.start_chat()
                for turn in conversation_history[-10:]:  # Last 10 turns
                    if turn['role'] == 'user':
                        chat.send_message(turn['content'])
            else:
                chat = model.start_chat()
            
            # Send current message
            response = chat.send_message(message)
            
            return response.text if response.text else "I couldn't generate a response."
            
        except Exception as e:
            return f"Chat error: {e}"
    
    def analyze_code(self, code: str, task: str = "analyze") -> str:
        """Analyze code using Gemini"""
        if not self.available:
            return "Vertex AI not available for code analysis."
        
        try:
            model = GenerativeModel("gemini-1.5-flash")
            
            prompts = {
                "analyze": f"Analyze this code and provide insights:\n\n{code}",
                "fix": f"Find and fix bugs in this code:\n\n{code}",
                "optimize": f"Optimize this code for better performance:\n\n{code}",
                "explain": f"Explain what this code does in simple terms:\n\n{code}",
                "review": f"Provide a code review with suggestions:\n\n{code}"
            }
            
            prompt = prompts.get(task, prompts["analyze"])
            response = model.generate_content(prompt)
            
            return response.text if response.text else "Analysis failed."
            
        except Exception as e:
            return f"Analysis error: {e}"
    
    def create_model_endpoint(self, model_name: str, model_path: str) -> Optional[str]:
        """Deploy a custom model to Vertex AI endpoint"""
        if not self.available:
            return None
        
        try:
            # Upload model
            model = aiplatform.Model.upload(
                display_name=model_name,
                artifact_uri=model_path,
                serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-3:latest"
            )
            
            # Create endpoint
            endpoint = aiplatform.Endpoint.create(
                display_name=f"{model_name}-endpoint"
            )
            
            # Deploy model to endpoint
            endpoint.deploy(
                model=model,
                deployed_model_display_name=model_name,
                machine_type="n1-standard-2",
                min_replica_count=1,
                max_replica_count=1
            )
            
            print(f"✅ Model '{model_name}' deployed to endpoint: {endpoint.resource_name}")
            return endpoint.resource_name
            
        except Exception as e:
            print(f"❌ Model deployment failed: {e}")
            return None
    
    def list_models(self) -> List[Dict]:
        """List all models in the project"""
        if not self.available:
            return []
        
        try:
            models = aiplatform.Model.list()
            
            model_list = []
            for model in models:
                model_list.append({
                    'name': model.display_name,
                    'resource_name': model.resource_name,
                    'created': model.create_time.isoformat() if model.create_time else 'Unknown',
                    'framework': model.version_description if hasattr(model, 'version_description') else 'Unknown'
                })
            
            return model_list
            
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def list_endpoints(self) -> List[Dict]:
        """List all endpoints in the project"""
        if not self.available:
            return []
        
        try:
            endpoints = aiplatform.Endpoint.list()
            
            endpoint_list = []
            for endpoint in endpoints:
                endpoint_list.append({
                    'name': endpoint.display_name,
                    'resource_name': endpoint.resource_name,
                    'created': endpoint.create_time.isoformat() if endpoint.create_time else 'Unknown',
                    'traffic': len(endpoint.traffic_split) if endpoint.traffic_split else 0
                })
            
            return endpoint_list
            
        except Exception as e:
            print(f"Error listing endpoints: {e}")
            return []
    
    def predict_endpoint(self, endpoint_name: str, instances: List[Dict]) -> Dict:
        """Make predictions using a deployed endpoint"""
        if not self.available:
            return {'error': 'Vertex AI not available'}
        
        try:
            # Get endpoint
            endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
            
            # Make prediction
            predictions = endpoint.predict(instances=instances)
            
            return {
                'predictions': predictions.predictions,
                'deployed_model_id': predictions.deployed_model_id,
                'model_version_id': getattr(predictions, 'model_version_id', None)
            }
            
        except Exception as e:
            return {'error': f'Prediction failed: {e}'}
    
    def run_batch_prediction(self, model_name: str, input_uri: str, output_uri: str) -> Optional[str]:
        """Run batch prediction job"""
        if not self.available:
            return None
        
        try:
            # Create batch prediction job
            job = aiplatform.BatchPredictionJob.create(
                job_display_name=f"batch-prediction-{int(time.time())}",
                model_name=model_name,
                instances_format='jsonl',
                predictions_format='jsonl',
                gcs_source_uris=[input_uri],
                gcs_destination_output_uri_prefix=output_uri,
                machine_type="n1-standard-2"
            )
            
            print(f"✅ Batch prediction job started: {job.resource_name}")
            return job.resource_name
            
        except Exception as e:
            print(f"❌ Batch prediction failed: {e}")
            return None
    
    def create_training_job(self, 
                          display_name: str,
                          script_path: str, 
                          container_uri: str,
                          args: List[str] = None) -> Optional[str]:
        """Create a custom training job"""
        if not self.available:
            return None
        
        try:
            # Define training job
            job = aiplatform.CustomTrainingJob(
                display_name=display_name,
                script_path=script_path,
                container_uri=container_uri,
                requirements=["scikit-learn", "pandas", "numpy"],
                model_serving_container_image_uri="gcr.io/cloud-aiplatform/prediction/sklearn-cpu.1-3:latest"
            )
            
            # Run the training job
            model = job.run(
                replica_count=1,
                machine_type="n1-standard-4",
                args=args or []
            )
            
            print(f"✅ Training job completed: {model.resource_name}")
            return model.resource_name
            
        except Exception as e:
            print(f"❌ Training job failed: {e}")
            return None
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get detailed information about a model"""
        if not self.available:
            return {'error': 'Vertex AI not available'}
        
        try:
            model = aiplatform.Model(model_name=model_name)
            
            return {
                'name': model.display_name,
                'resource_name': model.resource_name,
                'created': model.create_time.isoformat() if model.create_time else 'Unknown',
                'updated': model.update_time.isoformat() if model.update_time else 'Unknown',
                'description': model.description or 'No description',
                'labels': model.labels or {},
                'artifact_uri': model.artifact_uri or 'Not specified',
                'framework': getattr(model, 'version_description', 'Unknown')
            }
            
        except Exception as e:
            return {'error': f'Failed to get model info: {e}'}
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a model"""
        if not self.available:
            return False
        
        try:
            model = aiplatform.Model(model_name=model_name)
            model.delete()
            print(f"✅ Model deleted: {model_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete model: {e}")
            return False
    
    def delete_endpoint(self, endpoint_name: str) -> bool:
        """Delete an endpoint"""
        if not self.available:
            return False
        
        try:
            endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
            endpoint.delete()
            print(f"✅ Endpoint deleted: {endpoint_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to delete endpoint: {e}")
            return False
    
    def show_status(self) -> Dict:
        """Show Vertex AI status and configuration"""
        status = {
            'available': self.available,
            'project_id': self.project_id,
            'location': self.location,
            'sdk_installed': VERTEX_AI_AVAILABLE
        }
        
        if self.available:
            try:
                models = len(self.list_models())
                endpoints = len(self.list_endpoints())
                status.update({
                    'models_count': models,
                    'endpoints_count': endpoints
                })
            except:
                status.update({
                    'models_count': 'Unknown',
                    'endpoints_count': 'Unknown'
                })
        
        return status


# Convenience functions for DomAI integration
def quick_generate_code(description: str, language: str = "python") -> str:
    """Quick code generation using Vertex AI"""
    vertex = VertexAIManager()
    return vertex.generate_code_with_gemini(description, language)

def quick_chat(message: str) -> str:
    """Quick chat with Gemini"""
    vertex = VertexAIManager()
    return vertex.chat_with_gemini(message)

def quick_analyze_code(code: str, task: str = "analyze") -> str:
    """Quick code analysis"""
    vertex = VertexAIManager()
    return vertex.analyze_code(code, task)

if __name__ == "__main__":
    # Test Vertex AI integration
    print("🤖 Testing Vertex AI Integration")
    print("=" * 50)
    
    vertex = VertexAIManager()
    
    if vertex.available:
        print("✅ Vertex AI is ready!")
        
        # Test code generation
        print("\n🧪 Testing code generation...")
        test_code = vertex.generate_code_with_gemini("create a function to calculate fibonacci numbers")
        print("Generated code preview:")
        print(test_code[:200] + "..." if len(test_code) > 200 else test_code)
        
        # Test chat
        print("\n💬 Testing chat...")
        response = vertex.chat_with_gemini("Hello! What can you help me with?")
        print(f"Chat response: {response[:100]}...")
        
        # Show status
        print("\n📊 Status:")
        status = vertex.show_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
            
    else:
        print("❌ Vertex AI not available")
        print("Make sure you have:")
        print("  1. Vertex AI API enabled")
        print("  2. Proper authentication")
        print("  3. Valid GCP project")