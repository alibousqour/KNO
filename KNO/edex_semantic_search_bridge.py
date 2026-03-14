"""
eDEX-UI Semantic Search Bridge
==============================

Integrates KNO Semantic File System with eDEX-UI for visual progress tracking.
Provides async semantic search with real-time progress updates to the eDEX interface.

Features:
- Async semantic file search by meaning (not keywords)
- Real-time progress bar updates to eDEX-UI
- Status broadcasting via edex_status.json
- Search result caching and ranking
- Integration with semantic_file_system_enhanced.py

Author: KNO Architecture
License: MIT
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict

# Try to import semantic file system
try:
    from semantic_file_system_enhanced import (
        KNOFileSystem, SearchResult, IndexingMetrics
    )
    HAS_SEMANTIC_FS = True
except ImportError:
    HAS_SEMANTIC_FS = False
    logging.warning("semantic_file_system_enhanced not available - using fallback")

logger = logging.getLogger('KNO.SemanticSearchBridge')

# ============================================================================
# EDEX STATUS UPDATES
# ============================================================================

@dataclass
class EDEXProgress:
    """Progress information for eDEX-UI display"""
    operation: str  # search, indexing, etc.
    current: int    # Current progress
    total: int      # Total items
    percentage: float  # 0-100
    status: str     # Brief status message
    timestamp: str  # ISO timestamp
    elapsed_time: float  # Seconds elapsed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'operation': self.operation,
            'current': self.current,
            'total': self.total,
            'percentage': round(self.percentage, 2),
            'status': self.status,
            'timestamp': self.timestamp,
            'elapsed_seconds': round(self.elapsed_time, 2)
        }


class EDEXStatusBroadcaster:
    """Broadcasts search progress to eDEX-UI via JSON status file"""
    
    def __init__(self, status_file: str = "edex_status.json"):
        """
        Initialize status broadcaster.
        
        Args:
            status_file: Path to eDEX status file
        """
        self.status_file = status_file
        self.ensure_directory()
    
    def ensure_directory(self):
        """Ensure status file directory exists"""
        status_dir = os.path.dirname(self.status_file)
        if status_dir:
            os.makedirs(status_dir, exist_ok=True)
    
    def update_progress(self, progress: EDEXProgress):
        """
        Update eDEX-UI with progress information.
        
        Args:
            progress: EDEXProgress object with current status
        """
        try:
            status_data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'progress': progress.to_dict(),
                'ui_elements': {
                    'progress_bar': {
                        'visible': True,
                        'percentage': progress.percentage,
                        'label': progress.status,
                        'color': self._get_progress_color(progress.percentage)
                    },
                    'status_text': {
                        'primary': progress.status,
                        'secondary': f"{progress.current}/{progress.total} items",
                        'operation': progress.operation
                    }
                }
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            logger.debug(f"Updated eDEX status: {progress.status}")
        except Exception as e:
            logger.error(f"Failed to update eDEX status: {e}")
    
    @staticmethod
    def _get_progress_color(percentage: float) -> str:
        """Get color based on progress percentage"""
        if percentage < 33:
            return "#FF4444"  # Red
        elif percentage < 66:
            return "#FFAA44"  # Orange
        elif percentage < 90:
            return "#FFDD44"  # Yellow
        else:
            return "#44FF44"  # Green
    
    def clear_progress(self):
        """Clear progress from eDEX-UI"""
        try:
            status_data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'progress': None,
                'ui_elements': {
                    'progress_bar': {
                        'visible': False
                    }
                }
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            
            logger.info("Cleared eDEX progress display")
        except Exception as e:
            logger.error(f"Failed to clear eDEX status: {e}")


# ============================================================================
# SEMANTIC SEARCH WITH EDEX INTEGRATION
# ============================================================================

class SemanticSearchWithEDEX:
    """
    Semantic file search system with eDEX-UI integration.
    
    Provides async semantic search by meaning with real-time progress updates.
    """
    
    def __init__(
        self,
        sfs: Optional[KNOFileSystem] = None,
        status_file: str = "edex_status.json"
    ):
        """
        Initialize semantic search with eDEX integration.
        
        Args:
            sfs: KNOFileSystem instance (creates new if None)
            status_file: Path to eDEX status file
        """
        self.sfs = sfs
        self.status_broadcaster = EDEXStatusBroadcaster(status_file)
        self.search_cache = {}  # Cache search results
        self.max_cache_size = 100
        self.initialized = False
        self.start_time = None
    
    async def initialize(self) -> bool:
        """
        Initialize semantic file system and load models.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            if not HAS_SEMANTIC_FS:
                logger.error("Semantic file system not available")
                return False
            
            if self.sfs is None:
                logger.info("Initializing KNOFileSystem...")
                self.sfs = KNOFileSystem()
            
            success = await self.sfs.initialize()
            self.initialized = success
            
            if success:
                logger.info("Semantic search system initialized successfully")
                self.status_broadcaster.clear_progress()
            else:
                logger.error("Failed to initialize semantic search system")
            
            return success
        
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    async def search_files(
        self,
        query: str,
        limit: int = 10,
        show_progress: bool = True
    ) -> List[SearchResult]:
        """
        Search for files by meaning (semantic search).
        
        This function searches your codebase not by keyword matching,
        but by understanding the MEANING of your query, finding files
        that are related semantically.
        
        Args:
            query: Search query (e.g., "authentication logic" or "database queries")
            limit: Maximum results to return (default 10)
            show_progress: Show progress in eDEX-UI
        
        Returns:
            List of SearchResult objects with relevance scores
        
        Example:
            >>> results = await bridge.search_files("user authentication")
            >>> for result in results:
            ...     print(f"{result.file_path}: {result.relevance_score:.2f}")
        """
        
        if not self.initialized or not self.sfs:
            logger.error("Search system not initialized. Call initialize() first.")
            return []
        
        self.start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = f"{query}:{limit}"
            if cache_key in self.search_cache:
                logger.info(f"Returning cached results for: {query}")
                return self.search_cache[cache_key]
            
            # Update progress - searching
            if show_progress:
                progress = EDEXProgress(
                    operation="semantic_search",
                    current=0,
                    total=100,
                    percentage=5,
                    status=f"🔍 Searching: {query[:50]}...",
                    timestamp=datetime.now().isoformat(),
                    elapsed_time=(datetime.now() - self.start_time).total_seconds()
                )
                self.status_broadcaster.update_progress(progress)
            
            # Perform semantic search
            logger.info(f"Performing semantic search: {query}")
            results = await self.sfs.search_files(
                query=query,
                limit=limit,
                min_relevance_score=0.3  # Only include reasonably relevant results
            )
            
            # Update progress - processing results
            if show_progress:
                progress = EDEXProgress(
                    operation="semantic_search",
                    current=50,
                    total=100,
                    percentage=75,
                    status=f"📊 Processing {len(results)} results...",
                    timestamp=datetime.now().isoformat(),
                    elapsed_time=(datetime.now() - self.start_time).total_seconds()
                )
                self.status_broadcaster.update_progress(progress)
            
            # Sort by relevance and rank
            ranked_results = self._rank_results(results)
            
            # Cache results
            self._cache_results(cache_key, ranked_results)
            
            # Update progress - complete
            if show_progress:
                progress = EDEXProgress(
                    operation="semantic_search",
                    current=100,
                    total=100,
                    percentage=100,
                    status=f"✅ Found {len(ranked_results)} relevant files",
                    timestamp=datetime.now().isoformat(),
                    elapsed_time=(datetime.now() - self.start_time).total_seconds()
                )
                self.status_broadcaster.update_progress(progress)
                
                # Clear progress after 2 seconds
                await asyncio.sleep(2)
                self.status_broadcaster.clear_progress()
            
            logger.info(f"Semantic search completed: found {len(ranked_results)} results")
            return ranked_results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.status_broadcaster.clear_progress()
            return []
    
    async def index_directory(
        self,
        directory: str,
        show_progress: bool = True
    ) -> bool:
        """
        Index a directory with semantic search and eDEX progress tracking.
        
        Args:
            directory: Path to directory to index
            show_progress: Show progress in eDEX-UI
        
        Returns:
            bool: True if indexing successful
        
        Example:
            >>> success = await bridge.index_directory("./my_code")
            >>> if success:
            ...     print("Directory indexed successfully!")
        """
        
        if not self.initialized or not self.sfs:
            logger.error("Search system not initialized. Call initialize() first.")
            return False
        
        self.start_time = datetime.now()
        
        try:
            def progress_callback(progress_info: Dict[str, Any]):
                """Callback for indexing progress"""
                if show_progress:
                    indexed = progress_info.get('indexed_files', 0)
                    total = progress_info.get('total_files', 1)
                    percentage = (indexed / max(total, 1)) * 100
                    
                    progress = EDEXProgress(
                        operation="directory_indexing",
                        current=indexed,
                        total=total,
                        percentage=percentage,
                        status=f"📂 Indexing: {os.path.basename(directory)}",
                        timestamp=datetime.now().isoformat(),
                        elapsed_time=(datetime.now() - self.start_time).total_seconds()
                    )
                    self.status_broadcaster.update_progress(progress)
            
            logger.info(f"Starting directory indexing: {directory}")
            
            # Index directory
            indexed_files = await self.sfs.index_directory(
                directory=directory,
                progress_callback=progress_callback
            )
            
            # Final progress update
            if show_progress:
                stats = self.sfs.get_statistics()
                progress = EDEXProgress(
                    operation="directory_indexing",
                    current=stats.indexed_files,
                    total=stats.indexed_files,
                    percentage=100,
                    status=f"✅ Indexed {stats.indexed_files} files",
                    timestamp=datetime.now().isoformat(),
                    elapsed_time=(datetime.now() - self.start_time).total_seconds()
                )
                self.status_broadcaster.update_progress(progress)
                
                # Clear progress after 2 seconds
                await asyncio.sleep(2)
                self.status_broadcaster.clear_progress()
            
            logger.info(f"Directory indexing complete: {len(indexed_files)} files indexed")
            return True
        
        except Exception as e:
            logger.error(f"Directory indexing error: {e}")
            self.status_broadcaster.clear_progress()
            return False
    
    @staticmethod
    def _rank_results(results: List[SearchResult]) -> List[SearchResult]:
        """
        Rank search results by relevance and other factors.
        
        Args:
            results: List of search results
        
        Returns:
            Ranked list of results
        """
        # Sort by relevance score (descending)
        return sorted(results, key=lambda r: r.relevance_score, reverse=True)
    
    def _cache_results(self, key: str, results: List[SearchResult]):
        """
        Cache search results with LRU eviction.
        
        Args:
            key: Cache key
            results: Results to cache
        """
        self.search_cache[key] = results
        
        # Evict oldest if cache too large
        if len(self.search_cache) > self.max_cache_size:
            oldest_key = next(iter(self.search_cache))
            del self.search_cache[oldest_key]
    
    def get_statistics(self) -> Optional[IndexingMetrics]:
        """
        Get indexing statistics.
        
        Returns:
            IndexingMetrics object or None if not initialized
        """
        if self.sfs:
            return self.sfs.get_statistics()
        return None
    
    def clear_cache(self):
        """Clear search result cache"""
        self.search_cache.clear()
        logger.info("Search cache cleared")


