"""
eDEX-UI + Semantic File System Integration Examples
====================================================

Comprehensive examples showing how to integrate eDEX-UI progress bars
with semantic file system indexing and the KNO agent.

Author: KNO Architecture
License: MIT
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional
import time

# Import progress tracking
from edex_indexing_progress import (
    create_indexing_tracker,
    update_edex_progress,
    clear_edex_progress,
    IndexingProgressTracker
)

# Try to import semantic file system components
try:
    from semantic_file_system_enhanced import KNOFileSystem
    HAS_SEMANTIC_FS = True
except ImportError:
    HAS_SEMANTIC_FS = False
    print("[WARN] semantic_file_system_enhanced not available (optional for demos)")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger('KNO.IntegrationExamples')

# ============================================================================
# EXAMPLE 1: Basic Index with Progress
# ============================================================================

def example_1_basic_indexing():
    """
    Basic example: Index files in a directory with progress bar.
    
    Shows:
    - Creating a progress tracker
    - Processing files in a loop
    - Automatic eDEX-UI updates
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic File Indexing with Progress Bar")
    print("="*70)
    
    # Get files to index
    test_dir = Path("./src")
    if not test_dir.exists():
        print(f"Creating test directory: {test_dir}")
        test_dir.mkdir(parents=True, exist_ok=True)
        # Create sample files
        for i in range(10):
            (test_dir / f"file_{i:02d}.py").write_text(f"# File {i}\nprint('Hello {i}')\n")
    
    files = list(test_dir.glob("*.py"))
    
    if not files:
        print("No files found to index")
        return
    
    print(f"\n📂 Found {len(files)} files to index")
    print(f"💾 Total size: {sum(f.stat().st_size for f in files) / (1024*1024):.2f} MB")
    
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=len(files),
        operation=f"📚 Indexing {len(files)} Python files..."
    )
    
    # Process each file
    indexed = 0
    for file in files:
        try:
            # Mark file as current
            tracker.start_file(file.name)
            
            # Simulate processing
            content = file.read_text()
            lines = len(content.split('\n'))
            
            print(f"  ✓ {file.name} ({len(content)} bytes, {lines} lines)")
            
            # Mark file as complete
            tracker.complete_file(file.stat().st_size)
            indexed += 1
            
            time.sleep(0.1)  # Simulate work
            
        except Exception as e:
            print(f"  ✗ Error processing {file.name}: {e}")
    
    # Mark complete
    tracker.finish()
    print(f"\n✅ Indexing complete: {indexed}/{len(files)} files")
    
    # Check edex_status.json was created
    if Path("edex_status.json").exists():
        print("📊 edex_status.json created successfully")
        with open("edex_status.json") as f:
            import json
            status = json.load(f)
            print(f"   - Operation: {status['semantic_search']['operation']}")
            print(f"   - Progress: {status['semantic_search']['progress']['percentage']:.0f}%")

# ============================================================================
# EXAMPLE 2: Directory Tree Indexing (Recursive)
# ============================================================================

