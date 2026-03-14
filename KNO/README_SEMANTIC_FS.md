# KNO Semantic File System v2.0

<div align="center">

**Advanced Semantic Indexing & Search for KNO Operating System**

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/status-production-brightgreen.svg)](#)

[Features](#features) • [Installation](#installation) • [Quick Start](#quick-start) • [API](#api) • [Docs](#documentation)

</div>

---

## 🎯 Overview

The **Semantic File System (SFS)** is the intelligent file management core for KNO OS. It uses cutting-edge machine learning to understand file content by meaning, not just keywords. 

### Key Innovation
Instead of traditional file search ("find files named 'auth.py'"), semantic search finds "files related to authentication" - even if they're named differently or scattered across folders.

```
Traditional Search: "Find files with 'auth' in the name"
❌ Misses authentication.py, user_login.py, verify.py

Semantic Search: "Find files about authentication"  
✅ Finds: authentication.py, user_login.py, verify.py, session.py
```

---

## ✨ Features

### 🔍 **Semantic Search**
- Search files by meaning, not keywords
- Automatic keyword extraction
- Relevance scoring (0-100%)
- Similarity threshold customization

### 🚀 **High Performance**
- Asynchronous operations (non-blocking)
- Batch processing optimization
- Smart caching system
- Real-time progress tracking

### 🗄️ **Flexible Backends**
- **ChromaDB** (Recommended): Persistent, production-ready
- **FAISS**: Lightweight, ultra-fast for large datasets
- Automatic fallback support

### 📁 **Rich File Support**
- Text (.txt, .md)
- Code (Python, JavaScript, Java, C++, Go, Rust, etc.)
- Documents (.pdf)
- Structured data (.json)
- Intelligent PDF extraction

### 🔐 **Security First**
- Ignores sensitive files (.env, credentials)
- Configurable ignore patterns
- Safe by default

### 🤖 **LLM Integration**
- OpenAI-compatible tool definitions
- Function calling support
- Context-aware retrieval
- Works with any LLM coordinator

---

## 📦 Installation

### Requirements
- Python 3.8+
- ~2GB RAM minimum, 8GB+ recommended
- ~500MB for embedding models

### Step 1: Install Package
```bash
pip install -r requirements-semantic-fs.txt
```

### Step 2: Verify Installation
```python
from semantic_file_system_enhanced import KNOFileSystem
print("✓ Installation successful!")
```

---

## 🚀 Quick Start

### Async Usage (Recommended)
```python
import asyncio
from semantic_file_system_enhanced import KNOFileSystem

async def main():
    # Initialize
    fs = KNOFileSystem(index_dir="./sfs_index")
    if not await fs.initialize():
        print("Failed to initialize")
        return
    
    # Index your files
    metrics = await fs.index_directory("/path/to/files")
    print(f"✓ Indexed {metrics.indexed_files} files")
    
    # Search semantically
    results = await fs.search_files("authentication system", top_k=5)
    for result in results:
        print(f"  [{result.rank}] {result.file_path}: {result.relevance_score:.1%}")

asyncio.run(main())
```

### Synchronous Usage (GUI/Callbacks)
```python
from semantic_file_system_enhanced import KNOFileSystemSync

# Create and initialize
fs = KNOFileSystemSync(index_dir="./sfs_index")
fs.initialize()

# Index files (blocking)
metrics = fs.index_directory("/path/to/files")

# Search (blocking)
results = fs.search_files("error handling", top_k=3)

# View results
for r in results:
    print(f"{r.file_path}: {r.relevance_score:.0%}")
```

---

## 🔧 API Reference

### Core Methods

#### `async initialize() → bool`
Load embedding model and database backend.

#### `async index_directory(path, recursive=True, callback=None) → IndexingMetrics`
Index all files in a directory.
- `path` (str): Directory path
- `recursive` (bool): Include subdirectories
- `callback` (Callable): Progress callback function
- Returns: Metrics with `indexed_files`, `total_chunks`, `success_rate`, etc.

#### `async search_files(query, top_k=5, similarity_threshold=0.3) → List[SearchResult]`
Search files semantically.
- `query` (str): Search query
- `top_k` (int): Maximum results
- `similarity_threshold` (float): Minimum relevance (0-1)
- Returns: List of `SearchResult` objects with relevance scores

#### `get_statistics() → Dict`
Get indexing statistics and status.

#### `async clear_indexes() → bool`
Remove all indexes (irreversible!).

### Data Structures

#### `SearchResult`
```python
@dataclass
class SearchResult:
    file_path: str              # Full file path
    file_type: str              # python, markdown, text, etc.
    chunk_index: int            # Position in file
    relevance_score: float      # 0-1 (1 = perfect match)
    content_excerpt: str        # First 500 characters
    matched_query: str          # Original search query
    keywords: List[str]         # Extracted keywords
    rank: int                   # Position in results
```

#### `IndexingMetrics`
```python
@dataclass
class IndexingMetrics:
    indexed_files: int          # Successfully indexed
    total_files: int           # Total scanned
    failed_files: int          # Failed indexing
    total_chunks: int          # Text chunks created
    total_size_mb: float       # Total indexed size
    indexing_time_seconds: float
    
    def get_success_rate() → float  # 0-100
```

---

## 🤖 LLM Integration

Seamlessly integrate with LLM coordinators for intelligent context retrieval:

```python
from semantic_fs_coordinator_v2 import SemanticFSCoordinator

# Create coordinator
coordinator = SemanticFSCoordinator(fs)

# Get tools for function calling
tools = coordinator.get_tool_definitions()

# Execute tools
result = await coordinator.execute_tool(
    "search_knowledge_base",
    {"query": "authentication", "top_k": 5}
)

# Result formats automatically for LLM context
```

### Available Tools
- `search_knowledge_base` - Semantic file search
- `get_file_content` - Retrieve full file content
- `get_knowledge_base_stats` - Index statistics
- `index_directory` - Add files to index
- `clear_knowledge_base` - Reset index

---

## 🧪 Testing

Run comprehensive test suite:

```bash
python test_semantic_fs.py
```

Tests included:
- ✓ Initialization
- ✓ ChromaDB backend
- ✓ FAISS backend
- ✓ File indexing
- ✓ Semantic search
- ✓ Coordinator integration
- ✓ Statistics & metrics
- ✓ Memory efficiency

---

## 📊 Performance

Typical performance on modern hardware (8GB RAM, Intel Core i7):

| Operation | Time | Notes |
|-----------|------|-------|
| Initialize | 5-10s | Download embedding model |
| Index 100 files | 30-60s | Depends on file sizes |
| Semantic search | 10-50ms | Per query |
| Memory per file | 1-2MB | Indexed only |

**Optimizations:**
- Use FAISS for faster search on large datasets
- Increase batch_size (default: 32) for faster indexing
- Enable GPU with `faiss-gpu` for 10x speedup

---

## 📚 Documentation

Comprehensive documentation available in:
- [`SEMANTIC_FS_DOCUMENTATION.md`](SEMANTIC_FS_DOCUMENTATION.md) - Complete guide
- [Code comments in `semantic_file_system_enhanced.py`](semantic_file_system_enhanced.py) - API docs
- [Examples in `test_semantic_fs.py`](test_semantic_fs.py) - Usage examples

---

## 🎓 Examples

### Example 1: Index and Search
```python
async def analyze_codebase():
    fs = KNOFileSystem()
    await fs.initialize()
    
    # Index codebase
    metrics = await fs.index_directory("./src", recursive=True)
    print(f"Indexed {metrics.indexed_files} files")
    
    # Find error handling code
    results = await fs.search_files("error handling", top_k=5)
    for r in results:
        print(f"  {r.file_path}: {r.relevance_score:.0%}")
```

### Example 2: Real-time Progress
```python
async def index_with_progress():
    fs = KNOFileSystem()
    await fs.initialize()
    
    async def show_progress(current, total):
        pct = int(current / total * 100)
        print(f"  [{pct}%] {current}/{total}")
    
    await fs.index_directory("/docs", callback=show_progress)
```

### Example 3: Batch Operations
```python
async def index_multiple_projects():
    fs = KNOFileSystem()
    await fs.initialize()
    
    # Index multiple directories in parallel
    results = await asyncio.gather(
        fs.index_directory("/project1"),
        fs.index_directory("/project2"),
        fs.index_directory("/project3"),
    )
```

---

## 🐛 Troubleshooting

### "sentence-transformers not installed"
```bash
pip install sentence-transformers
```

### Out of Memory
```python
# Reduce batch size
fs = KNOFileSystem(batch_size=8)

# Or use FAISS (lighter)
fs = KNOFileSystem(use_chroma=False)
```

### Slow Search
- Use FAISS backend instead of ChromaDB
- Increase similarity_threshold
- Reduce top_k parameter

For more help, see [`SEMANTIC_FS_DOCUMENTATION.md`](SEMANTIC_FS_DOCUMENTATION.md#troubleshooting)

---

## 🔒 Security

The system is security-aware:
- Ignores `.env` files and credentials
- Skips hidden directories (`.git`, `.venv`)
- Avoids system files and executables
- Configurable ignore patterns

---

## 🏆 Architecture

```
Your Application
       ↓
KNOFileSystem API (async/sync)
       ↓
Sentence-Transformers (embeddings)
       ↓
┌─────────────────────────────┐
│ Vector Database Backend      │
├─────────────────────────────┤
│ ChromaDB (production)        │
│ or FAISS (lightweight)       │
└─────────────────────────────┘
       ↓
./sfs_index/ (local storage)
```

---

## 🤝 Integration with KNO

The SFS is designed as the core file management system for KNO OS:

1. **File Organization**: Maintains semantic index of all system files
2. **Knowledge Base**: Powers the LLM's ability to understand codebase
3. **Real-time Search**: Fast retrieval for documentation and code examples
4. **Self-Evolution**: Indexes and analyzes its own code for improvements

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file

---

## 🚀 Next Steps

1. **Install**: `pip install -r requirements-semantic-fs.txt`
2. **Read**: [`SEMANTIC_FS_DOCUMENTATION.md`](SEMANTIC_FS_DOCUMENTATION.md)
3. **Test**: `python test_semantic_fs.py`
4. **Integrate**: Use `SemanticFSCoordinator` with your LLM
5. **Deploy**: Use in production with ChromaDB backend

---

## 📧 Support

- Check documentation in `SEMANTIC_FS_DOCUMENTATION.md`
- Review examples in `test_semantic_fs.py`
- Check code comments for inline documentation
- Open issues for bugs or feature requests

---

**Built with ❤️ for the KNO Operating System**

*Last updated: 2026-03-09*
