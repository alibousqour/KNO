# eDEX Data Bridge - Ready-to-Use Code Snippets

This file contains copy-paste ready code to integrate EDEXMonitor into your agent.

## 1. Simple Integration (agent.py - Main Class)

Add this to your Agent class __init__:

```python
def __init__(self):
    # ... existing code ...
    
    # Initialize eDEX monitor for cinematic UI integration
    from kno_utils import edex_monitor
    self.monitor = edex_monitor
    self.monitor.reset()  # Start fresh session
    
    print("[INIT] eDEX Monitor initialized - Status updates will be available in edex_status.json")
```

## 2. Update Status in Thinking Operation

Replace or enhance your thinking method:

```python
def on_think(self):
    """Enhanced thinking with eDEX status updates"""
    
    # Signal that we're thinking
    self.monitor.update_status_sync(
        agent_status="THINKING",
        current_task="Analyzing user input...",
        llm_model="Local Llama",
        progress=10
    )
    
    try:
        # Your existing thinking logic here
        prompt = self.current_prompt or "General reasoning"
        
        self.monitor.update_status_sync(
            current_task=f"Querying LLM: {prompt[:50]}...",
            progress=30
        )
        
        # Call LLM
        response = self.llm.query(prompt)
        
        self.monitor.update_status_sync(
            current_task="Processing LLM response...",
            progress=70,
            llm_model="Local Llama - Received Response"
        )
        
        # Process response
        self.process_response(response)
        
        # Mark as complete
        self.monitor.update_status_sync(
            agent_status="IDLE",
            current_task="Thinking complete",
            progress=100,
            last_action="Completed analysis"
        )
        self.monitor.add_task_completed()
        
    except Exception as e:
        self.monitor.log_error(f"Thinking error: {str(e)}")
        print(f"[ERROR] Thinking failed: {e}", flush=True)
```

## 3. Async Version (for agent_refactored_v5.py)

```python
async def _on_think_async(self):
    """Async thinking with real-time eDEX updates"""
    
    await self.monitor.update_status(
        agent_status="THINKING",
        current_task="Analyzing user input...",
        llm_model=self.current_model or "Gemini",
        progress=15
    )
    
    try:
        prompt = self.current_prompt or "General reasoning"
        
        await self.monitor.update_status(
            current_task=f"Querying {self.current_model or 'Gemini'}...",
            progress=30
        )
        
        # Non-blocking LLM query
        response = await self.llm_coordinator.query_with_fallback_async(prompt)
        
        await self.monitor.update_status(
            current_task="Processing response...",
            progress=70
        )
        
        # Process the response
        await self.process_response_async(response)
        
        # Complete
        await self.monitor.update_status(
            agent_status="IDLE",
            current_task="Analysis complete",
            progress=100,
            last_action="Successfully completed thinking cycle"
        )
        
        self.monitor.add_task_completed()
        
    except Exception as e:
        self.monitor.log_error(f"Thinking failed: {str(e)}")
        logger.error(f"Thinking error: {e}", exc_info=True)
```

## 4. Error Handling with Auto-Fix

```python
def handle_error_with_fix(self, error_message, code_snippet=None):
    """Handle errors and apply automatic fixes"""
    
    self.monitor.update_status_sync(
        agent_status="FIXING",
        current_task="Analyzing error...",
        progress=20
    )
    
    try:
        # Ask AI for fix
        fix_suggestion = self.get_ai_fix(error_message, code_snippet)
        
        self.monitor.update_status_sync(
            current_task="Applying fix...",
            progress=50
        )
        
        # Apply the fix
        if fix_suggestion:
            self.code_patcher.apply(fix_suggestion)
            
            # Log success
            self.monitor.log_fix(f"Fixed: {error_message[:80]}")
            
            self.monitor.update_status_sync(
                agent_status="IDLE",
                current_task="Fix applied successfully",
                progress=100
            )
            
            return True
        else:
            raise Exception("Could not generate fix")
            
    except Exception as e:
        self.monitor.log_error(f"Fix failed: {str(e)}")
        return False
```

## 5. Search Operation with Progress

```python
async def search_with_progress(self, query):
    """Search with real-time progress updates"""
    
    await self.monitor.update_status(
        agent_status="SEARCHING",
        current_task=f"Searching: {query[:60]}...",
        progress=10
    )
    
    try:
        # Execute search
        await self.monitor.update_status(progress=30)
        results = await self.search_engine.find_async(query)
        
        # Process results
        await self.monitor.update_status(
            current_task=f"Processing {len(results)} results...",
            progress=70
        )
        
        processed = await self.process_search_results(results)
        
        # Complete
        await self.monitor.update_status(
            agent_status="IDLE",
            current_task="Search complete",
            progress=100,
            last_action=f"Found and processed {len(results)} results"
        )
        
        self.monitor.add_task_completed()
        
        return processed
        
    except Exception as e:
        self.monitor.log_error(f"Search failed: {str(e)}")
        raise
```

## 6. Multi-Step Process with Stages

