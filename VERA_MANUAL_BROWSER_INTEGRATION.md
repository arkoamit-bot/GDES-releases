# VERA_MANUAL_BROWSER_INTEGRATION.md

# Vera Health Manual Browser Integration

Version: 1.0

Status: Production Design

Priority: High

---

# Objective

Integrate Vera Health without using any unofficial browser automation, web scraping, or login bypass.

Since Vera does not provide an official API or authorization mechanism, authentication remains manual, while every other possible step is automated.

---

# Workflow

## First Use

User clicks

Verify with Vera

↓

GDES automatically opens the Vera Health website in the user's default browser.

↓

Display an instruction dialog.

--------------------------------

Complete Vera Login

1. Enter your Vera email address.

2. Enter the verification code sent by Vera.

3. Complete login.

4. Return to GDES.

5. Click "Continue Verification".

--------------------------------

Buttons

Continue Verification

Cancel

---

# Future Use

When Verify with Vera is clicked

Open Vera directly.

If the user's browser session is still active, Vera should already be logged in.

The user simply returns to GDES and clicks

Continue Verification

No email entry is required if Vera maintains its own login session.

---

# GDES Responsibilities

GDES SHALL

✓ Open Vera website automatically.

✓ Detect internet connectivity.

✓ Remember that Vera was previously connected.

✓ Remember the user's Vera email locally (optional).

✓ Never store passwords.

✓ Never store OTP codes.

✓ Never attempt to autofill OTP.

✓ Never automate Vera login using unofficial techniques.

---

# Browser Handling

Open the system default browser.

Do not embed Vera inside an iframe.

Do not use an embedded browser.

Do not inject JavaScript into Vera pages.

Do not inspect Vera cookies.

Do not scrape Vera pages.

---

# User Interface

Button

Verify with Vera

↓

Automatically

Launch browser

↓

Show waiting dialog

--------------------------------

Waiting for Vera Login

After you have completed authentication in your browser,

click Continue Verification.

[Continue Verification]

[Cancel]

--------------------------------

---

# Local Preferences

Remember

Last Vera email

Last successful verification time

Whether user previously connected

Do not remember

Password

OTP

Browser cookies

Session tokens

---

# Optional Convenience

Provide a button

Open Vera

which always opens the Vera dashboard.

If Vera has an active browser session, no login should be required.

---

# Error Handling

If browser cannot be opened

Display

Unable to open your default web browser.

Please open Vera manually.

---

If internet unavailable

Display

Internet connection required for Vera verification.

---

If user cancels

Return to GDES without changing the management plan.

---

# Security

Never

Automate login using browser scripting.

Read browser cookies.

Capture OTP.

Capture passwords.

Inject code into Vera.

Use unsupported browser automation.

Use unofficial reverse-engineered APIs.

---

# Future Upgrade

If Vera releases an official API or OAuth authentication,

replace this manual workflow with the official integration.

The UI should remain unchanged.

Only the backend implementation should change.

---

# Acceptance Criteria

✓ Clicking Verify with Vera opens Vera automatically.

✓ User completes login on the official Vera website.

✓ GDES never stores passwords or OTPs.

✓ Future visits reuse Vera's existing browser session whenever possible.

✓ Manual workflow can later be upgraded to an official API without redesigning the interface.