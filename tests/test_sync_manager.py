"""
Integration tests for Sync Manager
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.sync_manager import SyncManager


class TestSyncManager:
    """Test suite for SyncManager"""
    
    def test_init(self, mock_s3_client, mock_gdrive_client):
        """Test SyncManager initialization"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        assert manager.s3_client == mock_s3_client
        assert manager.gdrive_client == mock_gdrive_client
    
    def test_sync_upload_new_files(self, mock_s3_client, mock_gdrive_client):
        """Test syncing when there are new files to upload"""
        # Setup: S3 has files, GDrive is empty
        mock_s3_client.list_files.return_value = [
            {'key': 'new_file.txt', 'size': 100, 'etag': 'abc123', 'last_modified': '2024-01-01'}
        ]
        mock_gdrive_client.list_files.return_value = []
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        with patch.object(manager, '_upload_file', return_value=True) as mock_upload:
            stats = manager.sync()
            
            assert stats['uploaded'] == 1
            assert stats['deleted'] == 0
            assert stats['updated'] == 0
            assert stats['errors'] == 0
            mock_upload.assert_called_once_with('new_file.txt', 'new_file.txt')
    
    def test_sync_delete_removed_files(self, mock_s3_client, mock_gdrive_client):
        """Test syncing when files should be deleted from GDrive"""
        # Setup: S3 is empty, GDrive has files
        mock_s3_client.list_files.return_value = []
        mock_gdrive_client.list_files.return_value = [
            {'id': 'gdrive-id-1', 'name': 'old_file.txt', 'size': '100'}
        ]
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        stats = manager.sync()
        
        assert stats['deleted'] == 1
        assert stats['uploaded'] == 0
        assert stats['updated'] == 0
        mock_gdrive_client.delete_file.assert_called_once_with('gdrive-id-1', 'old_file.txt')
    
    def test_sync_update_modified_files(self, mock_s3_client, mock_gdrive_client):
        """Test syncing when files have been modified (size changed)"""
        # Setup: Same file in both, but different sizes
        mock_s3_client.list_files.return_value = [
            {'key': 'modified.txt', 'size': 200, 'etag': 'new-hash', 'last_modified': '2024-01-02'}
        ]
        mock_gdrive_client.list_files.return_value = [
            {'id': 'gdrive-id-1', 'name': 'modified.txt', 'size': '100'}
        ]
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        with patch.object(manager, '_update_file', return_value=True) as mock_update:
            stats = manager.sync()
            
            assert stats['updated'] == 1
            assert stats['uploaded'] == 0
            assert stats['deleted'] == 0
            mock_update.assert_called_once_with('modified.txt', 'gdrive-id-1', 'modified.txt')
    
    def test_sync_unchanged_files(self, mock_s3_client, mock_gdrive_client):
        """Test syncing when files are unchanged"""
        # Setup: Same file in both with same size
        mock_s3_client.list_files.return_value = [
            {'key': 'unchanged.txt', 'size': 100, 'etag': 'abc123', 'last_modified': '2024-01-01'}
        ]
        mock_gdrive_client.list_files.return_value = [
            {'id': 'gdrive-id-1', 'name': 'unchanged.txt', 'size': '100'}
        ]
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        stats = manager.sync()
        
        assert stats['unchanged'] == 1
        assert stats['uploaded'] == 0
        assert stats['deleted'] == 0
        assert stats['updated'] == 0
    
    def test_sync_mixed_operations(self, mock_s3_client, mock_gdrive_client):
        """Test syncing with multiple operations"""
        # Setup: Upload new, delete old, update modified, keep unchanged
        mock_s3_client.list_files.return_value = [
            {'key': 'new.txt', 'size': 50, 'etag': 'new1', 'last_modified': '2024-01-01'},
            {'key': 'modified.txt', 'size': 200, 'etag': 'mod1', 'last_modified': '2024-01-02'},
            {'key': 'unchanged.txt', 'size': 100, 'etag': 'unch1', 'last_modified': '2024-01-03'}
        ]
        mock_gdrive_client.list_files.return_value = [
            {'id': 'gd-1', 'name': 'old.txt', 'size': '75'},
            {'id': 'gd-2', 'name': 'modified.txt', 'size': '100'},
            {'id': 'gd-3', 'name': 'unchanged.txt', 'size': '100'}
        ]
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        with patch.object(manager, '_upload_file', return_value=True) as mock_upload, \
             patch.object(manager, '_update_file', return_value=True) as mock_update:
            
            stats = manager.sync()
            
            assert stats['uploaded'] == 1  # new.txt
            assert stats['deleted'] == 1   # old.txt
            assert stats['updated'] == 1   # modified.txt
            assert stats['unchanged'] == 1 # unchanged.txt
            assert stats['errors'] == 0
    
    @patch('src.sync_manager.tempfile.NamedTemporaryFile')
    @patch('src.sync_manager.os.path.exists')
    @patch('src.sync_manager.os.remove')
    def test_upload_file_success(self, mock_remove, mock_exists, mock_tempfile, 
                                  mock_s3_client, mock_gdrive_client):
        """Test _upload_file method success"""
        # Setup temp file mock
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test123'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_exists.return_value = True
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=False)
        result = manager._upload_file('test.txt', 'test.txt')
        
        assert result is True
        mock_s3_client.download_file.assert_called_once_with('test.txt', '/tmp/test123')
        mock_gdrive_client.upload_file.assert_called_once_with('/tmp/test123', 'test.txt')
        mock_remove.assert_called_once()
    
    @patch('src.sync_manager.tempfile.NamedTemporaryFile')
    @patch('src.sync_manager.os.path.exists')
    @patch('src.sync_manager.os.remove')
    def test_upload_file_download_failure(self, mock_remove, mock_exists, mock_tempfile,
                                          mock_s3_client, mock_gdrive_client):
        """Test _upload_file when S3 download fails"""
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test123'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_exists.return_value = True
        
        # Simulate download failure
        mock_s3_client.download_file.return_value = False
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=False)
        result = manager._upload_file('test.txt', 'test.txt')
        
        assert result is False
        mock_gdrive_client.upload_file.assert_not_called()
    
    @patch('src.sync_manager.tempfile.NamedTemporaryFile')
    @patch('src.sync_manager.os.path.exists')
    @patch('src.sync_manager.os.remove')
    def test_update_file_success(self, mock_remove, mock_exists, mock_tempfile,
                                 mock_s3_client, mock_gdrive_client):
        """Test _update_file method success"""
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test456'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_exists.return_value = True
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=False)
        result = manager._update_file('test.txt', 'gdrive-file-id', 'test.txt')
        
        assert result is True
        mock_s3_client.download_file.assert_called_once_with('test.txt', '/tmp/test456')
        mock_gdrive_client.update_file.assert_called_once_with('gdrive-file-id', '/tmp/test456', 'test.txt')
        mock_remove.assert_called_once()


