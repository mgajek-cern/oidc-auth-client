from .base import AuthStrategy

class SimpleFormStrategy(AuthStrategy):
    """Simple username/password form login"""
    
    def __init__(self, 
                 username_selector='input[name="username"]',
                 password_selector='input[name="password"]',
                 submit_selector='button[type="submit"]'):
        self.username_selector = username_selector
        self.password_selector = password_selector
        self.submit_selector = submit_selector
    
    def login(self, page, username, password):
        """Fill simple login form"""
        print("📍 Filling login form...")
        
        # Wait for and fill username
        page.wait_for_selector(self.username_selector, timeout=10000)
        page.fill(self.username_selector, username)
        
        # Fill password
        page.fill(self.password_selector, password)
        
        # Submit form
        page.click(self.submit_selector)
        page.wait_for_load_state('networkidle')
        
        print("   ✓ Login form submitted")