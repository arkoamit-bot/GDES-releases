# VERA_HEALTH_AUTHENTICATION.md

# Vera Health Authentication Integration
Version: 1.0
Status: Implementation Ready
Priority: High

---

# Objective

Implement a secure, passwordless authentication workflow between GDES and Vera Health that minimizes user interaction while maintaining enterprise-grade security.

The user should only need to provide their email address during the first login. All subsequent authentication should occur automatically using securely stored tokens.

---

# Design Goals

- Extremely simple for clinicians
- No username/password management
- Passwordless authentication
- Secure token-based login
- Automatic session renewal
- Enterprise security
- HIPAA/GDPR compatible
- Offline-safe GDES behavior
- Minimal clicks

---

# User Workflow

## First Login

User clicks:

```
verify with vera 
```

Display a modal dialog.

Title:

```
Connect to Vera Health
```

Fields

Email Address

Checkbox

```
☑ Remember this device
```

Buttons

```
Continue
Cancel
```

---

## Continue Button

When Continue is pressed:

1. Validate email format.
2. Send email securely to Vera Health Authentication API.
3. Vera Health verifies whether the account exists.
4. If valid:
   - Generate authentication challenge.
   - Send One-Time Password (OTP) OR Magic Link.
5. Prompt user for OTP if required.
6. Verify OTP.
7. Receive:

- Access Token
- Refresh Token
- Expiration
- User Profile
- Permissions

---

# Automatic Login

If valid refresh token exists:

DO NOT ask user for email again.

Instead:

1. Refresh access token silently.
2. Open verify with vera  immediately.
3. User experiences zero-click login.

---

# Token Storage

Never store passwords.

Store only:

- Email
- Access Token
- Refresh Token
- Expiration Time

Encrypt locally.

Preferred storage:

Windows
- Windows Credential Manager

macOS
- Keychain

Linux
- Secret Service API

Never store tokens in plaintext.

---

# Remember Device

If checked:

Persist encrypted refresh token.

If unchecked:

Delete token when GDES closes.

---

# Session Management

Automatically:

- Refresh token before expiration.
- Retry once if refresh fails.
- If refresh fails again:
    - Delete invalid token.
    - Ask for email again.

---

# Logout

User chooses

Settings

↓

Disconnect Vera Health

Actions

- Delete Access Token
- Delete Refresh Token
- Delete Cached Profile
- Return to logged-out state

---

# UI Requirements

Menu

Help
    verify with vera 

OR

Toolbar

[verify with vera ]

Status Indicator

Green

Connected

Yellow

Connecting

Red

Disconnected

---

# Error Handling

Unknown Email

Display

"This email is not registered with Vera Health."

Network Error

Display

"Unable to connect to Vera Health."

Expired Token

Automatically refresh.

Invalid OTP

Allow retry.

Server Error

Log silently.

Display friendly message.

---

# Security Requirements

Never log:

- Access Token
- Refresh Token
- OTP

Always use HTTPS.

Validate SSL certificates.

Implement request timeout.

Protect against replay attacks.

Protect against CSRF where applicable.

Encrypt all local credentials.

---

# Configuration

settings.py

VERA_API_BASE_URL

VERA_CLIENT_ID

VERA_CLIENT_SECRET

TOKEN_REFRESH_INTERVAL

TOKEN_ENCRYPTION_ENABLED

---

# Future Support

Architecture must support:

- OAuth2
- OpenID Connect (OIDC)
- Azure AD
- Google Workspace
- Microsoft Entra ID
- SAML
- Multi-factor Authentication

without major code changes.

---

# Audit Logging

Log:

Authentication Success

Authentication Failure

Token Refresh

Logout

Session Expired

Do NOT log:

OTP

Tokens

Passwords

Secrets

---

# API Abstraction

Create:

services/vera_auth.py

Responsibilities

- authenticate()
- verify_otp()
- refresh_token()
- logout()
- get_current_user()
- token_valid()
- token_expired()

No UI code should directly call Vera APIs.

Always use this service layer.

---

# Testing

Implement unit tests for:

✓ Email validation

✓ Successful login

✓ Invalid email

✓ OTP verification

✓ Token refresh

✓ Token expiration

✓ Logout

✓ Secure token storage

✓ Corrupted token recovery

✓ Offline behavior

Target test coverage >95%.

---

# User Experience

First Use

Click verify with vera 

↓

Enter Email

↓

Verify OTP (one time)

↓

Connected

Future Use

Click verify with vera 

↓

Automatically connected

No additional user interaction required.

---

# Acceptance Criteria

✓ Only email required for first login.

✓ Passwordless authentication implemented.

✓ Refresh tokens securely encrypted.

✓ Automatic silent login after first authentication.

✓ Automatic token refresh.

✓ Logout clears all credentials.

✓ Secure local credential storage.

✓ No sensitive information written to logs.

✓ Cross-platform compatibility.

✓ Clean separation between UI and authentication service.

✓ Production-ready implementation with extensible authentication architecture.