"""
KNO Semantic File System - Complete Documentation
================================================

Complete guide for the Semantic File System (SFS) v2.0

Table of Contents:
1. Overview
2. Installation
3. Quick Start
4. Core Features
5. API Reference
6. Integration Guide
7. Performance Tips
8. Troubleshooting
9. Examples

Author: KNO Architecture
License: MIT
Last Updated: 2026-03-09
"""

# ============================================================================
# 1. OVERVIEW
# ============================================================================

"""
The Semantic File System (SFS) is an intelligent file management system
that uses advanced machine learning to understand and search files by their
semantic meaning, not just their filenames.

Key Concepts:
- Vector Embeddings: Convert text to numerical vectors using Sentence-Transformers
- Semantic Search: Find files by meaning, not keywords
- Multiple Backends: Choose between ChromaDB or FAISS
- Async Operations: All operations are non-blocking
- Real-time Progress: Track indexing progress in real-time

Architecture:
    User Application
           ↓
    KNOFileSystem API
           ↓
    +─────────────────────────────────┐
    │ Sentence-Transformers Model     │
    │ (all-MiniLM-L6-v2)             │
    └─────────────────────────────────┘
           ↓
    +─────────────────────────────────┐
    │ Database Backend                │
    ├─────────────────────────────────┤
    │ ChromaDB OR FAISS               │
    │ (Vector Database)               │
    └─────────────────────────────────┘
           ↓
    Local Storage (./sfs_index)
"""

# ============================================================================
# 2. INSTALLATION
# ============================================================================

"""
## Step 1: Install Dependencies

```bash
# Option A: Install all packages from requirements
pip install -r requirements-semantic-fs.txt

# Option B: Install manually
pip install sentence-transformers>=2.2.0
pip install chromadb>=0.3.21
pip install faiss-cpu>=1.7.2  # or faiss-gpu for GPU support
pip install PyPDF2>=3.0.0
```

## Step 2: Verify Installation

```python
from semantic_file_system_enhanced import KNOFileSystem
print("✓ Semantic File System installed successfully")
```

## Supported Python Versions
- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+

## Hardware Requirements
- Minimum: 2GB RAM
- Recommended: 8GB+ RAM
- GPU: Optional (speeds up embeddings)

## Supported File Types
- Text files (.txt)
- Markdown (.md, .markdown)
- Python code (.py)
- JSON (.json)
- PDF (.pdf) - requires PyPDF2
- Other code files (.js, .ts, .java, .cpp, .c, .go, .rs, .sh)
"""

# ============================================================================
# 3. QUICK START
# ============================================================================

"""
## Async Usage (Recommended)

```python
import asyncio
from semantic_file_system_enhanced import KNOFileSystem

async def main():
    # Create instance
    fs = KNOFileSystem(
        index_dir="./sfs_index",
        use_chroma=True,  # or False for FAISS
    )
    
    # Initialize
    if not await fs.initialize():
        print("Failed to initialize")
        return
    
    # Index a directory
    metrics = await fs.index_directory("/path/to/files", recursive=True)
    print(f"Indexed {metrics.indexed_files}/{metrics.total_files} files")
    
    # Search
    results = await fs.search_files("authentication system", top_k=5)
    for result in results:
        print(f"  {result.file_path}: {result.relevance_score:.1%}")
    
    # Get statistics
    stats = fs.get_statistics()
    print(f"Total indexed: {stats['indexed_files_count']}")

asyncio.run(main())
```

## Synchronous Usage (For GUI/Callbacks)

```python
from semantic_file_system_enhanced import KNOFileSystemSync

# Create instance
fs = KNOFileSystemSync(index_dir="./sfs_index")

# Initialize
if not fs.initialize():
    print("Failed to initialize")
    exit()

# Index directory (blocking)
metrics = fs.index_directory("/path/to/files", recursive=True)

# Search (blocking)
results = fs.search_files("error handling", top_k=3)

# Get stats
stats = fs.get_statistics()
```
"""

# ============================================================================
# 4. CORE FEATURES
# ============================================================================

