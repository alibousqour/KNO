# eDEX-UI Indexing Progress Integration Guide for agent.py

**Purpose**: Update edex_status.json with real-time progress bars during file indexing operations in KNO agent.

**Status**: ✅ Ready to integrate

---

## Quick Integration (3 Steps)

### Step 1: Import the Module
```python
from edex_indexing_progress import (
    create_indexing_tracker,
    update_edex_progress,
    clear_edex_progress,
    IndexingProgressTracker
)
```

### Step 2: Create Tracker When Indexing Starts
```python
tracker = create_indexing_tracker(
    total_files=len(files_to_index),
    operation="🔍 Indexing knowledge base..."
)
```

### Step 3: Update Progress in Loop
```python
for file in files_to_index:
    tracker.start_file(file)
    process_file(file)
    tracker.complete_file(os.path.getsize(file))

tracker.finish()
```

---

## Complete Integration Example for agent.py

### Location 1: Agent Initialization
Add to `KNOAgent.__init__()`:

```python
# Initialize indexing progress tracker
self.indexing_tracker = None
self.progress_enabled = True  # Can be toggled
```

### Location 2: File Indexing Function
Add a new method or modify existing indexing:

```python
async def index_files_with_progress(self, directory: str):
    """
    Index files in directory with real-time eDEX-UI progress.
    
    Args:
        directory: Path to directory to index
    """
    try:
        # Get list of files
        files = list(Path(directory).rglob('*'))
        files = [f for f in files if f.is_file()]
        
        if not files:
            logger.info(f"No files to index in {directory}")
            return
        
        # Create progress tracker
        self.indexing_tracker = create_indexing_tracker(
            total_files=len(files),
            operation=f"📚 Indexing {len(files)} files from {directory}..."
        )
        
        logger.info(f"Starting indexing of {len(files)} files...")
        
        # Process each file
        for file in files:
            try:
                tracker.start_file(str(file))
                
                # Your indexing logic here
                await self.index_semantic_content(file)
                
                # Complete this file
                tracker.complete_file(file.stat().st_size)
                
            except Exception as e:
                logger.error(f"Failed to index {file}: {e}")
        
        # Mark complete
        self.indexing_tracker.finish()
        logger.info("Indexing complete!")
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        clear_edex_progress()

# Example indexing content function
async def index_semantic_content(self, file: Path):
    """
    Index file content using semantic search system.
    Integrate with your semantic_file_system_enhanced.py
    """
    try:
        # Read file content
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Index using semantic system (if available)
        if hasattr(self, 'semantic_fs') and self.semantic_fs:
            await self.semantic_fs.add_file_async(str(file), content)
        
        return True
    except Exception as e:
        logger.error(f"Error indexing {file}: {e}")
        return False
```

### Location 3: Hook into Existing Indexing
If you already have indexing code, modify it:

```python
# BEFORE: Regular indexing loop
for file in files:
    process_file(file)

# AFTER: With eDEX progress
tracker = create_indexing_tracker(len(files), "Indexing...")

for file in files:
    tracker.start_file(str(file))
    process_file(file)
    tracker.complete_file(os.path.getsize(file))

tracker.finish()
```

---

## API Reference

### Class: `IndexingProgressTracker`

Main class for tracking indexing progress with eDEX-UI updates.

#### Constructor
```python
tracker = IndexingProgressTracker(
    total_files: int = 0,          # Total files to process
    total_bytes: int = 0,           # Total bytes to process
    operation: str = "Indexing files...",  # Operation description
    status_file: str = "edex_status.json", # Status file path
    update_callback: Optional[Callable] = None  # Optional callback
)
```

#### Methods

**`start_file(filename: str)`**
- Mark the start of processing a file
- Called before processing each file
- Updates the "currently processing" display

**`complete_file(file_size: int = 0)`**
- Mark completion of processing a file
- Increments counter and updates display
- `file_size`: Size in bytes (for speed calculation)

**`set_operation(operation: str)`**
- Update the operation description mid-process
- Immediately updates eDEX-UI display

**`finish()`**
- Mark operation as complete
- Automatically clears progress after 2 seconds
- Sends final 100% to eDEX-UI

