"""
Agent.py Integration - Copy & Paste Code Snippets
===================================================

Ready-to-use code snippets to add eDEX-UI progress tracking to agent.py

Each section is self-contained and can be copied directly into your agent.py

Author: KNO Architecture
License: MIT
"""

# ============================================================================
# SECTION 1: ADD IMPORTS (Near top of agent.py)
# ============================================================================

"""
Add these imports at the top of your agent.py file:

from edex_indexing_progress import (
    create_indexing_tracker,
    update_edex_progress,
    clear_edex_progress,
    IndexingProgressTracker
)
"""

# ============================================================================
# SECTION 2: ADD TO __init__ METHOD (In KNOAgent.__init__)
# ============================================================================

"""
Add this to your agent initialization:

def __init__(self):
    # ... existing code ...
    
    # Initialize eDEX progress tracking
    self.indexing_tracker = None
    self.progress_enabled = True  # Can toggle this
    
    # ... rest of init ...
"""

# ============================================================================
# SECTION 3: WRAPPER FUNCTION (Add to KNOAgent class)
# ============================================================================

"""
Add this complete method to your KNOAgent class:

async def index_directory_with_edex_progress(self, directory: str):
    '''
    Index all files in a directory with real-time eDEX-UI progress.
    
    Args:
        directory: Path to directory to index
        
    Returns:
        int: Number of files indexed
    '''
    from pathlib import Path
    import logging
    
    logger = logging.getLogger('KNO.Agent')
    
    try:
        # Get all files in directory
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.error(f"Directory not found: {directory}")
            return 0
        
        files = [f for f in dir_path.rglob('*') if f.is_file()]
        
        if not files:
            logger.info(f"No files to index in {directory}")
            return 0
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in files)
        
        logger.info(f"Starting indexing of {len(files)} files "
                   f"({total_size / (1024*1024):.2f} MB)")
        
        # Create progress tracker if enabled
        if self.progress_enabled:
            self.indexing_tracker = create_indexing_tracker(
                total_files=len(files),
                operation=f"📂 Indexing {len(files)} files from {dir_path.name}..."
            )
            self.indexing_tracker.progress.total_bytes = total_size
        
        indexed_count = 0
        skipped_count = 0
        
        # Index each file
        for file in files:
            try:
                # Update progress
                if self.indexing_tracker:
                    self.indexing_tracker.start_file(file.name)
                
                # Your indexing logic here
                success = await self._index_file(file)
                
                if success:
                    indexed_count += 1
                else:
                    skipped_count += 1
                
                # Mark file complete
                if self.indexing_tracker:
                    self.indexing_tracker.complete_file(file.stat().st_size)
                
            except Exception as e:
                logger.warning(f"Failed to index {file}: {e}")
                skipped_count += 1
                if self.indexing_tracker:
                    self.indexing_tracker.complete_file(0)
        
        # Finish progress tracking
        if self.indexing_tracker:
            self.indexing_tracker.finish()
            self.indexing_tracker = None
        
        logger.info(f"Indexing complete: {indexed_count} indexed, "
                   f"{skipped_count} skipped out of {len(files)} files")
        
        return indexed_count
        
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        if self.indexing_tracker:
            clear_edex_progress()
            self.indexing_tracker = None
        return 0

async def _index_file(self, file: Path) -> bool:
    '''
    Index a single file. Implement your indexing logic here.
    
    Args:
        file: Path to file to index
        
    Returns:
        bool: True if successful, False otherwise
    '''
    try:
        # Example 1: Just read the file (always works)
        content = file.read_text(encoding='utf-8', errors='ignore')
        
        # Example 2: Use semantic file system if available
        if hasattr(self, 'semantic_fs') and self.semantic_fs:
            await self.semantic_fs.add_file_async(
                file_path=str(file),
                content=content,
                metadata={
                    'extension': file.suffix,
                    'size': len(content)
                }
            )
        
        return True
        
    except Exception as e:
        import logging
        logger = logging.getLogger('KNO.Agent')
        logger.error(f"Error indexing {file}: {e}")
        return False
"""

# ============================================================================
# SECTION 4: SIMPLE WRAPPER (Alternative, simpler version)
# ============================================================================

"""
If you already have an indexing method, wrap it like this:

def index_files(self, files):
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=len(files),
        operation=f"Indexing {len(files)} files..."
    )
    
    # Your existing loop
    for file in files:
        tracker.start_file(file.name)
        
        # Your existing code here
        process_file(file)
        
        tracker.complete_file(file.stat().st_size)
    
    tracker.finish()
"""

