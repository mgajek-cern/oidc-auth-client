import secrets
import hashlib
import base64
from urllib.parse import urlencode, urlparse, parse_qs
import requests
from requests.auth import HTTPBasicAuth
from playwright.sync_api import sync_playwright

from .strategies import SimpleFormStrategy


class OIDCAuthClient:
    def __init__(
        self,
        issuer_url,
        client_id,
        client_secret,
        username,
        password,
        redirect_uri="https://google.com",
        scope="openid profile email",
        auth_strategy=None,
    ):
        """
        Initialize OIDC Authentication Client
        
        Args:
            issuer_url: OIDC issuer URL
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            username: User username
            password: User password
            redirect_uri: OAuth2 redirect URI
            scope: OAuth2 scopes
            auth_strategy: AuthStrategy instance (defaults to SimpleFormStrategy)
        """
        self.issuer_url = issuer_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.auth_strategy = auth_strategy or SimpleFormStrategy()
        
    def generate_pkce(self):
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).decode('utf-8').rstrip('=')
        
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode('utf-8').rstrip('=')
        
        return code_verifier, code_challenge
    
    def create_auth_url(self, code_challenge, state):
        """Create authorization URL"""
        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': self.scope,
            'redirect_uri': self.redirect_uri,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        return f"{self.issuer_url}/protocol/openid-connect/auth?{urlencode(auth_params)}"
    
    def automate_login(self, auth_url, headless=True, debug=False):
        """Automate the login process using the configured strategy"""
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                slow_mo=500 if debug else 0
            )
            page = browser.new_page()
            
            try:
                # Navigate to auth URL
                print("📍 Navigating to authorization URL...")
                page.goto(auth_url)
                page.wait_for_load_state('networkidle')
                
                if debug:
                    page.screenshot(path='debug/debug_step0_initial.png')
                    print(f"   Current URL: {page.url}")
                
                # Enable debug mode in strategy if supported
                if hasattr(self.auth_strategy, 'debug'):
                    self.auth_strategy.debug = debug
                
                # Use strategy to perform login
                self.auth_strategy.login(page, self.username, self.password)
                
                # Redirected with authorization code
                print("📍 Redirected...")
                
                # Extract authorization code
                current_url = page.url
                parsed_url = urlparse(current_url)
                query_params = parse_qs(parsed_url.query)
                
                auth_code = query_params.get('code', [None])[0]
                state = query_params.get('state', [None])[0]
                
                if not auth_code:
                    raise Exception(f"No authorization code in URL: {current_url}")
                
                print(f"   ✓ Authorization code extracted")
                
                if debug:
                    page.screenshot(path='debug/debug_final_redirect.png')
                    print(f"   Final URL: {current_url}")
                
                return auth_code, state
                
            except Exception as e:
                page.screenshot(path='debug/debug_error.png')
                print(f"\n❌ Error at: {page.url}")
                print(f"   Screenshot: debug/debug_error.png")
                raise
            finally:
                browser.close()
    
    def exchange_code_for_tokens(self, auth_code, code_verifier):
        """Exchange authorization code for tokens"""
        token_url = f"{self.issuer_url}/protocol/openid-connect/token"
        
        response = requests.post(
            token_url,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            data={
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
                'code_verifier': code_verifier
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Token exchange failed: {response.text}")
    
    def get_tokens(self, headless=True, verbose=True, debug=False):
        """Complete automated PKCE flow to get tokens"""
        code_verifier, code_challenge = self.generate_pkce()
        state = secrets.token_urlsafe(16)
        
        if verbose:
            print(f"Code Verifier: {code_verifier}\n")
        
        auth_url = self.create_auth_url(code_challenge, state)
        
        if verbose:
            print("Starting automated login...\n")
        
        auth_code, returned_state = self.automate_login(auth_url, headless, debug)
        
        if verbose:
            print(f"\nState matches: {state == returned_state}")
            print("Exchanging code for tokens...\n")
        
        tokens = self.exchange_code_for_tokens(auth_code, code_verifier)
        return tokens