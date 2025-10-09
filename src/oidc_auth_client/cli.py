import argparse
import sys
from .client import OIDCAuthClient
from .strategies import SimpleFormStrategy, EGIStrategy


def main():
    parser = argparse.ArgumentParser(
        description="Automated OIDC authentication client with PKCE support"
    )
    parser.add_argument("--issuer", required=True, help="OIDC issuer URL")
    parser.add_argument("--client-id", required=True, help="OAuth2 client ID")
    parser.add_argument("--client-secret", required=True, help="OAuth2 client secret")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--redirect-uri", default="https://google.com", help="Redirect URI")
    parser.add_argument("--scope", default="openid profile email", help="OAuth2 scopes")
    parser.add_argument("--strategy", choices=["simple", "egi"], default="simple",
                        help="Authentication strategy (default: simple)")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with screenshots")
    
    args = parser.parse_args()
    
    # Select authentication strategy
    if args.strategy == "egi":
        auth_strategy = EGIStrategy()
    else:
        auth_strategy = SimpleFormStrategy()
    
    client = OIDCAuthClient(
        issuer_url=args.issuer,
        client_id=args.client_id,
        client_secret=args.client_secret,
        username=args.username,
        password=args.password,
        redirect_uri=args.redirect_uri,
        scope=args.scope,
        auth_strategy=auth_strategy,
    )
    
    try:
        tokens = client.get_tokens(
            headless=args.headless, 
            verbose=not args.quiet,
            debug=args.debug
        )
        
        print("\n✅ SUCCESS! Tokens received:")
        print(f"Access Token: {tokens['access_token']}")
        print(f"Token Type: {tokens['token_type']}")
        print(f"Expires In: {tokens['expires_in']} seconds")
        if 'id_token' in tokens:
            print(f"ID Token: {tokens['id_token']}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())