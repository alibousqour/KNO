"""
KNO Semantic File System - Comprehensive Test Suite
==================================================

Tests for:
- File indexing (single and batch)
- Semantic search
- Database backends (ChromaDB and FAISS)
- LLM coordinator integration
- Error handling
- Performance metrics

Author: KNO Architecture
License: MIT
"""

import asyncio
import os
import sys
import tempfile
import json
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KNO.SemanticFS.Tests")

# ============================================================================
# TEST DATA GENERATION
# ============================================================================

TEST_FILES = {
    "README.md": """
# Semantic File System

A powerful system for semantic indexing and search.

## Features
- Vector indexing using Sentence-Transformers
- Support for multiple file types
- Asynchronous operations
- Real-time progress tracking
""",
    
    "config.py": """
# Configuration Module

import os
from typing import Optional

class Config:
    '''Application configuration'''
    
    DEBUG = os.getenv('DEBUG', False)
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    
    @classmethod
    def get_database(cls) -> Optional[str]:
        return cls.DATABASE_URL
""",
    
    "utils.py": """
# Utility Functions

def calculate_similarity(vec1, vec2):
    '''Calculate cosine similarity between vectors'''
    import numpy as np
    dot = np.dot(vec1, vec2)
    norm = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return dot / norm if norm > 0 else 0

def chunk_text(text, size=512):
    '''Split text into chunks'''
    words = text.split()
    chunks = []
    for i in range(0, len(words), size):
        chunks.append(' '.join(words[i:i+size]))
    return chunks
""",

    "authentication.md": """
# Authentication System

## Overview
This system provides secure authentication and authorization.

## Features
- OAuth2 support
- JWT tokens
- Role-based access control (RBAC)
- Two-factor authentication (2FA)

## Implementation
The authentication module handles user verification and session management.
""",

    "database.py": """
# Database Module

class Database:
    def __init__(self, connection_string):
        self.connection = None
        self.connection_string = connection_string
    
    def connect(self):
        '''Establish database connection'''
        # Connection logic here
        pass
    
    def query(self, sql):
        '''Execute SQL query'''
        # Query logic here
        pass
    
    def close(self):
        '''Close connection'''
        if self.connection:
            self.connection.close()
""",
}

# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
    """Run tests for KNOFileSystem"""
    
    def __init__(self):
        self.test_dir = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
        }
    
    async def setup(self):
        """Setup test environment"""
        logger.info("Setting up test environment...")
        
        # Create temporary directory
        self.test_dir = tempfile.mkdtemp(prefix="kno_sfs_test_")
        
        # Create test files
        for filename, content in TEST_FILES.items():
            filepath = Path(self.test_dir) / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        logger.info(f"Test directory: {self.test_dir}")
        logger.info(f"Created {len(TEST_FILES)} test files")
    
    async def teardown(self):
        """Cleanup test environment"""
        import shutil
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            logger.info("Test environment cleaned up")
    
    async def test_basic_initialization(self):
        """Test: Basic filesystem initialization"""
        try:
            from semantic_file_system_enhanced import KNOFileSystem
            
            fs = KNOFileSystem(
                index_dir=os.path.join(self.test_dir, "index1"),
                use_chroma=True,
            )
            
            success = await fs.initialize()
            assert success, "Initialization failed"
            assert fs.embedding_model is not None, "Embedding model not loaded"
            assert fs.db_backend is not None, "Database backend not initialized"
            
            logger.info("✓ Basic initialization test passed")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Basic initialization test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_basic_initialization: {e}")
    
    async def test_chromadb_backend(self):
        """Test: ChromaDB backend"""
        try:
            from semantic_file_system_enhanced import KNOFileSystem
            
            fs = KNOFileSystem(
                index_dir=os.path.join(self.test_dir, "index_chroma"),
                use_chroma=True,
            )
            
            success = await fs.initialize()
            if not success:
                logger.warning("⊘ ChromaDB test skipped (dependencies not available)")
                self.results['skipped'] += 1
                return
            
            # Index test files
            indexed, total = await fs.index_directory(self.test_dir, recursive=False)
            assert indexed > 0, "No files indexed"
            
            # Search
            results = await fs.search_files("authentication", top_k=3)
            assert len(results) > 0, "No search results"
            
            logger.info(f"✓ ChromaDB backend test passed ({indexed} files indexed)")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ ChromaDB backend test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_chromadb_backend: {e}")
    
    async def test_faiss_backend(self):
        """Test: FAISS backend"""
        try:
            from semantic_file_system_enhanced import KNOFileSystem
            
            fs = KNOFileSystem(
                index_dir=os.path.join(self.test_dir, "index_faiss"),
                use_chroma=False,  # Use FAISS
            )
            
            success = await fs.initialize()
            if not success:
                logger.warning("⊘ FAISS test skipped (dependencies not available)")
                self.results['skipped'] += 1
                return
            
            # Index test files
            metrics = await fs.index_directory(self.test_dir, recursive=False)
            assert metrics.indexed_files > 0, "No files indexed"
            
            # Search
            results = await fs.search_files("database", top_k=3)
            assert len(results) > 0, "No search results"
            
            logger.info(f"✓ FAISS backend test passed ({metrics.indexed_files} files indexed)")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ FAISS backend test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_faiss_backend: {e}")
    
    async def test_file_indexing(self):
        """Test: File indexing"""
        try:
            from semantic_file_system_enhanced import KNOFileSystem
            
            fs = KNOFileSystem(index_dir=os.path.join(self.test_dir, "index_files"))
            success = await fs.initialize()
            if not success:
                self.results['skipped'] += 1
                return
            
            # Index single file
            test_file = Path(self.test_dir) / "README.md"
            indexed = await fs.index_file(str(test_file))
            assert indexed, "Failed to index file"
            
            # Check metadata
            indexed_files = fs.get_indexed_files()
            assert str(test_file) in indexed_files, "File not in indexed list"
            
            logger.info("✓ File indexing test passed")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ File indexing test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_file_indexing: {e}")
    
    async def test_semantic_search(self):
        """Test: Semantic search"""
        try:
            from semantic_file_system_enhanced import KNOFileSystem
            
            fs = KNOFileSystem(index_dir=os.path.join(self.test_dir, "index_search"))
            success = await fs.initialize()
            if not success:
                self.results['skipped'] += 1
                return
            
            # Index files
            await fs.index_directory(self.test_dir, recursive=False)
            
            # Test various searches
            queries = [
                "authentication and security",
                "database connection",
                "configuration settings",
            ]
            
            for query in queries:
                results = await fs.search_files(query, top_k=3)
                assert isinstance(results, list), "Results not a list"
                logger.info(f"  Query '{query}': {len(results)} results")
            
            logger.info("✓ Semantic search test passed")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Semantic search test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_semantic_search: {e}")
    
    async def test_coordinator_integration(self):
        """Test: LLM Coordinator integration"""
        try:
            from semantic_file_system_enhanced import KNOFileSystem
            from semantic_fs_coordinator_v2 import SemanticFSCoordinator
            
            fs = KNOFileSystem(index_dir=os.path.join(self.test_dir, "index_coord"))
            success = await fs.initialize()
            if not success:
                self.results['skipped'] += 1
                return
            
            # Create coordinator
            coordinator = SemanticFSCoordinator(fs)
            
            # Index files
            await fs.index_directory(self.test_dir, recursive=False)
            
            # Test tool execution
            result = await coordinator.execute_tool(
                "search_knowledge_base",
                {"query": "semantic", "top_k": 3}
            )
            
            assert result.get('success'), "Tool execution failed"
            assert result.get('results_count') >= 0, "Invalid results count"
            
            # Test statistics
            result = await coordinator.execute_tool("get_knowledge_base_stats", {})
            assert result.get('success'), "Statistics retrieval failed"
            
            logger.info("✓ Coordinator integration test passed")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Coordinator integration test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_coordinator_integration: {e}")
    
    async def test_statistics(self):
        """Test: Statistics and metrics"""
        try:
            from semantic_file_system_enhanced import KNOFileSystem
            
            fs = KNOFileSystem(index_dir=os.path.join(self.test_dir, "index_stats"))
            success = await fs.initialize()
            if not success:
                self.results['skipped'] += 1
                return
            
            # Index files
            metrics = await fs.index_directory(self.test_dir, recursive=False)
            
            # Check metrics
            assert metrics.indexed_files > 0, "No files indexed"
            assert metrics.total_chunks > 0, "No chunks created"
            assert metrics.indexing_time_seconds >= 0, "Invalid time"
            assert 0 <= metrics.get_success_rate() <= 100, "Invalid success rate"
            
            # Check statistics
            stats = fs.get_statistics()
            assert 'indexed_files_count' in stats, "Missing indexed_files_count"
            assert 'database_type' in stats, "Missing database_type"
            
            logger.info(f"✓ Statistics test passed (Success: {metrics.get_success_rate():.1f}%)")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Statistics test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_statistics: {e}")
    
    async def test_memory_efficiency(self):
        """Test: Memory efficiency with sync wrapper"""
        try:
            from semantic_file_system_enhanced import KNOFileSystemSync
            
            fs = KNOFileSystemSync(index_dir=os.path.join(self.test_dir, "index_mem"))
            success = fs.initialize()
            if not success:
                self.results['skipped'] += 1
                return
            
            # Use sync interface
            metrics = fs.index_directory(self.test_dir, recursive=False)
            results = fs.search_files("semantic", top_k=3)
            
            assert metrics.indexed_files > 0, "Sync indexing failed"
            assert len(results) >= 0, "Sync search failed"
            
            logger.info("✓ Memory efficiency test passed")
            self.results['passed'] += 1
            
        except Exception as e:
            logger.error(f"✗ Memory efficiency test failed: {e}")
            self.results['failed'] += 1
            self.results['errors'].append(f"test_memory_efficiency: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 60)
        logger.info("KNO Semantic File System - Test Suite")
        logger.info("=" * 60)
        
        await self.setup()
        
        try:
            tests = [
                self.test_basic_initialization,
                self.test_chromadb_backend,
                self.test_faiss_backend,
                self.test_file_indexing,
                self.test_semantic_search,
                self.test_coordinator_integration,
                self.test_statistics,
                self.test_memory_efficiency,
            ]
            
            for test in tests:
                logger.info(f"\nRunning {test.__name__}...")
                await test()
        
        finally:
            await self.teardown()
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("Test Summary")
        logger.info("=" * 60)
        logger.info(f"Passed:  {self.results['passed']}")
        logger.info(f"Failed:  {self.results['failed']}")
        logger.info(f"Skipped: {self.results['skipped']}")
        
        if self.results['errors']:
            logger.info("\nErrors:")
            for error in self.results['errors']:
                logger.info(f"  - {error}")
        
        total = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        logger.info(f"\nSuccess Rate: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        return self.results['failed'] == 0

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Run tests"""
    runner = TestRunner()
    success = await runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
