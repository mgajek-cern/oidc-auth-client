import argparse
import sys
from .client import OIDCAuthClient


def main():
    parser = argparse.ArgumentParser(
        description="Automated OIDC authentication client"
    )
    parser.add_argument("--issuer", required=True, help="OIDC issuer URL")
    parser.add_argument("--client-id", required=True, help="OAuth2 client ID")
    parser.add_argument("--client-secret", required=True, help="OAuth2 client secret")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--redirect-uri", default="https://google.com", help="Redirect URI")
    parser.add_argument("--scope", default="openid profile email", help="OAuth2 scopes")
    parser.add_argument("--identity-provider", help="Identity provider to select")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    
    args = parser.parse_args()
    
    client = OIDCAuthClient(
        issuer_url=args.issuer,
        client_id=args.client_id,
        client_secret=args.client_secret,
        username=args.username,
        password=args.password,
        redirect_uri=args.redirect_uri,
        scope=args.scope,
        identity_provider=args.identity_provider,
    )
    
    try:
        tokens = client.get_tokens(headless=args.headless, verbose=not args.quiet)
        
        print("\n✅ SUCCESS! Tokens received:")
        print(f"Access Token: {tokens['access_token'][:50]}...")
        print(f"Token Type: {tokens['token_type']}")
        print(f"Expires In: {tokens['expires_in']} seconds")
        if 'id_token' in tokens:
            print(f"ID Token: {tokens['id_token'][:50]}...")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())