**`set_total(total_files: int, total_bytes: int = 0)`**
- Update total items (if unknown initially)
- Recalculates all percentages

**`get_progress() -> IndexingProgress`**
- Get current progress snapshot
- Returns dataclass with all metrics

#### Properties (on IndexingProgress)

**`percentage`** (0-100)
- Current progress as percentage
- Automatically capped at 100%

**`elapsed_seconds`**
- Time elapsed since start

**`files_per_second`**
- Indexing speed (files/sec)

**`mb_per_second`**
- Throughput (MB/sec)

**`eta_seconds`**
- Estimated seconds remaining

**`status_message`**
- Complete status text with all metrics

### Function: `create_indexing_tracker()`

Convenience function to create a tracker:

```python
tracker = create_indexing_tracker(
    total_files: int,
    operation: str = "Indexing files...",
    status_file: str = "edex_status.json"
) -> IndexingProgressTracker
```

### Function: `update_edex_progress()`

Quick one-off update without tracker:

```python
success = update_edex_progress(
    current: int,                   # Current count
    total: int,                     # Total count
    operation: str = "Indexing...", # Operation description
    current_file: str = "",         # Currently processing file
    processed_bytes: int = 0,       # Bytes processed
    total_bytes: int = 0,           # Total bytes
    status_file: str = "edex_status.json"
) -> bool
```

Returns `True` if successful.

### Function: `clear_edex_progress()`

Clear progress from eDEX-UI:

```python
success = clear_edex_progress(
    status_file: str = "edex_status.json"
) -> bool
```

---

## edex_status.json Format

The integration automatically writes the following format:

```json
{
  "version": "2.0",
  "timestamp": "2026-03-09T15:45:30.123456",
  "semantic_search": {
    "active": true,
    "operation": "📂 Indexing Python files...",
    "progress": {
      "current": 50,
      "total": 100,
      "percentage": 50.0,
      "current_file": "src/modules/auth.py"
    },
    "performance": {
      "elapsed_seconds": 32.45,
      "files_per_second": 1.54,
      "mb_per_second": 0.98,
      "processed_bytes": 51380224,
      "total_bytes": 102760448,
      "eta_seconds": 31
    }
  },
  "ui_elements": {
    "progress_bar": {
      "visible": true,
      "percentage": 50.0,
      "color": "#FFAA44",
      "label": "50%"
    },
    "status_text": {
      "primary": "📂 Indexing Python files...",
      "secondary": "Indexing files...  (50/100) [50%] @ 1.5 files/sec (0.98 MB/s)",
      "tertiary": "ETA: 31s | 1.54 files/s"
    }
  }
}
```

### Color Progression
- 🔴 **#FF3333** (Red): 0-25% progress
- 🟠 **#FF8833** (Orange): 25-50% progress
- 🟡 **#FFDD33** (Yellow): 50-75% progress
- 🟢 **#88DD33** (Yellow-green): 75-90% progress
- ✅ **#33DD33** (Green): 90-100% progress

---

## Real-World Example: Indexing a Codebase

### Complete Function

```python
async def index_codebase(self, base_path: str = "./src"):
    """
    Index entire codebase with eDEX-UI progress display.
    
    Args:
        base_path: Path to source code directory
    """
    logger.info(f"Starting codebase indexing from {base_path}")
    
    try:
        # Find all source files
        source_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go'}
        files = []
        total_size = 0
        
        for ext in source_extensions:
            for file in Path(base_path).rglob(f'*{ext}'):
                if file.is_file():
                    files.append(file)
                    total_size += file.stat().st_size
        
        if not files:
            logger.warning(f"No source files found in {base_path}")
            return
        
        # Create progress tracker
        tracker = create_indexing_tracker(
            total_files=len(files),
            operation=f"🔍 Indexing {len(files)} source files..."
        )
        tracker.progress.total_bytes = total_size
        
        logger.info(f"Indexing {len(files)} files ({total_size / (1024*1024):.1f} MB)")
        
        # Index each file
        indexed_count = 0
        skipped_count = 0
        
        for file in files:
            try:
                tracker.start_file(str(file.relative_to(base_path)))
                
                # Index file content
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Add to semantic index
                if self.semantic_fs:
                    await self.semantic_fs.add_file_async(
                        str(file),
                        content,
                        metadata={
                            'extension': file.suffix,
                            'relative_path': str(file.relative_to(base_path))
                        }
                    )
                
                indexed_count += 1
                tracker.complete_file(file.stat().st_size)
                
            except Exception as e:
                logger.warning(f"Skipped {file}: {e}")
                skipped_count += 1
        
        # Complete
        tracker.finish()
        
        logger.info(f"Indexing complete: {indexed_count} files indexed, "
                   f"{skipped_count} skipped")
        
    except Exception as e:
        logger.error(f"Codebase indexing failed: {e}")
        clear_edex_progress()

```

