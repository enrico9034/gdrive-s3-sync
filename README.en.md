# S3 to Google Drive Sync

> 🌍 **Language**: [English](README.en.md) | [Italiano](README.md) | [📚 All Docs](docs/DOCS.md)  
> 🆘 **Common errors?** See [Common Errors Guide](docs/COMMON_ERRORS.md)

A containerized Python application that automatically synchronizes files from AWS S3 to Google Drive in one-way mode.

## 🚀 Features

- ✅ One-way synchronization from S3 to Google Drive
- 📤 Automatic upload of new files
- 🔄 Update of modified files (size-based detection)
- 🗑️ Automatic deletion from Google Drive of files removed from S3
- 🐳 Fully containerized with Docker
- 📊 Detailed logging for monitoring
- ⚙️ Configurable via environment variables
- 🧪 Complete suite of unit and integration tests
- 🏠 **Self-hosted S3 support** (MinIO, Wasabi, DigitalOcean Spaces, etc.)

> 💡 **Note**: Supports both AWS S3 and S3-compatible storage. [See self-hosted S3 guide](docs/S3_SELF_HOSTED.md)

## 📋 Prerequisites

- Docker and Docker Compose installed
- AWS account with S3 access
- Google Cloud account with Google Drive API enabled
- Python 3.11+ (if running without Docker)

## 🔑 Google Drive API Setup

> 📖 **Complete Guide**: See [OAUTH2_SETUP.en.md](docs/OAUTH2_SETUP.en.md) for detailed step-by-step instructions

### Authentication: OAuth2 vs Service Account

**For personal Google accounts: use OAuth2** (recommended)

| Method          | Supported Accounts   | Storage Quota      | Complexity                 | Recommended                 |
| --------------- | -------------------- | ------------------ | -------------------------- | --------------------------- |
| **OAuth2**      | Personal + Workspace | ✅ Uses your quota | Medium (authenticate once) | ✅ **Yes**                  |
| Service Account | Workspace only       | ❌ No quota        | Low                        | ❌ No for personal accounts |

> ⚠️ **IMPORTANT for Personal Accounts**: Service Accounts **have NO storage quota** and cannot use Shared Drives (Workspace only). **OAuth2 is the ONLY working method** for personal accounts.

### Quick OAuth2 Setup

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** (e.g., "GDrive S3 Sync")
3. **Enable Google Drive API**: APIs & Services → Library → Google Drive API → Enable
4. **Configure OAuth Consent Screen**: APIs & Services → OAuth consent screen
   - Type: "External" (for personal accounts)
   - Add your email as test user
   - Scope: `https://www.googleapis.com/auth/drive.file`
5. **Create OAuth2 credentials**: APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Type: **Desktop app**
   - Download the JSON file as `credentials.json`
6. **Create a folder on Google Drive** and copy the ID from the URL

> 📖 **Complete instructions**: See [docs/OAUTH2_SETUP.en.md](docs/OAUTH2_SETUP.en.md)

### ⚠️ Service Account Setup (Google Workspace Only)

<details>
<summary>Click here for Service Account instructions (NOT recommended for personal accounts)</summary>

> **Note**: Service Accounts work ONLY with Google Workspace and require Shared Drives or shared folders. **They do not work with personal Google accounts** due to lack of storage quota.

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" → "New Project"
3. Give it a name (e.g., "S3-GDrive-Sync") and click "Create"

### Step 2: Enable Google Drive API

1. In the navigation menu, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click on "Google Drive API" and then **"Enable"**

> ⚠️ **IMPORTANT**: Make sure to click **"Enable"** to activate the API.

### Step 3: Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in the details:
   - **Service account name**: `s3-gdrive-sync`
   - Click "Create and Continue"
4. Select the "Editor" role
5. Click "Continue" and then "Done"

### Step 4: Create and Download Keys

1. On the "Credentials" page, find the service account you just created
2. Click on the service account
3. Go to the "Keys" tab
4. Click "Add Key" → "Create new key"
5. Select "JSON" as the key type
6. Click "Create" - the JSON file will be downloaded automatically
7. **Rename the file** to `service_account.json`

### Step 5: Share the Google Drive Folder

> ⚠️ **IMPORTANT**: Service Accounts do NOT have their own storage quota.