def example_2_recursive_indexing():
    """
    Recursive indexing with progress tracking.
    
    Shows:
    - Finding all files in a directory tree
    - Calculating total size upfront
    - Progress with multiple file types
    - Filtering file types
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Recursive Directory Indexing")
    print("="*70)
    
    base_path = Path("./src")
    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)
    
    # Find all files recursively
    extensions = {'.py', '.md', '.json', '.txt'}
    files = []
    total_size = 0
    
    for file in base_path.rglob('*'):
        if file.is_file() and file.suffix in extensions:
            files.append(file)
            total_size += file.stat().st_size
    
    if not files:
        print("No files found in directory")
        return
    
    print(f"\n📁 Found {len(files)} files in {base_path}")
    print(f"📊 Total size: {total_size / (1024*1024):.2f} MB")
    
    # Organize by file type
    by_type = {}
    for file in files:
        ext = file.suffix
        if ext not in by_type:
            by_type[ext] = []
        by_type[ext].append(file)
    
    print(f"📋 File types: {', '.join(f'{k} ({len(v)})' for k, v in by_type.items())}")
    
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=len(files),
        operation=f"🔍 Indexing {len(files)} files from {base_path.name}..."
    )
    tracker.progress.total_bytes = total_size
    
    # Process each type separately
    for ext, ext_files in sorted(by_type.items()):
        print(f"\n  Processing *{ext} files ({len(ext_files)} items)...")
        tracker.set_operation(f"📑 Processing {ext} files ({len(ext_files)})...")
        
        for file in ext_files:
            tracker.start_file(str(file.relative_to(base_path)))
            
            # Simulate processing
            time.sleep(0.05)
            
            tracker.complete_file(file.stat().st_size)
    
    # Complete
    tracker.finish()
    print(f"\n✅ All {len(files)} files indexed successfully")

# ============================================================================
# EXAMPLE 3: Async Indexing with Semantic File System
# ============================================================================

async def example_3_async_semantic_indexing():
    """
    Async indexing with semantic file system integration.
    
    Shows:
    - Async file processing
    - Integration with semantic search
    - Parallel processing simulation
    - Result metrics
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Async Semantic Indexing")
    print("="*70)
    
    if not HAS_SEMANTIC_FS:
        print("⚠️  semantic_file_system_enhanced not available - skipping")
        return
    
    # Initialize semantic file system
    print("\n🔧 Initializing semantic file system...")
    semantic_fs = KNOFileSystem()
    await semantic_fs.initialize()
    
    # Get test files
    test_dir = Path("./src")
    if not test_dir.exists():
        test_dir.mkdir(parents=True, exist_ok=True)
    
    files = list(test_dir.glob("*.py"))
    
    if not files:
        print("No files to index")
        return
    
    print(f"📄 Found {len(files)} files")
    
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=len(files),
        operation="🤖 Semantic indexing in progress..."
    )
    
    # Index files asynchronously
    print("\n📚 Indexing files with semantic analysis...")
    indexed = 0
    
    for file in files:
        try:
            tracker.start_file(file.name)
            
            # Read file
            content = file.read_text()
            
            # Add to semantic index
            await semantic_fs.add_file_async(
                str(file),
                content,
                metadata={
                    'type': 'python',
                    'size': len(content)
                }
            )
            
            print(f"  ✓ {file.name} (🔤 {len(content)} chars)")
            
            tracker.complete_file(file.stat().st_size)
            indexed += 1
            
            # Simulate async work
            await asyncio.sleep(0.05)
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    tracker.finish()
    
    # Get statistics
    stats = semantic_fs.get_statistics()
    print(f"\n📊 Indexing Statistics:")
    print(f"  - Files indexed: {stats.get('indexed_files', 0)}")
    print(f"  - Total chunks: {stats.get('total_chunks', 0)}")
    print(f"  - Index size: {stats.get('index_size_mb', 0):.2f} MB")
    
    print(f"\n✅ Async indexing complete!")

# ============================================================================
# EXAMPLE 4: Batch Processing with Progress Updates
# ============================================================================

