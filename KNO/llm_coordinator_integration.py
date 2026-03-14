"""
LLM Coordinator Integration - Semantic Search Tool/Function
===========================================================

نموذج التكامل مع لتنسيق LLM كأداة (Tool/Function Calling)

Provides semantic search as a callable tool/function for LLM coordinators
and conversational agents.

Features:
- LLM-compatible function signatures
- Tool descriptions for LLM understanding
- Schema validation for LLM parameters
- Error handling and fallbacks
- Result formatting for LLM consumption

Author: KNO Architecture
License: MIT
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from agent_semantic_search_integration import (
        KNOAgentSemanticSearch,
        search_files
    )
    from security_filter import IgnoreListManager, SecureFileAnalyzer
    HAS_SEMANTIC_SEARCH = True
except ImportError:
    HAS_SEMANTIC_SEARCH = False
    logging.warning("Semantic search components not available")

logger = logging.getLogger('KNO.LLMCoordinator')

# ============================================================================
# LLM TOOL DEFINITIONS
# ============================================================================

class SemanticSearchTool:
    """
    أداة البحث الدلالي للمنسق اللغوي
    
    Semantic search tool definition for LLM coordinators.
    
    This tool allows LLMs to search your codebase by meaning when
    answering user questions about files and code.
    """
    
    # Tool metadata for LLM
    TOOL_NAME = "semantic_search_knowledge_base"
    TOOL_DESCRIPTION = """
    Search your project's codebase by meaning, not just keywords.
    
    استخدم هذه الأداة للبحث عن الملفات بناءً على المعنى والسياق.
    
    Examples:
    - "Find files about user authentication"
    - "Where is error handling implemented?"
    - "Show me websocket communication code"
    
    This tool understands natural language queries and finds related files
    even if they don't contain exact keywords.
    """
    
    # Function signature for LLM
    FUNCTION_SIGNATURE = {
        "type": "function",
        "function": {
            "name": "semantic_search_knowledge_base",
            "description": "Search codebase by meaning using semantic understanding",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g., 'user authentication', 'error handling')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default 10, max 50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    },
                    "context_type": {
                        "type": "string",
                        "description": "Type of context: 'general', 'code', 'documentation'",
                        "enum": ["general", "code", "documentation"],
                        "default": "general"
                    }
                },
                "required": ["query"]
            }
        }
    }
    
    def __init__(self, base_directory: str = "./KNO"):
        """
        Initialize semantic search tool.
        
        Args:
            base_directory: Directory to search in
        """
        self.base_directory = base_directory
        self.search_system = KNOAgentSemanticSearch(
            base_directory=base_directory
        ) if HAS_SEMANTIC_SEARCH else None
        
        self.security_filter = IgnoreListManager(base_directory)
        self.initialized = False
        self.usage_count = 0
        self.usage_log: List[Dict[str, Any]] = []
    
    async def initialize(self) -> bool:
        """Initialize the tool"""
        if not HAS_SEMANTIC_SEARCH:
            logger.error("Semantic search not available")
            return False
        
        try:
            logger.info("Initializing semantic search tool...")
            
            success = await self.search_system.initialize()
            if success:
                # Index directory
                logger.info("Indexing directory...")
                await self.search_system.index_directory()
            
            self.initialized = success
            return success
        
        except Exception as e:
            logger.error(f"Tool initialization error: {e}")
            return False
    
    async def __call__(
        self,
        query: str,
        max_results: int = 10,
        context_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Call the tool (implements LLM function calling interface).
        
        Args:
            query: Search query
            max_results: Maximum results
            context_type: Type of context
        
        Returns:
            LLM-formatted response
        """
        return await self.execute(query, max_results, context_type)
    
    async def execute(
        self,
        query: str,
        max_results: int = 10,
        context_type: str = "general"
    ) -> Dict[str, Any]:
        """
        تنفيذ البحث الدلالي
        
        Execute semantic search query.
        
        Args:
            query: Natural language query
            max_results: Maximum results (1-50)
            context_type: Type of context needed
        
        Returns:
            LLM-compatible response dictionary
        """
        
        if not self.initialized:
            logger.warning("Tool not initialized, attempting initialization...")
            await self.initialize()
        
        # Log usage
        self.usage_count += 1
        start_time = datetime.now()
        
        try:
            # Validate input
            if not query or len(query.strip()) < 2:
                return {
                    'success': False,
                    'error': 'Query too short. Provide at least 2 characters.',
                    'results': []
                }
            
            max_results = max(1, min(int(max_results), 50))
            
            logger.info(f"Executing semantic search: '{query}' (type: {context_type})")
            
            # Perform search
            search_results = await self.search_system.search_files(
                query,
                max_results
            )
            
            # Filter results using security filter
            filtered_results = [
                r for r in search_results
                if self.security_filter.should_include_file(r['file_path'])
            ]
            
            # Format for LLM
            formatted_results = self._format_for_llm(
                filtered_results,
                context_type
            )
            
            # Calculate elapsed time
            elapsed = (datetime.now() - start_time).total_seconds()
            
            response = {
                'success': True,
                'query': query,
                'context_type': context_type,
                'result_count': len(formatted_results),
                'results': formatted_results,
                'elapsed_seconds': round(elapsed, 2),
                'usage_count': self.usage_count,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log this usage
            self._log_usage(query, len(formatted_results), elapsed)
            
            return response
        
        except Exception as e:
            logger.error(f"Search execution error: {e}")
            return {
                'success': False,
                'error': f"Search failed: {str(e)}",
                'query': query,
                'results': []
            }
    
    def _format_for_llm(
        self,
        results: List[Dict[str, Any]],
        context_type: str
    ) -> List[Dict[str, Any]]:
        """
        Format search results for LLM consumption.
        
        Args:
            results: Raw search results
            context_type: Context type for formatting
        
        Returns:
            LLM-friendly formatted results
        """
        formatted = []
        
        for i, result in enumerate(results, 1):
            item = {
                'rank': i,
                'file': result['file_path'],
                'type': result.get('file_type', 'unknown'),
                'relevance': f"{result['relevance_score']}%",
                'summary': result.get('summary', result.get('matched_content', ''))[:150]
            }
            
            # Add context-specific information
            if context_type == "code":
                item['code_snippet'] = result.get('matched_content', '')[:200]
                item['line'] = result.get('line_numbers', [None])[0]
            
            elif context_type == "documentation":
                item['excerpt'] = result.get('summary', '')[:250]
            
            # Add keywords if available
            if result.get('keywords'):
                item['keywords'] = ', '.join(result['keywords'][:3])
            
            formatted.append(item)
        
        return formatted
    
    def _log_usage(self, query: str, result_count: int, elapsed: float) -> None:
        """Log tool usage for analytics"""
        usage = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'result_count': result_count,
            'elapsed_seconds': elapsed,
            'usage_number': self.usage_count
        }
        self.usage_log.append(usage)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        if not self.usage_log:
            return {'total_uses': 0}
        
        total_queries = len(self.usage_log)
        total_results = sum(u['result_count'] for u in self.usage_log)
        avg_time = sum(u['elapsed_seconds'] for u in self.usage_log) / total_queries
        
        return {
            'total_uses': self.usage_count,
            'total_queries': total_queries,
            'total_results_returned': total_results,
            'average_time_seconds': round(avg_time, 3),
            'last_query': self.usage_log[-1]['query'] if self.usage_log else None,
            'recent_queries': [u['query'] for u in self.usage_log[-5:]]
        }
    
    def save_usage_log(self, log_file: str = "llm_search_usage.json") -> bool:
        """Save usage log to file"""
        try:
            with open(log_file, 'w') as f:
                json.dump(self.usage_log, f, indent=2)
            logger.info(f"Saved usage log to {log_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save usage log: {e}")
            return False


