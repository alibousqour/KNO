"""
SEMANTIC SEARCH INTEGRATION GUIDE
================================

دليل شامل لاستخدام نظام البحث الدلالي مع KNO و eDEX-UI

Guide for using the Semantic Search System with KNO and eDEX-UI

Author: KNO Architecture
Date: 2026-03-09
"""

# ============================================================================
# 1. QUICK START
# ============================================================================

"""
الخطوة 1: التثبيت السريع
Step 1: Quick Installation

# Install required packages
pip install sentence-transformers numpy

# Basic usage
import asyncio
from agent_semantic_search_integration import search_files

async def main():
    results = await search_files("user authentication", directory="./src")
    for r in results:
        print(f"{r['file_path']}: {r['relevance_score']}%")

asyncio.run(main())
"""


# ============================================================================
# 2. INITIALIZATION
# ============================================================================

"""
الخطوة 2: إعداد النظام
Step 2: System Setup

from agent_semantic_search_integration import KNOAgentSemanticSearch
import asyncio

async def initialize():
    # Create search instance
    search = KNOAgentSemanticSearch(
        base_directory="./KNO",
        status_file="edex_status.json"
    )
    
    # Initialize models
    await search.initialize()
    
    # Index directory
    await search.index_directory()
    
    return search

# Run
search = asyncio.run(initialize())
"""


# ============================================================================
# 3. SEMANTIC SEARCH - البحث بالمعنى
# ============================================================================

"""
الخطوة 3: البحث الدلالي
Step 3: Semantic Search

Unlike keyword search, semantic search finds files by MEANING:

Keyword Search Example:
  query: "user"
  Result: Only files containing the word "user"

Semantic Search Example:
  query: "How do I authenticate users?"
  Result: Files about authentication, login, security, even if they don't use the word "user"

Usage:

import asyncio
from agent_semantic_search_integration import KNOAgentSemanticSearch

async def search_example():
    search = KNOAgentSemanticSearch(base_directory="./KNO")
    await search.initialize()
    
    # Search 1: Question-like query
    results1 = await search.search_files("How do I handle database errors?")
    
    # Search 2: Concept query
    results2 = await search.search_files("API endpoints for user management")
    
    # Search 3: Functional query
    results3 = await search.search_files("websocket real-time communication")
    
    # Display results
    for query_results in [results1, results2, results3]:
        for result in query_results:
            print(f"📄 {result['file_path']}")
            print(f"   Relevance: {result['relevance_score']}%")
            print(f"   Content: {result['summary']}")
            print()

asyncio.run(search_example())
"""


# ============================================================================
# 4. EDEX-UI INTEGRATION
# ============================================================================

"""
الخطوة 4: تكامل eDEX-UI
Step 4: eDEX-UI Integration

When you perform searches or index directories, the progress bar is automatically
updated in eDEX-UI through the edex_status.json file.

Progress Bar Features:
✓ Real-time percentage updates
✓ Color coding (Red→Orange→Yellow→Green)
✓ File name display
✓ Operation type (indexing/searching)
✓ Time elapsed
✓ Items processed

Status File Format (edex_status.json):
{
  "version": "3.0",
  "timestamp": "2026-03-09T10:30:45.123456",
  "progress": {
    "operation": "indexing",
    "current": 45,
    "total": 100,
    "percentage": 45.0,
    "status": "🗂️ Indexing: agent.py",
    "file_name": "agent.py",
    "elapsed_seconds": 23.45
  },
  "ui_elements": {
    "progress_bar": {
      "visible": true,
      "percentage": 45.0,
      "label": "🗂️ Indexing: agent.py",
      "color": "#FFAA44",
      "animated": true
    },
    "status_text": {
      "primary": "🗂️ Indexing: agent.py",
      "secondary": "45/100 items",
      "operation": "indexing"
    }
  }
}
"""


# ============================================================================
# 5. ADVANCED FEATURES
# ============================================================================

