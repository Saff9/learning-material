# Flask-Security-Too

Flask-Security-Too is a modern, actively maintained fork of the original Flask-Security package. It provides a complete solution for user authentication, registration, password recovery, and role-based access control (RBAC).

## Key Features
- Session based authentication
- Token based authentication (API)
- Role and Permission management
- Password hashing (bcrypt, argon2)
- Two-Factor Authentication (2FA)
- Unified login for multiple identity providers (OAuth)

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant App as Flask App (Flask-Security)
    participant DB as Database
    
    User->>Browser: Enters credentials
    Browser->>App: POST /login (email, password)
    App->>DB: Query User by email
    DB-->>App: Return User Record
    App->>App: Verify Password Hash
    alt Credentials Valid
        App->>Browser: Set Session Cookie / Auth Token
        Browser-->>User: Redirect to protected page
    else Credentials Invalid
        App->>Browser: Return 401 Unauthorized / Error message
    end
```

## Setup
To install Flask-Security-Too:
```bash
pip install Flask-Security-Too
```
