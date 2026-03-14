"""
KNO Semantic File System - LLMCoordinator Integration Module
============================================================

Integrates KNOFileSystem with LLMCoordinator as a callable tool
for Function Calling / Tool Use patterns.

This module enables KNO's LLM to semantically search files
when responding to user queries.

Author: KNO Architecture
License: MIT
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

logger = logging.getLogger('KNO.SemanticFS.Integration')

# ============================================================================
# TOOL DEFINITIONS FOR LLM
# ============================================================================

@dataclass
class ToolDefinition:
    """OpenAI-compatible tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]

# Tool definition for semantic file search
SEARCH_FILES_TOOL = ToolDefinition(
    name="search_knowledge_base",
    description="Search KNO's file system semantically. Returns relevant files and excerpts based on content meaning, not just filename.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Semantic search query (e.g., 'how to authenticate users', 'database configuration')",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return (1-10)",
                "default": 5,
                "minimum": 1,
                "maximum": 10,
            },
        },
        "required": ["query"],
    }
)

GET_FILE_CONTENT_TOOL = ToolDefinition(
    name="get_file_content",
    description="Retrieve full content of a file from the indexed knowledge base.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to retrieve",
            },
        },
        "required": ["file_path"],
    }
)

GET_STATISTICS_TOOL = ToolDefinition(
    name="get_knowledge_base_stats",
    description="Get statistics about indexed files and the semantic search index.",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    }
)

# ============================================================================
# SEMANTIC FILE SYSTEM COORDINATOR
# ============================================================================