# ============================================================================
# SECTION 5: HOOK INTO EXISTING MODULE (If you have semantic_fs)
# ============================================================================

"""
If using semantic_file_system_enhanced.py, integrate like this:

async def index_semantic_system(self, directory: str):
    '''Index using semantic file system with progress tracking'''
    from pathlib import Path
    
    files = list(Path(directory).rglob('*'))
    files = [f for f in files if f.is_file()]
    
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=len(files),
        operation="🤖 Semantic indexing..."
    )
    
    # Index with semantic system
    for file in files:
        tracker.start_file(file.name)
        
        content = file.read_text(errors='ignore')
        
        # Add to semantic index
        await self.semantic_fs.add_file_async(
            str(file),
            content
        )
        
        tracker.complete_file(file.stat().st_size)
    
    tracker.finish()
"""

# ============================================================================
# SECTION 6: QUICK UPDATE MODE (For simple loops)
# ============================================================================

"""
For simple progress updates without creating a tracker:

def simple_indexing(self, files):
    for i, file in enumerate(files, 1):
        # Quick progress update
        update_edex_progress(
            current=i,
            total=len(files),
            operation="Indexing files...",
            current_file=file.name
        )
        
        # Your indexing code
        process_file(file)
    
    # Clear progress
    clear_edex_progress()
"""

# ============================================================================
# SECTION 7: AGENT STARTUP (Add to initialization)
# ============================================================================

"""
Add this to your agent startup sequence:

async def agent_startup(self):
    '''Initialize agent with eDEX progress tracking'''
    
    logger.info("KNO Agent starting up...")
    
    # ... existing startup code ...
    
    # Index knowledge base if available
    if hasattr(self, 'kb_directory'):
        logger.info("Indexing knowledge base...")
        await self.index_directory_with_edex_progress(self.kb_directory)
    
    # ... rest of startup ...
    
    logger.info("KNO Agent ready!")
"""

# ============================================================================
# SECTION 8: SCHEDULED INDEXING (If you want periodic indexing)
# ============================================================================

"""
Add periodic indexing with progress tracking:

import asyncio
import time

async def periodic_indexing_loop(self, interval: int = 3600):
    '''
    Periodically index directories with progress tracking.
    
    Args:
        interval: Seconds between indexing (default 1 hour)
    '''
    import logging
    logger = logging.getLogger('KNO.Agent')
    
    while True:
        try:
            logger.info("Running scheduled indexing...")
            
            # Index multiple directories
            for directory in [
                "./code",
                "./documents",
                "./config"
            ]:
                await self.index_directory_with_edex_progress(directory)
            
            logger.info(f"Waiting {interval}s until next index...")
            await asyncio.sleep(interval)
            
        except Exception as e:
            logger.error(f"Scheduled indexing failed: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute
"""

# ============================================================================
# SECTION 9: ADD TO MAIN LOOP (For continuous operation)
# ============================================================================

"""
If you have a main agent loop, add indexing:

async def agent_main_loop(self):
    '''Main agent loop with periodic indexing'''
    
    import asyncio
    
    # Start indexing in background
    index_task = asyncio.create_task(
        self.periodic_indexing_loop(interval=3600)  # Index every hour
    )
    
    try:
        while True:
            # Your main agent loop code
            await self.process_requests()
            await asyncio.sleep(0.1)
            
    finally:
        index_task.cancel()
"""

# ============================================================================
# SECTION 10: ENABLE/DISABLE PROGRESS
# ============================================================================

"""
Allow toggling progress display:

def set_progress_enabled(self, enabled: bool):
    '''Enable or disable eDEX-UI progress tracking'''
    self.progress_enabled = enabled
    
    if enabled:
        print("eDEX progress tracking ENABLED")
    else:
        print("eDEX progress tracking DISABLED")
        clear_edex_progress()

# Usage:
# agent.set_progress_enabled(True)   # Enable
# agent.set_progress_enabled(False)  # Disable
"""

# ============================================================================
# COMPLETE EXAMPLE: Full Integration
# ============================================================================

