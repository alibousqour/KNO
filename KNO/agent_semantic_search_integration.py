"""
KNO Agent Semantic Search Integration
====================================

Integration module to connect semantic search with KNO agent and eDEX-UI.

يوفر:
- Async integration with KNO agent
- eDEX-UI progress visualization
- Search command interface
- Result caching
- Statistics tracking

Author: KNO Architecture
License: MIT
"""

import asyncio
import logging
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import threading

from semantic_search_advanced import (
    KNOSemanticSearch,
    SemanticSearchEngine,
    EDEXStatusManager,
    EDEXProgressData
)

logger = logging.getLogger('KNO.Agent.SemanticSearchIntegration')

# ============================================================================
# AGENT SEMANTIC SEARCH INTERFACE
# ============================================================================

class KNOAgentSemanticSearch:
    """
    Integration between KNO agent and semantic search system.
    Provides a simple interface for the agent to perform semantic searches.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(
        self,
        base_directory: str = ".",
        status_file: str = "edex_status.json"
    ):
        """
        Initialize the semantic search integration.
        
        Args:
            base_directory: Directory to index
            status_file: Path to eDEX status file
        """
        if self._initialized:
            return
        
        self.base_directory = base_directory
        self.status_file = status_file
        self.search_system = KNOSemanticSearch(
            base_directory=base_directory,
            status_file=status_file
        )
        self.search_cache = {}
        self.max_cache_size = 50
        self.last_search_results = []
        self._initialized = True
        
        logger.info("KNO Agent Semantic Search Integration initialized")
    
    # ====================================================================
    # MAIN SEARCH INTERFACE
    # ====================================================================
    
    async def search_files(
        self,
        query: str,
        max_results: int = 10,
        skip_cache: bool = False
    ) -> List[Dict[str, Any]]:
        """
        البحث عن ملفات بناءً على المعنى
        
        Search files semantically - find files by meaning, not just keywords.
        
        This is the main search interface for the agent.
        
        Args:
            query: Search query (e.g., "user authentication")
            max_results: Maximum results to return
            skip_cache: Skip the cache
        
        Returns:
            List of matching files with relevance scores
        
        Example:
            >>> agent_search = KNOAgentSemanticSearch()
            >>> await agent_search.initialize()
            >>> results = await agent_search.search_files("authentication logic")
            >>> for r in results:
            ...     print(f"{r['file_path']}: {r['relevance_score']}%")
        """
        
        # Check cache
        if not skip_cache and query in self.search_cache:
            logger.info(f"Returning cached results for: {query}")
            return self.search_cache[query]
        
        try:
            logger.info(f"Semantic search initiated: '{query}'")
            
            # Initialize if needed
            if not self.search_system.initialized:
                await self.search_system.initialize()
            
            # Perform search
            results = await self.search_system.search_files(query, max_results)
            
            # Cache results
            self._cache_results(query, results)
            
            # Store for later reference
            self.last_search_results = results
            
            logger.info(f"Search completed: found {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def index_directory(self, directory: str = None) -> bool:
        """
        فهرسة مجلد للبحث الدلالي
        
        Index a directory for semantic search.
        
        Args:
            directory: Directory to index (uses base_directory if None)
        
        Returns:
            bool: True if successful
        
        Example:
            >>> agent_search = KNOAgentSemanticSearch(base_directory="./src")
            >>> success = await agent_search.index_directory()
            >>> if success:
            ...     print("Directory indexed and ready for search!")
        """
        
        if directory:
            self.search_system.base_directory = directory
        
        try:
            logger.info(f"Indexing directory: {self.search_system.base_directory}")
            
            # Initialize if needed
            if not self.search_system.initialized:
                await self.search_system.initialize()
            
            success = await self.search_system.index_directory()
            
            if success:
                metrics = self.search_system.get_metrics()
                logger.info(
                    f"Indexing successful: {metrics['indexed_files']} files, "
                    f"{metrics['total_chunks']} chunks"
                )
            
            return success
        
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            return False
    
    async def initialize(self) -> bool:
        """
        Initialize the search system and load models.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Initializing search system...")
            success = await self.search_system.initialize()
            
            if success:
                logger.info("Search system initialized successfully")
            else:
                logger.error("Failed to initialize search system")
            
            return success
        
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    # ====================================================================
    # UTILITY METHODS
    # ====================================================================
    
    def _cache_results(self, query: str, results: List[Dict[str, Any]]):
        """Cache search results"""
        if len(self.search_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.search_cache))
            del self.search_cache[oldest_key]
        
        self.search_cache[query] = results
        logger.debug(f"Cached results for: {query}")
    
    def get_cached_results(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached results if available"""
        return self.search_cache.get(query)
    
    def clear_cache(self):
        """Clear the search cache"""
        self.search_cache.clear()
        logger.info("Search cache cleared")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        إحصائيات الفهرسة
        
        Get indexing statistics.
        
        Returns:
            Dictionary with metrics
        """
        return self.search_system.get_metrics()
    
    async def search_with_details(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search with detailed information about each match.
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            Dictionary with results and metadata
        """
        try:
            results = await self.search_files(query, max_results)
            
            return {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'result_count': len(results),
                'results': results,
                'metrics': self.get_metrics()
            }
        
        except Exception as e:
            logger.error(f"Search with details failed: {e}")
            return {
                'query': query,
                'error': str(e),
                'results': []
            }


# ============================================================================
# EDEX COMMAND HANDLER
# ============================================================================

class EDEXCommandHandler:
    """Handle semantic search commands from eDEX-UI"""
    
    def __init__(self):
        """Initialize command handler"""
        self.agent_search = KNOAgentSemanticSearch()
        self.edex_manager = EDEXStatusManager()
        self.command_log = []
    
    async def handle_search_command(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Handle search command from eDEX interface.
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            Command result
        """
        try:
            logger.info(f"eDEX search command: {query}")
            
            # Initialize if needed
            if not self.agent_search.search_system.initialized:
                await self.agent_search.initialize()
            
            # Perform search
            results = await self.agent_search.search_files(query, max_results)
            
            # Log command
            self.command_log.append({
                'timestamp': datetime.now().isoformat(),
                'command': 'search',
                'query': query,
                'result_count': len(results)
            })
            
            return {
                'success': True,
                'query': query,
                'results': results,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Command handling error: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    async def handle_index_command(
        self,
        directory: str = None
    ) -> Dict[str, Any]:
        """Handle indexing command from eDEX"""
        try:
            logger.info(f"eDEX index command: {directory or 'base'}")
            
            success = await self.agent_search.index_directory(directory)
            metrics = self.agent_search.get_metrics()
            
            return {
                'success': success,
                'directory': directory or 'base',
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Index command error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

async def search_files(
    query: str,
    directory: str = ".",
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """
    Convenience function for semantic file search.
    
    البحث السريع عن الملفات بالمعنى
    
    Usage:
        >>> results = await search_files("authentication logic", directory="./src")
        >>> for r in results:
        ...     print(f"{r['file_path']}: {r['relevance_score']}%")
    
    Args:
        query: Search query
        directory: Directory to search in
        max_results: Maximum results
    
    Returns:
        List of matching files
    """
    
    search = KNOAgentSemanticSearch(base_directory=directory)
    await search.initialize()
    return await search.search_files(query, max_results)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def demo():
    """Demo the semantic search system"""
    
    print("=" * 70)
    print("KNO Semantic Search Demo".center(70))
    print("=" * 70)
    
    # Initialize
    search = KNOAgentSemanticSearch(base_directory="./KNO")
    await search.initialize()
    
    # Index directory
    print("\n📁 Indexing directory...")
    await search.index_directory()
    
    # Show metrics
    metrics = search.get_metrics()
    print(f"\n📊 Indexing Metrics:")
    print(f"   Total Files: {metrics['total_files']}")
    print(f"   Indexed Files: {metrics['indexed_files']}")
    print(f"   Total Chunks: {metrics['total_chunks']}")
    print(f"   Time: {metrics['indexing_time_seconds']:.2f}s")
    
    # Search examples
    queries = [
        "user authentication and login",
        "error handling and exceptions",
        "database operations and queries",
        "configuration settings",
        "websocket communication"
    ]
    
    for query in queries:
        print(f"\n🔍 Searching: '{query}'")
        print("-" * 70)
        
        results = await search.search_files(query, max_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n  {i}. File: {result['file_path']}")
                print(f"     Relevance: {result['relevance_score']}%")
                print(f"     Content: {result['summary'][:60]}...")
        else:
            print("   No results found")


if __name__ == "__main__":
    asyncio.run(demo())
