
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
                        "jsCode": "// Process incoming data\nreturn items;"
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
