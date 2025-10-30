# Microsoft Azure Active Directory Setup Guide

## Complete Step-by-Step Configuration for Pepper Application

This comprehensive guide walks you through every step needed to configure Microsoft Azure Active Directory (Azure AD) for the Pepper application. Follow each section carefully and in order.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Stage 1: Azure Account Setup](#stage-1-azure-account-setup)
3. [Stage 2: Azure Portal Access](#stage-2-azure-portal-access)
4. [Stage 3: App Registration](#stage-3-app-registration)
5. [Stage 4: Configure Authentication](#stage-4-configure-authentication)
6. [Stage 5: API Permissions](#stage-5-api-permissions)
7. [Stage 6: Client Secret Creation](#stage-6-client-secret-creation)
8. [Stage 7: Token Configuration](#stage-7-token-configuration)
9. [Stage 8: Application Configuration](#stage-8-application-configuration)
10. [Stage 9: Testing the Integration](#stage-9-testing-the-integration)
11. [Stage 10: Production Configuration](#stage-10-production-configuration)
12. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts and Access

- [ ] **Microsoft Account**: Personal Microsoft account or work/school account
- [ ] **Azure Subscription**: Free tier is sufficient for development
  - If you don't have one: [Create free Azure account](https://azure.microsoft.com/free/)
- [ ] **Appropriate Permissions**:
  - For personal tenant: Full access
  - For organization tenant: Application Administrator or Global Administrator role

### Required Information to Gather

You'll need to collect the following during setup:
- Application (Client) ID
- Directory (Tenant) ID
- Client Secret (will be generated)
- Redirect URI (your application's callback URL)

### Development Environment

- [ ] Python 3.11+ installed
- [ ] Pepper application code downloaded
- [ ] Dependencies installed (`uv run python -m pip list`)
- [ ] Text editor for `.env` file

---

## Stage 1: Azure Account Setup

### Task 1.1: Create or Verify Azure Account

**If you already have a Microsoft account:**
- ✅ Skip to Stage 2

**If you need to create an account:**

1. **Navigate to Azure Portal**
   - URL: https://portal.azure.com
   - Click "Create One" or "Sign Up"

2. **Choose Account Type**
   - **Option A - Personal Microsoft Account**:
     - Best for: Individual developers, testing, personal projects
     - Cost: Free tier available
     - Setup: Quick (5-10 minutes)

   - **Option B - Work/School Account**:
     - Best for: Enterprise applications, team development
     - Cost: Usually covered by organization
     - Setup: Requires IT admin involvement

3. **Complete Registration**
   - Provide email address
   - Create strong password
   - Verify email address
   - Complete phone verification (required for free tier)

4. **Azure Free Account Setup** (if using free tier)
   - Navigate to: https://azure.microsoft.com/free/
   - Click "Start free"
   - Provide payment information (won't be charged for free services)
   - Complete identity verification

**Expected Outcome:** ✅ You can log in to https://portal.azure.com

**Notes:**
- Free tier includes: $200 credit for 30 days + 12 months of free services
- Credit card required for verification but won't be charged without explicit upgrade
- Perfect for development and testing Pepper application

---

## Stage 2: Azure Portal Access

### Task 2.1: Navigate to Azure Active Directory

1. **Open Azure Portal**
   - URL: https://portal.azure.com
   - Sign in with your Microsoft account

2. **Locate Azure Active Directory**
   - **Method A** - Search Bar:
     ```
     Click the search bar at top
     Type: "Azure Active Directory"
     Click the result
     ```

   - **Method B** - Left Navigation:
     ```
     Click hamburger menu (☰) top-left
     Scroll to "Azure Active Directory"
     Click to open
     ```

   - **Method C** - Direct Link:
     ```
     https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade
     ```

3. **Verify Directory Information**
   - You should see the "Overview" page
   - Note your **Default Directory** name
   - Check the **Tenant ID** (you'll need this later)

**Expected Outcome:** ✅ Azure AD Overview page is displayed

**Screenshot Reference:**
```
╔════════════════════════════════════════════════════════════╗
║ Azure Active Directory | Overview                          ║
╠════════════════════════════════════════════════════════════╣
║ Default Directory                                          ║
║ Tenant ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx           ║
║                                                            ║
║ [+ Add] [Diagnose and solve problems]                     ║
╚════════════════════════════════════════════════════════════╝
```

**Notes:**
- The tenant represents your organization's instance of Azure AD
- Each tenant has a unique Tenant ID (GUID format)
- Personal accounts get a default tenant automatically

---

## Stage 3: App Registration

### Task 3.1: Create New App Registration

1. **Navigate to App Registrations**
   ```
   Azure Active Directory → Manage → App registrations
   ```
   Or search for: "App registrations"

2. **Start New Registration**
   - Click **"+ New registration"** button at the top
   - The registration form will appear

3. **Fill in Application Details**

   **Field: Name**
   ```
   Recommended: "Pepper Outlook Agent"

   Notes:
   - This name is shown to users during consent
   - Can be changed later
   - Should be descriptive and professional
   ```

   **Field: Supported account types**

   Choose one of these options:

   ✅ **Option A - Accounts in this organizational directory only (Single tenant)**
   ```
   Best for:
   - Development and testing
   - Internal company applications
   - Personal projects

   Limitation:
   - Only users in your tenant can sign in
   - Most secure option

   Recommendation: START WITH THIS
   ```

   ⚠️ **Option B - Accounts in any organizational directory (Multi-tenant)**
   ```
   Best for:
   - SaaS applications
   - Apps serving multiple organizations

   Consideration:
   - Any Azure AD user can sign in
   - Requires more security considerations
   ```

   ⚠️ **Option C - Accounts in any organizational directory and personal Microsoft accounts**
   ```
   Best for:
   - Consumer-facing applications
   - Maximum compatibility

   Consideration:
   - Personal MSA accounts have different claims
   - Requires handling multiple account types
   ```

   **Field: Redirect URI (optional)**
   ```
   Platform: Web (select from dropdown)
   URL: http://localhost:8000/auth/callback

   Notes:
   - This MUST match exactly what's in your code
   - Include http:// prefix
   - No trailing slash
   - Port number matters (8000 is our default)
   - You can add more later
   ```

4. **Register the Application**
   - Review all fields
   - Click **"Register"** button
   - Wait for Azure to create the registration (5-10 seconds)

**Expected Outcome:** ✅ Application overview page appears with Application ID

**What You'll See:**
```
╔════════════════════════════════════════════════════════════╗
║ Pepper Outlook Agent | Overview                           ║
╠════════════════════════════════════════════════════════════╣
║ Application (client) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx ║
║ Directory (tenant) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx   ║
║ Object ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxx               ║
║                                                            ║
║ Redirect URIs: 1                                           ║
║ Client credentials: 0                                      ║
╚════════════════════════════════════════════════════════════╝
```

### Task 3.2: Copy Essential IDs

1. **Copy Application (client) ID**
   ```
   Location: Overview page, top section
   Format: GUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

   Action:
   - Click the copy icon next to the ID
   - Paste into a text file temporarily
   - Label it: "CLIENT_ID"
   ```

2. **Copy Directory (tenant) ID**
   ```
   Location: Overview page, top section
   Format: GUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

   Action:
   - Click the copy icon next to the ID
   - Paste into your text file
   - Label it: "TENANT_ID"
   ```

**⚠️ IMPORTANT**: Keep these IDs safe - you'll need them in Stage 8

**Notes:**
- **Application ID**: Uniquely identifies your application
- **Tenant ID**: Identifies your Azure AD organization
- **Object ID**: Internal Azure reference (not needed for configuration)
- These IDs are NOT secrets - they can be public

---

## Stage 4: Configure Authentication

### Task 4.1: Add Platform Configuration

1. **Navigate to Authentication**
   ```
   Your App → Manage → Authentication
   ```

2. **Verify Web Platform**
   - You should see "Web" platform already configured
   - Shows the redirect URI you entered: `http://localhost:8000/auth/callback`

3. **Add Additional Redirect URIs** (Optional but recommended)

   Click **"Add URI"** under Web platform and add:

   ```
   Development:
   http://localhost:8000/auth/callback
   http://127.0.0.1:8000/auth/callback

   Production (add later when deployed):
   https://yourdomain.com/auth/callback
   https://api.yourdomain.com/auth/callback
   ```

   **Why multiple URIs?**
   - `localhost` vs `127.0.0.1`: Some browsers treat these differently
   - HTTPS for production: Required for security
   - Multiple environments: Dev, staging, production

### Task 4.2: Configure Token Settings

1. **Implicit Grant and Hybrid Flows** (LEAVE UNCHECKED)
   ```
   ❌ Access tokens (used for implicit flows)
   ❌ ID tokens (used for implicit and hybrid flows)

   Reason: We're using Authorization Code flow with PKCE
           (more secure, recommended by Microsoft)
   ```

2. **Advanced Settings**

   **Allow public client flows**
   ```
   Setting: NO (leave disabled)

   Reason:
   - We're using PKCE which is secure for public clients
   - Enabling this allows less secure flows
   - Keep disabled unless you specifically need device code flow
   ```

   **Supported account types**
   ```
   Verify: Shows your selection from Stage 3
   Can change: Yes, if needed
   ```

3. **Live SDK Support** (Optional)
   ```
   Setting: NO (leave disabled)

   Reason: Only needed for older Microsoft Account integrations
   ```

### Task 4.3: Configure Logout URL (Optional)

1. **Front-channel logout URL**
   ```
   URL: http://localhost:8000/auth/logout

   Purpose: Where Azure redirects after centralized logout

   Note: Optional - implement if you want SSO logout
   ```

2. **Save Configuration**
   - Click **"Save"** at the top of the page
   - Wait for "Successfully updated" message

**Expected Outcome:** ✅ Authentication configuration saved

**Important Notes:**
- **Security First**: We're using the most secure OAuth flow (Authorization Code + PKCE)
- **HTTPS in Production**: Always use HTTPS for production redirect URIs
- **Exact Match Required**: Azure validates redirect URIs exactly (including trailing slashes)

---

## Stage 5: API Permissions

### Task 5.1: Understand Permission Types

**Before configuring, understand these concepts:**

**Delegated Permissions**
```
What: Act on behalf of the signed-in user
When: User is present and authenticated
Example: Read user's email, send email as user
Security: User consent required
Use in Pepper: ✅ YES - this is what we need
```

**Application Permissions**
```
What: Act as the application itself (no user)
When: Background services, daemons
Example: Read all users' email (admin-level access)
Security: Admin consent required
Use in Pepper: ❌ NO - too much privilege
```

### Task 5.2: Add Microsoft Graph Permissions

1. **Navigate to API Permissions**
   ```
   Your App → Manage → API permissions
   ```

2. **Review Default Permission**
   ```
   You should see:
   - Microsoft Graph → User.Read (Delegated) → Granted for [Tenant]

   This allows reading the signed-in user's profile
   ✅ Keep this - it's required
   ```

3. **Add Mail Permissions**

   Click **"+ Add a permission"**

   **Step 1: Select API**
   ```
   Click: "Microsoft Graph"
   (The large blue tile at the top)
   ```

   **Step 2: Select Permission Type**
   ```
   Click: "Delegated permissions"
   (NOT Application permissions)
   ```

   **Step 3: Find and Add Mail.ReadWrite**
   ```
   In search box, type: "Mail.ReadWrite"

   Expand: Mail (if collapsed)
   Check: ☑ Mail.ReadWrite

   Description: "Read and write access to user mail"

   Admin Consent Required: No
   ```

   **Step 4: Add Mail.Send**
   ```
   In search box, type: "Mail.Send"

   Expand: Mail (if collapsed)
   Check: ☑ Mail.Send

   Description: "Send mail as a user"

   Admin Consent Required: No
   ```

   Click **"Add permissions"** button at bottom

4. **Add Calendar Permissions**

   Click **"+ Add a permission"** again

   ```
   API: Microsoft Graph
   Type: Delegated permissions
   Search: "Calendars.ReadWrite"

   Check: ☑ Calendars.ReadWrite

   Description: "Have full access to user calendars"

   Admin Consent Required: No
   ```

   Click **"Add permissions"**

5. **Add Mailbox Settings Permission**

   Click **"+ Add a permission"** again

   ```
   API: Microsoft Graph
   Type: Delegated permissions
   Search: "MailboxSettings.Read"

   Check: ☑ MailboxSettings.Read

   Description: "Read user mailbox settings"

   Admin Consent Required: No
   ```

   Click **"Add permissions"**

### Task 5.3: Grant Admin Consent

**What is Admin Consent?**
```
Purpose: Pre-approve permissions for all users in the tenant
Benefit: Users don't see consent screen (better UX)
Required When:
  - Permission shows "Admin consent required: Yes"
  - You want to enable the app for all users
Optional When:
  - Testing with your own account
  - Each user can consent individually
```

**Who Can Grant Admin Consent?**
- Global Administrator
- Privileged Role Administrator
- Application Administrator
- Cloud Application Administrator

**Steps to Grant Consent:**

1. **Check Your Permissions**
   ```
   If you created the tenant: You're likely a Global Admin ✅
   If using company tenant: You may need to request admin approval ⚠️
   ```

2. **Grant Consent** (if you have admin rights)
   ```
   Button: "Grant admin consent for [Your Tenant]"
   Location: Top of API permissions page

   Click it → Confirm dialog → "Yes"

   Result: Green checkmarks appear in "Status" column
   ```

3. **If You Don't Have Admin Rights**
   ```
   Option A: Use your personal account for testing
   Option B: Request admin to grant consent
   Option C: Users will see consent screen on first login
   ```

**Expected Outcome:** ✅ All permissions show green checkmark in Status column

**Final Permission List Should Look Like:**
```
╔═══════════════════════════════════════════════════════════════╗
║ API / Permission name          │ Type      │ Status           ║
╟───────────────────────────────────────────────────────────────╢
║ Microsoft Graph                                               ║
║ Calendars.ReadWrite             │ Delegated │ ✓ Granted for...║
║ Mail.ReadWrite                  │ Delegated │ ✓ Granted for...║
║ Mail.Send                       │ Delegated │ ✓ Granted for...║
║ MailboxSettings.Read            │ Delegated │ ✓ Granted for...║
║ User.Read                       │ Delegated │ ✓ Granted for...║
╚═══════════════════════════════════════════════════════════════╝
```

**Permission Scope Summary:**
| Permission | What It Allows | Why We Need It |
|------------|----------------|----------------|
| User.Read | Read user profile | Get user info, display name |
| Mail.ReadWrite | Read/write mail | Create drafts, read emails |
| Mail.Send | Send mail | Send emails on behalf of user |
| Calendars.ReadWrite | Manage calendar | Schedule meetings, check availability |
| MailboxSettings.Read | Read settings | Get timezone, language preferences |

**Notes:**
- **Principle of Least Privilege**: Only request what you need
- **User Trust**: More permissions = more user concern
- **Future Additions**: Can add more permissions later if needed
- **Audit Trail**: All permission grants are logged by Azure

---

## Stage 6: Client Secret Creation

### Task 6.1: Understand Client Secrets vs Certificates

**Client Secret (Shared Secret)**
```
Type: Password-like string
Security: Medium
Best for: Development, server-side apps
Setup: Easy (this guide)
Rotation: Manual, requires app update
```

**Certificate (Public Key)**
```
Type: X.509 certificate
Security: High
Best for: Production, enterprise
Setup: More complex
Rotation: Can be automated
```

**For Pepper Development: Use Client Secret**

### Task 6.2: Create Client Secret

1. **Navigate to Certificates & Secrets**
   ```
   Your App → Manage → Certificates & secrets
   ```

2. **Create New Client Secret**

   Click **"+ New client secret"**

   **Field: Description**
   ```
   Enter: "Pepper Development Secret"

   Purpose: Identify what this secret is for
   Helpful when: You have multiple secrets
   ```

   **Field: Expires**

   Choose expiration period:

   ```
   Option 1: 6 months (recommended for development)
   - Safer: Forces regular rotation
   - Manageable: Not too frequent

   Option 2: 12 months
   - Longer validity
   - Less maintenance

   Option 3: 24 months (maximum)
   - Longest validity
   - Higher security risk if compromised

   Option 4: Custom
   - Set specific date
   - Good for aligning with project milestones

   ⚠️ IMPORTANT: Note the expiration date!
   Set a calendar reminder to rotate before expiration
   ```

3. **Add the Secret**
   - Click **"Add"** button
   - Wait for secret to be created

### Task 6.3: Copy Client Secret

**⚠️ CRITICAL: YOU CAN ONLY SEE THIS ONCE!**

1. **Copy the Secret Value**
   ```
   Location: "Value" column (NOT the "Secret ID")

   Looks like: "abC~d3fGhIjKlMnOpQrStUvWxYz1234567890"

   Action:
   - Click the copy icon immediately
   - Paste into your text file
   - Label it: "CLIENT_SECRET"
   - DO NOT close the page until you've saved it
   ```

2. **Verify You Copied Correctly**
   ```
   Check:
   - Length: Usually 30-40 characters
   - Contains: Letters, numbers, special characters
   - No spaces at beginning/end
   ```

3. **Save the Secret ID** (Optional)
   ```
   The Secret ID is useful for:
   - Identifying which secret is which
   - Logging secret rotation
   - Not needed for app configuration
   ```

**What If I Missed It?**
```
Problem: Closed page without copying secret
Solution:
  1. Delete the secret (click X next to it)
  2. Create a new secret (repeat Task 6.2)
  3. Copy the new value immediately

You cannot retrieve the secret value after closing
```

**Expected Outcome:** ✅ Client secret value safely saved in your text file

**Security Checklist:**
```
✅ Secret copied to secure location
✅ Not committed to git
✅ Not shared via email/chat
✅ Not stored in plain text in production
✅ Expiration date noted in calendar
```

### Task 6.4: Secret Management Best Practices

**Development:**
```
✅ Store in .env file (add to .gitignore)
✅ Keep backup in password manager
✅ Rotate every 6 months
```

**Production:**
```
✅ Use Azure Key Vault
✅ Use environment variables in deployment
✅ Implement secret rotation automation
✅ Audit secret access
```

**Never:**
```
❌ Commit secrets to source control
❌ Share secrets in Slack/Teams/Email
❌ Hard-code secrets in application code
❌ Store secrets in plain text files in production
❌ Use the same secret across environments
```

---

## Stage 7: Token Configuration

### Task 7.1: Configure Token Lifetime (Optional)

1. **Navigate to Token Configuration**
   ```
   Your App → Manage → Token configuration
   ```

2. **Understand Default Token Lifetimes**
   ```
   Access Token:  60-90 minutes (default: 60)
   Refresh Token: 90 days (default)
   ID Token:      60 minutes

   Note: These are controlled by Azure AD policies
   Generally, defaults are fine for most applications
   ```

3. **Optional Claims Configuration**

   **What Are Optional Claims?**
   ```
   Purpose: Request additional information in tokens
   Examples:
     - User's email
     - Preferred username
     - Profile information

   Default behavior: Minimal claims included
   ```

   **When to Add Optional Claims:**
   - If you need user email for display
   - If you need additional profile info
   - If you want to customize user experience

   **How to Add Optional Claims:**
   ```
   Click: "+ Add optional claim"

   Token type: ID
   Claims: email, preferred_username

   Click: "Add"

   If prompted about Graph permissions:
   Check: ☑ Turn on the Microsoft Graph email permission
   Click: "Add"
   ```

4. **Groups Claims** (Usually not needed)
   ```
   Purpose: Include user's group membership in tokens
   Use case: Role-based access control

   For Pepper: Not needed (skip this)
   ```

**Expected Outcome:** ✅ Token configuration reviewed (modifications optional)

**Notes:**
- Token lifetime cannot be increased beyond Azure AD maximums
- Shorter tokens are more secure but require more frequent refreshes
- Pepper handles token refresh automatically

---

## Stage 8: Application Configuration

### Task 8.1: Prepare Environment File

1. **Navigate to Project Directory**
   ```bash
   cd /home/josephwalton/PycharmProjects/pepper
   ```

2. **Copy Example Environment File**
   ```bash
   cp .env.example .env
   ```

3. **Open .env File**
   ```bash
   # Use your preferred editor
   nano .env
   # or
   vim .env
   # or
   code .env
   ```

### Task 8.2: Configure Environment Variables

**Fill in Your Azure AD Values:**

```bash
# Microsoft Azure AD Configuration
CLIENT_ID=paste-your-application-client-id-here
TENANT_ID=paste-your-directory-tenant-id-here
REDIRECT_URI=http://localhost:8000/auth/callback
CLIENT_SECRET=paste-your-client-secret-here

# Security - Generate a strong random key
SECRET_KEY=generate-a-strong-key-here
```

**Detailed Instructions for Each Variable:**

1. **CLIENT_ID**
   ```
   Source: Stage 3, Task 3.2
   Format: GUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
   Example: CLIENT_ID=12345678-1234-1234-1234-123456789abc

   Paste the Application (client) ID you copied earlier
   ```

2. **TENANT_ID**
   ```
   Source: Stage 3, Task 3.2
   Format: GUID (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
   Example: TENANT_ID=87654321-4321-4321-4321-abcdefghijkl

   Paste the Directory (tenant) ID you copied earlier
   ```

3. **REDIRECT_URI**
   ```
   Default: http://localhost:8000/auth/callback

   MUST MATCH: The URI you configured in Stage 4

   Common Variations:
   - http://localhost:8000/auth/callback  (default)
   - http://127.0.0.1:8000/auth/callback  (alternative)
   - https://yourdomain.com/auth/callback (production)

   ⚠️ IMPORTANT: Must match EXACTLY (including http/https, port, path)
   ```

4. **CLIENT_SECRET**
   ```
   Source: Stage 6, Task 6.3
   Format: Random string with letters, numbers, symbols
   Example: CLIENT_SECRET=abC~d3fGhIjKlMnOpQrStUvWxYz1234567890

   Paste the client secret value you copied

   ⚠️ CRITICAL: This is a sensitive secret!
   ```

5. **SECRET_KEY**
   ```
   Purpose: Encrypts OAuth tokens in storage
   Format: Random string (32+ characters recommended)

   Generate using Python:
   ```

   **Generate SECRET_KEY:**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Output example:
   ```
   xPQR1aBcD2eFg3HiJ4kLm5NoPq6RsT7uVwXyZ8
   ```

   Paste this value:
   ```
   SECRET_KEY=xPQR1aBcD2eFg3HiJ4kLm5NoPq6RsT7uVwXyZ8
   ```

### Task 8.3: Verify .env File

**Your .env file should look like:**

```bash
# Microsoft Azure AD Configuration
CLIENT_ID=12345678-1234-1234-1234-123456789abc
TENANT_ID=87654321-4321-4321-4321-abcdefghijkl
REDIRECT_URI=http://localhost:8000/auth/callback
CLIENT_SECRET=abC~d3fGhIjKlMnOpQrStUvWxYz1234567890

# Security
SECRET_KEY=xPQR1aBcD2eFg3HiJ4kLm5NoPq6RsT7uVwXyZ8
```

**Verification Checklist:**
```
✅ CLIENT_ID is a valid GUID (8-4-4-4-12 format)
✅ TENANT_ID is a valid GUID
✅ REDIRECT_URI matches Azure AD configuration
✅ CLIENT_SECRET has no extra spaces
✅ SECRET_KEY is long and random
✅ No quotes around values
✅ No spaces around = signs
```

### Task 8.4: Secure Your Configuration

1. **Verify .gitignore**
   ```bash
   # Check that .env is in .gitignore
   grep -q "^\.env$" .gitignore && echo "✅ .env is ignored" || echo "❌ Add .env to .gitignore"
   ```

2. **Set File Permissions** (Linux/Mac)
   ```bash
   chmod 600 .env
   # Only you can read/write the file
   ```

3. **Create Backup** (in secure location)
   ```bash
   # Copy to password manager or encrypted storage
   # DO NOT commit backup to git
   ```

**Expected Outcome:** ✅ .env file configured with all required values

---

## Stage 9: Testing the Integration

### Task 9.1: Start the Application

1. **Ensure Dependencies Are Installed**
   ```bash
   cd /home/josephwalton/PycharmProjects/pepper
   uv run python -m pip list | grep -E "(fastapi|msal|azure)"
   ```

   Should see:
   ```
   azure-identity    1.x.x
   msal              1.x.x
   fastapi           0.x.x
   ```

2. **Start the Server**
   ```bash
   uv run python main.py
   ```

3. **Verify Server Started**
   ```
   Expected output:

   INFO:     Started server process [12345]
   INFO:     Waiting for application startup.
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

4. **Check Health Endpoint**
   ```bash
   # Open new terminal
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "message": "Service is running",
     "environment": {
       "client_id_set": true,
       "tenant_id_set": true,
       "redirect_uri_set": true
     }
   }
   ```

**If status is "unhealthy":**
```
Problem: Missing environment variables
Solution:
  1. Check .env file exists in project root
  2. Verify all required variables are set
  3. Restart the server
```

### Task 9.2: Test OAuth Login Flow

**⚠️ IMPORTANT: Use an Incognito/Private Browser Window**
- Reason: Avoids cached authentication state
- Better for testing the full flow

1. **Open Browser to Login Endpoint**
   ```
   URL: http://localhost:8000/auth/login
   ```

2. **Expected: Redirect to Microsoft Login**
   ```
   URL should change to:
   https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize?...

   You should see Microsoft login page
   ```

3. **Sign In with Your Account**
   ```
   Use the Microsoft account associated with your tenant:
   - Personal Microsoft Account (if using personal tenant)
   - Work/School Account (if using organization tenant)

   Enter credentials
   Complete MFA if required
   ```

4. **Grant Consent** (if prompted)
   ```
   You may see a consent screen asking:

   "Pepper Outlook Agent wants to:
   - Read your profile
   - Read and write your mail
   - Send mail as you
   - Read and write your calendar
   - Read your mailbox settings"

   Click: "Accept"

   Note: This screen only appears once per user
         (unless admin consent was granted in Stage 5)
   ```

5. **Expected: Redirect to Callback**
   ```
   URL should change to:
   http://localhost:8000/auth/callback?code=...&state=...

   Response should be JSON:
   {
     "message": "Authentication successful",
     "user_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
     "scopes": [
       "Calendars.ReadWrite",
       "Mail.ReadWrite",
       "Mail.Send",
       "MailboxSettings.Read",
       "User.Read"
     ]
   }
   ```

6. **Save Your User ID**
   ```
   Copy the user_id value from the response
   You'll need it for subsequent tests

   Example: user_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
   ```

**Expected Outcome:** ✅ Successful authentication with user_id returned

### Task 9.3: Test Authentication Status

```bash
# Replace {user_id} with your actual user_id
curl http://localhost:8000/auth/status/{user_id}
```

Expected response:
```json
{
  "authenticated": true,
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "token_expired": false,
  "has_refresh_token": true
}
```

**Status Indicators:**
- ✅ `authenticated: true` - User has valid tokens
- ✅ `token_expired: false` - Access token is still valid
- ✅ `has_refresh_token: true` - Can refresh when expired

### Task 9.4: Test Token Refresh

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your-user-id-here"}'
```

Expected response:
```json
{
  "message": "Token refreshed successfully",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**What This Tests:**
- Refresh token is valid
- MSAL can acquire new access token
- Token storage is working
- Encryption/decryption is functional

### Task 9.5: Test Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your-user-id-here"}'
```

Expected response:
```json
{
  "message": "Logged out successfully",
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Verify Logout:**
```bash
# Check status again - should show not authenticated
curl http://localhost:8000/auth/status/{user_id}
```

Expected:
```json
{
  "authenticated": false,
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Task 9.6: Run Automated Tests

```bash
# Run all unit tests
uv run pytest tests/ -v

# Should see all 34 tests pass
```

Expected output:
```
============================== test session starts ==============================
...
tests/test_auth_routes.py::TestAuthLogin::test_login_redirect PASSED     [  2%]
tests/test_auth_routes.py::TestAuthCallback::test_callback_success PASSED [  5%]
...
============================== 34 passed in 0.56s ===============================
```

**Expected Outcome:** ✅ All integration tests pass

### Task 9.7: Test API Documentation

1. **Open Interactive API Docs**
   ```
   Browser: http://localhost:8000/docs
   ```

2. **You Should See:**
   - Swagger UI interface
   - All API endpoints listed
   - "authentication" section with OAuth endpoints
   - Health check endpoints

3. **Test an Endpoint via Docs**
   ```
   1. Expand: GET /auth/status/{user_id}
   2. Click: "Try it out"
   3. Enter: Your user_id
   4. Click: "Execute"
   5. Verify: 200 response with user status
   ```

**Expected Outcome:** ✅ API documentation loads and works

---

## Stage 10: Production Configuration

### Task 10.1: Production App Registration

**Create Separate Production App Registration:**

1. **Why Separate?**
   ```
   Benefits:
   - Different credentials (if dev is compromised, prod is safe)
   - Separate permissions (can be more restrictive in prod)
   - Clear audit trail
   - Different token lifetimes
   - Separate monitoring
   ```

2. **Create New Registration**
   ```
   Follow Stage 3 again with these changes:

   Name: "Pepper Outlook Agent - Production"

   Redirect URI: https://yourdomain.com/auth/callback
   (Must be HTTPS!)
   ```

3. **Save Production Credentials Separately**
   ```
   File: .env.production
   (DO NOT commit to git)
   ```

### Task 10.2: Production Redirect URI

1. **Requirements for Production URI:**
   ```
   ✅ MUST use HTTPS (not HTTP)
   ✅ Must be publicly accessible
   ✅ Must have valid SSL certificate
   ❌ Cannot use localhost
   ❌ Cannot use IP address directly
   ```

2. **Examples:**
   ```
   ✅ https://api.pepper.example.com/auth/callback
   ✅ https://pepper-api.azurewebsites.net/auth/callback
   ✅ https://prod.pepper.com/auth/callback

   ❌ http://pepper.com/auth/callback (no HTTPS)
   ❌ https://192.168.1.100/auth/callback (IP address)
   ❌ https://localhost/auth/callback (localhost not allowed)
   ```

3. **Add Production URI to App Registration**
   ```
   Azure Portal → Your App → Authentication → Add URI
   Add: https://your-production-domain.com/auth/callback
   Save
   ```

### Task 10.3: Production Secrets Management

**DO NOT use .env file in production!**

**Recommended Options:**

**Option A: Azure Key Vault** (Best for Azure deployments)
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(
    vault_url="https://your-keyvault.vault.azure.net",
    credential=credential
)

client_secret = client.get_secret("CLIENT-SECRET").value
```

**Option B: Environment Variables** (Platform-agnostic)
```bash
# Set in deployment platform
# Azure App Service: Configuration → Application settings
# AWS: Systems Manager Parameter Store
# Heroku: Config Vars
# Docker: --env or --env-file
```

**Option C: Managed Identity** (No secrets needed!)
```python
# Azure Managed Identity - no client secret required
from azure.identity import ManagedIdentityCredential

credential = ManagedIdentityCredential(
    client_id="your-app-client-id"
)
```

### Task 10.4: Production Security Checklist

```
Authentication:
✅ Using HTTPS for all endpoints
✅ Valid SSL certificate installed
✅ Separate production app registration
✅ Client secret stored securely (not in code)
✅ SECRET_KEY is cryptographically random
✅ Different SECRET_KEY than development

Authorization:
✅ Admin consent granted for all users
✅ Only necessary permissions configured
✅ Regular permission audits scheduled

Tokens:
✅ Token storage is persistent (database, not memory)
✅ Token encryption enabled
✅ Regular token cleanup for inactive users
✅ Refresh token rotation enabled

Monitoring:
✅ Logging enabled for auth events
✅ Alerts configured for auth failures
✅ Audit logs reviewed regularly
✅ Rate limiting implemented

Compliance:
✅ Privacy policy published
✅ Terms of service available
✅ Data retention policy defined
✅ GDPR compliance verified (if applicable)
```

### Task 10.5: Production Deployment

**Deployment Checklist:**

```
Pre-Deployment:
1. ✅ Create production app registration
2. ✅ Configure production redirect URI (HTTPS)
3. ✅ Generate production client secret
4. ✅ Store secrets in secure vault
5. ✅ Update application configuration
6. ✅ Run full test suite
7. ✅ Review security checklist

Deployment:
8. ✅ Deploy application to hosting platform
9. ✅ Configure environment variables
10. ✅ Verify HTTPS is working
11. ✅ Test OAuth flow in production
12. ✅ Verify API endpoints accessible

Post-Deployment:
13. ✅ Monitor logs for errors
14. ✅ Test with real user accounts
15. ✅ Verify token refresh works
16. ✅ Set up monitoring/alerting
17. ✅ Schedule secret rotation
```

---

## Troubleshooting

### Issue 1: "Reply URL mismatch"

**Error Message:**
```
AADSTS50011: The reply URL specified in the request does not match
the reply URLs configured for the application
```

**Cause:** Redirect URI mismatch between app and Azure AD

**Solutions:**

1. **Check Exact Match**
   ```bash
   # In your .env file:
   REDIRECT_URI=http://localhost:8000/auth/callback

   # Must EXACTLY match Azure AD:
   # - Same protocol (http vs https)
   # - Same host (localhost vs 127.0.0.1)
   # - Same port (8000)
   # - Same path (/auth/callback)
   # - No trailing slash
   ```

2. **Verify in Azure AD**
   ```
   Portal → App Registration → Authentication
   Look under "Web" platform
   Ensure your URI is listed
   ```

3. **Common Mistakes**
   ```
   ❌ http://localhost:8000/auth/callback/  (trailing slash)
   ❌ https://localhost:8000/auth/callback  (https instead of http)
   ❌ http://127.0.0.1:8000/auth/callback   (IP vs localhost)
   ✅ http://localhost:8000/auth/callback   (correct)
   ```

### Issue 2: "Invalid client secret"

**Error Message:**
```
AADSTS7000215: Invalid client secret provided
```

**Cause:** Client secret is wrong or expired

**Solutions:**

1. **Check for Extra Characters**
   ```bash
   # NO quotes around value
   ❌ CLIENT_SECRET="abc123..."
   ✅ CLIENT_SECRET=abc123...

   # NO spaces before/after
   ❌ CLIENT_SECRET= abc123...
   ❌ CLIENT_SECRET=abc123...
   ✅ CLIENT_SECRET=abc123...
   ```

2. **Verify Secret Not Expired**
   ```
   Portal → App Registration → Certificates & secrets
   Check "Expires" column
   If expired: Create new secret, update .env
   ```

3. **Copy Secret Again**
   ```
   If uncertain: Delete old secret, create new one
   Copy immediately (you can't see it again)
   Update .env file
   Restart application
   ```

### Issue 3: "Insufficient privileges to complete the operation"

**Error Message:**
```
Authorization_RequestDenied: Insufficient privileges
to complete the operation
```

**Cause:** Missing API permissions or consent

**Solutions:**

1. **Verify Permissions Granted**
   ```
   Portal → App Registration → API permissions
   Check "Status" column
   All should show green checkmark: "✓ Granted for [Tenant]"
   ```

2. **Grant Admin Consent**
   ```
   Click: "Grant admin consent for [Tenant]"
   Confirm: "Yes"
   Wait for green checkmarks
   ```

3. **Check Delegated vs Application**
   ```
   Ensure using "Delegated" permissions
   Not "Application" permissions
   ```

4. **Re-authenticate User**
   ```
   User may need to log out and log in again
   To pick up new permissions
   ```

### Issue 4: "Token endpoint returned error: invalid_grant"

**Error Message:**
```
Token endpoint returned error: invalid_grant
```

**Cause:** Authorization code expired or already used

**Solutions:**

1. **Restart OAuth Flow**
   ```
   Authorization codes expire after ~10 minutes
   Don't save the code from URL
   Must complete flow immediately
   ```

2. **Check Server Time**
   ```bash
   # Ensure system time is correct
   date

   # If wrong, sync with NTP
   sudo ntpdate time.google.com
   ```

3. **Clear Browser Cache**
   ```
   Old cached redirect may contain expired code
   Use incognito mode for testing
   ```

### Issue 5: "Unhealthy" Health Check

**Response:**
```json
{
  "status": "unhealthy",
  "message": "Missing required environment variables: CLIENT_ID, TENANT_ID",
  "missing_vars": ["CLIENT_ID", "TENANT_ID"]
}
```

**Cause:** Environment variables not loaded

**Solutions:**

1. **Check .env File Location**
   ```bash
   # Must be in project root
   ls -la .env

   # Should show:
   -rw------- 1 user user 256 Oct 30 12:00 .env
   ```

2. **Check .env File Contents**
   ```bash
   cat .env

   # Should show all variables set
   # No empty values like: CLIENT_ID=
   ```

3. **Restart Application**
   ```bash
   # Stop server (Ctrl+C)
   # Start again
   uv run python main.py
   ```

4. **Check Environment Loading**
   ```python
   # In Python shell
   from app.config import settings
   print(settings.client_id)  # Should print your client ID
   ```

### Issue 6: "Login redirects but returns error"

**Symptoms:** After Microsoft login, callback shows error

**Debugging Steps:**

1. **Check Browser Console**
   ```
   F12 → Console tab
   Look for JavaScript errors or network errors
   ```

2. **Check Server Logs**
   ```
   Terminal where app is running
   Look for stack traces or error messages
   ```

3. **Verify State Parameter**
   ```
   Error: "Invalid state parameter"
   Cause: PKCE verifier storage issue
   Solution: Restart server, try again
   ```

4. **Check Network Tab**
   ```
   F12 → Network tab
   Find callback request
   Check response status and body
   ```

### Issue 7: Token Refresh Fails

**Error:**
```json
{
  "detail": "Token refresh failed: invalid_grant"
}
```

**Causes and Solutions:**

1. **Refresh Token Expired**
   ```
   Default lifetime: 90 days
   Solution: User must re-authenticate
   ```

2. **User Changed Password**
   ```
   Refresh token automatically revoked
   Solution: User must log in again
   ```

3. **Token Revoked by Admin**
   ```
   Admin can revoke user's tokens
   Solution: Check with admin, re-authenticate
   ```

### Issue 8: Permissions Not Working

**Symptoms:** Can authenticate but API calls fail with 403

**Debugging:**

1. **Check Token Scopes**
   ```bash
   # Decode JWT token (use jwt.io)
   # Check "scp" claim
   # Should contain: Mail.ReadWrite Mail.Send etc.
   ```

2. **Verify Permissions Granted**
   ```
   Portal → App Registration → API permissions
   All permissions should have green checkmark
   ```

3. **Re-consent**
   ```
   Portal → Enterprise Applications
   Find your app → Users and groups
   Remove user → Re-add user
   User must consent again
   ```

### Common Error Codes Reference

| Error Code | Meaning | Solution |
|------------|---------|----------|
| AADSTS50011 | Reply URL mismatch | Fix redirect URI |
| AADSTS7000215 | Invalid client secret | Check/regenerate secret |
| AADSTS7000222 | Invalid client secret (expired) | Create new secret |
| AADSTS50076 | MFA required | User must complete MFA |
| AADSTS65001 | User consent required | User must accept consent |
| AADSTS70011 | Invalid scope | Check permission names |
| AADSTS90002 | Tenant not found | Check TENANT_ID |
| AADSTS90014 | Missing required field | Check request parameters |

### Getting Help

**Documentation:**
- [Microsoft Identity Platform Docs](https://docs.microsoft.com/en-us/azure/active-directory/develop/)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Microsoft Graph API Docs](https://docs.microsoft.com/en-us/graph/)

**Error Code Lookup:**
- [Azure AD Error Codes](https://login.microsoftonline.com/error)
- Search: "AADSTS[error code]"

**Community:**
- [Stack Overflow - azure-ad-msal](https://stackoverflow.com/questions/tagged/azure-ad-msal)
- [Microsoft Q&A](https://docs.microsoft.com/en-us/answers/)

**Logs and Diagnostics:**
- Azure Portal → Azure AD → Sign-in logs
- Azure Portal → Your App → Diagnose and solve problems

---

## Appendix A: Quick Reference

### Essential Azure AD URLs

```
Azure Portal:
https://portal.azure.com

Azure AD Blade:
https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade

App Registrations:
https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps

Microsoft Graph Explorer (testing):
https://developer.microsoft.com/en-us/graph/graph-explorer
```

### Environment Variables Template

```bash
# Copy this template to .env and fill in values

# Azure AD Configuration
CLIENT_ID=
TENANT_ID=
REDIRECT_URI=http://localhost:8000/auth/callback
CLIENT_SECRET=

# Security
SECRET_KEY=

# Optional: Advanced Configuration
# SCOPES=User.Read,Mail.ReadWrite,Mail.Send,Calendars.ReadWrite,MailboxSettings.Read
```

### Quick Test Commands

```bash
# Health check
curl http://localhost:8000/health

# Start login
# (Open in browser)
http://localhost:8000/auth/login

# Check auth status
curl http://localhost:8000/auth/status/{user_id}

# Refresh token
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"user_id": "{user_id}"}'

# Logout
curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"user_id": "{user_id}"}'
```

---

## Appendix B: Security Best Practices Checklist

### Development
- [ ] .env file in .gitignore
- [ ] Secrets not in code
- [ ] HTTPS in production redirect URI
- [ ] Strong SECRET_KEY generated
- [ ] Client secret noted with expiration date

### Production
- [ ] Separate production app registration
- [ ] Secrets in secure vault (not .env)
- [ ] HTTPS enforced
- [ ] SSL certificate valid
- [ ] Token storage persistent
- [ ] Logging enabled
- [ ] Monitoring configured
- [ ] Rate limiting implemented

### Compliance
- [ ] Privacy policy published
- [ ] Terms of service available
- [ ] User consent documented
- [ ] Data retention policy defined
- [ ] Regular security audits scheduled

---

## Summary

You have completed the Azure AD setup! Your application can now:

✅ Authenticate users via Microsoft
✅ Request and receive OAuth tokens
✅ Access Microsoft Graph API with delegated permissions
✅ Refresh tokens automatically
✅ Store tokens securely with encryption

**Next Steps:**
1. Proceed to implement Microsoft Graph API operations (Stage 1.3 in TODO.md)
2. Test with your Microsoft account
3. Build the AI agent layer (Stage 2 in TODO.md)

**Remember:**
- Keep client secret secure
- Note secret expiration date
- Use separate credentials for production
- Regularly review and audit permissions

For questions or issues, refer to the Troubleshooting section or consult the official Microsoft documentation.