class TestSyncManagerHelpers:
    """Test suite for SyncManager helper methods"""
    
    def test_parse_s3_key_with_path(self, mock_s3_client, mock_gdrive_client):
        """Test parsing S3 key with directory path"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        dir_path, filename = manager._parse_s3_key('dir1/dir2/file.txt')
        
        assert dir_path == 'dir1/dir2'
        assert filename == 'file.txt'
    
    def test_parse_s3_key_no_path(self, mock_s3_client, mock_gdrive_client):
        """Test parsing S3 key without directory path"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        dir_path, filename = manager._parse_s3_key('file.txt')
        
        assert dir_path == ''
        assert filename == 'file.txt'
    
    def test_parse_s3_key_single_level(self, mock_s3_client, mock_gdrive_client):
        """Test parsing S3 key with single directory"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        dir_path, filename = manager._parse_s3_key('docs/readme.md')
        
        assert dir_path == 'docs'
        assert filename == 'readme.md'
    
    def test_get_file_identifier_preserve_structure(self, mock_s3_client, mock_gdrive_client):
        """Test get file identifier with preserve_structure=True"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=True)
        
        identifier = manager._get_file_identifier('dir1/dir2/file.txt')
        
        assert identifier == 'dir1/dir2/file.txt'
    
    def test_get_file_identifier_flatten_structure(self, mock_s3_client, mock_gdrive_client):
        """Test get file identifier with preserve_structure=False"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=False)
        
        identifier = manager._get_file_identifier('dir1/dir2/file.txt')
        
        assert identifier == 'dir1_dir2_file.txt'
    
    def test_get_file_identifier_no_path(self, mock_s3_client, mock_gdrive_client):
        """Test get file identifier without directory path"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=False)
        
        identifier = manager._get_file_identifier('file.txt')
        
        assert identifier == 'file.txt'
    
    def test_get_gdrive_folder_for_path_empty(self, mock_s3_client, mock_gdrive_client):
        """Test get folder for empty path returns root folder"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        folder_id = manager._get_gdrive_folder_for_path('')
        
        assert folder_id == mock_gdrive_client.folder_id
    
    def test_get_gdrive_folder_for_path_cached(self, mock_s3_client, mock_gdrive_client):
        """Test folder path caching"""
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        mock_gdrive_client.get_or_create_path.return_value = 'folder-123'
        
        # First call - should call get_or_create_path
        folder_id1 = manager._get_gdrive_folder_for_path('dir1/dir2')
        assert folder_id1 == 'folder-123'
        mock_gdrive_client.get_or_create_path.assert_called_once_with('dir1/dir2')
        
        # Second call - should use cache
        folder_id2 = manager._get_gdrive_folder_for_path('dir1/dir2')
        assert folder_id2 == 'folder-123'
        # Still called once (cached)
        mock_gdrive_client.get_or_create_path.assert_called_once()


class TestSyncManagerPreserveStructure:
    """Test suite for preserve_structure mode"""
    
    def test_upload_with_preserve_structure(self, mock_s3_client, mock_gdrive_client):
        """Test upload with preserve_structure=True creates folders"""
        mock_s3_client.list_files.return_value = [
            {'key': 'docs/readme.md', 'size': 100, 'etag': 'abc', 'last_modified': '2024-01-01'}
        ]
        mock_gdrive_client.list_files.return_value = []
        mock_gdrive_client.get_or_create_path.return_value = 'folder-docs'
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=True)
        
        with patch.object(manager, '_upload_file', return_value=True) as mock_upload:
            stats = manager.sync()
            
            assert stats['uploaded'] == 1
            # Should be called with full path as identifier
            mock_upload.assert_called_once_with('docs/readme.md', 'docs/readme.md')
    
    def test_upload_with_flatten_structure(self, mock_s3_client, mock_gdrive_client):
        """Test upload with preserve_structure=False flattens names"""
        mock_s3_client.list_files.return_value = [
            {'key': 'docs/readme.md', 'size': 100, 'etag': 'abc', 'last_modified': '2024-01-01'}
        ]
        mock_gdrive_client.list_files.return_value = []
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=False)
        
        with patch.object(manager, '_upload_file', return_value=True) as mock_upload:
            stats = manager.sync()
            
            assert stats['uploaded'] == 1
            # Should be called with flattened name
            mock_upload.assert_called_once_with('docs_readme.md', 'docs/readme.md')
    
    @patch('src.sync_manager.tempfile.NamedTemporaryFile')
    @patch('src.sync_manager.os.path.exists')
    @patch('src.sync_manager.os.remove')
    def test_upload_file_with_folders(self, mock_remove, mock_exists, mock_tempfile,
                                     mock_s3_client, mock_gdrive_client):
        """Test _upload_file creates folders when preserve_structure=True"""
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/test123'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        mock_exists.return_value = True
        mock_gdrive_client.get_or_create_path.return_value = 'folder-id-123'
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client, preserve_structure=True)
        result = manager._upload_file('docs/images/logo.png', 'docs/images/logo.png')
        
        assert result is True
        # Should get/create folder path
        mock_gdrive_client.get_or_create_path.assert_called_once_with('docs/images')
        # Should download from S3
        mock_s3_client.download_file.assert_called_once_with('docs/images/logo.png', '/tmp/test123')
        # Should upload to correct folder with just filename
        mock_gdrive_client.upload_file.assert_called_once_with('/tmp/test123', 'logo.png', 'folder-id-123')


class TestSyncManagerErrorHandling:
    """Test suite for error handling"""
    
    @patch('src.sync_manager.tempfile.NamedTemporaryFile')
    def test_upload_file_exception_handling(self, mock_tempfile, mock_s3_client, mock_gdrive_client):
        """Test _upload_file handles exceptions"""
        mock_tempfile.side_effect = Exception("Temp file error")
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        result = manager._upload_file('test.txt', 'test.txt')
        
        assert result is False
    
    @patch('src.sync_manager.tempfile.NamedTemporaryFile')
    def test_update_file_exception_handling(self, mock_tempfile, mock_s3_client, mock_gdrive_client):
        """Test _update_file handles exceptions"""
        mock_tempfile.side_effect = Exception("Temp file error")
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        result = manager._update_file('test.txt', 'file-id', 'test.txt')
        
        assert result is False
    
    def test_sync_with_upload_error(self, mock_s3_client, mock_gdrive_client):
        """Test sync counts errors when upload fails"""
        mock_s3_client.list_files.return_value = [
            {'key': 'test.txt', 'size': 100, 'etag': 'abc', 'last_modified': '2024-01-01'}
        ]
        mock_gdrive_client.list_files.return_value = []
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        with patch.object(manager, '_upload_file', return_value=False) as mock_upload:
            stats = manager.sync()
            
            assert stats['errors'] == 1
            assert stats['uploaded'] == 0
    
    def test_sync_with_update_error(self, mock_s3_client, mock_gdrive_client):
        """Test sync counts errors when update fails"""
        mock_s3_client.list_files.return_value = [
            {'key': 'test.txt', 'size': 200, 'etag': 'new', 'last_modified': '2024-01-02'}
        ]
        mock_gdrive_client.list_files.return_value = [
            {'id': 'file-1', 'name': 'test.txt', 'size': '100'}
        ]
        
        manager = SyncManager(mock_s3_client, mock_gdrive_client)
        
        with patch.object(manager, '_update_file', return_value=False) as mock_update:
            stats = manager.sync()
            
            assert stats['errors'] == 1
            assert stats['updated'] == 0
