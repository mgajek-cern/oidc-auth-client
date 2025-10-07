# oidc-auth-client

Automated OIDC authentication client with PKCE support for any Keycloak or OAuth2 provider.

## Features

- 🔐 **PKCE (Proof Key for Code Exchange)** - Secure authorization code flow
- 🤖 **Automated browser login** - No manual intervention needed
- 🔌 **Provider agnostic** - Works with any OIDC/OAuth2 provider
- 🎯 **Simple API** - Easy integration in Python scripts

## Prerequisites

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

## Setup

```bash
uv sync
uv run playwright install chromium
```

## Usage

**CLI:**
```bash
uv run oidc-auth \
  --issuer https://aai-dev.egi.eu/auth/realms/egi \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_SECRET \
  --username user@example.com \
  --password yourpassword \
  --headless
```

**Python:**
```python
from oidc_auth_client import OIDCAuthClient

client = OIDCAuthClient(
    issuer_url="https://keycloak.example.com/auth/realms/realm",
    client_id="client-id",
    client_secret="secret",
    username="user@example.com",
    password="password",
)

# Automatically handles PKCE code challenge/verifier generation
tokens = client.get_tokens()
print(tokens['access_token'])
```

## How It Works

1. **Generates PKCE** code verifier and challenge (SHA-256)
2. **Creates authorization URL** with PKCE parameters
3. **Automates browser login** via Playwright
4. **Exchanges authorization code** for tokens using code verifier
5. **Returns tokens** (access_token, id_token, refresh_token)

## License

MIT