def example_4_batch_processing():
    """
    Process files in batches with progress tracking.
    
    Shows:
    - Batch processing pattern
    - Dynamic progress updates
    - Performance metrics per batch
    - Large file handling
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Batch Processing")
    print("="*70)
    
    # Create sample files of varying sizes
    test_dir = Path("./data")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    files = []
    for i in range(25):
        file = test_dir / f"data_{i:03d}.txt"
        file.write_text(f"Data file {i}\n" * (i + 1) * 100)
        files.append(file)
    
    print(f"\n📦 Created {len(files)} test files")
    total_size = sum(f.stat().st_size for f in files)
    print(f"💾 Total size: {total_size / (1024*1024):.2f} MB")
    
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=len(files),
        operation="🚀 Batch processing files..."
    )
    tracker.progress.total_bytes = total_size
    
    # Process in batches
    batch_size = 5
    batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]
    
    print(f"\n⚙️  Processing {len(batches)} batches (size: {batch_size})")
    print("-" * 70)
    
    start_time = time.time()
    
    for batch_num, batch in enumerate(batches, 1):
        batch_start = time.time()
        
        tracker.set_operation(
            f"⚙️  Batch {batch_num}/{len(batches)} ({len(batch)} files)"
        )
        
        # Process batch files
        for file in batch:
            tracker.start_file(file.name)
            
            # Simulate processing
            content = file.read_text()
            size = file.stat().st_size
            
            tracker.complete_file(size)
            time.sleep(0.05)
        
        # Show batch stats
        batch_duration = time.time() - batch_start
        batch_bytes = sum(f.stat().st_size for f in batch)
        batch_speed = batch_bytes / (1024 * 1024) / batch_duration if batch_duration > 0 else 0
        
        progress = tracker.get_progress()
        print(f"  Batch {batch_num}: {len(batch)} files in {batch_duration:.2f}s "
              f"({batch_speed:.2f} MB/s, {progress.percentage:.0f}% overall)")
    
    tracker.finish()
    
    total_duration = time.time() - start_time
    total_speed = total_size / (1024 * 1024) / total_duration
    
    print("-" * 70)
    print(f"\n✅ Batch processing complete!")
    print(f"   Total: {len(files)} files in {total_duration:.2f}s ({total_speed:.2f} MB/s)")

# ============================================================================
# EXAMPLE 5: Error Handling and Recovery
# ============================================================================

def example_5_error_handling():
    """
    Handle errors gracefully while tracking progress.
    
    Shows:
    - Skipping failed files
    - Continuing after errors
    - Error statistics
    - Progress recovery
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Error Handling and Recovery")
    print("="*70)
    
    # Create test files with some problematic ones
    test_dir = Path("./error_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    files = []
    for i in range(20):
        file = test_dir / f"file_{i:02d}.txt"
        # Some files will be "unreadable"
        if i % 5 == 0:
            files.append(None)  # Simulate missing file
        else:
            file.write_text(f"Valid file {i}\n")
            files.append(file)
    
    valid_files = [f for f in files if f is not None]
    
    print(f"\n📁 Created {len(valid_files)} valid files")
    print(f"⚠️  {len(files) - len(valid_files)} problematic files to handle")
    
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=len(files),
        operation="⚠️  Processing files with error handling..."
    )
    
    success_count = 0
    skipped_count = 0
    error_count = 0
    
    print("\n📊 Processing with error recovery:")
    print("-" * 70)
    
    for i, file in enumerate(files, 1):
        try:
            if file is None:
                raise FileNotFoundError("File not found (simulated)")
            
            tracker.start_file(file.name)
            
            # Read file
            content = file.read_text()
            
            print(f"  ✓ {file.name if file else 'FILE_NOT_FOUND'}")
            
            tracker.complete_file(file.stat().st_size if file else 0)
            success_count += 1
            
            time.sleep(0.02)
            
        except FileNotFoundError as e:
            print(f"  ⊘ File not found (skipped)")
            skipped_count += 1
            tracker.complete_file(0)  # Count it but with 0 bytes
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1
            tracker.complete_file(0)
    
    tracker.finish()
    
    print("-" * 70)
    print(f"\n📈 Results:")
    print(f"   ✅ Successful: {success_count}/{len(files)}")
    print(f"   ⊘ Skipped: {skipped_count}/{len(files)}")
    print(f"   ✗ Failed: {error_count}/{len(files)}")
    print(f"   📊 Success rate: {(success_count/len(files)*100):.0f}%")

# ============================================================================
# MAIN RUNNER
# ============================================================================

async def main():
    """Run all examples"""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "eDEX-UI Integration Examples Demo" + " "*25 + "║")
    print("║" + " "*15 + "Semantic File System Integration" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        # Example 1: Basic indexing
        example_1_basic_indexing()
        input("\nPress Enter to continue to Example 2...")
        
        # Example 2: Recursive indexing
        example_2_recursive_indexing()
        input("\nPress Enter to continue to Example 3...")
        
        # Example 3: Async semantic indexing
        await example_3_async_semantic_indexing()
        input("\nPress Enter to continue to Example 4...")
        
        # Example 4: Batch processing
        example_4_batch_processing()
        input("\nPress Enter to continue to Example 5...")
        
        # Example 5: Error handling
        example_5_error_handling()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("✅ All Examples Complete!")
    print("="*70)
    print("\n📚 Key Takeaways:")
    print("  1. Create tracker with total file count")
    print("  2. Call start_file() before processing each file")
    print("  3. Call complete_file() after processing (with size)")
    print("  4. Call finish() when done")
    print("  5. Progress automatically updates edex_status.json")
    print("  6. eDEX-UI reads file and shows progress bar")
    print("\n💡 Tips:")
    print("  - Use async/await for non-blocking operations")
    print("  - Handle errors gracefully with try/except")
    print("  - Process files in batches for better performance")
    print("  - Monitor edex_status.json to verify updates")
    print("\n🚀 Next Steps:")
    print("  1. Review EDEX_INDEXING_INTEGRATION_GUIDE.md")
    print("  2. Integrate into your agent.py")
    print("  3. Test with your codebase")
    print("  4. Monitor progress in eDEX-UI interface")

if __name__ == "__main__":
    asyncio.run(main())
