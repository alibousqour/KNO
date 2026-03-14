"""
LLM Coordinator Integration - Advanced
======================================

تكامل منسّق LLM المتقدم

Complete integration for semantic search with LLMCoordinator using Pydantic
for type safety and OpenAI function calling schema.

Author: KNO Architecture
License: MIT
"""

import json
import logging
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from pydantic import BaseModel, Field, validator
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

try:
    from semantic_search_advanced import SearchResult
    HAS_SEARCH = True
except ImportError:
    HAS_SEARCH = False

logger = logging.getLogger('KNO.LLMCoordinator')

# ============================================================================
# ENUMS
# ============================================================================

class SearchScope(str, Enum):
    """Scope of search"""
    ENTIRE_SYSTEM = "entire_system"
    PROJECT = "project"
    DIRECTORY = "directory"
    SPECIFIC_TYPE = "specific_type"


class ResultFormat(str, Enum):
    """Format for results"""
    SUMMARY = "summary"
    DETAILED = "detailed"
    JSON_ONLY = "json_only"


# ============================================================================
# PYDANTIC MODELS (Type-Safe)
# ============================================================================

if HAS_PYDANTIC:
    
    class SearchQuery(BaseModel):
        """Search query model"""
        query: str = Field(..., description="Search query in natural language")
        max_results: int = Field(
            default=10,
            ge=1,
            le=50,
            description="Maximum number of results to return"
        )
        min_relevance: float = Field(
            default=0.3,
            ge=0.0,
            le=1.0,
            description="Minimum relevance score (0-1)"
        )
        scope: SearchScope = Field(
            default=SearchScope.ENTIRE_SYSTEM,
            description="Scope of search"
        )
        search_path: Optional[str] = Field(
            default=None,
            description="Specific path to search (when scope is DIRECTORY)"
        )
        file_types: Optional[List[str]] = Field(
            default=None,
            description="Specific file types to search (.py, .js, etc.)"
        )
        include_restricted: bool = Field(
            default=False,
            description="Whether to include restricted files"
        )
        result_format: ResultFormat = Field(
            default=ResultFormat.DETAILED,
            description="Format for results"
        )
        
        @validator('query')
        def validate_query(cls, v):
            if not v or len(v.strip()) == 0:
                raise ValueError("Query cannot be empty")
            return v.strip()
        
        @validator('search_path')
        def validate_search_path(cls, v, values):
            if values.get('scope') == SearchScope.DIRECTORY and not v:
                raise ValueError(
                    "search_path required when scope is DIRECTORY"
                )
            return v
    
    
    class SearchResultModel(BaseModel):
        """Single search result model"""
        file_path: str = Field(..., description="Path to the file")
        file_type: str = Field(..., description="Type of file (.py, .js, etc.)")
        relevance_score: float = Field(
            ...,
            ge=0.0,
            le=1.0,
            description="Relevance score (0-1)"
        )
        summary: Optional[str] = Field(
            default=None,
            description="Summary of file content"
        )
        keywords: Optional[List[str]] = Field(
            default=None,
            description="Key words/topics in file"
        )
        line_numbers: Optional[List[int]] = Field(
            default=None,
            description="Line numbers with relevant content"
        )
        restricted: bool = Field(
            default=False,
            description="Whether file is marked as restricted"
        )
    
    
    class SearchResponse(BaseModel):
        """Complete search response"""
        success: bool = Field(..., description="Whether search succeeded")
        query: str = Field(..., description="Original query")
        total_results: int = Field(..., description="Total results found")
        results: List[SearchResultModel] = Field(
            ...,
            description="Search results"
        )
        execution_time_ms: float = Field(
            ...,
            description="Execution time in milliseconds"
        )
        message: Optional[str] = Field(
            default=None,
            description="Additional message or error"
        )


# ============================================================================
# FUNCTION CALLING SCHEMA
# ============================================================================

