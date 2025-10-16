# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-16

### 🚀 Added - OAuth2 Support

- **OAuth2 Authentication**: New `GDriveOAuth2Client` class for OAuth2-based authentication
  - Full support for personal Google accounts
  - Automatic token refresh
  - Persistent token storage in `token.pickle`
  - Browser-based authentication flow
- **New Documentation**:
  - `docs/OAUTH2_SETUP.md` - Complete OAuth2 setup guide (Italian)
  - `docs/OAUTH2_SETUP.en.md` - Complete OAuth2 setup guide (English)
  - `docs/TEST_OAUTH2.md` - OAuth2 testing script documentation
- **Test Script**: `scripts/test_oauth2.py` to verify OAuth2 setup
- **Dual Authentication Support**: Application now supports both OAuth2 and Service Account (via `GDRIVE_USE_OAUTH2` env var)

### 🔄 Changed

- **Default Authentication**: OAuth2 is now the default and recommended method (`GDRIVE_USE_OAUTH2=true`)
- **Environment Variables**:
  - Added `GDRIVE_USE_OAUTH2` to choose authentication method
  - Added `GDRIVE_TOKEN_PATH` for OAuth2 token storage
- **Documentation**: Major updates to `README.md` and `README.en.md`
  - OAuth2 now featured as primary authentication method
  - Service Account instructions moved to collapsible section
  - Clear warnings about Service Account limitations for personal accounts

### ⚠️ Breaking Changes

- **Service Account Deprecated for Personal Accounts**: Service Accounts do NOT work with personal Google accounts due to storage quota limitations
- OAuth2 is now the only supported method for personal Google accounts
- Users with Service Account setup should migrate to OAuth2 for personal accounts

### 📝 Notes

- **For Personal Google Accounts**: MUST use OAuth2 (Service Accounts have no storage quota)
- **For Google Workspace**: Can use either OAuth2 or Service Account
- Migration guide included in OAuth2 setup documentation

## [1.2.0] - 2025-10-16

### Changed

- **Documentation Restructuring**: Moved all documentation files to `docs/` folder for better organization
  - Moved `QUICKSTART.md` → `docs/QUICKSTART.md`
  - Moved `QUICKSTART.en.md` → `docs/QUICKSTART.en.md`
  - Moved `CONTRIBUTING.md` → `docs/CONTRIBUTING.md`
  - Moved `CONTRIBUTING.en.md` → `docs/CONTRIBUTING.en.md`
  - Moved `CHANGELOG.md` → `docs/CHANGELOG.md`
  - Moved `STRUCTURE.md` → `docs/STRUCTURE.md`
  - Moved `DOCS.md` → `docs/DOCS.md`
  - Kept `README.md` and `README.en.md` in root for easy access

### Added

- **Documentation Map**: New `docs/DOCUMENTATION_MAP.md` file with complete navigation guide
- Updated all internal documentation links to reflect new structure

### Fixed

- All internal documentation links now point to correct locations
- Cross-references between documentation files updated

## [1.1.0] - 2025-10-16

### Added

- **S3 Self-Hosted Support**: Support for S3-compatible storage (MinIO, Wasabi, DigitalOcean Spaces, Backblaze B2, etc.)
- `S3_ENDPOINT_URL` environment variable for custom S3 endpoints
- Comprehensive documentation for S3-compatible storage (`docs/S3_SELF_HOSTED.md`)
- Quick start guide for MinIO (`docs/QUICKSTART_MINIO.md`)
- Docker Compose configuration for testing with MinIO (`docker-compose.minio.yml`)
- Example MinIO configuration (`.env.minio.example`)
- **Multilingual Documentation**: Complete Italian and English versions
  - `README.en.md` - English documentation
  - `QUICKSTART.en.md` - English quick start
  - `CONTRIBUTING.en.md` - English contributing guidelines
  - `DOCS.md` - Multilingual documentation index
  - Language selector in all main documents
- Documentation verification script (`check-docs.sh`)
- Multilingual documentation guide (`MULTILINGUAL.md`)

### Changed

- S3Client now accepts optional `endpoint_url` parameter
- Updated main.py to read and use `S3_ENDPOINT_URL`
- Enhanced .env.example with S3 endpoint configuration examples
- Updated README files to highlight S3-compatible storage support

### Testing

- Added unit test for S3Client with custom endpoint
- Updated example scripts to demonstrate custom endpoint usage

## [1.0.0] - 2025-10-16

### Added

- Initial release
- One-way sync from AWS S3 to Google Drive
- Automatic file upload for new files
- Automatic file update detection (based on file size)
- Automatic file deletion when removed from S3
- Docker containerization with docker-compose
- Comprehensive logging with configurable levels
- Environment-based configuration
- Complete test suite (unit and integration tests)
- Detailed documentation (README, QUICKSTART, CONTRIBUTING)
- GitHub Actions CI/CD workflow
- Makefile for common operations
- Setup script for local development
- VS Code configuration
- Example scripts for programmatic usage

### Features

- S3 client for file operations
- Google Drive client with service account authentication
- Sync manager with one-way synchronization logic
- Configurable sync interval
- File size-based change detection
- Automatic cleanup of temporary files
- Comprehensive error handling and logging

### Documentation

- Complete README with setup instructions
- Quick start guide
- Google Drive API setup guide (step-by-step)
- Contributing guidelines
- Integration test examples
- Code examples

## [Unreleased]

### Planned Features

- Bidirectional sync support
- MD5 hash-based change detection
- Support for S3 prefixes/folders
- Web dashboard for monitoring
- Email/Slack notifications
- Retry logic with exponential backoff
- Large file support (multipart upload)
- State tracking database

---

For more details, see the [README](../README.md).
