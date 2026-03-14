"""
KNO Semantic File System - Quick Start Guide
===========================================

Follow these steps to get Semantic File System running in 5 minutes!

Created: 2026-03-09
"""

# ============================================================================
# STEP 1: INSTALLATION (1 minute)
# ============================================================================

"""
1. Install dependencies:
   
   pip install -r requirements-semantic-fs.txt

2. Verify installation:
   
   python -c "from semantic_file_system_enhanced import KNOFileSystem; print('✓ Ready!')"
"""

# ============================================================================
# STEP 2: BASIC USAGE (2 minutes)
# ============================================================================

"""
Create a file 'quick_demo.py' and run:
"""

import asyncio
from pathlib import Path

async def demo():
    """Quick demonstration of Semantic File System"""
    
    # Step 1: Import
    from semantic_file_system_enhanced import KNOFileSystem
    
    # Step 2: Create instance
    fs = KNOFileSystem(
        index_dir="./sfs_index_demo",
        use_chroma=True,  # Try False for faster FAISS
    )
    
    # Step 3: Initialize
    print("🔄 Initializing Semantic File System...")
    if not await fs.initialize():
        print("❌ Failed to initialize")
        return
    print("✓ Initialized")
    
    # Step 4: Index files
    print("\n📑 Indexing files...")
    # Index current directory (only .py, .md files)
    metrics = await fs.index_directory(".", recursive=False)
    print(f"✓ Indexed {metrics.indexed_files}/{metrics.total_files} files")
    print(f"  - Chunks: {metrics.total_chunks}")
    print(f"  - Time: {metrics.indexing_time_seconds:.2f}s")
    print(f"  - Success: {metrics.get_success_rate():.1f}%")
    
    # Step 5: Search
    print("\n🔍 Searching...")
    queries = [
        "semantic search and indexing",
        "file management",
        "configuration settings",
    ]
    
    for query in queries:
        results = await fs.search_files(query, top_k=2)
        print(f"\n  Query: '{query}'")
        for result in results:
            print(f"    [{result.rank}] {Path(result.file_path).name}")
            print(f"        Relevance: {result.relevance_score:.0%}")
            print(f"        Type: {result.file_type}")
    
    # Step 6: Statistics
    print("\n📊 Statistics:")
    stats = fs.get_statistics()
    print(f"  Total indexed: {stats['indexed_files_count']}")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Database: {stats['database_type']}")
    print(f"  Status: {stats['indexing_status']}")

# Run demo
if __name__ == "__main__":
    asyncio.run(demo())

# ============================================================================
# STEP 3: LLM INTEGRATION (2 minutes)
# ============================================================================

"""
To use with an LLM coordinator:

from semantic_fs_coordinator_v2 import SemanticFSCoordinator

async def integrate_with_llm():
    fs = KNOFileSystem()
    await fs.initialize()
    
    # Create coordinator
    coordinator = SemanticFSCoordinator(fs)
    
    # Index files
    await fs.index_directory("/your/project")
    
    # Get tools for function calling
    tools = coordinator.get_tool_definitions()
    
    # Use with LLM
    # Pass 'tools' to ChatGPT/Claude/etc.
    
    # When LLM needs file search:
    result = await coordinator.execute_tool(
        "search_knowledge_base",
        {"query": "user query", "top_k": 5}
    )
    
    # Use result in LLM response context

asyncio.run(integrate_with_llm())
"""

# ============================================================================
# COMMON CONFIGURATIONS
# ============================================================================

"""
## Configuration 1: Production Setup (Much data, fast search)
```python
fs = KNOFileSystem(
    index_dir="/var/lib/kno/sfs_index",
    use_chroma=True,           # Persistent storage
    model_name="all-MiniLM-L6-v2",  # Fast and accurate
    batch_size=64,             # Faster indexing
)
```

## Configuration 2: Development Setup (Fast indexing, memory efficient)
```python
fs = KNOFileSystem(
    index_dir="./sfs_index",
    use_chroma=False,          # FAISS (lighter)
    model_name="all-MiniLM-L12-v1",  # Faster
    batch_size=32,
)
```

## Configuration 3: High Quality Search
```python
fs = KNOFileSystem(
    index_dir="./sfs_index",
    use_chroma=True,
    model_name="all-mpnet-base-v2",  # Better quality
    batch_size=16,             # Lower batch for quality
)
```

## Configuration 4: GPU Acceleration
```python
# Use faiss-gpu (10x faster!)
fs = KNOFileSystem(
    index_dir="./sfs_index",
    use_chroma=False,          # Use FAISS with GPU
    batch_size=128,            # Can go higher with GPU
)
# Then just use normally - FAISS will use GPU automatically
```
"""

# ============================================================================
# QUICK REFERENCE
# ============================================================================

"""
## Async Pattern (Recommended)
```python
import asyncio
from semantic_file_system_enhanced import KNOFileSystem

async def main():
    fs = KNOFileSystem()
    await fs.initialize()
    
    metrics = await fs.index_directory("/path")
    results = await fs.search_files("query", top_k=5)
    
    stats = fs.get_statistics()

asyncio.run(main())
```

## Sync Pattern (GUI/Callbacks)
```python
from semantic_file_system_enhanced import KNOFileSystemSync

fs = KNOFileSystemSync()
fs.initialize()

metrics = fs.index_directory("/path")  # Blocking
results = fs.search_files("query", top_k=5)  # Blocking
```

## With Progress Callback
```python
async def with_progress():
    fs = KNOFileSystem()
    await fs.initialize()
    
    async def progress(current, total):
        pct = int(current / total * 100)
        print(f"[{pct}%] {current}/{total}")
    
    await fs.index_directory("/path", callback=progress)
```

## Multiple Searches
```python
async def batch_search():
    fs = KNOFileSystem()
    await fs.initialize()
    
    queries = ["auth", "database", "errors"]
    
    # Search all in parallel
    results = await asyncio.gather(*[
        fs.search_files(q, top_k=3) for q in queries
    ])
```

## Error Handling
```python
try:
    fs = KNOFileSystem()
    if not await fs.initialize():
        print("Init failed - check logs")
        return
    
    results = await fs.search_files("query", top_k=5)
except Exception as e:
    print(f"Error: {e}")
    # Check semantic_fs.log for details
```
"""

