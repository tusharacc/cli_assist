"""
Unit tests for SafeFileEditor
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.lumos_cli.core.safety import SafeFileEditor

class TestSafeFileEditor:
    """Test cases for SafeFileEditor"""
    
    def test_safety_initialization(self):
        """Test SafeFileEditor initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            assert editor is not None
            assert editor.backup_dir == temp_dir
    
    def test_create_backup(self):
        """Test creating file backups"""
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, 'w') as f:
                f.write("original content")
            
            # Create backup
            backup_path = editor.create_backup(test_file)
            
            assert os.path.exists(backup_path)
            assert backup_path != test_file
            
            # Verify backup content
            with open(backup_path, 'r') as f:
                assert f.read() == "original content"
    
    def test_preview_changes(self):
        """Test previewing changes before applying"""
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            original_content = "def hello():\n    return 'world'"
            with open(test_file, 'w') as f:
                f.write(original_content)
            
            # Preview changes
            new_content = "def hello():\n    return 'hello world'"
            preview = editor.preview_changes(test_file, new_content)
            
            assert preview is not None
            assert 'diff' in preview
            assert 'original' in preview
            assert 'modified' in preview
    
    def test_apply_changes(self):
        """Test applying changes to files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            original_content = "def hello():\n    return 'world'"
            with open(test_file, 'w') as f:
                f.write(original_content)
            
            # Apply changes
            new_content = "def hello():\n    return 'hello world'"
            result = editor.apply_changes(test_file, new_content)
            
            assert result['success'] is True
            assert result['backup_path'] is not None
            
            # Verify file was modified
            with open(test_file, 'r') as f:
                assert f.read() == new_content
            
            # Verify backup exists
            assert os.path.exists(result['backup_path'])
    
    def test_rollback_changes(self):
        """Test rolling back changes"""
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            original_content = "def hello():\n    return 'world'"
            with open(test_file, 'w') as f:
                f.write(original_content)
            
            # Apply changes and get backup path
            new_content = "def hello():\n    return 'hello world'"
            result = editor.apply_changes(test_file, new_content)
            backup_path = result['backup_path']
            
            # Rollback changes
            rollback_result = editor.rollback_changes(test_file, backup_path)
            
            assert rollback_result['success'] is True
            
            # Verify file was restored
            with open(test_file, 'r') as f:
                assert f.read() == original_content
    
    def test_validate_syntax(self):
        """Test syntax validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            
            # Test valid Python code
            valid_code = "def hello():\n    return 'world'"
            result = editor.validate_syntax(valid_code, 'python')
            assert result['valid'] is True
            
            # Test invalid Python code
            invalid_code = "def hello():\n    return 'world'  # missing closing quote"
            result = editor.validate_syntax(invalid_code, 'python')
            assert result['valid'] is False
            assert 'error' in result
    
    def test_get_file_info(self):
        """Test getting file information"""
        with tempfile.TemporaryDirectory() as temp_dir:
            editor = SafeFileEditor(backup_dir=temp_dir)
            
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            content = "def hello():\n    return 'world'"
            with open(test_file, 'w') as f:
                f.write(content)
            
            # Get file info
            info = editor.get_file_info(test_file)
            
            assert info['exists'] is True
            assert info['size'] > 0
            assert info['extension'] == '.py'
            assert info['lines'] == 2
