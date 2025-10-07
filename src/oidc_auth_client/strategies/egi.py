from .base import AuthStrategy


class EGIStrategy(AuthStrategy):
    """EGI Check-in specific authentication flow"""
    
    def __init__(self, 
                 identity_provider="EGI Check-in (Devel)",
                 sso_provider="EGI SSO",
                 debug=False):
        self.identity_provider = identity_provider
        self.sso_provider = sso_provider
        self.debug = debug
    
    def login(self, page, username, password):
        """Execute EGI-specific multi-step login"""
        
        # Step 1: Select identity provider
        print(f"📍 Clicking '{self.identity_provider}'...")
        page.wait_for_selector(f'text={self.identity_provider}', timeout=5000)
        page.click(f'text={self.identity_provider}')
        page.wait_for_load_state('networkidle')
        
        if self.debug:
            page.screenshot(path='debug/debug_step1_identity_provider.png')
            print(f"   Current URL: {page.url}")
        
        # Step 2: Select SSO provider
        print(f"📍 Clicking '{self.sso_provider}'...")
        page.wait_for_selector(f'text={self.sso_provider}', timeout=5000)
        page.click(f'text={self.sso_provider}')
        page.wait_for_load_state('networkidle')
        
        if self.debug:
            page.screenshot(path='debug/debug_step2_sso_provider.png')
            print(f"   Current URL: {page.url}")
        
        # Step 3: Fill login form (EGI uses j_username/j_password)
        print("📍 Filling login credentials...")
        page.wait_for_selector('input[name="j_username"]', timeout=10000)
        page.fill('input[name="j_username"]', username)
        page.fill('input[name="j_password"]', password)
        print("   ✓ Credentials filled")
        
        if self.debug:
            page.screenshot(path='debug/debug_step3_credentials_filled.png')
        
        # Step 4: Submit login
        print("📍 Submitting login...")
        page.click('button[name="_eventId_proceed"]')
        page.wait_for_load_state('networkidle')
        
        if self.debug:
            page.screenshot(path='debug/debug_step4_after_login.png')
            print(f"   Current URL: {page.url}")
        
        # Step 5: Handle consent page
        print("📍 Checking for consent page...")
        try:
            page.wait_for_selector('button:has-text("Accept")', timeout=5000)
            print("   ✓ Consent page found, clicking Accept...")
            page.click('button:has-text("Accept")')
            page.wait_for_load_state('networkidle')
            
            if self.debug:
                page.screenshot(path='debug/debug_step5_after_consent.png')
        except:
            print("   ℹ No consent page (already accepted)")