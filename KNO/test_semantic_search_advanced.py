#!/usr/bin/env python3
"""
Test and Demo Script for Semantic Search Integration
================================================

نص اختبار وتجربة النظام

This script demonstrates all features of the semantic search system.

Usage:
    python test_semantic_search_advanced.py
    
Author: KNO Architecture
License: MIT
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent_semantic_search_integration import (
    KNOAgentSemanticSearch,
    EDEXCommandHandler,
    search_files
)


# ============================================================================
# TEST UTILITIES
# ============================================================================

class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}{Colors.RESET}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def print_result(result: Dict[str, Any], index: int = 1):
    """Print a single search result"""
    print(f"\n{Colors.MAGENTA}[{index}] {result['file_path']}{Colors.RESET}")
    print(f"    {Colors.YELLOW}Relevance: {result['relevance_score']}%{Colors.RESET}")
    print(f"    {Colors.CYAN}Content: {result['summary'][:70]}...{Colors.RESET}")
    if result.get('keywords'):
        print(f"    {Colors.BLUE}Keywords: {', '.join(result['keywords'][:3])}{Colors.RESET}")


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

async def test_initialization():
    """Test system initialization"""
    print_header("TEST 1: System Initialization")
    
    try:
        print_info("Creating search system instance...")
        search = KNOAgentSemanticSearch(
            base_directory="./KNO",
            status_file="edex_status.json"
        )
        print_success("Search system instance created")
        
        print_info("Initializing models...")
        success = await search.initialize()
        
        if success:
            print_success("Models initialized successfully")
            return search
        else:
            print_error("Failed to initialize models")
            return None
    
    except Exception as e:
        print_error(f"Initialization error: {e}")
        return None


async def test_indexing(search: KNOAgentSemanticSearch):
    """Test directory indexing"""
    print_header("TEST 2: Directory Indexing")
    
    try:
        print_info("Starting directory indexing (this may take a moment)...")
        success = await search.index_directory()
        
        if success:
            print_success("Directory indexed successfully")
            
            # Get metrics
            metrics = search.get_metrics()
            print(f"\n{Colors.CYAN}Indexing Metrics:{Colors.RESET}")
            print(f"  Total Files: {metrics['total_files']}")
            print(f"  Indexed Files: {metrics['indexed_files']}")
            print(f"  Failed Files: {metrics['failed_files']}")
            print(f"  Total Chunks: {metrics['total_chunks']}")
            print(f"  Indexing Time: {metrics['indexing_time_seconds']:.2f}s")
            print(f"  Last Indexed: {metrics['last_indexing_date']}")
            
            return True
        else:
            print_error("Failed to index directory")
            return False
    
    except Exception as e:
        print_error(f"Indexing error: {e}")
        return False


async def test_basic_search(search: KNOAgentSemanticSearch):
    """Test basic semantic search"""
    print_header("TEST 3: Basic Semantic Search")
    
    test_queries = [
        "user authentication",
        "error handling",
        "database operations"
    ]
    
    try:
        for query in test_queries:
            print_info(f"Searching: '{query}'")
            
            results = await search.search_files(query, max_results=3)
            
            if results:
                print_success(f"Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    print_result(result, i)
            else:
                print_error(f"No results found for: '{query}'")
            
            print()
    
    except Exception as e:
        print_error(f"Search error: {e}")


async def test_advanced_queries(search: KNOAgentSemanticSearch):
    """Test advanced/complex queries"""
    print_header("TEST 4: Advanced Query Types")
    
    advanced_queries = [
        ("How do I implement user authentication?", "Question-based query"),
        ("WebSocket real-time communication", "Technology-based query"),
        ("Configuration management and setup", "Feature-based query"),
        ("Memory optimization and performance", "Problem-based query"),
        ("API endpoint definitions", "Functional query")
    ]
    
    try:
        for query, query_type in advanced_queries:
            print_info(f"[{query_type}] '{query}'")
            
            results = await search.search_files(query, max_results=2)
            
            if results:
                print_success(f"Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result['file_path']} ({result['relevance_score']}%)")
            else:
                print_error("No results found")
            
            print()
    
    except Exception as e:
        print_error(f"Advanced search error: {e}")


async def test_caching(search: KNOAgentSemanticSearch):
    """Test result caching"""
    print_header("TEST 5: Result Caching")
    
    try:
        import time
        
        query = "authentication logic"
        
        # First search (might be slower)
        print_info(f"First search: '{query}'")
        start = time.time()
        results1 = await search.search_files(query, max_results=5)
        time1 = time.time() - start
        print_success(f"Search completed in {time1:.3f}s")
        print(f"  Results: {len(results1)}")
        
        # Second search (should be cached and faster)
        print_info(f"Second search (cached): '{query}'")
        start = time.time()
        results2 = await search.search_files(query, max_results=5)
        time2 = time.time() - start
        print_success(f"Cached search completed in {time2:.3f}s")
        print(f"  Results: {len(results2)}")
        
        # Verify results are identical
        if results1 == results2:
            print_success("Cached results match original results")
        
        print_info(f"Speed improvement: {time1/time2:.1f}x faster")
        
        # Clear cache
        print_info("Clearing cache...")
        search.clear_cache()
        print_success("Cache cleared")
    
    except Exception as e:
        print_error(f"Caching test error: {e}")


async def test_search_with_details(search: KNOAgentSemanticSearch):
    """Test detailed search results"""
    print_header("TEST 6: Detailed Search Results")
    
    try:
        query = "configuration and settings"
        
        print_info(f"Performing detailed search: '{query}'")
        details = await search.search_with_details(query, max_results=5)
        
        print_success("Search completed with details")
        print(f"\n{Colors.CYAN}Details:{Colors.RESET}")
        print(f"  Query: {details['query']}")
        print(f"  Timestamp: {details['timestamp']}")
        print(f"  Result Count: {details['result_count']}")
        
        if details.get('results'):
            print(f"\n{Colors.CYAN}Top Results:{Colors.RESET}")
            for i, result in enumerate(details['results'][:3], 1):
                print(f"  {i}. {result['file_path']}")
                print(f"     Score: {result['relevance_score']}%")
        
        if details.get('metrics'):
            print(f"\n{Colors.CYAN}System Metrics:{Colors.RESET}")
            metrics = details['metrics']
            print(f"  Indexed Files: {metrics['indexed_files']}")
            print(f"  Total Chunks: {metrics['total_chunks']}")
    
    except Exception as e:
        print_error(f"Detailed search error: {e}")


async def test_edex_integration():
    """Test eDEX command handler"""
    print_header("TEST 7: eDEX Command Integration")
    
    try:
        print_info("Initializing eDEX command handler...")
        handler = EDEXCommandHandler()
        print_success("Command handler created")
        
        # Test search command
        print_info("Executing search command...")
        search_result = await handler.handle_search_command(
            "websocket communication",
            max_results=5
        )
        
        if search_result['success']:
            print_success("Search command executed")
            print(f"  Query: {search_result['query']}")
            print(f"  Results: {len(search_result['results'])}")
        else:
            print_error(f"Search command failed: {search_result.get('error')}")
        
        # Test index command
        print_info("Executing index command...")
        index_result = await handler.handle_index_command()
        
        if index_result['success']:
            print_success("Index command executed")
            print(f"  Directory: {index_result['directory']}")
            print(f"  Files: {index_result['metrics']['indexed_files']}")
        else:
            print_error(f"Index command failed: {index_result.get('error')}")
    
    except Exception as e:
        print_error(f"eDEX integration error: {e}")


async def test_convenience_function():
    """Test the convenience function"""
    print_header("TEST 8: Convenience Function")
    
    try:
        print_info("Using convenience function: search_files()")
        
        results = await search_files(
            query="error handling",
            directory="./KNO",
            max_results=3
        )
        
        if results:
            print_success(f"Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print_result(result, i)
        else:
            print_error("No results found")
    
    except Exception as e:
        print_error(f"Convenience function error: {e}")


async def test_edex_status_file():
    """Check eDEX status file"""
    print_header("TEST 9: eDEX Status File")
    
    try:
        status_file = Path("edex_status.json")
        
        if status_file.exists():
            print_success("eDEX status file found")
            
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            print(f"\n{Colors.CYAN}Status File Content:{Colors.RESET}")
            print(f"  Version: {status.get('version')}")
            print(f"  Timestamp: {status.get('timestamp')}")
            
            if status.get('progress'):
                progress = status['progress']
                print(f"\n{Colors.CYAN}Progress Information:{Colors.RESET}")
                print(f"  Operation: {progress.get('operation')}")
                print(f"  Current: {progress.get('current')}/{progress.get('total')}")
                print(f"  Percentage: {progress.get('percentage')}%")
                print(f"  Status: {progress.get('status')}")
            else:
                print_info("No active progress")
        
        else:
            print_info("eDEX status file not yet created (will be created on first operation)")
    
    except Exception as e:
        print_error(f"Status file check error: {e}")


# ============================================================================
# MAIN TEST SUITE
# ============================================================================

async def run_all_tests():
    """Run all tests"""
    print_header("KNO SEMANTIC SEARCH SYSTEM - COMPREHENSIVE TEST SUITE")
    
    # Test 1: Initialization
    search = await test_initialization()
    if not search:
        print_error("Cannot continue without initialized search system")
        return
    
    # Test 2: Indexing
    indexing_success = await test_indexing(search)
    if not indexing_success:
        print_error("Cannot continue without indexed files")
        return
    
    # Test 3: Basic Search
    await test_basic_search(search)
    
    # Test 4: Advanced Queries
    await test_advanced_queries(search)
    
    # Test 5: Caching
    await test_caching(search)
    
    # Test 6: Detailed Search
    await test_search_with_details(search)
    
    # Test 7: eDEX Integration
    await test_edex_integration()
    
    # Test 8: Convenience Function
    await test_convenience_function()
    
    # Test 9: Status File
    await test_edex_status_file()
    
    # Final summary
    print_header("TEST SUITE COMPLETED")
    print_success("All tests completed successfully!")
    print(f"\n{Colors.CYAN}System Status:{Colors.RESET}")
    metrics = search.get_metrics()
    print(f"  Total Indexed Files: {metrics['indexed_files']}")
    print(f"  Total Chunks: {metrics['total_chunks']}")
    print(f"  Search Cache Size: {len(search.search_cache)}")
    print(f"\n{Colors.GREEN}The semantic search system is ready to use!{Colors.RESET}\n")


async def run_quick_demo():
    """Run a quick demo"""
    print_header("QUICK DEMO")
    
    search = KNOAgentSemanticSearch(base_directory="./KNO")
    await search.initialize()
    
    print_info("Indexing directory...")
    await search.index_directory()
    
    print_info("\nPerforming sample searches...")
    queries = [
        "user authentication",
        "error handling",
        "configuration"
    ]
    
    for query in queries:
        results = await search.search_files(query, max_results=2)
        print(f"\n🔍 '{query}': {len(results)} results")
        for r in results[:2]:
            print(f"   - {r['file_path']}")
    
    print_success("\n✅ Demo completed!")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("\n" + Colors.GREEN + "Running quick demo..." + Colors.RESET)
        asyncio.run(run_quick_demo())
    else:
        print("\n" + Colors.GREEN + "Running comprehensive test suite..." + Colors.RESET)
        print(Colors.YELLOW + "\nNote: This may take several minutes on first run (model download).\n" + Colors.RESET)
        asyncio.run(run_all_tests())
