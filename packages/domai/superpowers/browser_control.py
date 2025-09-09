
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
