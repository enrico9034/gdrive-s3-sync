# Path Handling in gdrive-s3-sync

This document explains how the application handles S3 directory structures when syncing to Google Drive.

## Overview

S3 uses a flat key-value structure where paths like `dir1/dir2/file.txt` are just object keys with `/` characters. Google Drive, on the other hand, has a true hierarchical folder structure. This application provides two modes to handle this difference.

## Configuration

Set the `PRESERVE_STRUCTURE` environment variable to control how S3 paths are mapped to Google Drive:

```bash
# .env file
PRESERVE_STRUCTURE=true   # Default: Recreate folder structure (recommended)
# or
PRESERVE_STRUCTURE=false  # Flatten to root folder with normalized names
```

## Modes

### Mode 1: Preserve Structure (Default - Recommended)

**Setting:** `PRESERVE_STRUCTURE=true`

This mode recreates the S3 directory structure as actual folders in Google Drive.

**Example:**

```
S3 Structure:
  docs/readme.md
  docs/images/logo.png
  src/main.py
  src/utils/helper.py
  test.txt

Google Drive Structure:
  📁 Your Sync Folder
    📁 docs
      📄 readme.md
      📁 images
        📄 logo.png
    📁 src
      📄 main.py
      📁 utils
        📄 helper.py
    📄 test.txt
```

**How it works:**

1. Parses S3 keys to extract directory path and filename
2. Creates nested folders in Google Drive matching the S3 path
3. Uploads files to the correct folder
4. Caches folder IDs for performance

**Advantages:**

- Maintains logical organization
- Easy to navigate in Google Drive
- Preserves directory context
- Matches S3 structure exactly

**Use cases:**

- Projects with organized folder structures
- Multi-level directory hierarchies
- When you want Google Drive to mirror S3

### Mode 2: Flatten Structure

**Setting:** `PRESERVE_STRUCTURE=false`

This mode uploads all files to the root sync folder with normalized filenames.

**Example:**

```
S3 Structure:
  docs/readme.md
  docs/images/logo.png
  src/main.py
  src/utils/helper.py
  test.txt

Google Drive Structure:
  📁 Your Sync Folder
    📄 docs_readme.md
    📄 docs_images_logo.png
    📄 src_main.py
    📄 src_utils_helper.py
    📄 test.txt
```

**How it works:**

1. Replaces `/` with `_` in S3 keys
2. Uploads all files to the root sync folder
3. Uses the normalized name as the filename

**Advantages:**

- Simple flat structure
- All files in one location
- No folder management needed

**Disadvantages:**

- Can create long filenames
- Loses directory context
- Harder to navigate with many files

**Use cases:**

- Simple buckets with few files
- When you want all files in one place
- Legacy compatibility

## Directory Marker Filtering

The application automatically filters S3 directory markers (keys ending with `/`) to avoid creating empty files. This is handled regardless of the `PRESERVE_STRUCTURE` setting.

**Example:**

```
S3 Bucket:
  dir1/              ← Skipped (directory marker)
  dir1/file.txt      ← Synced
  dir2/              ← Skipped (directory marker)
  dir2/subdir/       ← Skipped (directory marker)
  dir2/subdir/data.json  ← Synced
```

## Implementation Details

### Preserve Structure Mode

**File Identifier:** Full S3 key (e.g., `dir1/dir2/file.txt`)

**Parsing Logic:**

```python
# dir1/dir2/file.txt → ("dir1/dir2", "file.txt")
# test.txt → ("", "test.txt")
```

**Folder Creation:**

- Uses Google Drive API folder operations
- Creates parent folders recursively
- Caches folder IDs to avoid duplicate API calls

**Metadata Storage:**

```json
{
  "identifier": "dir1/dir2/file.txt",
  "s3_key": "dir1/dir2/file.txt"
}
```

### Flatten Structure Mode

**File Identifier:** Normalized filename (e.g., `dir1_dir2_file.txt`)

**Normalization:**

```python
# dir1/dir2/file.txt → dir1_dir2_file.txt
# test.txt → test.txt
```

**Metadata Storage:**

```json
{
  "identifier": "dir1_dir2_file.txt",
  "s3_key": "dir1/dir2/file.txt"
}
```

## Testing

Use the provided test script to verify folder structure handling:

```bash
python tests/test_folder_structure.py
```

This creates test files with nested directories and syncs them using both modes.

## Migration

### From Flatten to Preserve Structure

If you're switching from `PRESERVE_STRUCTURE=false` to `PRESERVE_STRUCTURE=true`:

1. **Files will be re-uploaded** because identifiers change:

   - Old: `dir1_file.txt`
   - New: `dir1/file.txt`

2. **Old flattened files won't be deleted automatically**

   - You may want to clean them up manually

3. **Recommendation:** Start with a fresh Google Drive folder

### From Preserve to Flatten

If you're switching from `PRESERVE_STRUCTURE=true` to `PRESERVE_STRUCTURE=false`:

1. **Files will be re-uploaded** to the root folder
2. **Folders and files will remain** in the old structure
3. **Recommendation:** Clean up the old folders manually

## Best Practices

1. **Choose the right mode early:** Changing modes later requires re-sync
2. **Use preserve structure for:** Projects, organized data, multi-level hierarchies
3. **Use flatten for:** Simple buckets, legacy systems, flat structures
4. **Test first:** Use `test_folder_structure.py` before production sync
5. **Monitor logs:** Check for folder creation and file placement

## Troubleshooting

### Issue: Files not in expected folders

**Check:**

- `PRESERVE_STRUCTURE` value in .env
- Logs for folder creation messages
- S3 keys don't have unexpected characters

### Issue: Duplicate files after mode change

**Cause:** Different identifiers between modes

**Solution:**

- Clean up old files manually
- Or use a fresh Google Drive folder

### Issue: Folder creation errors

**Check:**

- Google Drive API quota
- Folder permissions
- Parent folder ID is correct

## Performance Considerations

- **Folder caching:** Reduces API calls for repeated paths
- **Batch operations:** Creates folders only when needed
- **Metadata queries:** Uses identifier for efficient file lookup

## API Methods

### GDrive Clients (OAuth2 & Service Account)

```python
# Create a folder
folder_id = client.create_folder("folder_name", parent_folder_id)

# Find folder by name
folder_id = client.find_folder_by_name("folder_name", parent_folder_id)

# Get or create folder (idempotent)
folder_id = client.get_or_create_folder("folder_name", parent_folder_id)

# Create nested path
folder_id = client.get_or_create_path("dir1/dir2/dir3")

# Upload to specific folder
file_id = client.upload_file(file_path, filename, parent_folder_id)
```

## See Also

- [OAuth2 Setup Guide](OAUTH2_SETUP.md)
- [Integration Tests](../tests/README.md)
- [API Documentation](API.md)
