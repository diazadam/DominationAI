#!/usr/bin/env python3
"""
Setup Vertex AI authentication for DominateAI
"""

import os
import json
import subprocess
from pathlib import Path

def setup_service_account_auth():
    """Set up service account authentication for Vertex AI"""
    
    print("🔐 Setting up Vertex AI Authentication")
    print("=" * 50)
    
    # Your project details
    project_id = "gen-lang-client-0093497568"
    service_account_email = "vertex-express@acoustic-fusion-467407-c3.iam.gserviceaccount.com"
    
    print(f"📊 Project: {project_id}")
    print(f"🔑 Service Account: {service_account_email}")
    
    # Check if gcloud is configured
    try:
        result = subprocess.run(
            ['gcloud', 'config', 'get-value', 'account'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            current_account = result.stdout.strip()
            print(f"👤 Current gcloud account: {current_account}")
        else:
            print("⚠️  No gcloud account configured")
            
    except Exception as e:
        print(f"❌ gcloud not available: {e}")
        return False
    
    # Try to create and download a service account key
    print("\n🔧 Creating service account key...")
    
    key_file = Path.home() / ".config" / "gcloud" / "vertex-ai-key.json"
    key_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create service account key
        result = subprocess.run([
            'gcloud', 'iam', 'service-accounts', 'keys', 'create',
            str(key_file),
            f'--iam-account={service_account_email}',
            f'--project={project_id}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Service account key created: {key_file}")
            
            # Set environment variable for the session
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(key_file)
            
            # Add to shell profiles for persistence
            shell_configs = [
                Path.home() / ".zshrc",
                Path.home() / ".bash_profile",
                Path.home() / ".bashrc"
            ]
            
            export_line = f'export GOOGLE_APPLICATION_CREDENTIALS="{key_file}"'
            
            for config_file in shell_configs:
                if config_file.exists():
                    # Check if already added
                    content = config_file.read_text()
                    if 'GOOGLE_APPLICATION_CREDENTIALS' not in content:
                        with open(config_file, 'a') as f:
                            f.write(f'\n# Vertex AI Authentication\n{export_line}\n')
                        print(f"✅ Added to {config_file}")
            
            return True
            
        else:
            print(f"❌ Failed to create service account key: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating service account key: {e}")
        return False

def test_vertex_ai_access():
    """Test Vertex AI access with authentication"""
    
    print("\n🧪 Testing Vertex AI Access")
    print("-" * 30)
    
    try:
        import vertexai
        from vertexai.generative_models import GenerativeModel
        
        # Initialize Vertex AI
        project_id = "gen-lang-client-0093497568"
        vertexai.init(project=project_id, location="us-central1")
        
        # Create model
        model = GenerativeModel("gemini-1.5-flash")
        
        # Test generation
        print("🤖 Testing Gemini generation...")
        response = model.generate_content("Say 'DominateAI is ready!' in a creative way")
        
        if response and response.text:
            print("✅ SUCCESS! Gemini is working!")
            print(f"🎉 Response: {response.text}")
            return True
        else:
            print("❌ No response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Vertex AI test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 DominateAI Vertex AI Setup")
    print("=" * 40)
    
    # Setup authentication
    auth_success = setup_service_account_auth()
    
    if auth_success:
        # Test Vertex AI
        test_success = test_vertex_ai_access()
        
        if test_success:
            print("\n🎯 Setup Complete!")
            print("✅ Vertex AI authentication configured")
            print("✅ Gemini models accessible")
            print("✅ DominateAI ready for AI-powered automation")
            
            print("\n🚀 You can now use:")
            print("   DomAI > generate code for a web scraper")
            print("   DomAI > chat about deployment strategies")
            print("   DomAI > analyze code main.py")
            
        else:
            print("\n❌ Setup incomplete - Vertex AI test failed")
    else:
        print("\n❌ Authentication setup failed")
        print("💡 Alternative: Run 'gcloud auth application-default login' manually")

if __name__ == "__main__":
    main()