"""
## Feature 1: Intelligent Indexing

The system automatically:
- Detects file types
- Extracts text content (including PDFs)
- Splits content into intelligent chunks
- Ignores sensitive/system files
- Calculates file hashes for change detection
- Extracts keywords

Configuration:
```python
fs = KNOFileSystem(
    index_dir="./sfs_index",           # Where to store index
    use_chroma=True,                   # Backend choice
    model_name="all-MiniLM-L6-v2",     # Embedding model
    ignore_patterns=[...],             # Custom ignore list
    batch_size=32,                     # Embedding batch size
)

# Customize chunking
TEXT_CHUNK_SIZE = 500      # words per chunk
TEXT_OVERLAP = 75          # overlap in words
MIN_CHUNK_LENGTH = 20      # minimum words per chunk
```

## Feature 2: Semantic Search

Search by meaning, not keywords:
```python
# These all find similar results:
await fs.search_files("user login system")
await fs.search_files("authenticate users")
await fs.search_files("securely verify identity")

# Advanced parameters
results = await fs.search_files(
    query="database configuration",
    top_k=10,                          # Return top 10
    similarity_threshold=0.4,          # Minimum relevance
)

# Results include:
# - file_path: Full path to file
# - file_type: Type of file
# - relevance_score: 0-1 (higher = more relevant)
# - content_excerpt: First 500 chars
# - keywords: Extracted keywords
# - rank: Position in results
```

## Feature 3: Multiple Backends

### ChromaDB (Recommended)
- Persistent storage
- Faster queries
- Better for production
- Requires: chromadb

```python
fs = KNOFileSystem(use_chroma=True)
```

### FAISS
- Lightweight
- In-memory storage
- Better for large datasets
- Requires: faiss-cpu or faiss-gpu

```python
fs = KNOFileSystem(use_chroma=False)
```

## Feature 4: Real-time Progress Tracking

```python
async def progress_callback(current, total):
    percentage = int(current / total * 100)
    print(f"Progress: {current}/{total} ({percentage}%)")

metrics = await fs.index_directory(
    "/path/to/files",
    callback=progress_callback
)

# Or check status anytime
print(f"Status: {fs.indexing_status}")  # idle, indexing, optimizing, completed
```

## Feature 5: Comprehensive Statistics

```python
stats = fs.get_statistics()

# Returns:
{
    'indexed_files_count': 150,
    'total_chunks': 1200,
    'total_size_mb': 45.3,
    'database_type': 'ChromaDB',
    'indexing_status': 'idle',
    'model_loaded': True,
    'last_index_time': '2026-03-09T...',
    'indexed_files': 150,
    'failed_files': 0,
    'success_rate': 100.0,
}
```
"""

# ============================================================================
# 5. API REFERENCE
# ============================================================================

"""
## KNOFileSystem Class

### Constructor
KNOFileSystem(
    index_dir: Optional[str] = None,
    edex_status_file: Optional[str] = None,
    use_chroma: bool = True,
    model_name: str = "all-MiniLM-L6-v2",
    ignore_patterns: List[str] = None,
    batch_size: int = 32,
)

### Async Methods

#### initialize() -> bool
Initialize the filesystem and load models.
```python
success = await fs.initialize()
```

#### index_directory(directory, recursive=True, callback=None) -> IndexingMetrics
Index all files in a directory.
```python
metrics = await fs.index_directory("/path", recursive=True)
# Returns: indexed_files, total_files, failed_files, total_chunks, etc.
```

#### index_file(file_path: str) -> bool
Index a single file.
```python
success = await fs.index_file("/path/to/file.py")
```

#### search_files(query, top_k=5, similarity_threshold=0.3) -> List[SearchResult]
Search for files semantically.
```python
results = await fs.search_files("query", top_k=10)
```

#### clear_indexes() -> bool
Remove all indexes.
```python
success = await fs.clear_indexes()
```

### Sync Methods

#### initialize() -> bool
```python
success = fs.initialize()
```

#### index_directory(directory, recursive=True) -> IndexingMetrics
```python
metrics = fs.index_directory("/path")
```

#### search_files(query, top_k=5) -> List[SearchResult]
```python
results = fs.search_files("query")
```

### Properties

#### indexing_status
Current indexing status: 'idle', 'indexing', 'optimizing', 'completed', 'error'
```python
status = fs.indexing_status
```

### Data Classes

#### SearchResult
```python
@dataclass
class SearchResult:
    file_path: str           # Full path to file
    file_type: str          # File type (python, markdown, etc.)
    chunk_index: int        # Chunk position
    relevance_score: float  # 0-1, higher = more relevant
    content_excerpt: str    # First 500 characters
    matched_query: str      # Original query
    keywords: List[str]     # Extracted keywords
    rank: int              # Result position
```

#### IndexingMetrics
```python
@dataclass
class IndexingMetrics:
    indexed_files: int          # Successfully indexed
    total_files: int           # Total scanned
    failed_files: int          # Failed indexing
    total_chunks: int          # Total text chunks
    total_size_mb: float       # Total indexed size
    indexing_time_seconds: float

    def get_success_rate() -> float
```
"""

# ============================================================================
# 6. INTEGRATION GUIDE
# ============================================================================

