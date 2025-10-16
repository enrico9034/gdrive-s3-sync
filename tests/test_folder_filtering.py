#!/usr/bin/env python3
"""
Quick test to verify folder filtering in list_files()
"""

# Mock data simulating Google Drive API response
mock_gdrive_response = {
    'files': [
        {'id': '1', 'name': 'file1.txt', 'size': '100', 'modifiedTime': '2024-01-01', 'mimeType': 'text/plain'},
        {'id': '2', 'name': 'backup', 'size': '0', 'modifiedTime': '2024-01-01', 'mimeType': 'application/vnd.google-apps.folder'},
        {'id': '3', 'name': 'actualbudget', 'size': '0', 'modifiedTime': '2024-01-01', 'mimeType': 'application/vnd.google-apps.folder'},
        {'id': '4', 'name': 'file2.tar', 'size': '5000', 'modifiedTime': '2024-01-02', 'mimeType': 'application/x-tar'},
    ]
}

# Simulate filtering logic
files = mock_gdrive_response['files']
actual_files = [f for f in files if f.get('mimeType') != 'application/vnd.google-apps.folder']

print("All entries from Google Drive:")
for f in files:
    print(f"  - {f['name']} ({f['mimeType']})")

print(f"\nFiltered files (excluding folders):")
for f in actual_files:
    print(f"  - {f['name']} ({f['mimeType']})")

print(f"\nTotal entries: {len(files)}")
print(f"Actual files: {len(actual_files)}")
print(f"Folders filtered out: {len(files) - len(actual_files)}")
