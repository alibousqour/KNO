"""
KNO Agent Integration with Semantic Search & eDEX-UI
====================================================

This module integrates semantic file search directly into the KNO agent,
allowing it to search your codebase by meaning through the eDEX-UI interface.

Features:
- Async semantic search integrated with KNO agent
- Real-time progress updates to eDEX-UI
- Automatic index management
- Search result caching for performance

Author: KNO Architecture
License: MIT
"""

import asyncio
import logging
import json
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

# Import semantic search bridge
try:
    from edex_semantic_search_bridge import (
        SemanticSearchWithEDEX,
        SemanticSearchAPI,
        EDEXStatusBroadcaster
    )
    HAS_EDEX_BRIDGE = True
except ImportError as e:
    HAS_EDEX_BRIDGE = False
    logging.warning(f"eDEX bridge not available: {e}")

logger = logging.getLogger('KNO.Agent.SemanticSearch')


class KNOSemanticAgent:
    """
    KNO Agent with integrated semantic file search and eDEX-UI visualization.
    
    This agent can search your entire codebase by meaning, not just keywords,
    and display progress in the eDEX-UI interface.
    """
    
    def __init__(self, edex_status_file: str = "edex_status.json"):
        """
        Initialize KNO semantic search agent.
        
        Args:
            edex_status_file: Path to eDEX status file
        """
        self.edex_status_file = edex_status_file
        self.search_api = SemanticSearchAPI.get_instance()
        self.initialized = False
        self.last_search_results = []
    
    async def initialize(self) -> bool:
        """
        Initialize the semantic search system.
        
        Returns:
            bool: True if initialization successful
        """
        try:
            logger.info("Initializing KNO Semantic Agent...")
            
            success = await self.search_api.initialize(
                status_file=self.edex_status_file
            )
            
            if success:
                self.initialized = True
                logger.info("KNO Semantic Agent initialized successfully")
            else:
                logger.error("Failed to initialize KNO Semantic Agent")
            
            return success
        
        except Exception as e:
            logger.error(f"Initialization error: {e}")
            return False
    
    # ====================================================================
    # MAIN SEMANTIC SEARCH METHODS
    # ====================================================================
    
    async def search_files(
        self,
        query: str,
        limit: int = 10,
        show_edex_progress: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search codebase by MEANING (semantic search).
        
        Instead of keyword matching, this searches for files related to the
        MEANING of your query. For example:
        - "How do I authenticate users?" → finds authentication code
        - "Database operations" → finds database query files
        - "Error handling" → finds error/exception handling code
        
        Args:
            query: Your search query (natural language)
            limit: Maximum number of results (default 10)
            show_edex_progress: Show progress bar in eDEX-UI (default True)
        
        Returns:
            List of search results with file info and relevance scores
        
        Example:
            >>> results = await agent.search_files("user authentication")
            >>> for r in results:
            ...     print(f"{r['file_path']}: {r['relevance_score']:.2f}")
        """
        
        if not self.initialized:
            logger.error("Agent not initialized. Call initialize() first.")
            return []
        
        try:
            logger.info(f"Semantic search initiated: {query}")
            
            # Perform search
            search_results = await self.search_api.search(
                query=query,
                limit=limit,
                show_edex_progress=show_edex_progress
            )
            
            # Store results
            self.last_search_results = search_results
            
            # Convert to dict format for easier use
            result_list = [
                {
                    'file_path': str(result.file_path),
                    'file_type': result.file_type,
                    'relevance_score': result.relevance_score,
                    'rank': i + 1,
                    'content_excerpt': result.content_excerpt,
                    'keywords': result.keywords,
                    'chunk_index': result.chunk_index
                }
                for i, result in enumerate(search_results)
            ]
            
            logger.info(f"Search complete: found {len(result_list)} results")
            return result_list
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def index_directory_with_progress(
        self,
        directory: str,
        show_edex_progress: bool = True
    ) -> bool:
        """
        Index a directory for semantic search with eDEX progress visualization.
        
        This processes all files in the directory and prepares them for
        semantic search. Progress is shown in the eDEX-UI.
        
        Args:
            directory: Path to directory to index
            show_edex_progress: Show progress in eDEX-UI
        
        Returns:
            bool: True if indexing successful
        
        Example:
            >>> success = await agent.index_directory_with_progress("./src")
            >>> if success:
            ...     print("Directory indexed and ready for search!")
        """
        
        if not self.initialized:
            logger.error("Agent not initialized. Call initialize() first.")
            return False
        
        try:
            logger.info(f"Starting directory indexing: {directory}")
            
            success = await self.search_api.bridge.index_directory(
                directory=directory,
                show_progress=show_edex_progress
            )
            
            if success:
                stats = self.search_api.bridge.get_statistics()
                logger.info(
                    f"Directory indexed successfully: "
                    f"{stats.indexed_files} files, "
                    f"{stats.total_chunks} chunks"
                )
            else:
                logger.error("Directory indexing failed")
            
            return success
        
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            return False
    
    # ====================================================================
    # ADVANCED SEARCH METHODS
    # ====================================================================
    
    async def search_with_ranking(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search with advanced relevance ranking.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            Ranked list of results
        """
        results = await self.search_files(query, limit, show_edex_progress=False)
        
        # Additional ranking by relevance
        return sorted(
            results,
            key=lambda x: x['relevance_score'],
            reverse=True
        )
    
    async def search_by_file_type(
        self,
        query: str,
        file_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search files of a specific type.
        
        Args:
            query: Search query
            file_type: File type to search (code, document, config, etc.)
            limit: Maximum results
        
        Returns:
            Results filtered by file type
        """
        results = await self.search_files(query, limit, show_edex_progress=False)
        
        # Filter by file type
        return [r for r in results if r['file_type'] == file_type]
    
    async def multi_query_search(
        self,
        queries: List[str],
        limit: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform multiple searches at once.
        
        Args:
            queries: List of search queries
            limit: Results per query
        
        Returns:
            Dictionary mapping queries to results
        """
        results = {}
        
        for query in queries:
            results[query] = await self.search_files(
                query,
                limit,
                show_edex_progress=False
            )
        
        return results
    
    # ====================================================================
    # UTILITY METHODS
    # ====================================================================
    
    def get_search_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get statistics about indexed files.
        
        Returns:
            Statistics dictionary or None if not available
        """
        if not self.search_api.bridge:
            return None
        
        stats = self.search_api.bridge.get_statistics()
        
        if stats:
            return {
                'indexed_files': stats.indexed_files,
                'total_files': stats.total_files,
                'failed_files': stats.failed_files,
                'total_chunks': stats.total_chunks,
                'total_size_mb': stats.total_size_mb,
                'indexing_time_seconds': stats.indexing_time
            }
        
        return None
    
    def get_last_search_results(self) -> List[Dict[str, Any]]:
        """
        Get results from last search.
        
        Returns:
            Results from previous search
        """
        return [
            {
                'file_path': str(result.file_path),
                'relevance_score': result.relevance_score,
                'content_excerpt': result.content_excerpt
            }
            for result in self.last_search_results
        ]
    
    def clear_search_cache(self):
        """Clear cached search results"""
        if self.search_api.bridge:
            self.search_api.bridge.clear_cache()
            logger.info("Search cache cleared")
    
    def get_edex_status_file(self) -> str:
        """Get path to eDEX status file"""
        return self.edex_status_file


# ====================================================================
# INTEGRATION EXAMPLE FOR agent.py
# ====================================================================

class AgentSemanticSearchExtension:
    """
    Extension module to add to existing KNO agent.
    
    Add this to your agent class:
    
    ```python
    class KNOAgent:
        def __init__(self):
            # ... existing init code ...
            self.semantic_agent = AgentSemanticSearchExtension()
        
        async def initialize(self):
            # ... existing code ...
            await self.semantic_agent.initialize()
        
        async def search_codebase(self, query):
            return await self.semantic_agent.search(query)
    ```
    """
    
    def __init__(self, edex_status_file: str = "edex_status.json"):
        """Initialize extension"""
        self.agent = KNOSemanticAgent(edex_status_file)
    
    async def initialize(self) -> bool:
        """Initialize the extension"""
        return await self.agent.initialize()
    
    async def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform semantic search"""
        return await self.agent.search_files(query, limit)
    
    async def index_directory(self, directory: str) -> bool:
        """Index a directory"""
        return await self.agent.index_directory_with_progress(directory)
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Get indexing statistics"""
        return self.agent.get_search_statistics()


# ====================================================================
# USAGE EXAMPLES
# ====================================================================

async def example_basic_search():
    """Example 1: Basic semantic search"""
    print("=" * 70)
    print("Example 1: Basic Semantic Search")
    print("=" * 70)
    
    agent = KNOSemanticAgent()
    await agent.initialize()
    
    # Search for authentication-related files
    results = await agent.search_files(
        "user authentication and login",
        limit=5
    )
    
    print(f"\nFound {len(results)} relevant files:")
    for result in results:
        print(
            f"  📄 {result['file_path']}\n"
            f"     Relevance: {result['relevance_score']:.2f}\n"
            f"     Preview: {result['content_excerpt'][:80]}...\n"
        )


async def example_index_and_search():
    """Example 2: Index directory then search"""
    print("=" * 70)
    print("Example 2: Index Directory and Search")
    print("=" * 70)
    
    agent = KNOSemanticAgent()
    await agent.initialize()
    
    # Index the code directory
    print("\n📂 Indexing code directory...")
    success = await agent.index_directory_with_progress("./src")
    
    if success:
        # Get statistics
        stats = agent.get_search_statistics()
        print(f"\n✅ Indexed successfully:")
        print(f"   - Files: {stats['indexed_files']}")
        print(f"   - Chunks: {stats['total_chunks']}")
        print(f"   - Size: {stats['total_size_mb']:.2f} MB")
        
        # Now search
        print("\n🔍 Searching...")
        results = await agent.search_files("database operations", limit=5)
        
        for result in results:
            print(f"  • {result['file_path']} ({result['relevance_score']:.2f})")


async def example_multiple_searches():
    """Example 3: Multiple semantic searches"""
    print("=" * 70)
    print("Example 3: Multiple Semantic Searches")
    print("=" * 70)
    
    agent = KNOSemanticAgent()
    await agent.initialize()
    
    queries = [
        "error handling and exceptions",
        "configuration management",
        "logging and monitoring",
        "testing and validation"
    ]
    
    results = await agent.multi_query_search(queries, limit=3)
    
    for query, matches in results.items():
        print(f"\n📌 {query}")
        for match in matches:
            print(f"   ✓ {match['file_path']} ({match['relevance_score']:.2f})")


# ====================================================================
# STANDALONE RUNNER
# ====================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] %(levelname)s: %(message)s'
    )
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║   KNO Semantic Search Agent - eDEX-UI Integration Examples           ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Run examples
        asyncio.run(example_basic_search())
        
        # Uncomment to run other examples:
        # asyncio.run(example_index_and_search())
        # asyncio.run(example_multiple_searches())
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