# ============================================================================
# UTILITY FUNCTIONS FOR EASY INTEGRATION
# ============================================================================

class SemanticSearchAPI:
    """
    High-level API for semantic search with eDEX integration.
    
    Singleton-style access to semantic search functionality.
    """
    
    _instance = None
    
    def __init__(self):
        self.bridge = None
    
    async def initialize(
        self,
        sfs: Optional[KNOFileSystem] = None,
        status_file: str = "edex_status.json"
    ) -> bool:
        """
        Initialize the semantic search API.
        
        Args:
            sfs: Optional KNOFileSystem instance
            status_file: Path to eDEX status file
        
        Returns:
            bool: True if initialization successful
        """
        self.bridge = SemanticSearchWithEDEX(sfs, status_file)
        return await self.bridge.initialize()
    
    async def search(
        self,
        query: str,
        limit: int = 10,
        show_edex_progress: bool = True
    ) -> List[SearchResult]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            limit: Maximum results
            show_edex_progress: Show progress in eDEX-UI
        
        Returns:
            List of search results
        """
        if not self.bridge:
            logger.error("API not initialized. Call initialize() first.")
            return []
        
        return await self.bridge.search_files(
            query=query,
            limit=limit,
            show_progress=show_edex_progress
        )
    
    @classmethod
    def get_instance(cls) -> 'SemanticSearchAPI':
        """Get or create singleton instance"""
        if cls._instance is None:
            cls._instance = SemanticSearchAPI()
        return cls._instance


# ============================================================================
# QUICK START EXAMPLE
# ============================================================================

async def example_usage():
    """Example of using semantic search with eDEX integration"""
    
    # Initialize
    api = SemanticSearchAPI.get_instance()
    success = await api.initialize(status_file="edex_status.json")
    
    if not success:
        print("Failed to initialize semantic search")
        return
    
    # Index a directory (with progress in eDEX)
    print("Indexing directory...")
    success = await api.bridge.index_directory(
        "./your_code_directory",
        show_progress=True
    )
    
    if not success:
        print("Failed to index directory")
        return
    
    # Perform searches with results showing in eDEX
    queries = [
        "user authentication and login",
        "database queries and models",
        "error handling and exceptions"
    ]
    
    for query in queries:
        print(f"\nSearching for: {query}")
        results = await api.search(query, limit=5)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.file_path} (Score: {result.relevance_score:.2f})")
            print(f"   {result.content_excerpt[:100]}...")


# ============================================================================
# STANDALONE RUNNER
# ============================================================================

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] %(message)s'
    )
    
    # Run example
    print("=" * 70)
    print("KNO Semantic Search with eDEX-UI Integration")
    print("=" * 70)
    
    try:
        asyncio.run(example_usage())
    except KeyboardInterrupt:
        print("\n\nSearch interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
