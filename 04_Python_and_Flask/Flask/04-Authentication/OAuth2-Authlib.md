# OAuth2 with Authlib

OAuth2 is an authorization framework that enables applications to obtain limited access to user accounts on an HTTP service, such as Facebook, GitHub, or Google. Authlib is an excellent, comprehensive library for building OAuth and OpenID Connect clients and providers in Python.

## Authlib Features
- Generic OAuth 1.0 and OAuth 2.0 Client
- Flask/Django integrations built-in
- Support for OpenID Connect

## OAuth2 Authorization Code Flow

```mermaid
sequenceDiagram
    participant User
    participant Client as Flask App (Authlib)
    participant AuthServer as OAuth Provider (e.g., Google)
    participant ResourceServer as API Server

    User->>Client: Click "Login with Provider"
    Client->>User: Redirect to Authorization URL
    User->>AuthServer: Authenticate and Consent
    AuthServer->>User: Redirect back to Client with Auth Code
    User->>Client: Pass Auth Code
    Client->>AuthServer: Exchange Auth Code for Access Token
    AuthServer-->>Client: Return Access Token & (optional) ID Token
    Client->>ResourceServer: Fetch User Profile using Access Token
    ResourceServer-->>Client: Return Profile Data
    Client->>User: Log user in and show dashboard
```

## Setup
```bash
pip install Authlib requests
```