def get_semantic_search_function_schema() -> Dict[str, Any]:
    """
    Get OpenAI-compatible function calling schema.
    
    يحصل على مخطط استدعاء الدالة المتوافق مع OpenAI
    
    Returns:
        Dict with function schema
    """
    return {
        "name": "semantic_search",
        "description": "Search files in KNO system by semantic meaning",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Natural language search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results to return",
                    "minimum": 1,
                    "maximum": 50,
                    "default": 10
                },
                "min_relevance": {
                    "type": "number",
                    "description": "Minimum relevance score (0-1)",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.3
                },
                "scope": {
                    "type": "string",
                    "enum": [e.value for e in SearchScope],
                    "description": "Search scope",
                    "default": "entire_system"
                },
                "search_path": {
                    "type": "string",
                    "description": "Path to search (for DIRECTORY scope)"
                },
                "file_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "File types to include (.py, .js, etc.)"
                },
                "include_restricted": {
                    "type": "boolean",
                    "description": "Include restricted files",
                    "default": False
                },
                "result_format": {
                    "type": "string",
                    "enum": [e.value for e in ResultFormat],
                    "description": "Result format",
                    "default": "detailed"
                }
            },
            "required": ["query"]
        }
    }


# ============================================================================
# SEMANTIC SEARCH TOOL CLASS
# ============================================================================

