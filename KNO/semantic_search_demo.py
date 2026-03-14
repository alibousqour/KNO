#!/usr/bin/env python3
"""
KNO Semantic Search Demo - Ready to Run
=======================================

Interactive demo of semantic file search with eDEX-UI integration.
This script shows all the capabilities in action.

Usage:
    python semantic_search_demo.py

Features:
    - Interactive search queries
    - Real-time progress visualization
    - Directory indexing with progress
    - Search result analysis
    - Performance metrics

Author: KNO Architecture
License: MIT
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)-8s %(message)s'
)
logger = logging.getLogger('KNO.Demo')

# Import semantic search components
try:
    from kno_agent_semantic_search import KNOSemanticAgent
    logger.info("✅ Imported semantic search agent successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import semantic search agent: {e}")
    logger.error("Please ensure semantic_file_system_enhanced.py is available")
    sys.exit(1)


# ============================================================================
# DEMO CLASS
# ============================================================================

class SemanticSearchDemo:
    """Interactive demo of semantic search with eDEX integration"""
    
    def __init__(self):
        """Initialize demo"""
        self.agent = KNOSemanticAgent(edex_status_file="edex_status.json")
        self.initialized = False
    
    async def setup(self) -> bool:
        """Setup the demo"""
        print("=" * 70)
        print("🚀 KNO Semantic Search Demo - Initializing...")
        print("=" * 70)
        
        try:
            print("\n1️⃣  Initializing semantic search system...")
            success = await self.agent.initialize()
            
            if not success:
                print("❌ Failed to initialize")
                return False
            
            self.initialized = True
            print("✅ Semantic search system initialized\n")
            return True
        
        except Exception as e:
            logger.error(f"Setup error: {e}")
            return False
    
    async def demo_basic_search(self):
        """Demo 1: Basic semantic search"""
        print("\n" + "=" * 70)
        print("DEMO 1: Basic Semantic Search")
        print("=" * 70)
        
        queries = [
            "user authentication and login",
            "database operations and queries",
            "error handling and exceptions",
            "configuration and settings management"
        ]
        
        print("\n📌 Performing semantic searches...")
        print("(These search by MEANING, not keywords)\n")
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. Query: \"{query}\"")
            print("-" * 70)
            
            results = await self.agent.search_files(
                query,
                limit=3,
                show_edex_progress=True
            )
            
            if results:
                print(f"✅ Found {len(results)} relevant files:\n")
                for j, result in enumerate(results, 1):
                    score = result['relevance_score']
                    color = "🟢" if score > 0.8 else "🟡" if score > 0.6 else "🟠"
                    
                    print(f"  {j}. {color} {result['file_path']}")
                    print(f"     Relevance: {score:.2%} | Type: {result['file_type']}")
                    if result['content_excerpt']:
                        excerpt = result['content_excerpt'][:60]
                        print(f"     Preview: {excerpt}...\n")
            else:
                print("⚠️  No relevant files found\n")
    
    async def demo_directory_indexing(self):
        """Demo 2: Index a directory with progress"""
        print("\n" + "=" * 70)
        print("DEMO 2: Directory Indexing with Progress")
        print("=" * 70)
        
        # Use current directory or a sample directory
        test_dir = "./KNO" if os.path.exists("./KNO") else "."
        
        print(f"\n📂 Indexing directory: {test_dir}")
        print("(Watch the progress in edex_status.json)\n")
        
        success = await self.agent.index_directory_with_progress(
            test_dir,
            show_edex_progress=True
        )
        
        if success:
            # Get statistics
            stats = self.agent.get_search_statistics()
            if stats:
                print("\n✅ Indexing complete! Statistics:")
                print(f"   📄 Files indexed: {stats['indexed_files']}")
                print(f"   📦 Text chunks: {stats['total_chunks']}")
                print(f"   💾 Total size: {stats['total_size_mb']:.2f} MB")
                print(f"   ⏱️  Time taken: {stats['indexing_time_seconds']:.2f}s")
        else:
            print("❌ Indexing failed")
    
    async def demo_advanced_search(self):
        """Demo 3: Advanced search features"""
        print("\n" + "=" * 70)
        print("DEMO 3: Advanced Search Features")
        print("=" * 70)
        
        # Feature 1: Search with ranking
        print("\n1️⃣  Search with Advanced Ranking:")
        print("-" * 70)
        
        results = await self.agent.search_with_ranking(
            "system initialization and startup",
            limit=5
        )
        
        if results:
            print(f"✅ Top results (ranked by relevance):\n")
            for i, result in enumerate(results, 1):
                print(
                    f"{i}. {result['file_path']}\n"
                    f"   Score: {result['relevance_score']:.2%}\n"
                )
        else:
            print("No results found")
        
        # Feature 2: Multiple searches
        print("\n2️⃣  Multiple Searches (batch):")
        print("-" * 70)
        
        queries = [
            "testing and validation",
            "performance optimization",
            "security and encryption"
        ]
        
        print(f"Searching for {len(queries)} topics in parallel...\n")
        
        results_map = await self.agent.multi_query_search(queries, limit=2)
        
        for query, results in results_map.items():
            print(f"📌 {query}: {len(results)} results")
            for r in results:
                print(f"   • {Path(r['file_path']).name} ({r['relevance_score']:.0%})")
            print()
    
    async def demo_performance_metrics(self):
        """Demo 4: Performance and statistics"""
        print("\n" + "=" * 70)
        print("DEMO 4: Performance Metrics")
        print("=" * 70)
        
        print("\n📊 Indexing Statistics:")
        print("-" * 70)
        
        stats = self.agent.get_search_statistics()
        
        if stats:
            # Display statistics
            print(f"✅ Current System Status:\n")
            print(f"   Indexed Files: {stats['indexed_files']:,}")
            print(f"   Total Files Scanned: {stats['total_files']:,}")
            print(f"   Failed Files: {stats['failed_files']}")
            print(f"   Total Chunks: {stats['total_chunks']:,}")
            print(f"   Database Size: {stats['total_size_mb']:.2f} MB")
            print(f"   Indexing Time: {stats['indexing_time_seconds']:.2f}s")
            
            # Calculate metrics
            if stats['total_files'] > 0:
                success_rate = (stats['indexed_files'] / stats['total_files']) * 100
                print(f"\n   Success Rate: {success_rate:.1f}%")
            
            if stats['indexing_time_seconds'] > 0:
                speed = stats['indexed_files'] / stats['indexing_time_seconds']
                print(f"   Indexing Speed: {speed:.1f} files/sec")
            
            # Performance benchmarks
            print(f"\n📈 Expected Performance:")
            print(f"   Search latency: ~50-100ms (first query)")
            print(f"   Search latency: ~5-10ms (cached)")
            print(f"   Indexing speed: ~30-100 files/sec")
            print(f"   Memory per file: ~2-5 KB")
        else:
            print("⚠️  No statistics available yet (index empty?)")
    
    async def demo_interactive_search(self):
        """Demo 5: Interactive search"""
        print("\n" + "=" * 70)
        print("DEMO 5: Interactive Search")
        print("=" * 70)
        print("\nEnter search queries (type 'quit' to exit):\n")
        
        while True:
            try:
                query = input("🔍 Search query: ").strip()
                
                if query.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                print("\nSearching...")
                results = await self.agent.search_files(
                    query,
                    limit=5,
                    show_edex_progress=True
                )
                
                if results:
                    print(f"\n✅ Found {len(results)} results:\n")
                    for i, result in enumerate(results, 1):
                        print(
                            f"{i}. {result['file_path']}\n"
                            f"   Relevance: {result['relevance_score']:.1%}\n"
                            f"   Type: {result['file_type']}\n"
                        )
                else:
                    print("⚠️  No results found\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")
    
    async def run_all_demos(self):
        """Run all demos in sequence"""
        if not self.initialized:
            if not await self.setup():
                return
        
        try:
            # Run demos
            await self.demo_basic_search()
            
            # Optional: uncomment to run additional demos
            # await self.demo_directory_indexing()
            # await self.demo_advanced_search()
            # await self.demo_performance_metrics()
            # await self.demo_interactive_search()
            
            print("\n" + "=" * 70)
            print("✅ Demo Complete!")
            print("=" * 70)
            print("\n💡 Next Steps:")
            print("   1. Edit this script to uncomment other demos")
            print("   2. Try the interactive search demo")
            print("   3. Integrate with your agent.py")
            print("   4. Monitor progress in edex_status.json")
            print()
        
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user")
        except Exception as e:
            logger.error(f"Demo error: {e}")
            import traceback
            traceback.print_exc()


# ============================================================================
# MENU SYSTEM
# ============================================================================

async def interactive_menu():
    """Interactive menu for demo selection"""
    demo = SemanticSearchDemo()
    
    if not await demo.setup():
        return
    
    while True:
        print("\n" + "=" * 70)
        print("🎯 KNO Semantic Search Demo - Menu")
        print("=" * 70)
        print("""
