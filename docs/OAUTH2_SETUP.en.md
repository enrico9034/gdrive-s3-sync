# OAuth2 Setup for Google Drive

This guide explains how to configure OAuth2 authentication to access Google Drive with a personal account.

## Why OAuth2?

**OAuth2 is the ONLY supported method for personal Google accounts** because:

- ❌ **Service Accounts** have no storage quota on Google Drive
- ❌ **Shared Drives** are only available for Google Workspace (business accounts)
- ✅ OAuth2 uses **your user credentials** and accesses your personal storage space

## Prerequisites

- A personal Google account or Workspace account
- Access to Google Cloud Console

## Step 1: Create a Project in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter a name (e.g., "GDrive S3 Sync") and click **"Create"**
4. Select the newly created project

## Step 2: Enable Google Drive API

1. In the sidebar menu, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Drive API"**
3. Click on **"Google Drive API"** then **"Enable"**

## Step 3: Configure OAuth Consent Screen

1. In the sidebar menu, go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (for personal accounts) or **"Internal"** (for Workspace)
3. Click **"Create"**
4. Fill in the required fields:
   - **App name**: "GDrive S3 Sync" (or your preferred name)
   - **User support email**: your email address
   - **Developer contact email**: your email address
5. Click **"Save and Continue"**
6. **Scopes**: Click **"Add or Remove Scopes"**
   - Search and select: `https://www.googleapis.com/auth/drive.file`
   - This allows the app to access only files it creates
7. Click **"Update"** → **"Save and Continue"**
8. **Test users** (only for "External" apps not published):
   - Click **"Add Users"**
   - Add your email address
   - Click **"Save and Continue"**
9. Click **"Back to Dashboard"**

## Step 4: Create OAuth2 Credentials

1. In the sidebar menu, go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Application type"**: **"Desktop app"**
4. Enter a name (e.g., "GDrive S3 Sync Desktop")
5. Click **"Create"**
6. **Download the JSON file**:
   - Click the download button (down arrow icon)
   - Save the file as `credentials.json`

## Step 5: Configure the Application

1. Copy the `credentials.json` file to the project's `credentials/` folder:

   ```bash
   mkdir -p credentials
   cp ~/Downloads/credentials.json credentials/
   ```

2. Create the `.env` file from the template:

   ```bash
   cp .env.example .env
   ```

3. Edit `.env` and make sure:
   ```bash
   GDRIVE_USE_OAUTH2=true
   GDRIVE_CREDENTIALS_PATH=/app/credentials/credentials.json
   GDRIVE_TOKEN_PATH=/app/credentials/token.pickle
   ```

## Step 6: First Run - Authentication

The **first time** you start the application:

1. Start the application:

   ```bash
   python main.py
   ```

   Or with Docker:

   ```bash
   docker-compose up
   ```

2. **A browser will automatically open** with the Google authentication page

3. If you see a warning **"Google hasn't verified this app"**:

   - Click **"Advanced"**
   - Click **"Go to [app name] (unsafe)"**
   - This is normal for apps in testing mode

4. **Select your Google account**

5. Click **"Allow"** to grant permissions to the app

6. The browser will show **"The authentication flow has completed"**

7. **Token saved**: The application saves a `token.pickle` file for future runs

8. **Close the browser** and return to the terminal

## Step 7: Subsequent Runs

After the first run, the application:

- ✅ Reuses the saved `token.pickle`
- ✅ Automatically refreshes the token when it expires
- ✅ **Will NOT require authentication again** as long as the token is valid

If the token expires or is revoked, the app will request authentication again.

## Troubleshooting

### Browser doesn't open

If you're in a headless environment (remote server):

1. Run the first authentication on a local machine
2. Copy the generated `token.pickle` file to the server:
   ```bash
   scp credentials/token.pickle user@server:/path/to/project/credentials/
   ```

### Error "redirect_uri_mismatch"

- Make sure you selected **"Desktop app"** as the application type
- If you selected "Web application", recreate it as "Desktop app"

### Error "invalid_grant"

The token has expired or been revoked:

1. Delete the `token.pickle` file:
   ```bash
   rm credentials/token.pickle
   ```
2. Restart the application to re-authenticate

### Error "Access blocked: This app's request is invalid"

The OAuth consent screen is not configured correctly:

1. Verify you completed all required fields
2. Make sure you added your email as a test user
3. Check that the `drive.file` scope is selected

## Security

- ⚠️ **DO NOT share** the `credentials.json` or `token.pickle` files
- ⚠️ Add these files to `.gitignore` (already done in the project)
- ✅ The `token.pickle` only allows access to files created by the app
- ✅ The `drive.file` scope limits access to only app-managed files

## Differences with Service Account

| Feature            | OAuth2               | Service Account           |
| ------------------ | -------------------- | ------------------------- |
| Supported accounts | Personal + Workspace | Workspace only            |
| Storage quota      | Uses your quota      | ❌ No quota               |
| Initial setup      | Browser once         | JSON file                 |
| Token renewal      | Automatic            | N/A                       |
| Shared Drive       | Not needed           | Required (Workspace only) |

## Next Steps

1. ✅ OAuth2 configuration completed
2. Read [QUICKSTART.en.md](QUICKSTART.en.md) for complete setup
3. Configure S3 variables in `.env` file
4. Start syncing!

## Useful Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [OAuth2 Scopes](https://developers.google.com/identity/protocols/oauth2/scopes#drive)
