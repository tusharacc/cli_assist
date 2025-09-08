"""
Unit tests for EmbeddingDB
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.lumos_cli.core.embeddings import EmbeddingDB

class TestEmbeddingDB:
    """Test cases for EmbeddingDB"""
    
    def test_embeddings_initialization(self):
        """Test EmbeddingDB initialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmbeddingDB(db_path=os.path.join(temp_dir, "test.db"))
            assert db is not None
    
    def test_add_document(self):
        """Test adding documents to the database"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmbeddingDB(db_path=os.path.join(temp_dir, "test.db"))
            
            # Test adding a document
            doc_id = "test_doc_1"
            content = "This is a test document"
            metadata = {"file_path": "test.py", "line_number": 1}
            
            db.add_document(doc_id, content, metadata)
            
            # Verify document was added
            result = db.search("test document", top_k=1)
            assert len(result) > 0
            assert result[0][1] == content
    
    def test_search_documents(self):
        """Test searching documents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmbeddingDB(db_path=os.path.join(temp_dir, "test.db"))
            
            # Add test documents
            db.add_document("doc1", "Python function for data processing", {"file": "data.py"})
            db.add_document("doc2", "JavaScript function for UI rendering", {"file": "ui.js"})
            db.add_document("doc3", "Database schema definition", {"file": "schema.sql"})
            
            # Search for Python-related content
            results = db.search("Python data processing", top_k=2)
            assert len(results) > 0
            
            # The first result should be the most relevant
            assert "Python" in results[0][1]
    
    def test_get_document_by_id(self):
        """Test retrieving document by ID"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmbeddingDB(db_path=os.path.join(temp_dir, "test.db"))
            
            doc_id = "test_doc_1"
            content = "Test content"
            metadata = {"file": "test.py"}
            
            db.add_document(doc_id, content, metadata)
            
            # Retrieve document
            result = db.get_document(doc_id)
            assert result is not None
            assert result[0] == content
            assert result[1] == metadata
    
    def test_delete_document(self):
        """Test deleting documents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmbeddingDB(db_path=os.path.join(temp_dir, "test.db"))
            
            doc_id = "test_doc_1"
            content = "Test content"
            metadata = {"file": "test.py"}
            
            db.add_document(doc_id, content, metadata)
            
            # Verify document exists
            result = db.get_document(doc_id)
            assert result is not None
            
            # Delete document
            db.delete_document(doc_id)
            
            # Verify document is deleted
            result = db.get_document(doc_id)
            assert result is None
    
    def test_get_stats(self):
        """Test getting database statistics"""
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmbeddingDB(db_path=os.path.join(temp_dir, "test.db"))
            
            # Add some documents
            db.add_document("doc1", "Content 1", {})
            db.add_document("doc2", "Content 2", {})
            db.add_document("doc3", "Content 3", {})
            
            stats = db.get_stats()
            assert stats['total_documents'] == 3
            assert stats['total_chunks'] >= 3