"""
الخطوة 5: الميزات المتقدمة
Step 5: Advanced Features

A. Caching Search Results
   Searches are cached for faster subsequent queries
   
   search = KNOAgentSemanticSearch()
   await search.initialize()
   
   # First call - will index and search
   results1 = await search.search_files("authentication")
   
   # Second call - will return cached results immediately
   results2 = await search.search_files("authentication")
   
   # Skip cache if needed
   results3 = await search.search_files("authentication", skip_cache=True)
   
   # Clear cache
   search.clear_cache()

B. Get Statistics
   metrics = search.get_metrics()
   print(f"Indexed Files: {metrics['indexed_files']}")
   print(f"Total Chunks: {metrics['total_chunks']}")
   print(f"Indexing Time: {metrics['indexing_time_seconds']}s")

C. Search with Details
   details = await search.search_with_details("database")
   print(f"Query: {details['query']}")
   print(f"Results: {details['result_count']}")
   print(f"Metrics: {details['metrics']}")

D. eDEX Command Handler
   from agent_semantic_search_integration import EDEXCommandHandler
   
   handler = EDEXCommandHandler()
   
   # From eDEX interface
   result = await handler.handle_search_command("authentication logic")
   
   result = await handler.handle_index_command("./src")
"""


# ============================================================================
# 6. INTEGRATION WITH KNO AGENT
# ============================================================================

"""
الخطوة 6: التكامل مع وكيل KNO
Step 6: KNO Agent Integration

Add to your agent.py or main agent file:

async def on_search_command(query: str):
    '''Handle semantic search commands in the agent'''
    
    from agent_semantic_search_integration import KNOAgentSemanticSearch
    
    # Get or create search instance
    search = KNOAgentSemanticSearch()
    
    # Initialize if first time
    if not search.search_system.initialized:
        await search.initialize()
    
    # Perform search
    results = await search.search_files(query, max_results=10)
    
    # Process results
    for result in results:
        print(f"Found: {result['file_path']} ({result['relevance_score']}%)")
    
    return results

# Usage in agent
results = asyncio.run(on_search_command("user authentication"))
"""


# ============================================================================
# 7. FILE TYPES SUPPORTED
# ============================================================================

"""
الملفات المدعومة
Supported File Types:

✓ Python (.py)          - Full semantic analysis
✓ JavaScript (.js, .ts) - Function and class detection
✓ Java (.java)          - Method and class extraction
✓ C# (.cs)              - Code semantic analysis
✓ C++ (.cpp, .h)        - Header and implementation analysis
✓ JSON (.json)          - Key-value semantic extraction
✓ YAML (.yml, .yaml)    - Configuration semantic analysis
✓ XML (.xml)            - Element semantic extraction
✓ Markdown (.md)        - Document section analysis
✓ Text (.txt)           - Plain text analysis

Ignored Directories:
✗ __pycache__
✗ node_modules
✗ .git
✗ dist
✗ build
✗ venv
"""


# ============================================================================
# 8. EXAMPLE QUERIES
# ============================================================================

"""
أمثلة على الاستعلامات
Example Query Types:

1. Question-based queries:
   "How do I authenticate users?"
   "Where is error handling implemented?"
   "What functions handle database operations?"

2. Feature-based queries:
   "User authentication implementation"
   "Database connection management"
   "API endpoint definitions"

3. Technology-based queries:
   "WebSocket communication"
   "JSON parsing logic"
   "Async/await patterns"

4. Problem-based queries:
   "Exception handling and error recovery"
   "Memory optimization"
   "Performance tuning"

5. Concept-based queries:
   "Security mechanisms"
   "Logging and monitoring"
   "Configuration management"
"""


# ============================================================================
# 9. PERFORMANCE TIPS
# ============================================================================

"""
نصائح الأداء
Performance Tips:

1. Index once, search many times
   await search.index_directory()  # Do this once
   await search.search_files(query1)  # Then search multiple times
   await search.search_files(query2)

2. Use max_results to limit results
   # Good
   results = await search.search_files(query, max_results=10)
   
   # Intensive
   results = await search.search_files(query, max_results=1000)

3. Cache results
   # Searches are automatically cached
   # Subsequent identical queries are fast
   
   # Clear cache only when needed
   search.clear_cache()  # Clears entire cache
   
4. Batch searches
   queries = ["auth", "database", "api"]
   results = {q: await search.search_files(q) for q in queries}

5. Monitor metrics
   metrics = search.get_metrics()
   print(f"Cache size: {len(search.search_cache)}")
   print(f"Total chunks: {metrics['total_chunks']}")
"""


# ============================================================================
# 10. TROUBLESHOOTING
# ============================================================================