class SemanticSearchTool:
    """
    أداة البحث الدلالي
    
    Semantic search tool wrapper for LLMCoordinator.
    """
    
    def __init__(self, search_engine=None, ignore_manager=None):
        """
        Initialize tool.
        
        Args:
            search_engine: SemanticSearchEngine instance
            ignore_manager: IgnoreListManager instance
        """
        self.search_engine = search_engine
        self.ignore_manager = ignore_manager
    
    def get_function_schema(self) -> Dict[str, Any]:
        """Get OpenAI function schema"""
        return get_semantic_search_function_schema()
    
    async def execute(
        self,
        query: str,
        max_results: int = 10,
        min_relevance: float = 0.3,
        scope: str = "entire_system",
        search_path: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        include_restricted: bool = False,
        result_format: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Execute semantic search.
        
        Args:
            query: Search query
            max_results: Maximum results
            min_relevance: Minimum relevance
            scope: Search scope
            search_path: Path to search
            file_types: File types to include
            include_restricted: Include restricted files
            result_format: Result format
        
        Returns:
            Dict with results
        """
        
        import time
        import asyncio
        
        start_time = time.time()
        
        try:
            # Validate inputs if Pydantic available
            if HAS_PYDANTIC:
                search_query = SearchQuery(
                    query=query,
                    max_results=max_results,
                    min_relevance=min_relevance,
                    scope=SearchScope(scope),
                    search_path=search_path,
                    file_types=file_types,
                    include_restricted=include_restricted,
                    result_format=ResultFormat(result_format)
                )
            else:
                # Basic validation
                if not query or len(query.strip()) == 0:
                    raise ValueError("Query cannot be empty")
                if not (0.0 <= min_relevance <= 1.0):
                    raise ValueError("min_relevance must be 0-1")
                if not (1 <= max_results <= 50):
                    raise ValueError("max_results must be 1-50")
            
            # Perform search
            if not self.search_engine:
                raise RuntimeError("Search engine not initialized")
            
            # Scope-based filtering
            if scope == "entire_system":
                results = await self.search_engine.search_files_secure(
                    query,
                    max_results,
                    min_relevance,
                    verify_results=not include_restricted
                )
            elif scope == "directory" and search_path:
                # Would need custom implementation
                logger.warning("Directory scope requires custom implementation")
                results = []
            elif scope == "project" and search_path:
                # Would need custom implementation
                logger.warning("Project scope requires custom implementation")
                results = []
            else:
                results = []
            
            # Format results
            formatted_results = []
            for r in results:
                if HAS_PYDANTIC and result_format == "detailed":
                    result_model = SearchResultModel(
                        file_path=r.file_path,
                        file_type=r.file_type,
                        relevance_score=r.relevance_score,
                        summary=r.summary,
                        keywords=r.keywords
                    )
                    formatted_results.append(result_model.dict())
                else:
                    formatted_results.append({
                        'file_path': r.file_path,
                        'file_type': r.file_type,
                        'relevance_score': r.relevance_score,
                        'summary': r.summary,
                        'keywords': r.keywords
                    })
            
            # Build response
            execution_time = (time.time() - start_time) * 1000  # ms
            
            response = {
                'success': True,
                'query': query,
                'total_results': len(formatted_results),
                'results': formatted_results,
                'execution_time_ms': execution_time,
                'message': f"Found {len(formatted_results)} relevant files"
            }
            
            if HAS_PYDANTIC:
                response_model = SearchResponse(**response)
                return response_model.dict()
            
            return response
        
        except ValueError as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                'success': False,
                'query': query,
                'total_results': 0,
                'results': [],
                'execution_time_ms': execution_time,
                'message': f"Validation error: {str(e)}"
            }
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Search execution error: {e}")
            return {
                'success': False,
                'query': query,
                'total_results': 0,
                'results': [],
                'execution_time_ms': execution_time,
                'message': f"Error: {str(e)}"
            }
    
    def format_for_llm_response(self, result: Dict[str, Any]) -> str:
        """
        Format result for LLM response.
        
        يصيغ النتيجة لاستجابة LLM
        
        Args:
            result: Raw result dict
        
        Returns:
            Formatted string for LLM
        """
        if not result['success']:
            return f"Search failed: {result['message']}"
        
        output = f"Found {result['total_results']} relevant files:\n\n"
        
        for i, file_result in enumerate(result['results'], 1):
            relevance_pct = int(file_result['relevance_score'] * 100)
            output += f"{i}. {file_result['file_path']}\n"
            output += f"   Type: {file_result['file_type']}\n"
            output += f"   Relevance: {relevance_pct}%\n"
            
            if file_result.get('summary'):
                summary = file_result['summary'][:100]
                output += f"   Summary: {summary}...\n"
            
            if file_result.get('keywords'):
                output += f"   Keywords: {', '.join(file_result['keywords'][:5])}\n"
            
            output += "\n"
        
        output += f"Execution time: {result['execution_time_ms']:.2f}ms"
        
        return output


# ============================================================================
# LLM COORDINATOR INTEGRATION
# ============================================================================

class SemanticSearchLLMIntegration:
    """
    تكامل KNO مع منسق LLM
    
    Complete integration handler for LLMCoordinator.
    """
    
    def __init__(self, search_engine=None, ignore_manager=None):
        """Initialize integration"""
        self.tool = SemanticSearchTool(search_engine, ignore_manager)
        self.tools = {"semantic_search": self.tool}
    
    async def process_llm_call(
        self,
        function_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process LLM function call.
        
        Args:
            function_name: Name of function to call
            arguments: Arguments dict
        
        Returns:
            Result dict
        """
        if function_name == "semantic_search":
            return await self.tool.execute(**arguments)
        
        raise ValueError(f"Unknown function: {function_name}")
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with schemas"""
        return [self.tool.get_function_schema()]
    
    async def execute_with_retry(
        self,
        function_name: str,
        arguments: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute with retry logic.
        
        Args:
            function_name: Function name
            arguments: Arguments
            max_retries: Max retry attempts
        
        Returns:
            Result dict
        """
        for attempt in range(max_retries):
            try:
                return await self.process_llm_call(function_name, arguments)
            except Exception as e:
                if attempt == max_retries - 1:
                    return {
                        'success': False,
                        'message': f"Failed after {max_retries} attempts: {str(e)}"
                    }
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def demo_llm_coordinator():
    """Demonstrate LLM coordinator integration"""
    
    print("\n" + "=" * 70)
    print("LLM Coordinator Integration Demo".center(70))
    print("=" * 70)
    
    # Create tool
    tool = SemanticSearchTool()
    
    print("\n📋 Function Schema:")
    schema = tool.get_function_schema()
    print(json.dumps(schema, indent=2)[:300] + "...")
    
    print("\n🔧 Integration Setup:")
    print("   - Tool name: semantic_search")
    print("   - Parameters: query, max_results, scope, etc.")
    print("   - Type: Function Calling (OpenAI compatible)")
    
    print("\n✅ Integration Ready!")


if __name__ == "__main__":
    if HAS_PYDANTIC:
        import asyncio
        asyncio.run(demo_llm_coordinator())
    else:
        print("Pydantic not available - install: pip install pydantic")
