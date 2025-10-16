#!/usr/bin/env python3
"""
Test script for OAuth2 authentication
Run this to verify OAuth2 setup before running the full sync
"""

import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.gdrive_oauth2_client import GDriveOAuth2Client


def main():
    """Test OAuth2 authentication and list files"""
    print("=" * 60)
    print("Google Drive OAuth2 Authentication Test")
    print("=" * 60)
    print()
    
    # Get configuration
    credentials_path = os.getenv('GDRIVE_CREDENTIALS_PATH', 'credentials/credentials.json')
    folder_id = os.getenv('GDRIVE_FOLDER_ID')
    token_path = os.getenv('GDRIVE_TOKEN_PATH', 'credentials/token.pickle')
    
    if not folder_id:
        print("❌ Error: GDRIVE_FOLDER_ID not set in .env file")
        sys.exit(1)
    
    print(f"Credentials path: {credentials_path}")
    print(f"Folder ID: {folder_id}")
    print(f"Token path: {token_path}")
    print()
    
    # Test authentication
    print("🔐 Authenticating with Google Drive...")
    print()
    
    try:
        client = GDriveOAuth2Client(
            credentials_path=credentials_path,
            folder_id=folder_id,
            token_path=token_path
        )
        
        print("✅ Authentication successful!")
        print()
        
        # List files
        print("📁 Listing files in Google Drive folder...")
        files = client.list_files()
        
        print(f"Found {len(files)} files:")
        print()
        
        if files:
            for file in files:
                size_mb = file['size'] / (1024 * 1024)
                print(f"  - {file['name']}")
                print(f"    Size: {size_mb:.2f} MB")
                print(f"    Modified: {file['modified_time']}")
                print()
        else:
            print("  (No files in folder)")
            print()
        
        print("=" * 60)
        print("✅ OAuth2 setup is working correctly!")
        print("=" * 60)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("Please make sure:")
        print("1. You have downloaded credentials.json from Google Cloud Console")
        print("2. The file is in the correct location")
        print("3. You have set up OAuth2 credentials (not Service Account)")
        print()
        print("See docs/OAUTH2_SETUP.md for detailed instructions")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("Please check:")
        print("1. Your credentials.json file is valid")
        print("2. The folder ID is correct")
        print("3. You have enabled Google Drive API")
        print()
        print("See docs/OAUTH2_SETUP.md for troubleshooting")
        sys.exit(1)


if __name__ == "__main__":
    main()