1. Open [Google Drive](https://drive.google.com) with your Workspace account
2. Create a new folder or use an existing one
3. Right-click on the folder → "Share"
4. Copy the service account email from the `service_account.json` file (`client_email` field)
5. Paste the email and set permissions to "Editor"
6. Uncheck "Notify people"
7. Click "Share"
8. Copy the folder ID from the URL

</details>

## 🛠️ Installation

### Option 1: Run with Docker (Recommended)

1. **Clone or download the project:**

```bash
git clone <repository-url>
cd gdrive-s3-sync
```

2. **Create the credentials folder and copy the credentials file:**

```bash
mkdir credentials
# Copy the credentials.json file downloaded from Google Cloud into credentials/
cp ~/Downloads/credentials.json credentials/
```

> 💡 **OAuth2 Note**: The `credentials.json` file contains OAuth2 credentials (not Service Account). On first run, the application will open a browser for authentication and save a `token.pickle` for subsequent runs.

3. **Configure environment variables:**

```bash
cp .env.example .env
```

Edit the `.env` file with your values:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Google Drive Configuration (OAuth2)
GDRIVE_USE_OAUTH2=true
GDRIVE_FOLDER_ID=your_gdrive_folder_id_here
GDRIVE_CREDENTIALS_PATH=/app/credentials/credentials.json
GDRIVE_TOKEN_PATH=/app/credentials/token.pickle

# Sync Configuration
SYNC_INTERVAL_SECONDS=300  # 5 minutes
LOG_LEVEL=INFO
```

> 📖 **First OAuth2 authentication**: On first run, a browser will automatically open for you to authenticate with Google. After authentication, the token will be saved and no longer required. See [docs/OAUTH2_SETUP.en.md](docs/OAUTH2_SETUP.en.md) for details.

4. **Start the container:**

```bash
docker-compose up -d
```

5. **View logs:**

```bash
docker-compose logs -f
```

### Option 2: Run Locally (Without Docker)

1. **Create a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your values
# Set GDRIVE_CREDENTIALS_PATH=./credentials/credentials.json
```

4. **Run the application:**

```bash
python main.py
```

## 🧪 Testing

### Unit Tests

Run the complete unit test suite:

```bash
# With virtual environment active
pytest tests/ -v
```

Run tests with coverage:

```bash
pytest tests/ -v --cov=src --cov-report=html
```

### Integration Tests

Integration tests require real credentials and test the complete flow:

```bash
# Make sure you've configured .env correctly
python tests/integration_test.py
```

The integration tests will:

1. **Upload and Delete Test**: Upload a file to S3, sync to GDrive, delete from S3, verify deletion from GDrive
2. **Update Test**: Upload a file, modify it on S3, verify it gets updated on GDrive

## 📊 Logging

The application provides detailed logging:

- **Console output**: Real-time logs visible with `docker-compose logs -f`
- **Log file**: Logs are saved to `sync.log`

Available log levels:

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about the sync process (default)
- `WARNING`: Warnings and potential issues
- `ERROR`: Errors that don't stop the application
- `CRITICAL`: Critical errors

Change the level with the `LOG_LEVEL` variable in the `.env` file.

## 🔄 How It Works

The sync manager performs the following operations on each cycle:

1. **Lists files** from S3 and Google Drive
2. **Identifies new files** (present in S3 but not in GDrive) → **Upload**
3. **Identifies modified files** (same key but different size) → **Update**
4. **Identifies removed files** (present in GDrive but not in S3) → **Delete**
5. **Unchanged files** are skipped
6. **Waits** for the configured interval before the next sync

### Example Output

```
2024-01-15 10:30:00 - __main__ - INFO - Starting S3 to Google Drive Sync Application
2024-01-15 10:30:00 - src.s3_client - INFO - S3 client initialized for bucket: my-bucket
2024-01-15 10:30:00 - src.gdrive_client - INFO - Google Drive client initialized for folder: ABC123XYZ
2024-01-15 10:30:00 - src.sync_manager - INFO - Sync Manager initialized
2024-01-15 10:30:00 - src.sync_manager - INFO - ============================================================
2024-01-15 10:30:00 - src.sync_manager - INFO - Starting synchronization from S3 to Google Drive
2024-01-15 10:30:00 - src.sync_manager - INFO - ============================================================
2024-01-15 10:30:01 - src.s3_client - INFO - Found 3 files in S3 bucket
2024-01-15 10:30:02 - src.gdrive_client - INFO - Found 2 files in Google Drive folder
2024-01-15 10:30:02 - src.sync_manager - INFO - Files to upload: 1
2024-01-15 10:30:02 - src.sync_manager - INFO - Files to check for updates: 2
2024-01-15 10:30:02 - src.sync_manager - INFO - Files to delete: 0
2024-01-15 10:30:05 - src.sync_manager - INFO - Successfully synced new file: newfile.txt
2024-01-15 10:30:05 - src.sync_manager - INFO - ============================================================
2024-01-15 10:30:05 - src.sync_manager - INFO - Synchronization completed
2024-01-15 10:30:05 - src.sync_manager - INFO - Statistics: {'uploaded': 1, 'updated': 0, 'deleted': 0, 'errors': 0, 'unchanged': 2}
```

## 🐳 Useful Docker Commands

```bash
# Start the container
docker-compose up -d

# Stop the container
docker-compose down

# View logs in real-time
docker-compose logs -f

# Restart the container
docker-compose restart

# Rebuild the image
docker-compose build

# Rebuild and restart
docker-compose up -d --build

# Access the container for debugging
docker-compose exec sync /bin/bash
```

## 📁 Project Structure

```
gdrive-s3-sync/
├── src/
│   ├── __init__.py
│   ├── s3_client.py          # AWS S3 client
│   ├── gdrive_client.py      # Google Drive client
│   └── sync_manager.py       # Synchronization logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_s3_client.py     # S3 client tests
│   ├── test_gdrive_client.py # GDrive client tests
│   ├── test_sync_manager.py  # Sync Manager tests
│   └── integration_test.py   # End-to-end integration tests
├── credentials/
│   └── credentials.json      # Google credentials (to be created)
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Docker Compose setup
├── .env.example              # Environment variables template
├── .env                      # Environment variables (to be created)
├── .gitignore
├── .dockerignore
└── README.md
```

## 🔒 Security

⚠️ **IMPORTANT:**

- **NEVER commit** the `credentials.json` or `.env` file to the repository
- Use `.gitignore` to exclude sensitive files
- Limit Google service account permissions to the minimum necessary
- Use restrictive IAM policies for AWS credentials
- Consider using AWS Secrets Manager or similar for credentials in production

## 🐛 Troubleshooting

> 💡 **Complete guide**: See [docs/COMMON_ERRORS.md](docs/COMMON_ERRORS.md) for quick solutions to all common errors.

### Error: "Google Drive API has not been used" or 403 "accessNotConfigured"

```
HttpError 403: Google Drive API has not been used in project XXXXX before or it is disabled
```

**Solution**:

1. Go to [Google Cloud Console - APIs](https://console.cloud.google.com/apis/library)
2. Search for "Google Drive API"
3. Click **"Enable"** to activate the API
4. Wait 2-3 minutes for propagation
5. Try again

> ⚠️ This is the most common error! Make sure you completed **Step 2** of the Google Drive API setup.

### Error: "Service Accounts do not have storage quota" or 403 "storageQuotaExceeded"

```
HttpError 403: Service Accounts do not have storage quota
```

**Cause**: Service Accounts do not have their own storage quota.

**Solution**:

1. Create the folder with **your personal Google Drive account** (not with the Service Account)
2. Share the folder with the Service Account email (from `credentials.json`, `client_email` field)
3. Grant "Editor" permissions
4. Use this folder's ID in `GDRIVE_FOLDER_ID`

> 💡 The folder must belong to a real user. The Service Account will use the owner's storage quota.

### Error: "Credentials file not found"

Make sure that:

- The `credentials.json` file is in the `credentials/` folder
- The path in `.env` is correct (`/app/credentials/credentials.json` for Docker)

### Error: "Access denied" on Google Drive

- Verify you've shared the folder with the service account email
- Check that `GDRIVE_FOLDER_ID` is correct

### Error: "Access Denied" on S3

- Verify AWS credentials
- Check that the IAM user has `s3:GetObject`, `s3:ListBucket` permissions

### Error: "Could not connect to the endpoint URL" (S3 custom endpoint)

If using S3-compatible storage (MinIO, Garage, etc.):

- Verify that `S3_ENDPOINT_URL` is configured correctly in `.env`
- Check that the endpoint is reachable
- See [docs/S3_SELF_HOSTED.md](docs/S3_SELF_HOSTED.md) for more details

### Files are not syncing

- Check logs: `docker-compose logs -f`
- Verify that `SYNC_INTERVAL_SECONDS` is not too long
- Make sure the S3 bucket and GDrive folder exist

## 📝 Notes

- Synchronization is **one-way**: S3 → Google Drive
- Modified files are detected via **size** (not hash)
- Minimum recommended sync interval is 60 seconds
- Temporary files are automatically deleted after each operation

## 🚦 Future Roadmap

Possible improvements:

- [ ] Support for bidirectional sync
- [ ] Change detection based on MD5 hash
- [ ] Support for S3 prefixes/folders
- [ ] Web dashboard for monitoring
- [ ] Notifications (email, Slack, etc.)
- [ ] Automatic retry with exponential backoff
- [ ] Support for large files (multipart upload)
- [ ] Database for file state tracking

## 📄 License

MIT License - Feel free to use and modify this project.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.

See [CONTRIBUTING.md](docs/CONTRIBUTING.en.md) for guidelines.

---

**Author**: Enrico  
**Date**: 2024