# ============================================================================
# DIRECTORY ANALYSIS TOOL
# ============================================================================

class DirectoryAnalysisTool:
    """
    أداة تحليل المجلد
    
    Tool for analyzing project structure and file information.
    """
    
    TOOL_NAME = "analyze_project_structure"
    TOOL_DESCRIPTION = """
    Analyze project structure and get file information.
    
    Returns information about files, directories, and project structure,
    filtered for security (excluding sensitive files).
    """
    
    FUNCTION_SIGNATURE = {
        "type": "function",
        "function": {
            "name": "analyze_project_structure",
            "description": "Analyze project directory structure and file statistics",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to analyze (default: project root)",
                        "default": "."
                    },
                    "include_hidden": {
                        "type": "boolean",
                        "description": "Include hidden files and directories",
                        "default": False
                    }
                }
            }
        }
    }
    
    def __init__(self, base_directory: str = "./KNO"):
        """Initialize directory analysis tool"""
        self.base_directory = base_directory
        self.security_filter = IgnoreListManager(base_directory)
        self.analyzer = SecureFileAnalyzer(base_directory, self.security_filter)
    
    async def execute(
        self,
        directory: str = None,
        include_hidden: bool = False
    ) -> Dict[str, Any]:
        """
        Execute directory analysis.
        
        Args:
            directory: Directory to analyze
            include_hidden: Include hidden files
        
        Returns:
            Analysis results
        """
        
        try:
            scan_dir = Path(directory or self.base_directory)
            
            logger.info(f"Analyzing directory: {scan_dir}")
            
            scan_results = self.analyzer.scan_directory_safely(str(scan_dir))
            
            return {
                'success': True,
                'directory': str(scan_dir),
                'total_files': scan_results['total_files'],
                'indexable_files': scan_results['indexable_files'],
                'ignored_files': scan_results['ignored_files'],
                'restricted_files': scan_results['restricted_files'],
                'file_types': scan_results['files_by_type'],
                'security_warnings': len(scan_results['security_warnings']),
                'timestamp': scan_results['scan_date']
            }
        
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# ============================================================================
# LLM COORDINATOR ADAPTER
# ============================================================================