"""
استكشاف الأخطاء
Troubleshooting:

Q: "No files indexed. Please call index_directory() first."
A: You need to initialize and index before searching
   await search.initialize()
   await search.index_directory()

Q: Search results are empty
A: Try different query wording
   "user login" vs "authenticate users" vs "authentication system"

Q: Indexing is slow
A: This is normal for first indexing
   Use cached results for subsequent searches

Q: edex_status.json not updating
A: Check file permissions
   Check that status_file path is correct
   Ensure eDEX-UI is watching this file

Q: Memory usage high
A: Reduce max_results
   Clear cache periodically: search.clear_cache()
   Index smaller directories

Q: Model download fails
A: Internet connection required for first model download
   Model is cached after first download
   Can specify offline_mode or use keyword search
"""


# ============================================================================
# 11. API REFERENCE
# ============================================================================

"""
مرجع API
API Reference:

Class: KNOAgentSemanticSearch

Methods:
  
  async initialize() -> bool
    Initialize the search system and load models
    
  async search_files(
    query: str,
    max_results: int = 10,
    skip_cache: bool = False
  ) -> List[Dict[str, Any]]
    Perform semantic search
    
  async index_directory(directory: str = None) -> bool
    Index a directory for semantic search
    
  def get_metrics() -> Dict[str, Any]
    Get indexing statistics
    
  def get_cached_results(query: str) -> Optional[List[Dict]]
    Get cached results for a query
    
  def clear_cache() -> None
    Clear the search cache
    
  async search_with_details(query: str, max_results: int = 10) -> Dict
    Search with detailed metadata


Return Format for search_files():
[
  {
    'file_path': '/path/to/file.py',
    'file_type': 'python',
    'relevance_score': 87.5,          # 0-100
    'matched_content': 'def authenticate(user):',
    'line_numbers': [45],
    'keywords': ['authenticate', 'user', 'token'],
    'summary': 'def authenticate(user):'
  },
  ...
]
"""


# ============================================================================
# 12. COMPLETE EXAMPLE
# ============================================================================

"""
مثال شامل
Complete Example:

import asyncio
from agent_semantic_search_integration import (
    KNOAgentSemanticSearch,
    EDEXCommandHandler
)

async def main():
    # 1. Initialize search system
    print("🔧 Setting up semantic search...")
    search = KNOAgentSemanticSearch(
        base_directory="./KNO",
        status_file="edex_status.json"
    )
    
    # 2. Initialize models
    print("📦 Loading models...")
    await search.initialize()
    
    # 3. Index directory (progress shown in eDEX-UI)
    print("📁 Indexing directory...")
    await search.index_directory()
    
    # 4. Show metrics
    metrics = search.get_metrics()
    print(f"\\n✅ Indexing Complete!")
    print(f"   Files Indexed: {metrics['indexed_files']}")
    print(f"   Total Chunks: {metrics['total_chunks']}")
    print(f"   Time: {metrics['indexing_time_seconds']:.2f}s")
    
    # 5. Perform searches
    print(f"\\n🔍 Searching...")
    queries = [
        "user authentication and login",
        "error handling and exceptions",
        "database operations"
    ]
    
    for query in queries:
        print(f"\\n  Query: {query}")
        results = await search.search_files(query, max_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"    {i}. {result['file_path']} ({result['relevance_score']}%)")
    
    # 6. Optional: Use command handler for eDEX interface
    print(f"\\n⚙️  Setting up eDEX command handler...")
    handler = EDEXCommandHandler()
    
    cmd_result = await handler.handle_search_command("websocket integration")
    if cmd_result['success']:
        print(f"   Found {cmd_result['result_count']} results via eDEX")

# Run example
if __name__ == "__main__":
    asyncio.run(main())
"""


# ============================================================================
# FINAL NOTES
# ============================================================================

"""
ملاحظات نهائية
Final Notes:

✅ This system provides:
   - Semantic search by meaning (not just keywords)
   - Real-time progress visualization in eDEX-UI
   - Automatic caching for performance
   - Support for multiple file types
   - Easy integration with KNO agent

🚀 Next Steps:
   1. Install dependencies: pip install sentence-transformers
   2. Import and initialize: KNOAgentSemanticSearch()
   3. Index your directory: await search.index_directory()
   4. Start searching: await search.search_files("your query")

📚 Documentation:
   - semantic_search_advanced.py - Core engine
   - agent_semantic_search_integration.py - Integration layer
   - edex_status.json - Progress visualization

❓ Questions?
   Check the logs: semantic_search.log
   Review error messages for details
   Adjust query wording for better results

Happy searching! 🔍
"""