# ============================================================================
# TESTING
# ============================================================================

"""
## Run Test Suite
```bash
python test_semantic_fs.py
```

Expected output:
```
============================================================
KNO Semantic File System - Test Suite
============================================================

Running test_basic_initialization...
✓ Basic initialization test passed

Running test_chromadb_backend...
✓ ChromaDB backend test passed (5 files indexed)

... more tests ...

============================================================
Test Summary
============================================================
Passed:  8
Failed:  0
Skipped: 0

Success Rate: 100.0%
============================================================
```
"""

# ============================================================================
# TROUBLESHOOTING QUICK FIXES
# ============================================================================

"""
## Problem: "Module not found: sentence_transformers"
Fix: pip install sentence-transformers

## Problem: "No space left on device"
Fix: Reduce batch_size or use FAISS instead of ChromaDB

## Problem: "Very slow search"
Fix 1: Switch to FAISS backend (use_chroma=False)
Fix 2: Reduce top_k (e.g., 3 instead of 10)
Fix 3: Use GPU acceleration (faiss-gpu)

## Problem: "OutOfMemory"
Fix 1: fs = KNOFileSystem(batch_size=8)
Fix 2: fs = KNOFileSystem(use_chroma=False)
Fix 3: Clear cache: coordinator.clear_cache()

## Problem: "ChromaDB not found but FAISS too"
Fix: pip install chromadb faiss-cpu

## Problem: "Embedding model download stuck"
Fix: Manually set: export HF_HOME="/large/disk/path"
     Then retry
"""

# ============================================================================
# NEXT STEPS
# ============================================================================

"""
1. ✓ Run quick_demo.py to verify setup
   
2. ✓ Index your project:
   fs = KNOFileSystem()
   await fs.index_directory("/your/project")
   
3. ✓ Try searching:
   results = await fs.search_files("your query")
   
4. ✓ Integrate with LLM:
   coordinator = SemanticFSCoordinator(fs)
   # Use coordinator.get_tool_definitions() with your LLM
   
5. ✓ Read full docs:
   - SEMANTIC_FS_DOCUMENTATION.md (comprehensive)
   - README_SEMANTIC_FS.md (overview)
   - Code comments in semantic_file_system_enhanced.py

6. ✓ Contribute!
   - Test with your data
   - Report issues
   - Suggest improvements
"""

# ============================================================================
# FILE STRUCTURE
# ============================================================================

"""
KNO/
├── semantic_file_system_enhanced.py    ← Main SFS class
├── semantic_fs_coordinator_v2.py       ← LLM integration
├── test_semantic_fs.py                 ← Test suite
├── README_SEMANTIC_FS.md               ← Overview
├── SEMANTIC_FS_DOCUMENTATION.md        ← Complete docs
├── requirements-semantic-fs.txt        ← Dependencies
└── QUICK_START.md                      ← This file

Generated (auto-created):
├── sfs_index/                          ← Index directory
│   ├── chroma_db/                      ← ChromaDB storage
│   ├── metadata.json                   ← File metadata
│   └── FAISS files (if using FAISS)
└── semantic_fs.log                     ← Detailed logs
"""

# ============================================================================
# KEY FILES REFERENCE
# ============================================================================

"""
| File | Purpose |
|------|---------|
| semantic_file_system_enhanced.py | Core SFS implementation |
| semantic_fs_coordinator_v2.py | LLM integration layer |
| test_semantic_fs.py | Comprehensive test suite |
| SEMANTIC_FS_DOCUMENTATION.md | 200+ lines of detailed docs |
| README_SEMANTIC_FS.md | Quick overview with examples |
| requirements-semantic-fs.txt | All dependencies listed |
| QUICK_START.md | This file |
"""

# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
Faster Indexing:
- Increase batch_size: KNOFileSystem(batch_size=64)
- Use SSD storage for index
- Use fewer files initially

Faster Search:
- Use FAISS: KNOFileSystem(use_chroma=False)
- Increase similarity_threshold: threshold=0.5
- Reduce top_k: top_k=3

Better Quality:
- Use better model: model_name="all-mpnet-base-v2"
- Lower similarity_threshold: threshold=0.2
- Increase top_k: top_k=10

GPU Acceleration:
- Install faiss-gpu: pip install faiss-gpu
- Automatically speeds up by 10x
- Requires NVIDIA GPU + CUDA
"""

print("""
╔════════════════════════════════════════════════════════════╗
║   KNO Semantic File System - Quick Start Guide            ║
║                                                            ║
║   1. Install: pip install -r requirements-semantic-fs.txt ║
║   2. Run: python -c "from semantic_file_system_enhanced   ║
║           import KNOFileSystem; print('✓ Ready!')"        ║
║   3. Demo: See code in this file                          ║
║   4. Docs: Read SEMANTIC_FS_DOCUMENTATION.md              ║
║   5. Test: python test_semantic_fs.py                     ║
║                                                            ║
║   Questions? Check README_SEMANTIC_FS.md                 ║
╚════════════════════════════════════════════════════════════╝
""")