class LLMSemanticSearchAdapter:
    """
    محول التكامل مع منسق LLM
    
    Adapter to integrate semantic search into LLM coordinators.
    """
    
    def __init__(self, base_directory: str = "./KNO"):
        """Initialize adapter"""
        self.base_directory = base_directory
        self.search_tool = SemanticSearchTool(base_directory)
        self.analysis_tool = DirectoryAnalysisTool(base_directory)
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all tools"""
        try:
            logger.info("Initializing LLM adapter...")
            success = await self.search_tool.initialize()
            self.initialized = success
            return success
        except Exception as e:
            logger.error(f"Adapter initialization error: {e}")
            return False
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions for LLM.
        
        Returns list of tool definitions compatible with OpenAI Function Calling,
        Anthropic Tool Use, and other LLM API formats.
        """
        return [
            self.search_tool.FUNCTION_SIGNATURE,
            self.analysis_tool.FUNCTION_SIGNATURE
        ]
    
    async def handle_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle LLM tool call.
        
        Args:
            tool_name: Name of tool to call
            tool_input: Tool input parameters
        
        Returns:
            Tool execution result
        """
        
        if tool_name == self.search_tool.TOOL_NAME:
            return await self.search_tool.execute(**tool_input)
        
        elif tool_name == self.analysis_tool.TOOL_NAME:
            return await self.analysis_tool.execute(**tool_input)
        
        else:
            return {
                'success': False,
                'error': f'Unknown tool: {tool_name}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get adapter status"""
        return {
            'initialized': self.initialized,
            'search_tool': {
                'initialized': self.search_tool.initialized,
                'usage_count': self.search_tool.usage_count,
                'stats': self.search_tool.get_usage_stats()
            },
            'base_directory': self.base_directory,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_llm_integration():
    """Example of LLM integration"""
    
    print("\n" + "=" * 70)
    print("LLM Coordinator Integration Example".center(70))
    print("=" * 70)
    
    # Initialize adapter
    adapter = LLMSemanticSearchAdapter(base_directory="./KNO")
    
    print("\n🔧 Initializing adapter...")
    await adapter.initialize()
    
    # Get tool definitions
    print("\n📋 Available Tools:")
    tools = adapter.get_tools()
    for tool in tools:
        print(f"   - {tool['function']['name']}")
        print(f"     {tool['function']['description'][:60]}...")
    
    # Example tool calls
    print("\n🔍 Example Tool Call #1: Semantic Search")
    result1 = await adapter.handle_tool_call(
        "semantic_search_knowledge_base",
        {
            'query': 'user authentication and login',
            'max_results': 5,
            'context_type': 'code'
        }
    )
    
    print(f"   Results: {result1['result_count']}")
    if result1['results']:
        for r in result1['results'][:2]:
            print(f"   - {r['file']}")
    
    # Get status
    print("\n📊 Adapter Status:")
    status = adapter.get_status()
    print(f"   Initialized: {status['initialized']}")
    print(f"   Usage Count: {status['search_tool']['usage_count']}")
    print(f"   Stats: {status['search_tool']['stats']}")


if __name__ == "__main__":
    asyncio.run(example_llm_integration())
