"""
Secure Semantic Search Engine with Security Integration
========================================================

نسخة محسّنة من محرك البحث الدلالي مع تكامل الأمان

Extends the base semantic search engine with integrated security filtering
and audit capabilities.

Author: KNO Architecture
License: MIT
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import os

try:
    from semantic_search_advanced import (
        SemanticSearchEngine,
        SearchResult,
        FileAnalyzer as BaseFileAnalyzer,
        EDEXStatusManager,
        EDEXProgressData
    )
    from security_filter import IgnoreListManager, SecureFileAnalyzer
    HAS_BASE = True
except ImportError:
    HAS_BASE = False

logger = logging.getLogger('KNO.SecureSemanticSearch')

# ============================================================================
# SECURE FILE ANALYZER
# ============================================================================

class SecureFileAnalyzerEnhanced(BaseFileAnalyzer if HAS_BASE else object):
    """
    محلل ملفات محسّن مع الأمان
    
    Enhanced file analyzer with integrated security filtering.
    """
    
    def __init__(self, ignore_manager: Optional[IgnoreListManager] = None):
        """Initialize secure analyzer"""
        if HAS_BASE:
            super().__init__()
        self.ignore_manager = ignore_manager
    
    def should_include_file_secure(
        self,
        file_path: str,
        ignore_manager: IgnoreListManager = None
    ) -> bool:
        """
        Check if file should be included with security filtering.
        
        Args:
            file_path: Path to check
            ignore_manager: Optional ignore manager (uses instance if None)
        
        Returns:
            bool: True if file should be included
        """
        # Use provided manager or instance manager
        manager = ignore_manager or self.ignore_manager
        
        if manager:
            # Use security filter first
            if not manager.should_include_file(file_path):
                return False
        
        # Then use base analyzer
        if HAS_BASE:
            return super().should_include_file(file_path)
        
        return True


# ============================================================================
# SECURE SEMANTIC SEARCH ENGINE
# ============================================================================

class SecureSemanticSearchEngine:
    """
    محرك البحث الدلالي الآمن
    
    Semantic search engine with integrated security filtering.
    """
    
    def __init__(
        self,
        base_engine: Optional[SemanticSearchEngine] = None,
        ignore_manager: Optional[IgnoreListManager] = None,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize secure search engine.
        
        Args:
            base_engine: Underlying search engine (creates new if None)
            ignore_manager: Security filter manager
            model_name: Model name for embeddings
        """
        if HAS_BASE:
            self.engine = base_engine or SemanticSearchEngine(model_name)
        else:
            self.engine = None
        
        self.ignore_manager = ignore_manager
        self.secure_analyzer = SecureFileAnalyzerEnhanced(ignore_manager)
        self.security_audit = {
            'total_files_scanned': 0,
            'files_filtered': 0,
            'restricted_files_blocked': 0,
            'suspicious_patterns': []
        }
    
    async def initialize(self) -> bool:
        """Initialize the engine"""
        if not HAS_BASE or not self.engine:
            logger.error("Base engine not available")
            return False
        
        try:
            success = await self.engine.initialize()
            if success:
                logger.info("Secure semantic search engine initialized")
            return success
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    async def index_directory_secure(
        self,
        directory: str,
        progress_callback: Optional[callable] = None,
        verbose_security: bool = False
    ) -> bool:
        """
        فهرسة آمنة للمجلد
        
        Securely index a directory with security filtering.
        
        Args:
            directory: Directory to index
            progress_callback: Optional callback
            verbose_security: Log security details
        
        Returns:
            bool: True if successful
        """
        
        if not HAS_BASE or not self.engine:
            logger.error("Search engine not initialized")
            return False
        
        try:
            logger.info(f"Starting secure indexing: {directory}")
            
            # Collect files with security filtering
            files_to_index = []
            self.security_audit['total_files_scanned'] = 0
            self.security_audit['files_filtered'] = 0
            self.security_audit['restricted_files_blocked'] = 0
            
            for root, dirs, files in os.walk(directory):
                # Filter directories first
                if self.ignore_manager:
                    dirs[:] = [
                        d for d in dirs
                        if self.ignore_manager.should_include_file(
                            os.path.join(root, d)
                        )
                    ]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    self.security_audit['total_files_scanned'] += 1
                    
                    # Check security filter
                    if self.ignore_manager:
                        filter_result = self.ignore_manager.should_ignore_file(
                            file_path,
                            reason_output=True
                        )
                        
                        if filter_result['ignored']:
                            self.security_audit['files_filtered'] += 1
                            
                            if filter_result['sensitivity'] == 'restricted':
                                self.security_audit['restricted_files_blocked'] += 1
                                
                                if verbose_security:
                                    logger.warning(
                                        f"Blocked restricted file: {file_path} "
                                        f"({filter_result['reason']})"
                                    )
                            continue
                    
                    # Check file analyzer
                    if BaseFileAnalyzer.should_include_file(file_path):
                        files_to_index.append(file_path)
            
            logger.info(
                f"Security filter results: "
                f"scanned={self.security_audit['total_files_scanned']}, "
                f"filtered={self.security_audit['files_filtered']}, "
                f"restricted_blocked={self.security_audit['restricted_files_blocked']}, "
                f"to_index={len(files_to_index)}"
            )
            
            # Index the filtered files
            success = await self.engine.index_directory(directory)
            
            if success:
                logger.info("Secure indexing completed successfully")
            
            return success
        
        except Exception as e:
            logger.error(f"Secure indexing error: {e}")
            return False
    
    async def search_files_secure(
        self,
        query: str,
        max_results: int = 10,
        min_relevance: float = 0.3,
        verify_results: bool = True
    ) -> List[SearchResult]:
        """
        آمن البحث عن الملفات
        
        Securely search for files with result verification.
        
        Args:
            query: Search query
            max_results: Maximum results
            min_relevance: Minimum relevance
            verify_results: Verify results are not restricted
        
        Returns:
            List of search results
        """
        
        if not HAS_BASE or not self.engine:
            logger.error("Search engine not initialized")
            return []
        
        try:
            # Perform search
            results = await self.engine.search_files(
                query,
                max_results,
                min_relevance
            )
            
            # Verify results are not restricted
            if verify_results and self.ignore_manager:
                verified_results = []
                
                for result in results:
                    filter_result = self.ignore_manager.should_ignore_file(
                        result.file_path,
                        reason_output=True
                    )
                    
                    if not filter_result['ignored']:
                        verified_results.append(result)
                    else:
                        logger.warning(
                            f"Filtered restricted result: {result.file_path}"
                        )
                        self.security_audit['restricted_files_blocked'] += 1
                
                return verified_results
            
            return results
        
        except Exception as e:
            logger.error(f"Secure search error: {e}")
            return []
    
    def get_security_audit(self) -> Dict[str, Any]:
        """Get security audit information"""
        return self.security_audit.copy()
    
    def get_ignore_summary(self) -> Dict[str, Any]:
        """Get ignore list summary"""
        if not self.ignore_manager:
            return {}
        
        return self.ignore_manager.get_rules_summary()
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get overall security status"""
        return {
            'ignore_manager': self.ignore_manager is not None,
            'audit': self.get_security_audit(),
            'ignore_summary': self.get_ignore_summary(),
            'engine_initialized': self.engine.initialized if self.engine else False
        }


# ============================================================================
# INTEGRATED SECURE SEARCH SYSTEM
# ============================================================================

class SecureKNOSemanticSearch:
    """
    نظام البحث الدلالي الآمن المتكامل
    
    Complete integrated secure semantic search system.
    """
    
    def __init__(
        self,
        base_directory: str = ".",
        status_file: str = "edex_status.json",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize secure search system.
        
        Args:
            base_directory: Base directory to search
            status_file: eDEX status file path
            model_name: Embedding model
        """
        self.base_directory = base_directory
        self.status_file = status_file
        
        # Initialize components
        self.ignore_manager = IgnoreListManager(base_directory)
        
        if HAS_BASE:
            base_engine = SemanticSearchEngine(model_name)
            self.search_engine = SecureSemanticSearchEngine(
                base_engine=base_engine,
                ignore_manager=self.ignore_manager,
                model_name=model_name
            )
        else:
            self.search_engine = None
        
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the system"""
        if not HAS_BASE or not self.search_engine:
            logger.error("Components not available")
            return False
        
        try:
            success = await self.search_engine.initialize()
            self.initialized = success
            return success
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    async def index_directory(
        self,
        directory: str = None,
        verbose: bool = False
    ) -> bool:
        """
        Index directory with security.
        
        Args:
            directory: Directory to index (uses base if None)
            verbose: Verbose security logging
        
        Returns:
            bool: True if successful
        """
        if not self.initialized:
            logger.warning("System not initialized, initializing...")
            await self.initialize()
        
        index_dir = directory or self.base_directory
        
        return await self.search_engine.index_directory_secure(
            index_dir,
            verbose_security=verbose
        )
    
    async def search(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search semantically with security.
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            List of results
        """
        if not self.initialized:
            logger.error("System not initialized")
            return []
        
        results = await self.search_engine.search_files_secure(
            query,
            max_results
        )
        
        return [
            {
                'file_path': r.file_path,
                'file_type': r.file_type,
                'relevance_score': r.relevance_score,
                'summary': r.summary,
                'keywords': r.keywords
            }
            for r in results
        ]
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        return {
            'ignore_rules': self.ignore_manager.get_rules_summary(),
            'security_audit': self.search_engine.get_security_audit() if self.search_engine else {},
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def demo_secure_search():
    """Demonstrate secure search"""
    
    print("\n" + "=" * 70)
    print("Secure Semantic Search Demo".center(70))
    print("=" * 70)
    
    # Initialize
    search = SecureKNOSemanticSearch(base_directory="./KNO")
    
    print("\n🔒 Security Report:")
    report = search.get_security_report()
    print(f"   Ignore Rules: {report['ignore_rules']['total_rules']}")
    
    print("\n📁 Indexing with security...")
    await search.initialize()
    await search.index_directory(verbose=True)
    
    print("\n🔍 Searching...")
    results = await search.search("user authentication", max_results=5)
    
    print(f"   Results: {len(results)}")
    for r in results[:3]:
        print(f"   - {r['file_path']} ({r['relevance_score']}%)")
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    if HAS_BASE:
        asyncio.run(demo_secure_search())
    else:
        print("Base semantic search module not available")
