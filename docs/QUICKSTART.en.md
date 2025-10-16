# Quick Start Guide

> 🌍 **Language**: [English](QUICKSTART.en.md) | [Italiano](QUICKSTART.md) | [📚 All Docs](DOCS.md)

This guide will help you quickly configure the S3 to Google Drive Sync project.

## ⚡ Quick Setup (5 minutes)

### 1. Prerequisites

Before starting, make sure you have:

- ✅ Docker and Docker Compose installed
- ✅ An S3 bucket on AWS
- ✅ A Google Cloud account

### 2. Clone the Project

```bash
git clone <repository-url>
cd gdrive-s3-sync
```

### 3. Google Drive API Setup

#### A. Create a Google Cloud project

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "Google Drive API"

#### B. Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. "Create Credentials" → "Service Account"
3. Name: `s3-gdrive-sync`
4. Role: `Editor`
5. "Create and Continue" → "Done"

#### C. Download Credentials

1. Click on the created service account
2. "Keys" tab → "Add Key" → "Create new key"
3. Type: `JSON`
4. Save the file as `credentials.json`

#### D. Share Drive Folder

1. Open Google Drive
2. Create/select a folder
3. Share with the service account email (from credentials.json)
4. Copy the folder ID from the URL (after `/folders/`)

### 4. Configure the Project

```bash
# Create structure
mkdir -p credentials logs

# Copy Google credentials
mv ~/Downloads/credentials.json credentials/

# Create .env file
cp .env.example .env
```

### 5. Edit .env

Open `.env` and enter your data:

```env
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET_NAME=my-s3-bucket

# Google Drive
GDRIVE_FOLDER_ID=1a2b3c4d5e6f7g8h9i0j  # From folder URL
GDRIVE_CREDENTIALS_PATH=/app/credentials/credentials.json

# Sync Settings
SYNC_INTERVAL_SECONDS=300  # 5 minutes
LOG_LEVEL=INFO
```

### 6. Start the Container

```bash
docker-compose up -d
```

### 7. Verify It's Working

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

## 🧪 Quick Test

### Test Sync Manually

1. Upload a file to S3:

```bash
aws s3 cp test.txt s3://my-bucket/test.txt
```

2. Wait for the next sync (max 5 minutes) or restart:

```bash
docker-compose restart
```

3. Check Google Drive - the file should appear!

4. Delete the file from S3:

```bash
aws s3 rm s3://my-bucket/test.txt
```

5. On the next sync, the file will also be deleted from Google Drive

### Automatic Integration Tests

```bash
# Install local dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python tests/integration_test.py
```

## 📊 Monitoring

### View Logs in Real-Time

```bash
docker-compose logs -f
```

### Typical Success Logs

```
INFO - Starting synchronization from S3 to Google Drive
INFO - S3 files count: 5
INFO - Google Drive files count: 4
INFO - Files to upload: 1
INFO - Successfully synced new file: document.pdf
INFO - Synchronization completed
INFO - Statistics: {'uploaded': 1, 'updated': 0, 'deleted': 0, 'errors': 0}
```

## 🛑 Stop and Restart

```bash
# Stop the container
docker-compose down

# Start again
docker-compose up -d

# Restart (without stopping)
docker-compose restart
```

## 🔧 Useful Commands

```bash
# Show all available commands
make help

# Setup development environment
./setup.sh

# Run unit tests
make test

# Rebuild the image
make rebuild

# Clean temporary files
make clean
```

## ⚠️ Troubleshooting

### Container won't start

```bash
# Check logs for errors
docker-compose logs

# Verify .env is configured correctly
cat .env

# Verify credentials.json exists
ls -la credentials/
```

### "Credentials file not found"

- Make sure `credentials.json` is in `credentials/`
- Check permissions: `chmod 644 credentials/credentials.json`

### "Access Denied" on Google Drive

- Verify you've shared the folder with the service account email
- Check that `GDRIVE_FOLDER_ID` is correct

### "Access Denied" on S3

- Verify AWS credentials in `.env`
- Make sure the IAM user has `s3:GetObject`, `s3:ListBucket` permissions

## 📚 Next Steps

1. ✅ Read the complete [README.md](../README.en.md) for details
2. 📖 Check [CONTRIBUTING.md](CONTRIBUTING.en.md) if you want to contribute
3. 🔍 Explore the source code in `src/`
4. 🧪 Run the tests in `tests/`

## 💡 Tips

- **Sync Interval**: 300 seconds (5 min) is a good default. Lower for more frequent syncs
- **Log Level**: Use `DEBUG` for detailed troubleshooting
- **Backup**: Consider backing up the GDrive folder before starting
- **Monitoring**: Regularly check logs for any errors

## 🎉 You're Done!

Your S3 → Google Drive sync is now active!

Files will be automatically synced every 5 minutes.

---

**Having problems?** Open an issue on GitHub or check the complete README.