### Running the Function

```python
# In your agent's main loop or startup
agent = KNOAgent()
await agent.initialize()

# Index the codebase
await agent.index_codebase("./src")

# Now search is available
results = await agent.search_files("authentication handler")
```

---

## Integration Checklist

- [ ] Import `edex_indexing_progress` module
- [ ] Add `indexing_tracker` property to agent
- [ ] Create indexing function (or modify existing)
- [ ] Use `create_indexing_tracker()` to initialize
- [ ] Call `tracker.start_file()` before processing each file
- [ ] Call `tracker.complete_file()` after processing each file
- [ ] Call `tracker.finish()` when done
- [ ] Test with sample directory
- [ ] Verify edex_status.json is being updated
- [ ] Check progress bar appears in eDEX-UI
- [ ] Verify color progression (red → green)

---

## Troubleshooting

### Q: Progress bar not showing in eDEX-UI
**A**: 
1. Check edex_status.json exists in root directory
2. Verify `"ui_elements.progress_bar.visible"` is `true`
3. Check eDEX-UI is reading the file (refresh if needed)

### Q: Percentage stuck at 0% or 100%
**A**:
1. Ensure `total_files` is set correctly in tracker
2. Verify `complete_file()` is called for each file
3. Check `percentage` property calculation

### Q: ETA always shows 0 seconds
**A**:
1. ETA needs at least a few files processed
2. Speed calculation requires elapsed time (>0 seconds)
3. Normal behavior in first few seconds

### Q: Performance is slow when updating frequently
**A**:
1. Tracker limits updates to every 500ms (configurable)
2. File operations are atomic and thread-safe
3. JSON writes are optimized with temp files

### Q: Getting permission errors writing edex_status.json
**A**:
1. Check write permissions on root directory
2. Ensure directory exists and is accessible
3. Check file isn't locked by another process

---

## Performance Tips

### Optimize Update Frequency
```python
tracker = IndexingProgressTracker(total_files=10000)
tracker.update_interval = 1.0  # Update every 1 second instead of 500ms
```

### Batch Small Files
```python
# Instead of updating per 1KB file, batch them
tracker.complete_file()  # Creates update
time.sleep(0.5)  # Wait for update to complete
```

### Use Quick Function for One-Offs
```python
# For simple progress update
update_edex_progress(50, 100, "Processing...")

# Instead of creating a tracker
```

---

## Testing

Run the built-in demo:

```bash
python edex_indexing_progress.py
```

This will:
1. Create 100 test items
2. Update progress in real-time
3. Write to edex_status.json
4. Show color progression
5. Display speed and ETA metrics

---

## Files Reference

- **edex_indexing_progress.py** (350+ lines)
  - `IndexingProgressTracker` class
  - `EDEXStatusManager` class
  - Convenience functions
  - Built-in demo

- **edex_semantic_search_bridge.py** (480 lines)
  - Semantic search integration
  - Search progress tracking
  - Result caching

- **agent.py** (your integration point)
  - Add indexing tracker initialization
  - Add indexing functions
  - Hook into existing index methods

---

## Summary

This integration provides:

✅ **Real-time progress visualization** in eDEX-UI  
✅ **Color-coded progress** (red → green)  
✅ **Speed metrics** (files/sec, MB/sec)  
✅ **ETA calculation** (seconds remaining)  
✅ **File-by-file tracking** (current file display)  
✅ **Thread-safe operations** (concurrent access)  
✅ **Zero breaking changes** to existing code  

Just add 3 lines of code to start using it! 🚀