"""
## Integration with LLMCoordinator

### Step 1: Create Coordinator

```python
from semantic_file_system_enhanced import KNOFileSystem
from semantic_fs_coordinator_v2 import SemanticFSCoordinator

fs = KNOFileSystem()
await fs.initialize()

coordinator = SemanticFSCoordinator(fs)
```

### Step 2: Get Tool Definitions

```python
tools = coordinator.get_tool_definitions()
# Returns list of tools compatible with OpenAI API
```

### Step 3: Execute Tools

```python
result = await coordinator.execute_tool(
    "search_knowledge_base",
    {"query": "authentication", "top_k": 5}
)

result = await coordinator.execute_tool(
    "get_file_content",
    {"file_path": "/path/to/file.py"}
)
```

### Available Tools

1. **search_knowledge_base**
   - Search files semantically
   - Parameters: query (required), top_k, similarity_threshold

2. **get_file_content**
   - Retrieve full file content
   - Parameters: file_path (required)

3. **get_knowledge_base_stats**
   - Get indexing statistics
   - Parameters: none

4. **index_directory**
   - Index a directory
   - Parameters: directory (required), recursive

5. **clear_knowledge_base**
   - Clear all indexes
   - Parameters: none (WARNING: irreversible)

### Integration Example

```python
async def answer_with_context(user_query):
    # 1. Search knowledge base
    search_result = await coordinator.execute_tool(
        "search_knowledge_base",
        {"query": user_query, "top_k": 3}
    )
    
    # 2. Get relevant files
    files_to_read = [r['file'] for r in search_result['results']]
    
    # 3. Retrieve content
    context = ""
    for file_path in files_to_read:
        file_result = await coordinator.execute_tool(
            "get_file_content",
            {"file_path": file_path}
        )
        if file_result['success']:
            context += file_result['content']
    
    # 4. Send to LLM with context
    response = await llm.generate(
        query=user_query,
        context=context,
    )
    
    return response
```
"""

# ============================================================================
# 7. PERFORMANCE TIPS
# ============================================================================

"""
## Optimization Tips

### 1. Choose Right Backend
```
ChromaDB:
  - Better for: Production, frequent searches, persistence
  - Speed: Medium-fast
  - Memory: ~500MB-2GB for 10k files

FAISS:
  - Better for: Large datasets, development
  - Speed: Very fast
  - Memory: Lower than ChromaDB
```

### 2. Tune Batch Size
```python
# Larger batch size = faster but more memory
fs = KNOFileSystem(batch_size=64)  # Default: 32

# Recommended by RAM:
# 2GB: batch_size=8
# 8GB: batch_size=32
# 16GB: batch_size=64
```

### 3. Optimize Chunking
```python
# Larger chunks = fewer chunks but less granular search
TEXT_CHUNK_SIZE = 750        # Default: 500
TEXT_OVERLAP = 100            # Default: 75

# Recommended by file types:
# Code: chunk_size=500, overlap=50
# Docs: chunk_size=750, overlap=100
# Mixed: chunk_size=500, overlap=75
```

### 4. Use Appropriate Model
```python
# Fast (default)
fs = KNOFileSystem(model_name="all-MiniLM-L6-v2")

# Very fast but lower quality
fs = KNOFileSystem(model_name="all-MiniLM-L12-v1")

# Slower but higher quality
fs = KNOFileSystem(model_name="all-mpnet-base-v2")
```

### 5. Cache Management
```python
# Coordinator keeps last 100 files in cache
coordinator.clear_cache()  # Free memory
cache_stats = coordinator.get_cache_stats()
```

### 6. Parallel Operations
```python
# Index multiple directories
results = await asyncio.gather(
    fs.index_directory('/path1'),
    fs.index_directory('/path2'),
    fs.index_directory('/path3'),
)
```

## Performance Benchmarks

Typical performance on modern hardware:
- Embedding generation: ~50-100 files/second
- Search: ~10-50ms per query
- Memory: ~1-2MB per indexed file
"""

# ============================================================================
# 8. TROUBLESHOOTING
# ============================================================================

"""
## Common Issues

### Issue 1: "sentence-transformers not installed"
Solution:
```bash
pip install sentence-transformers>=2.2.0
```

### Issue 2: "Neither ChromaDB nor FAISS available"
Solution:
```bash
pip install chromadb>=0.3.21
# OR
pip install faiss-cpu>=1.7.2
```

### Issue 3: Out of Memory
Solution:
- Reduce batch_size: `KNOFileSystem(batch_size=8)`
- Use FAISS instead of ChromaDB
- Clear cache: `coordinator.clear_cache()`
- Search in smaller directories

### Issue 4: Very slow search
Solution:
- Use FAISS backend
- Reduce top_k parameter
- Use higher similarity_threshold
- Increase batch_size for indexing

### Issue 5: PDF extraction not working
Solution:
```bash
pip install PyPDF2>=3.0.0
```

### Issue 6: Index file not found after indexing
Solution:
- The file might be ignored by default patterns
- Check: `should_ignore_file(path, fs.ignore_patterns)`
- Customize ignore patterns: `KNOFileSystem(ignore_patterns=[...])`

## Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('KNO.SemanticFS')
logger.setLevel(logging.DEBUG)
```
"""