1. Basic Search (Example queries)
2. Index Directory (With progress)
3. Advanced Features (Ranking, batch)
4. Performance Metrics (Stats)
5. Interactive Search (Manual queries)
0. Exit

        """)
        
        choice = input("Select demo (0-5): ").strip()
        
        try:
            if choice == "1":
                await demo.demo_basic_search()
            elif choice == "2":
                await demo.demo_directory_indexing()
            elif choice == "3":
                await demo.demo_advanced_search()
            elif choice == "4":
                await demo.demo_performance_metrics()
            elif choice == "5":
                await demo.demo_interactive_search()
            elif choice == "0":
                print("\n👋 Thank you for using KNO Semantic Search!")
                break
            else:
                print("❌ Invalid choice")
        
        except Exception as e:
            print(f"❌ Error: {e}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    import sys
    
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🚀 KNO SEMANTIC SEARCH DEMO - INTERACTIVE DEMONSTRATION             ║
║                                                                      ║
║   Search your codebase by MEANING, not keywords!                    ║
║   Real-time progress visualization in eDEX-UI                       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        # Command line mode
        query = " ".join(sys.argv[1:])
        demo = SemanticSearchDemo()
        await demo.setup()
        results = await demo.agent.search_files(query, limit=5)
        
        print(f"\nResults for: \"{query}\"\n")
        for result in results:
            print(
                f"📄 {result['file_path']}\n"
                f"   Score: {result['relevance_score']:.1%}\n"
            )
    else:
        # Interactive menu
        await interactive_menu()


# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