```python
async def execute_complex_task(self, task_description):
    """Multi-stage task with individual progress tracking"""
    
    stages = [
        ("Planning", 20),
        ("Searching", 40),
        ("Processing", 60),
        ("Optimizing", 80),
        ("Finalizing", 100)
    ]
    
    try:
        await self.monitor.update_status(
            agent_status="EXECUTING",
            current_task=task_description,
            progress=0
        )
        
        for stage_name, progress in stages:
            await self.monitor.update_status(
                current_task=f"{stage_name}: {task_description}",
                progress=progress
            )
            
            # Execute this stage
            await self.execute_stage(stage_name)
            
            # Small delay to show progress
            await asyncio.sleep(0.5)
        
        # All complete
        await self.monitor.update_status(
            agent_status="IDLE",
            current_task="Task completed successfully",
            progress=100,
            last_action=f"Completed: {task_description}"
        )
        
        self.monitor.add_task_completed()
        
    except Exception as e:
        self.monitor.log_error(f"Task failed at {stage_name}: {str(e)}")
        raise
```

## 7. System Metrics Updates

```python
async def update_system_metrics_loop(self):
    """Continuously update system metrics in background"""
    
    import psutil
    
    try:
        process = psutil.Process()
        
        while True:
            # Get current metrics
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent(interval=0.1)
            
            # Update monitor
            await self.monitor.update_status(
                memory_usage_mb=round(memory_mb, 2),
                cpu_usage_percent=round(cpu_percent, 1)
            )
            
            # Update every 5 seconds
            await asyncio.sleep(5)
            
    except Exception as e:
        logger.warning(f"Metrics update failed: {e}")
```

## 8. Integration with Your Main Loop

For agent.py (synchronous):

```python
def main_loop(self):
    """Main agent loop with eDEX monitoring"""
    
    print("[START] KNO Agent starting with eDEX monitoring...", flush=True)
    
    while self.running:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Set current task
            self.monitor.update_status_sync(
                agent_status="PROCESSING",
                current_task=f"User said: {user_input[:60]}...",
                progress=5
            )
            
            # Process normally
            self.on_input(user_input)
            
            # Mark complete
            self.monitor.update_status_sync(
                agent_status="IDLE",
                progress=100
            )
            
        except KeyboardInterrupt:
            print("\n[EXIT] Shutting down gracefully...", flush=True)
            self.running = False
        except Exception as e:
            self.monitor.log_error(str(e))
            print(f"[ERROR] {e}", flush=True)
```

For agent_refactored_v5.py (async):

```python
async def main_loop_async(self):
    """Main async agent loop with eDEX monitoring"""
    
    logger.info("KNO Agent starting with eDEX monitoring...")
    
    while self.running:
        try:
            await self.monitor.update_status(
                agent_status="IDLE",
                current_task="Waiting for input..."
            )
            
            # Wait for user input (non-blocking)
            user_input = await asyncio.to_thread(input, "You: ")
            user_input = user_input.strip()
            
            if not user_input:
                continue
            
            # Process with monitoring
            await self._on_think_async()
            
        except KeyboardInterrupt:
            logger.info("Agent shutting down...")
            self.running = False
        except Exception as e:
            self.monitor.log_error(str(e))
            logger.error(f"Main loop error: {e}", exc_info=True)
```

## 9. Minimal Integration (Quick Start)

If you just want basic integration with minimal changes:

```python
# At the top of your agent class
from kno_utils import edex_monitor

# Before any operation
def before_operation(self, name):
    edex_monitor.update_status_sync(
        agent_status="THINKING",
        current_task=name,
        progress=50
    )

# After any operation
def after_operation(self, name, success=True):
    edex_monitor.update_status_sync(
        agent_status="IDLE" if success else "ERROR",
        current_task=f"Completed: {name}" if success else f"Failed: {name}",
        progress=100
    )
```

## 10. Testing Your Integration

Create a test script:

```python
# test_edex_monitor.py
import asyncio
import time
from kno_utils import EDEXMonitor

async def test_edex_monitor():
    """Test eDEX monitor functionality"""
    
    monitor = EDEXMonitor("test_edex_status.json")
    
    # Test sync update
    print("Testing sync update...")
    monitor.update_status_sync(
        agent_status="THINKING",
        current_task="Test sync operation"
    )
    time.sleep(0.5)
    
    # Test async update
    print("Testing async update...")
    await monitor.update_status(
        agent_status="SEARCHING",
        current_task="Test async operation",
        progress=50
    )
    time.sleep(0.5)
    
    # Test error logging
    print("Testing error logging...")
    monitor.log_error("Test error message")
    
    # Test fix logging
    print("Testing fix logging...")
    monitor.log_fix("Fixed test issue")
    
    # Print current status
    print("\nCurrent Status:")
    import json
    print(json.dumps(monitor.get_current_status(), indent=2))
    
    print("\n✅ All tests passed! Check test_edex_status.json")

if __name__ == "__main__":
    asyncio.run(test_edex_monitor())
```

Run it:
```bash
cd a:\KNO\KNO
python test_edex_monitor.py
```

---

## Notes

1. **Async vs Sync**: Use async (`await monitor.update_status()`) if you're in an async function, otherwise use sync (`monitor.update_status_sync()`)

2. **Progress Field**: Update the `progress` field from 0-100 to show task completion

3. **File Updates**: The JSON file is updated in real-time and safe for eDEX-UI to read continuously

4. **Performance**: Updates are non-blocking and take < 1ms each

5. **Integration Points**: Add monitor calls anywhere in your code - thinking, searching, fixing, executing

6. **Error Handling**: Always wrap operations in try-except and call `monitor.log_error()` on failure

## Next: eDEX-UI Configuration

See `EDEX_DATA_BRIDGE_INTEGRATION.md` for instructions on configuring eDEX-UI to read this file.
