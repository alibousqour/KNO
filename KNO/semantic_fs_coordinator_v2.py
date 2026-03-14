"""
KNO Semantic File System - Advanced LLMCoordinator Integration
==============================================================

Integrates KNOFileSystem with LLMCoordinator for intelligent
function calling and tool use patterns with context awareness.

Features:
- Tool definition for semantic search
- File content retrieval
- Index management
- Search result formatting
- Real-time statistics
- Error handling and fallbacks

Author: KNO Architecture
License: MIT
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
from pathlib import Path

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
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API calls"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }

# Tool definitions
SEARCH_FILES_TOOL = ToolDefinition(
    name="search_knowledge_base",
    description=(
        "Search KNO's semantic file system. Searches for relevant files based on content meaning. "
        "Perfect for finding code examples, documentation, configuration files, and technical references. "
        "Returns file paths with relevance scores and content excerpts."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query - describe what you're looking for (e.g., 'authentication system', 'error handling', 'database connection')",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of results to return (1-20, default 5)",
                "default": 5,
                "minimum": 1,
                "maximum": 20,
            },
            "similarity_threshold": {
                "type": "number",
                "description": "Minimum relevance score (0.0-1.0, default 0.3)",
                "default": 0.3,
                "minimum": 0.0,
                "maximum": 1.0,
            },
        },
        "required": ["query"],
    }
)

GET_FILE_CONTENT_TOOL = ToolDefinition(
    name="get_file_content",
    description=(
        "Retrieve the full content of a file from the indexed knowledge base. "
        "Use after search_knowledge_base to get complete file content."
    ),
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the file to retrieve",
            },
        },
        "required": ["file_path"],
    }
)

GET_STATISTICS_TOOL = ToolDefinition(
    name="get_knowledge_base_stats",
    description=(
        "Get statistics about the indexed knowledge base. "
        "Returns information about indexed files, chunks, database type, and indexing status."
    ),
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    }
)

CLEAR_INDEXES_TOOL = ToolDefinition(
    name="clear_knowledge_base",
    description=(
        "Clear all indexes from the knowledge base. WARNING: This action cannot be undone. "
        "Use only when you need to reset the entire index."
    ),
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    }
)

INDEX_DIRECTORY_TOOL = ToolDefinition(
    name="index_directory",
    description=(
        "Index a directory to add files to the knowledge base. "
        "Recursively scans the directory for supported file types (txt, md, py, json, pdf, code files)."
    ),
    parameters={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Absolute path to the directory to index",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to recursively index subdirectories (default: true)",
                "default": True,
            },
        },
        "required": ["directory"],
    }
)

# ============================================================================
# SEMANTIC FILE SYSTEM COORDINATOR
# ============================================================================

class SemanticFSCoordinator:
    """
    Bridge between KNOFileSystem and LLMCoordinator
    
    Provides:
    1. Tool definitions for function calling
    2. Tool execution handlers
    3. Result formatting for LLM context
    4. Error handling and logging
    """
    
    def __init__(self, filesystem):
        """
        Initialize coordinator
        
        Args:
            filesystem: KNOFileSystem instance (async or sync wrapper)
        """
        self.filesystem = filesystem
        self.logger = logging.getLogger('KNO.SemanticFS.Coordinator')
        
        # Cache for file contents
        self._file_cache = {}
        self._cache_max_size = 100  # Keep last 100 files in memory
    
    def get_tool_definitions(self) -> List[Dict]:
        """Get all tool definitions for LLM"""
        return [
            SEARCH_FILES_TOOL.to_dict(),
            GET_FILE_CONTENT_TOOL.to_dict(),
            GET_STATISTICS_TOOL.to_dict(),
            INDEX_DIRECTORY_TOOL.to_dict(),
            CLEAR_INDEXES_TOOL.to_dict(),
        ]
    
    def get_tool_definition(self, tool_name: str) -> Optional[Dict]:
        """Get specific tool definition"""
        tools = {
            "search_knowledge_base": SEARCH_FILES_TOOL,
            "get_file_content": GET_FILE_CONTENT_TOOL,
            "get_knowledge_base_stats": GET_STATISTICS_TOOL,
            "clear_knowledge_base": CLEAR_INDEXES_TOOL,
            "index_directory": INDEX_DIRECTORY_TOOL,
        }
        tool = tools.get(tool_name)
        return tool.to_dict() if tool else None
    
    async def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool
        
        Args:
            tool_name: Name of the tool
            tool_input: Input parameters
        
        Returns:
            Result dictionary
        """
        try:
            if tool_name == "search_knowledge_base":
                return await self._search_knowledge_base(tool_input)
            elif tool_name == "get_file_content":
                return await self._get_file_content(tool_input)
            elif tool_name == "get_knowledge_base_stats":
                return await self._get_statistics(tool_input)
            elif tool_name == "clear_knowledge_base":
                return await self._clear_knowledge_base(tool_input)
            elif tool_name == "index_directory":
                return await self._index_directory(tool_input)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _search_knowledge_base(self, params: Dict) -> Dict[str, Any]:
        """Search knowledge base"""
        try:
            query = params.get("query", "")
            top_k = params.get("top_k", 5)
            threshold = params.get("similarity_threshold", 0.3)
            
            if not query:
                return {"success": False, "error": "Query is required"}
            
            # Check if filesystem is async or sync
            if hasattr(self.filesystem, 'async_fs'):
                # Sync wrapper
                results = self.filesystem.search_files(query, top_k)
            else:
                # Async filesystem
                results = await self.filesystem.search_files(query, top_k, threshold)
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "file": result.file_path,
                    "type": result.file_type,
                    "rank": result.rank,
                    "relevance": f"{result.relevance_score:.1%}",
                    "excerpt": result.content_excerpt[:200] + "..." if len(result.content_excerpt) > 200 else result.content_excerpt,
                    "keywords": result.keywords[:3] if result.keywords else [],
                })
            
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": formatted_results,
                "total_indexed_files": len(self.filesystem.get_indexed_files() if hasattr(self.filesystem, 'get_indexed_files') else {}),
            }
        
        except Exception as e:
            self.logger.error(f"Search failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _get_file_content(self, params: Dict) -> Dict[str, Any]:
        """Get file content"""
        try:
            file_path = params.get("file_path", "")
            
            if not file_path:
                return {"success": False, "error": "file_path is required"}
            
            # Check cache first
            if file_path in self._file_cache:
                return {
                    "success": True,
                    "file_path": file_path,
                    "content": self._file_cache[file_path],
                    "cached": True,
                }
            
            # Read file
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return {"success": False, "error": f"File not found: {file_path}"}
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Cache it
            if len(self._file_cache) >= self._cache_max_size:
                # Remove oldest entry
                oldest_key = next(iter(self._file_cache))
                del self._file_cache[oldest_key]
            
            self._file_cache[file_path] = content
            
            return {
                "success": True,
                "file_path": file_path,
                "content": content,
                "size_bytes": len(content),
                "lines": content.count('\n') + 1,
            }
        
        except Exception as e:
            self.logger.error(f"Get file content failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _get_statistics(self, params: Dict) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            if hasattr(self.filesystem, 'get_statistics'):
                stats = self.filesystem.get_statistics()
            else:
                stats = self.filesystem.async_fs.get_statistics()
            
            return {
                "success": True,
                "statistics": {
                    "indexed_files": stats.get("indexed_files_count", 0),
                    "total_chunks": stats.get("total_chunks", 0),
                    "database_type": stats.get("database_type", "unknown"),
                    "indexing_status": stats.get("indexing_status", "unknown"),
                    "model_loaded": stats.get("model_loaded", False),
                    "total_size_mb": stats.get("total_size_mb", 0),
                    "last_index_time": stats.get("last_index_time"),
                }
            }
        
        except Exception as e:
            self.logger.error(f"Get statistics failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _clear_knowledge_base(self, params: Dict) -> Dict[str, Any]:
        """Clear knowledge base"""
        try:
            self.logger.warning("Clearing knowledge base...")
            
            if hasattr(self.filesystem, 'async_fs'):
                success = await self.filesystem.async_fs.clear_indexes()
            else:
                success = await self.filesystem.clear_indexes()
            
            if success:
                self._file_cache.clear()
                return {
                    "success": True,
                    "message": "Knowledge base cleared successfully",
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to clear indexes",
                }
        
        except Exception as e:
            self.logger.error(f"Clear knowledge base failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _index_directory(self, params: Dict) -> Dict[str, Any]:
        """Index directory"""
        try:
            directory = params.get("directory", "")
            recursive = params.get("recursive", True)
            
            if not directory:
                return {"success": False, "error": "directory is required"}
            
            self.logger.info(f"Indexing directory: {directory}")
            
            if hasattr(self.filesystem, 'async_fs'):
                metrics = await self.filesystem.async_fs.index_directory(directory, recursive)
            else:
                metrics = self.filesystem.index_directory(directory, recursive)
            
            return {
                "success": True,
                "directory": directory,
                "metrics": {
                    "indexed_files": metrics.indexed_files,
                    "total_files": metrics.total_files,
                    "failed_files": metrics.failed_files,
                    "total_chunks": metrics.total_chunks,
                    "indexing_time_seconds": metrics.indexing_time_seconds,
                    "success_rate": f"{metrics.get_success_rate():.1f}%",
                }
            }
        
        except Exception as e:
            self.logger.error(f"Index directory failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def clear_cache(self):
        """Clear file content cache"""
        self._file_cache.clear()
        self.logger.info("File cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_files": len(self._file_cache),
            "cache_max_size": self._cache_max_size,
        }


# ============================================================================
# INTEGRATION HELPER FUNCTIONS
# ============================================================================

def create_coordinator(filesystem) -> SemanticFSCoordinator:
    """Factory function to create coordinator"""
    return SemanticFSCoordinator(filesystem)

async def process_tool_call(coordinator: SemanticFSCoordinator, 
                          tool_name: str, 
                          tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Process tool call from LLM"""
    return await coordinator.execute_tool(tool_name, tool_input)

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    import asyncio
    from semantic_file_system_enhanced import KNOFileSystem
    
    async def example():
        # Initialize filesystem
        fs = KNOFileSystem(index_dir="./test_sfs_index")
        if not await fs.initialize():
            print("Failed to initialize")
            return
        
        # Create coordinator
        coordinator = create_coordinator(fs)
        
        # Get tool definitions
        print("Available tools:")
        for tool in coordinator.get_tool_definitions():
            print(f"  - {tool['function']['name']}")
        
        # Example: Search
        print("\nSearching knowledge base...")
        result = await coordinator.execute_tool(
            "search_knowledge_base",
            {"query": "semantic indexing", "top_k": 3}
        )
        print(f"Found {result.get('results_count', 0)} results")
        
        # Example: Get statistics
        print("\nGetting statistics...")
        result = await coordinator.execute_tool("get_knowledge_base_stats", {})
        if result.get('success'):
            stats = result.get('statistics', {})
            print(f"  Indexed files: {stats.get('indexed_files', 0)}")
            print(f"  Total chunks: {stats.get('total_chunks', 0)}")
    
    asyncio.run(example())