class SemanticFSCoordinator:
    """
    Bridge between KNOFileSystem and LLMCoordinator
    
    Provides tools for LLM to:
    1. Search files semantically
    2. Retrieve full file content
    3. Get indexing statistics
    """
    
    def __init__(self, filesystem):
        """
        Initialize coordinator
        
        Args:
            filesystem: KNOFileSystem instance
        """
        self.fs = filesystem
        self.logger = logger
        
        # Tool registry
        self.tools = {
            'search_knowledge_base': self.search_files,
            'get_file_content': self.get_file_content,
            'get_knowledge_base_stats': self.get_statistics,
        }
    
    def get_tool_definitions(self) -> List[ToolDefinition]:
        """
        Get tool definitions for LLM
        
        Returns:
            List of ToolDefinition objects
        """
        return [
            SEARCH_FILES_TOOL,
            GET_FILE_CONTENT_TOOL,
            GET_STATISTICS_TOOL,
        ]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool with arguments
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
        
        Returns:
            Tool result
        """
        if tool_name not in self.tools:
            return {
                'success': False,
                'error': f"Unknown tool: {tool_name}",
            }
        
        try:
            tool_func = self.tools[tool_name]
            
            # Handle both async and sync functions
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**arguments)
            else:
                result = tool_func(**arguments)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Tool call failed: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    # ========================================================================
    # TOOL IMPLEMENTATIONS
    # ========================================================================
    
    async def search_files(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Search files semantically
        
        Args:
            query: Search query
            top_k: Number of results
        
        Returns:
            Search results
        """
        try:
            # Validate inputs
            if not query or len(query.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Query cannot be empty',
                }
            
            if not (1 <= top_k <= 10):
                top_k = 5
            
            # Perform search
            results = await self.fs.search_files(query, top_k=top_k)
            
            if not results:
                return {
                    'success': True,
                    'query': query,
                    'results': [],
                    'message': 'No relevant files found',
                }
            
            # Format results for LLM
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'file_path': result.file_path,
                    'file_type': result.file_type,
                    'relevance_score': f"{result.relevance_score:.2%}",
                    'excerpt': result.content_excerpt,
                    'chunk_index': result.chunk_index,
                })
            
            return {
                'success': True,
                'query': query,
                'results_count': len(results),
                'results': formatted_results,
            }
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """
        Retrieve full file content
        
        Args:
            file_path: Path to file
        
        Returns:
            File content or error
        """
        try:
            if file_path not in self.fs.indexed_files:
                return {
                    'success': False,
                    'error': f'File not indexed: {file_path}',
                }
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Limit size returned to LLM
            max_chars = 8000
            if len(content) > max_chars:
                content = content[:max_chars] + f"\n\n[... truncated, file is {len(content)} chars total ...]"
            
            return {
                'success': True,
                'file_path': file_path,
                'file_type': self.fs.indexed_files[file_path].file_type,
                'content': content,
                'size_bytes': len(content),
            }
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve file: {e}")
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get indexing statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            stats = self.fs.get_statistics()
            
            return {
                'success': True,
                'statistics': {
                    'total_files_indexed': stats.get('total_files_indexed', 0),
                    'total_chunks': stats.get('total_chunks', 0),
                    'database_type': stats.get('database_type', 'unknown'),
                    'model_name': self.fs.model_name,
                    'model_loaded': stats.get('model_loaded', False),
                    'last_index_time': stats.get('last_index_time', None),
                },
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {
                'success': False,
                'error': str(e),
            }


# ============================================================================
# LLMCOORDINATOR INTEGRATION HELPER
# ============================================================================

class LLMCoordinatorIntegration:
    """
    Helper class for integrating with LLMCoordinator
    
    Usage in LLMCoordinator:
    ```python
    integration = LLMCoordinatorIntegration(semantic_fs)
    
    # In your agent loop:
    response = llm.query(
        prompt=user_question,
        tools=integration.get_tools(),
    )
    
    # When LLM calls a tool:
    for tool_call in response.tool_calls:
        result = integration.call_tool(
            tool_call.name,
            tool_call.arguments
        )
    ```
    """
    
    def __init__(self, semantic_fs):
        """
        Initialize integration
        
        Args:
            semantic_fs: KNOFileSystem instance
        """
        self.coordinator = SemanticFSCoordinator(semantic_fs)
        self.logger = logger
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get tools in OpenAI format
        
        Returns:
            List of tool definitions
        """
        tools = []
        for tool_def in self.coordinator.get_tool_definitions():
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_def.name,
                    "description": tool_def.description,
                    "parameters": tool_def.parameters,
                }
            })
        return tools
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call tool (synchronous wrapper)
        
        Args:
            tool_name: Tool name
            arguments: Tool arguments
        
        Returns:
            Tool result
        """
        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        self.coordinator.call_tool(tool_name, arguments)
                    )
                    return future.result(timeout=30)
            else:
                return asyncio.run(self.coordinator.call_tool(tool_name, arguments))
        except RuntimeError:
            # No event loop
            return asyncio.run(self.coordinator.call_tool(tool_name, arguments))


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import json
    
    async def example():
        """Example of using semantic file system with LLM coordinator"""
        
        # Import the filesystem
        from semantic_file_system import KNOFileSystem
        
        # Initialize filesystem
        print("Initializing KNOFileSystem...")
        fs = KNOFileSystem(
            index_dir="./sfs_index",
            use_chroma=True,
        )
        
        if not await fs.initialize():
            print("Failed to initialize filesystem")
            return
        
        # Create coordinator
        print("Creating LLMCoordinator integration...")
        coord = SemanticFSCoordinator(fs)
        
        # Example: How LLM would call the tools
        print("\n=== Example Tool Calls ===\n")
        
        # Search files
        print("1. Search for 'authentication'")
        result = await coord.call_tool(
            'search_knowledge_base',
            {'query': 'authentication and security', 'top_k': 3}
        )
        print(json.dumps(result, indent=2))
        
        # Get statistics
        print("\n2. Get knowledge base statistics")
        result = coord.get_statistics()
        print(json.dumps(result, indent=2))
        
        # Show tool definitions
        print("\n3. Tool definitions for LLM:")
        llm_integration = LLMCoordinatorIntegration(fs)
        tools = llm_integration.get_tools()
        for tool in tools:
            print(f"\n  Tool: {tool['function']['name']}")
            print(f"  Description: {tool['function']['description']}")
    
    asyncio.run(example())
