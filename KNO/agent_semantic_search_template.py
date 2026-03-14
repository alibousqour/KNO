"""
KNO Agent - Semantic Search Integration Template
===============================================

This file shows how to integrate semantic search into the main KNO agent.

نموذج تكامل البحث الدلالي مع وكيل KNO

Author: KNO Architecture
License: MIT
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional

# Import semantic search components
try:
    from agent_semantic_search_integration import (
        KNOAgentSemanticSearch,
        EDEXCommandHandler
    )
    HAS_SEMANTIC_SEARCH = True
except ImportError:
    HAS_SEMANTIC_SEARCH = False
    logging.warning("Semantic search not available")

logger = logging.getLogger('KNO.Agent.SemanticIntegration')


# ============================================================================
# SEMANTIC SEARCH COMMANDS
# ============================================================================

class KNOSemanticSearchCommands:
    """
    Semantic search command interface for KNO agent.
    
    Provides methods to integrate semantic search into agent conversations.
    """
    
    def __init__(self, base_directory: str = "./KNO"):
        """
        Initialize semantic search commands.
        
        Args:
            base_directory: Directory to index
        """
        if not HAS_SEMANTIC_SEARCH:
            self.search = None
            logger.warning("Semantic search disabled")
            return
        
        self.search = KNOAgentSemanticSearch(
            base_directory=base_directory,
            status_file="edex_status.json"
        )
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize semantic search system"""
        if not HAS_SEMANTIC_SEARCH or not self.search:
            return False
        
        try:
            await self.search.initialize()
            self.initialized = True
            logger.info("Semantic search initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize semantic search: {e}")
            return False
    
    async def index_directory(self) -> bool:
        """Index directory for semantic search"""
        if not self.initialized:
            logger.error("Semantic search not initialized")
            return False
        
        try:
            logger.info("Starting directory indexing...")
            success = await self.search.index_directory()
            
            if success:
                metrics = self.search.get_metrics()
                logger.info(
                    f"Indexing complete: {metrics['indexed_files']} files, "
                    f"{metrics['total_chunks']} chunks"
                )
            
            return success
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            return False
    
    async def search_files(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        البحث عن ملفات بناءً على المعنى
        
        Search files semantically.
        
        Args:
            query: Search query (natural language)
            max_results: Maximum results to return
        
        Returns:
            List of matching files
        
        Example:
            >>> cmd = KNOSemanticSearchCommands()
            >>> await cmd.initialize()
            >>> results = await cmd.search_files("user authentication")
        """
        if not self.initialized:
            logger.error("Semantic search not initialized")
            return []
        
        try:
            logger.info(f"Semantic search: {query}")
            results = await self.search.search_files(query, max_results)
            
            logger.info(f"Search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get indexing metrics"""
        if not self.initialized:
            return {}
        
        return self.search.get_metrics()


# ============================================================================
# INTEGRATION WITH AGENT
# ============================================================================

class KNOAgentWithSemanticSearch:
    """
    KNO Agent with integrated semantic search capabilities.
    
    This is an example of how to add semantic search to the main agent.
    """
    
    def __init__(self, base_directory: str = "./KNO"):
        """Initialize agent with semantic search"""
        self.semantic_commands = KNOSemanticSearchCommands(base_directory)
        self.agent_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the agent and semantic search"""
        try:
            logger.info("Initializing KNO Agent with Semantic Search...")
            
            # Initialize semantic search
            search_initialized = await self.semantic_commands.initialize()
            
            if search_initialized:
                logger.info("Semantic search ready")
                
                # Index directory (optional - do once)
                logger.info("Indexing directory for semantic search...")
                await self.semantic_commands.index_directory()
            
            self.agent_initialized = True
            logger.info("KNO Agent initialization complete")
            
            return True
        
        except Exception as e:
            logger.error(f"Agent initialization error: {e}")
            return False
    
    async def handle_semantic_search_request(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Handle semantic search request from user/interface.
        
        Args:
            query: User's search query
            max_results: Maximum results
        
        Returns:
            Response with search results
        """
        if not self.agent_initialized:
            return {
                'success': False,
                'error': 'Agent not initialized'
            }
        
        try:
            # Provide user feedback
            logger.info(f"Processing semantic search: '{query}'")
            
            # Perform search
            results = await self.semantic_commands.search_files(query, max_results)
            
            # Format response
            return {
                'success': True,
                'query': query,
                'result_count': len(results),
                'results': results,
                'metrics': self.semantic_commands.get_metrics()
            }
        
        except Exception as e:
            logger.error(f"Search handling error: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }
    
    async def search_for_code_pattern(
        self,
        pattern_description: str
    ) -> List[Dict[str, Any]]:
        """
        Search for code patterns by description.
        
        Useful for finding similar code or patterns.
        
        Args:
            pattern_description: Description of pattern to find
        
        Returns:
            Matching files
        """
        return await self.semantic_commands.search_files(
            pattern_description,
            max_results=5
        )
    
    async def search_for_functionality(
        self,
        functionality_description: str
    ) -> List[Dict[str, Any]]:
        """
        Search for specific functionality.
        
        Args:
            functionality_description: What functionality to find
        
        Returns:
            Files implementing that functionality
        """
        return await self.semantic_commands.search_files(
            functionality_description,
            max_results=10
        )


# ============================================================================
# CONVENIENCE FUNCTIONS FOR AGENT
# ============================================================================

_semantic_agent: Optional[KNOAgentWithSemanticSearch] = None


async def get_semantic_agent() -> KNOAgentWithSemanticSearch:
    """Get or create the semantic search agent (singleton)"""
    global _semantic_agent
    
    if _semantic_agent is None:
        _semantic_agent = KNOAgentWithSemanticSearch()
        await _semantic_agent.initialize()
    
    return _semantic_agent


async def agent_search(query: str) -> List[Dict[str, Any]]:
    """
    Convenience function for semantic search from the agent.
    
    Usage in agent:
        results = await agent_search("user authentication")
    
    Args:
        query: Search query
    
    Returns:
        List of matching files
    """
    agent = await get_semantic_agent()
    return await agent.semantic_commands.search_files(query)


async def agent_search_detailed(query: str) -> Dict[str, Any]:
    """
    Search with detailed response.
    
    Args:
        query: Search query
    
    Returns:
        Detailed search response
    """
    agent = await get_semantic_agent()
    return await agent.handle_semantic_search_request(query)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_usage():
    """
    Example of how to use semantic search in KNO agent.
    """
    
    print("=" * 70)
    print("KNO Agent with Semantic Search Example".center(70))
    print("=" * 70)
    
    # Create agent with semantic search
    agent = KNOAgentWithSemanticSearch(base_directory="./KNO")
    
    # Initialize
    print("\n📦 Initializing agent...")
    await agent.initialize()
    
    # Example 1: Simple search
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Simple Semantic Search".center(70))
    print("=" * 70)
    
    query1 = "user authentication and login"
    print(f"\n🔍 Searching: '{query1}'")
    
    results1 = await agent.semantic_commands.search_files(query1, max_results=3)
    
    for i, result in enumerate(results1, 1):
        print(f"\n  {i}. {result['file_path']}")
        print(f"     Relevance: {result['relevance_score']}%")
        print(f"     Content: {result['matched_content'][:60]}...")
    
    # Example 2: Detailed search
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Detailed Search Response".center(70))
    print("=" * 70)
    
    query2 = "error handling and exceptions"
    print(f"\n🔍 Searching: '{query2}'")
    
    response = await agent.handle_semantic_search_request(query2, max_results=3)
    
    print(f"\n  Success: {response['success']}")
    print(f"  Query: {response['query']}")
    print(f"  Results Found: {response['result_count']}")
    
    if response.get('metrics'):
        metrics = response['metrics']
        print(f"\n  📊 System Metrics:")
        print(f"     Indexed Files: {metrics['indexed_files']}")
        print(f"     Total Chunks: {metrics['total_chunks']}")
    
    # Example 3: Pattern search
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Pattern Search".center(70))
    print("=" * 70)
    
    pattern = "websocket real-time communication"
    print(f"\n🔍 Finding pattern: '{pattern}'")
    
    patterns = await agent.search_for_code_pattern(pattern)
    
    for i, p in enumerate(patterns, 1):
        print(f"  {i}. {p['file_path']}")
    
    # Example 4: Using convenience function
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Using Convenience Function".center(70))
    print("=" * 70)
    
    query4 = "database operations"
    print(f"\n🔍 Quick search: '{query4}'")
    
    quick_results = await agent_search(query4)
    
    print(f"  Found: {len(quick_results)} results")
    for r in quick_results[:2]:
        print(f"    - {r['file_path']}")
    
    print("\n" + "=" * 70)
    print("✅ Example completed!".center(70))
    print("=" * 70 + "\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
