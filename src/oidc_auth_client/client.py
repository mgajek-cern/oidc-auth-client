import secrets
import hashlib
import base64
from urllib.parse import urlencode, urlparse, parse_qs
import requests
from requests.auth import HTTPBasicAuth
from playwright.sync_api import sync_playwright


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
        identity_provider=None,
    ):
        """
        Initialize OIDC Authentication Client
        
        Args:
            issuer_url: OIDC issuer URL (e.g., https://aai-dev.egi.eu/auth/realms/egi)
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            username: User username
            password: User password
            redirect_uri: OAuth2 redirect URI
            scope: OAuth2 scopes
            identity_provider: Identity provider name to select (optional)
        """
        self.issuer_url = issuer_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.identity_provider = identity_provider
        
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
    
    def automate_login(self, auth_url, headless=True):
        """Automate the login process and get authorization code"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            
            # Navigate to auth URL
            page.goto(auth_url)
            page.wait_for_load_state('networkidle')
            
            # Select identity provider if specified
            if self.identity_provider:
                page.click(f'text={self.identity_provider}')
            
            # Wait for login form
            page.wait_for_selector('input[name="username"]', timeout=10000)
            
            # Fill in credentials
            page.fill('input[name="username"]', self.username)
            page.fill('input[name="password"]', self.password)
            
            # Click login button
            page.click('input[type="submit"], button[type="submit"]')
            
            # Wait for redirect with the code
            page.wait_for_url(f'{self.redirect_uri}*', timeout=15000)
            
            # Extract the authorization code from URL
            current_url = page.url
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            
            auth_code = query_params.get('code', [None])[0]
            state = query_params.get('state', [None])[0]
            
            browser.close()
            
            return auth_code, state
    
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
    
    def get_tokens(self, headless=True, verbose=True):
        """
        Complete automated flow to get tokens
        
        Args:
            headless: Run browser in headless mode
            verbose: Print progress information
            
        Returns:
            dict: Token response containing access_token, id_token, etc.
        """
        # Generate PKCE values
        code_verifier, code_challenge = self.generate_pkce()
        state = secrets.token_urlsafe(16)
        
        if verbose:
            print(f"Code Verifier: {code_verifier}")
            print(f"State: {state}\n")
        
        # Create auth URL
        auth_url = self.create_auth_url(code_challenge, state)
        if verbose:
            print(f"Authorization URL: {auth_url}\n")
        
        # Automate login and get code
        if verbose:
            print("Starting automated login...")
        auth_code, returned_state = self.automate_login(auth_url, headless)
        
        if not auth_code:
            raise Exception("Failed to get authorization code")
        
        if verbose:
            print(f"Authorization Code: {auth_code}")
            print(f"State matches: {state == returned_state}\n")
        
        # Exchange code for tokens
        if verbose:
            print("Exchanging code for tokens...")
        tokens = self.exchange_code_for_tokens(auth_code, code_verifier)
        
        return tokens