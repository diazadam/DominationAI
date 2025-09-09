
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