# ============================================================================
# 9. EXAMPLES
# ============================================================================

"""
## Example 1: Index Project and Analyze

```python
import asyncio
from semantic_file_system_enhanced import KNOFileSystem

async def analyze_project(project_path):
    fs = KNOFileSystem(index_dir="./analysis_index")
    await fs.initialize()
    
    # Index the project
    metrics = await fs.index_directory(project_path, recursive=True)
    
    print(f"Project Analysis")
    print(f"================")
    print(f"Files indexed: {metrics.indexed_files}")
    print(f"Total size: {metrics.total_size_mb:.2f} MB")
    print(f"Success rate: {metrics.get_success_rate():.1f}%")
    
    # Analyze areas
    areas = [
        "authentication",
        "database operations",
        "error handling",
        "testing",
        "configuration",
    ]
    
    for area in areas:
        results = await fs.search_files(area, top_k=3)
        print(f"\\n{area.title()}:")
        for result in results:
            print(f"  - {result.file_path}: {result.relevance_score:.0%}")

asyncio.run(analyze_project("./my_project"))
```

## Example 2: Build Documentation Index

```python
async def index_documentation():
    fs = KNOFileSystem(
        index_dir="./doc_index",
        use_chroma=True,
    )
    await fs.initialize()
    
    # Index documentation
    docs_dir = "/path/to/docs"
    metrics = await fs.index_directory(docs_dir)
    
    # Example searches
    queries = [
        "how to install",
        "API reference",
        "troubleshooting",
        "quick start",
    ]
    
    for query in queries:
        results = await fs.search_files(query, top_k=2)
        print(f"Query: {query}")
        for r in results:
            print(f"  → {r.file_path}: {r.relevance_score:.1%}")
```

## Example 3: GUI Integration

```python
import tkinter as tk
from semantic_file_system_enhanced import KNOFileSystemSync

class SearchGUI:
    def __init__(self, root):
        self.fs = KNOFileSystemSync()
        self.fs.initialize()
        
        self.root = root
        self.root.title("Semantic Search")
        
        # Create widgets
        search_frame = tk.Frame(root)
        search_frame.pack()
        
        self.query_entry = tk.Entry(search_frame)
        self.query_entry.pack()
        
        search_btn = tk.Button(
            search_frame,
            text="Search",
            command=self.on_search
        )
        search_btn.pack()
        
        self.results_text = tk.Text(root, height=10, width=60)
        self.results_text.pack()
    
    def on_search(self):
        query = self.query_entry.get()
        results = self.fs.search_files(query, top_k=5)
        
        self.results_text.delete(1.0, tk.END)
        for result in results:
            text = f"[{result.rank}] {result.file_path}\\n"
            text += f"    Relevance: {result.relevance_score:.0%}\\n"
            text += f"    {result.content_excerpt[:100]}...\\n\\n"
            self.results_text.insert(tk.END, text)

root = tk.Tk()
app = SearchGUI(root)
root.mainloop()
```

## Example 4: Real-time Progress Monitoring

```python
async def index_with_progress(directory):
    fs = KNOFileSystem()
    await fs.initialize()
    
    progress_file = Path("indexing_progress.json")
    
    async def update_progress(current, total):
        progress = {
            "current": current,
            "total": total,
            "percentage": int(current / total * 100),
            "status": fs.indexing_status,
        }
        progress_file.write_text(json.dumps(progress))
    
    metrics = await fs.index_directory(
        directory,
        callback=update_progress
    )
    
    return metrics
```
"""

# ============================================================================
# SUMMARY
# ============================================================================

"""
The KNO Semantic File System provides enterprise-grade semantic search
capabilities for file management. With support for multiple backends,
async operations, and LLM integration, it's ideal for knowledge management,
code analysis, and intelligent document retrieval.

Key Takeaways:
1. Easy to use: Simple API for complex operations
2. Powerful: Semantic understanding of file content
3. Flexible: Choose between ChromaDB or FAISS
4. Fast: Asynchronous operations, caching, optimization
5. Integrated: Works seamlessly with LLMCoordinator

For questions and support, see README.md or open an issue.
"""