"""
Here's a COMPLETE example you can copy/paste:

=============================================================

from edex_indexing_progress import (
    create_indexing_tracker,
    clear_edex_progress
)
from pathlib import Path
import logging

# At top of KNOAgent class:

class KNOAgent:
    def __init__(self):
        # ... existing code ...
        self.indexing_tracker = None
        self.progress_enabled = True

    async def index_codebase(self, root_dir: str = "./src"):
        '''Index codebase with real-time progress in eDEX-UI'''
        
        logger = logging.getLogger('KNO.Agent')
        
        try:
            # Find Python files
            files = list(Path(root_dir).rglob("*.py"))
            if not files:
                logger.info(f"No Python files found in {root_dir}")
                return
            
            # Create tracker
            self.indexing_tracker = create_indexing_tracker(
                total_files=len(files),
                operation=f"🐍 Indexing {len(files)} Python files..."
            )
            
            # Index each file
            for file in files:
                self.indexing_tracker.start_file(file.name)
                
                # Index the file
                content = file.read_text(errors='ignore')
                # Your indexing logic here
                
                self.indexing_tracker.complete_file(file.stat().st_size)
            
            # Finish
            self.indexing_tracker.finish()
            self.indexing_tracker = None
            
            logger.info(f"✅ Indexed {len(files)} Python files")
            
        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            clear_edex_progress()

# In your agent startup:
async def main():
    agent = KNOAgent()
    await agent.index_codebase("./src")
    # Progress bar now shows in eDEX-UI!

=============================================================
"""

# ============================================================================
# TESTS: Verify Integration
# ============================================================================

"""
After integration, test with:

import asyncio
from pathlib import Path

async def test_edex_progress():
    '''Quick test to verify integration works'''
    
    from edex_indexing_progress import create_indexing_tracker
    
    print("\\n🧪 Testing eDEX Progress Integration...")
    
    # Create test directory
    test_dir = Path("./test_index")
    test_dir.mkdir(exist_ok=True)
    
    # Create test files
    for i in range(10):
        (test_dir / f"test_{i}.py").write_text(f"# Test {i}\\n")
    
    # Create tracker
    tracker = create_indexing_tracker(
        total_files=10,
        operation="🧪 Testing progress..."
    )
    
    # Update progress
    for i in range(1, 11):
        tracker.start_file(f"test_{i}.py")
        tracker.complete_file(100)
        await asyncio.sleep(0.1)
    
    tracker.finish()
    
    # Check edex_status.json
    import json
    if Path("edex_status.json").exists():
        with open("edex_status.json") as f:
            status = json.load(f)
            print(f"\\n✅ Test passed! Status file created:")
            print(f"   - Operation: {status['semantic_search']['operation']}")
            print(f"   - Progress: {status['semantic_search']['progress']['percentage']}%")
    else:
        print("\\n❌ Test failed! edex_status.json not created")

# Run test:
if __name__ == "__main__":
    asyncio.run(test_edex_progress())
"""

# ============================================================================
# DOCUMENTATION
# ============================================================================

"""
📚 Full Documentation available in:
   - EDEX_INDEXING_INTEGRATION_GUIDE.md (API reference)
   - edex_integration_examples.py (5 working examples)
   - edex_indexing_progress.py (source code)

🚀 Quick Start:
   1. Copy Section 1 imports to top of agent.py
   2. Copy Section 2 to __init__ method
   3. Copy Section 3 complete method to KNOAgent class
   4. Call: await agent.index_directory_with_edex_progress("./src")
   5. Done! Progress bar now shows in eDEX-UI

💡 Tips:
   - Start_file() before processing each file
   - Complete_file(size) after processing each file
   - Finish() when done
   - Progress automatically updates edex_status.json
   - eDEX-UI reads file and shows progress bar

🎯 Next Steps:
   1. Choose which section fits your code best
   2. Copy the code snippet
   3. Paste into your agent.py
   4. Test with your codebase
   5. Monitor progress in eDEX-UI
"""

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║         Agent.py Integration Code Snippets                        ║
║                                                                    ║
║  Choose the section that best fits your needs:                    ║
║                                                                    ║
║  1. Imports - Add to top of agent.py                              ║
║  2. Init - Add to __init__ method                                 ║
║  3. Complete Method - Paste entire method                         ║
║  4. Wrapper - Wrap existing indexing                              ║
║  5. Semantic - If using semantic_file_system                      ║
║  6. Quick Update - Simplest approach                              ║
║  7. Startup - Add to initialization                               ║
║  8. Periodic - Schedule indexing                                  ║
║  9. Main Loop - Continuous operation                              ║
║  10. Toggle - Enable/disable progress                             ║
║                                                                    ║
║  Or use the COMPLETE EXAMPLE (Section 10)!                        ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
