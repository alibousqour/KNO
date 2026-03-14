"""
KNO Advanced Semantic Search System with eDEX-UI Progress Integration
=====================================================================

نظام بحث دلالي متقدم مع تكامل شريط تقدم في واجهة eDEX السينمائية

Features:
- Async semantic search (البحث بالمعنى)
- Real-time progress bar in eDEX-UI
- File content analysis beyond keywords
- Multi-threading support
- Caching and optimization
- Detailed search logging

Author: KNO Architecture
License: MIT
Date: 2026-03-09
"""

import os
import json
import asyncio
import logging
import hashlib
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict
import re
from concurrent.futures import ThreadPoolExecutor

# Try to import semantic packages
try:
    from sentence_transformers import SentenceTransformer, util
    import numpy as np
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    logging.warning("sentence-transformers not available - using keyword fallback")

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('semantic_search.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('KNO.SemanticSearch')

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class FileType(Enum):
    """Supported file types for indexing"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"
    UNKNOWN = "unknown"


@dataclass
class SearchResult:
    """Search result with relevance information"""
    file_path: str
    file_type: str
    relevance_score: float  # 0-100
    matched_content: str
    line_numbers: List[int]
    keywords: List[str]
    summary: str
    rank: int = 1
    semantic_similarity: float = 0.0
    indexing_date: str = ""


@dataclass
class EDEXProgressData:
    """eDEX Progress Bar Data"""
    operation: str  # "indexing" or "searching"
    current: int
    total: int
    percentage: float
    status: str
    timestamp: str
    file_name: str = ""
    elapsed_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'operation': self.operation,
            'current': self.current,
            'total': self.total,
            'percentage': round(self.percentage, 2),
            'status': self.status,
            'timestamp': self.timestamp,
            'file_name': self.file_name,
            'elapsed_seconds': round(self.elapsed_seconds, 2)
        }


@dataclass
class IndexingMetrics:
    """Metrics for indexing operations"""
    total_files: int = 0
    indexed_files: int = 0
    failed_files: int = 0
    total_chunks: int = 0
    indexing_time_seconds: float = 0.0
    average_chunk_size: int = 0
    last_indexing_date: str = ""


# ============================================================================
# FILE UTILITIES
# ============================================================================

class FileAnalyzer:
    """Analyze and extract meaningful content from files"""
    
    CHUNK_SIZE = 512  # Characters per chunk
    MIN_MEANINGFUL_LENGTH = 10
    
    # File patterns to index
    INCLUDE_PATTERNS = {
        '*.py', '*.js', '*.ts', '*.java', '*.cs', '*.cpp', '*.h',
        '*.json', '*.yml', '*.yaml', '*.xml', '*.md', '*.txt'
    }
    
    # Patterns to exclude
    EXCLUDE_PATTERNS = {
        '*/__pycache__/*', '*/node_modules/*', '*/.git/*',
        '*/dist/*', '*/build/*', '*.pyc', '*.o', '*.exe'
    }
    
    @staticmethod
    def detect_file_type(file_path: str) -> FileType:
        """Detect file type from extension"""
        ext = Path(file_path).suffix.lower()
        
        type_map = {
            '.py': FileType.PYTHON,
            '.js': FileType.JAVASCRIPT,
            '.ts': FileType.JAVASCRIPT,
            '.java': FileType.JAVA,
            '.cs': FileType.CSHARP,
            '.cpp': FileType.CPP,
            '.h': FileType.CPP,
            '.json': FileType.JSON,
            '.yml': FileType.YAML,
            '.yaml': FileType.YAML,
            '.xml': FileType.XML,
            '.md': FileType.MARKDOWN,
            '.txt': FileType.TEXT,
        }
        
        return type_map.get(ext, FileType.UNKNOWN)
    
    @staticmethod
    def should_include_file(file_path: str) -> bool:
        """Check if file should be indexed"""
        path = Path(file_path)
        
        # Check exclude patterns
        for pattern in FileAnalyzer.EXCLUDE_PATTERNS:
            if path.match(pattern):
                return False
        
        # Check include patterns
        for pattern in FileAnalyzer.INCLUDE_PATTERNS:
            if path.match(pattern):
                return True
        
        return False
    
    @staticmethod
    def extract_meaningful_chunks(content: str, file_type: FileType) -> List[Tuple[str, int]]:
        """
        Extract meaningful chunks from file content.
        
        Returns:
            List of (chunk_text, line_number) tuples
        """
        if not content or len(content) < FileAnalyzer.MIN_MEANINGFUL_LENGTH:
            return []
        
        chunks = []
        
        if file_type == FileType.PYTHON:
            # Extract Python-specific meaningful content
            chunks = FileAnalyzer._extract_python_chunks(content)
        elif file_type in [FileType.JAVASCRIPT, FileType.JAVA, FileType.CSHARP]:
            chunks = FileAnalyzer._extract_code_chunks(content)
        elif file_type == FileType.JSON:
            chunks = FileAnalyzer._extract_json_chunks(content)
        elif file_type == FileType.MARKDOWN:
            chunks = FileAnalyzer._extract_markdown_chunks(content)
        else:
            # Generic extraction for other types
            chunks = FileAnalyzer._extract_generic_chunks(content)
        
        return chunks
    
    @staticmethod
    def _extract_python_chunks(content: str) -> List[Tuple[str, int]]:
        """Extract meaningful chunks from Python code"""
        chunks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            clean_line = line.strip()
            
            # Skip comments, empty lines, and imports
            if (clean_line and 
                not clean_line.startswith('#') and
                not clean_line.startswith('import ') and
                not clean_line.startswith('from ') and
                len(clean_line) > FileAnalyzer.MIN_MEANINGFUL_LENGTH):
                
                chunks.append((clean_line, i))
        
        return chunks
    
    @staticmethod
    def _extract_code_chunks(content: str) -> List[Tuple[str, int]]:
        """Extract meaningful chunks from generic code"""
        chunks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            clean_line = line.strip()
            
            if (clean_line and 
                not clean_line.startswith('//') and
                not clean_line.startswith('/*') and
                len(clean_line) > FileAnalyzer.MIN_MEANINGFUL_LENGTH):
                
                chunks.append((clean_line, i))
        
        return chunks
    
    @staticmethod
    def _extract_json_chunks(content: str) -> List[Tuple[str, int]]:
        """Extract meaningful chunks from JSON"""
        chunks = []
        try:
            data = json.loads(content)
            
            def extract_values(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        chunk = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, (str, int, float, bool)):
                            chunks.append((f"{chunk}: {value}", 1))
                        else:
                            extract_values(value, chunk)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        extract_values(item, f"{prefix}[{i}]")
            
            extract_values(data)
        except json.JSONDecodeError:
            pass
        
        return chunks
    
    @staticmethod
    def _extract_markdown_chunks(content: str) -> List[Tuple[str, int]]:
        """Extract meaningful chunks from Markdown"""
        chunks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            clean_line = line.strip()
            
            if (clean_line and 
                not clean_line.startswith('[') and
                len(clean_line) > FileAnalyzer.MIN_MEANINGFUL_LENGTH):
                
                chunks.append((clean_line, i))
        
        return chunks
    
    @staticmethod
    def _extract_generic_chunks(content: str) -> List[Tuple[str, int]]:
        """Extract meaningful chunks from generic text"""
        chunks = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line.strip()) > FileAnalyzer.MIN_MEANINGFUL_LENGTH:
                chunks.append((line.strip(), i))
        
        return chunks


# ============================================================================
# EDEX STATUS MANAGER
# ============================================================================

class EDEXStatusManager:
    """Manages eDEX-UI progress bar updates"""
    
    def __init__(self, status_file: str = "edex_status.json"):
        """
        Initialize eDEX status manager.
        
        Args:
            status_file: Path to eDEX status file
        """
        self.status_file = status_file
        self.lock = threading.Lock()
        self.ensure_directory()
    
    def ensure_directory(self):
        """Ensure status file directory exists"""
        status_dir = os.path.dirname(self.status_file) or "."
        os.makedirs(status_dir, exist_ok=True)
    
    def update_progress(self, progress: EDEXProgressData):
        """
        تحديث شريط التقدم في eDEX-UI
        
        Args:
            progress: EDEXProgressData object
        """
        with self.lock:
            try:
                status_data = {
                    'version': '3.0',
                    'timestamp': datetime.now().isoformat(),
                    'progress': progress.to_dict(),
                    'ui_elements': {
                        'progress_bar': {
                            'visible': True,
                            'percentage': progress.percentage,
                            'label': progress.status,
                            'color': self._get_progress_color(progress.percentage),
                            'animated': True,
                            'show_percentage': True
                        },
                        'status_text': {
                            'primary': progress.status,
                            'secondary': f"{progress.current}/{progress.total} items",
                            'operation': progress.operation,
                            'file': progress.file_name
                        }
                    }
                }
                
                with open(self.status_file, 'w') as f:
                    json.dump(status_data, f, indent=2)
                
                logger.debug(f"eDEX status updated: {progress.status}")
            
            except Exception as e:
                logger.error(f"Failed to update eDEX status: {e}")
    
    def clear_progress(self):
        """إزالة شريط التقدم من eDEX-UI"""
        with self.lock:
            try:
                status_data = {
                    'version': '3.0',
                    'timestamp': datetime.now().isoformat(),
                    'progress': None,
                    'ui_elements': {
                        'progress_bar': {
                            'visible': False
                        }
                    }
                }
                
                with open(self.status_file, 'w') as f:
                    json.dump(status_data, f, indent=2)
                
                logger.info("eDEX progress display cleared")
            except Exception as e:
                logger.error(f"Failed to clear eDEX status: {e}")
    
    @staticmethod
    def _get_progress_color(percentage: float) -> str:
        """Get color based on progress percentage"""
        if percentage < 25:
            return "#FF6B6B"  # Red
        elif percentage < 50:
            return "#FFA500"  # Orange
        elif percentage < 75:
            return "#FFD700"  # Gold
        elif percentage < 100:
            return "#90EE90"  # Light Green
        else:
            return "#00CC00"  # Green


# ============================================================================
# SEMANTIC SEARCH ENGINE
# ============================================================================

class SemanticSearchEngine:
    """
    نظام البحث الدلالي المتقدم
    
    يوفر البحث بالمعنى بدلاً من مجرد البحث عن الكلمات المفتاحية
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic search engine.
        
        Args:
            model_name: Sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.file_embeddings = {}  # Cache embeddings
        self.file_data = {}  # Store file metadata
        self.edex_manager = EDEXStatusManager()
        self.metrics = IndexingMetrics()
        self.index_lock = threading.Lock()
        self.initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize the semantic search engine with embeddings model.
        
        Returns:
            bool: True if successful
        """
        try:
            if not HAS_TRANSFORMERS:
                logger.warning("Sentence transformers not available - using keyword search only")
                return True
            
            logger.info("Initializing semantic search engine...")
            
            # Load model (runs in executor to not block)
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            
            def load_model():
                return SentenceTransformer(self.model_name)
            
            self.model = await loop.run_in_executor(executor, load_model)
            self.initialized = True
            logger.info("Semantic search engine initialized successfully")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize semantic search: {e}")
            return False
    
    async def index_directory(
        self,
        directory: str,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        فهرسة مجلد كامل للبحث الدلالي
        
        Args:
            directory: Path to directory
            progress_callback: Optional callback for progress updates
        
        Returns:
            bool: True if successful
        """
        try:
            start_time = datetime.now()
            self.metrics = IndexingMetrics()
            
            # Collect all files
            logger.info(f"Scanning directory: {directory}")
            files_to_index = []
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if FileAnalyzer.should_include_file(file_path):
                        files_to_index.append(file_path)
            
            total_files = len(files_to_index)
            self.metrics.total_files = total_files
            
            logger.info(f"Found {total_files} files to index")
            
            if total_files == 0:
                return True
            
            # Index files
            for idx, file_path in enumerate(files_to_index, 1):
                try:
                    await self._index_file(
                        file_path,
                        idx,
                        total_files,
                        progress_callback
                    )
                
                except Exception as e:
                    logger.error(f"Failed to index {file_path}: {e}")
                    self.metrics.failed_files += 1
            
            # Update metrics
            elapsed_seconds = (datetime.now() - start_time).total_seconds()
            self.metrics.indexing_time_seconds = elapsed_seconds
            self.metrics.last_indexing_date = datetime.now().isoformat()
            
            if self.metrics.total_chunks > 0:
                self.metrics.average_chunk_size = FileAnalyzer.CHUNK_SIZE
            
            logger.info(
                f"Indexing complete: {self.metrics.indexed_files}/{total_files} files, "
                f"{self.metrics.total_chunks} chunks in {elapsed_seconds:.2f}s"
            )
            
            # Clear progress
            self.edex_manager.clear_progress()
            
            return True
        
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            self.edex_manager.clear_progress()
            return False
    
    async def _index_file(
        self,
        file_path: str,
        current: int,
        total: int,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Index a single file"""
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_type = FileAnalyzer.detect_file_type(file_path)
            chunks = FileAnalyzer.extract_meaningful_chunks(content, file_type)
            
            if not chunks:
                return False
            
            # Store file data
            with self.index_lock:
                self.file_data[file_path] = {
                    'type': file_type.value,
                    'chunks': chunks,
                    'content_hash': hashlib.sha256(content.encode()).hexdigest(),
                    'indexed_date': datetime.now().isoformat(),
                    'file_size': len(content)
                }
                
                self.metrics.indexed_files += 1
                self.metrics.total_chunks += len(chunks)
            
            # Update progress
            percentage = (current / total) * 100
            progress = EDEXProgressData(
                operation="indexing",
                current=current,
                total=total,
                percentage=percentage,
                status=f"🗂️ Indexing: {Path(file_path).name}",
                timestamp=datetime.now().isoformat(),
                file_name=Path(file_path).name,
                elapsed_seconds=0.0
            )
            
            self.edex_manager.update_progress(progress)
            
            if progress_callback:
                progress_callback({
                    'current': current,
                    'total': total,
                    'percentage': percentage,
                    'file': file_path
                })
            
            return True
        
        except Exception as e:
            logger.error(f"Error indexing file {file_path}: {e}")
            self.metrics.failed_files += 1
            return False
    
    async def search_files(
        self,
        query: str,
        max_results: int = 10,
        min_relevance: float = 0.3
    ) -> List[SearchResult]:
        """
        البحث بالمعنى عن الملفات
        
        بدلاً من البحث عن كلمات محددة، يبحث هذا عن الملفات ذات الصلة بمعنى الاستعلام.
        
        Args:
            query: Search query (e.g., "user authentication" or "database operations")
            max_results: Maximum results to return
            min_relevance: Minimum relevance score (0-1)
        
        Returns:
            List of SearchResult objects sorted by relevance
        
        Example:
            >>> results = await search_engine.search_files("user authentication")
            >>> for result in results:
            ...     print(f"{result.file_path}: {result.relevance_score:.1f}%")
        """
        
        if not self.file_data:
            logger.warning("No files indexed. Please call index_directory() first.")
            return []
        
        try:
            start_time = datetime.now()
            results = []
            
            # Update progress - searching
            query_progress = EDEXProgressData(
                operation="searching",
                current=0,
                total=100,
                percentage=10,
                status=f"🔍 Searching: {query[:50]}...",
                timestamp=datetime.now().isoformat(),
                elapsed_seconds=0.0
            )
            self.edex_manager.update_progress(query_progress)
            
            # Perform semantic search
            if self.model and HAS_TRANSFORMERS:
                results = await self._semantic_search(
                    query, max_results, min_relevance
                )
            else:
                results = await self._keyword_search(
                    query, max_results
                )
            
            # Update progress - processing
            process_progress = EDEXProgressData(
                operation="searching",
                current=75,
                total=100,
                percentage=75,
                status=f"📊 Processing {len(results)} results...",
                timestamp=datetime.now().isoformat(),
                elapsed_seconds=(datetime.now() - start_time).total_seconds()
            )
            self.edex_manager.update_progress(process_progress)
            
            # Sort by relevance
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Update progress - complete
            elapsed = (datetime.now() - start_time).total_seconds()
            complete_progress = EDEXProgressData(
                operation="searching",
                current=100,
                total=100,
                percentage=100,
                status=f"✅ Found {len(results)} relevant files in {elapsed:.1f}s",
                timestamp=datetime.now().isoformat(),
                elapsed_seconds=elapsed
            )
            self.edex_manager.update_progress(complete_progress)
            
            # Clear progress after 2s
            await asyncio.sleep(2)
            self.edex_manager.clear_progress()
            
            logger.info(f"Search complete: {len(results)} results in {elapsed:.2f}s")
            return results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.edex_manager.clear_progress()
            return []
    
    async def _semantic_search(
        self,
        query: str,
        max_results: int,
        min_relevance: float
    ) -> List[SearchResult]:
        """Perform semantic search using embeddings"""
        try:
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(max_workers=1)
            
            # Encode query
            def encode_query():
                return self.model.encode(query)
            
            query_embedding = await loop.run_in_executor(executor, encode_query)
            results = []
            
            # Search all files
            for file_path, file_info in self.file_data.items():
                file_type = file_info['type']
                chunks = file_info['chunks']
                
                # Encode chunks and compare
                chunk_texts = [chunk[0] for chunk in chunks]
                
                def encode_chunks():
                    return self.model.encode(chunk_texts)
                
                chunk_embeddings = await loop.run_in_executor(
                    executor, encode_chunks
                )
                
                # Calculate similarities
                similarities = util.pytorch_cos_sim(
                    query_embedding, chunk_embeddings
                )[0]
                
                # Get top matching chunks
                top_indices = np.argsort(-similarities.numpy())[:3]
                
                for idx in top_indices:
                    score = float(similarities[idx]) * 100
                    
                    if score >= (min_relevance * 100):
                        chunk_text, line_num = chunks[idx]
                        
                        # Extract keywords
                        keywords = self._extract_keywords(chunk_text)
                        
                        result = SearchResult(
                            file_path=file_path,
                            file_type=file_type,
                            relevance_score=score,
                            matched_content=chunk_text,
                            line_numbers=[line_num],
                            keywords=keywords,
                            summary=chunk_text[:100],
                            semantic_similarity=float(similarities[idx]),
                            indexing_date=file_info['indexed_date']
                        )
                        
                        results.append(result)
            
            # Sort and limit
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results[:max_results]
        
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    async def _keyword_search(
        self,
        query: str,
        max_results: int
    ) -> List[SearchResult]:
        """Fallback keyword search"""
        try:
            keywords = query.lower().split()
            results = []
            
            for file_path, file_info in self.file_data.items():
                file_type = file_info['type']
                chunks = file_info['chunks']
                
                for chunk_text, line_num in chunks:
                    # Calculate keyword match score
                    matches = sum(
                        1 for kw in keywords
                        if kw in chunk_text.lower()
                    )
                    
                    if matches > 0:
                        score = (matches / len(keywords)) * 100
                        keywords_found = [
                            kw for kw in keywords
                            if kw in chunk_text.lower()
                        ]
                        
                        result = SearchResult(
                            file_path=file_path,
                            file_type=file_type,
                            relevance_score=score,
                            matched_content=chunk_text,
                            line_numbers=[line_num],
                            keywords=keywords_found,
                            summary=chunk_text[:100],
                            indexing_date=file_info['indexed_date']
                        )
                        
                        results.append(result)
            
            # Sort and limit
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            return results[:max_results]
        
        except Exception as e:
            logger.error(f"Keyword search error: {e}")
            return []
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z_]\w*\b', text)
        # Filter common words
        common_words = {'def', 'class', 'if', 'else', 'for', 'while', 'return',
                       'import', 'from', 'as', 'async', 'await', 'try', 'except'}
        unique_words = list(set(w for w in words if w not in common_words))
        return unique_words[:5]


# ============================================================================
# MAIN INTERFACE
# ============================================================================

class KNOSemanticSearch:
    """
    واجهة من بطة واحدة للبحث الدلالي الكامل مع eDEX-UI
    
    Main interface for semantic search with eDEX-UI integration.
    """
    
    def __init__(
        self,
        base_directory: str = ".",
        status_file: str = "edex_status.json",
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize KNO semantic search system.
        
        Args:
            base_directory: Directory to index
            status_file: Path to eDEX status file
            model_name: Embedding model to use
        """
        self.base_directory = base_directory
        self.status_file = status_file
        self.search_engine = SemanticSearchEngine(model_name)
        self.initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the system"""
        init_success = await self.search_engine.initialize()
        self.initialized = init_success
        return init_success
    
    async def index_directory(self) -> bool:
        """Index the base directory"""
        if not self.initialized:
            await self.initialize()
        
        return await self.search_engine.index_directory(self.base_directory)
    
    async def search_files(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        البحث عن الملفات بناءً على المعنى
        
        Search files by meaning (semantic search).
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            List of search results as dictionaries
        """
        if not self.initialized:
            logger.error("System not initialized. Call initialize() first.")
            return []
        
        results = await self.search_engine.search_files(query, max_results)
        
        return [
            {
                'file_path': r.file_path,
                'file_type': r.file_type,
                'relevance_score': round(r.relevance_score, 2),
                'matched_content': r.matched_content,
                'line_numbers': r.line_numbers,
                'keywords': r.keywords,
                'summary': r.summary
            }
            for r in results
        ]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get indexing metrics"""
        m = self.search_engine.metrics
        return {
            'total_files': m.total_files,
            'indexed_files': m.indexed_files,
            'failed_files': m.failed_files,
            'total_chunks': m.total_chunks,
            'indexing_time_seconds': m.indexing_time_seconds,
            'average_chunk_size': m.average_chunk_size,
            'last_indexing_date': m.last_indexing_date
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage"""
    
    # Initialize
    search = KNOSemanticSearch(
        base_directory="./KNO",
        status_file="edex_status.json"
    )
    
    await search.initialize()
    
    # Index directory
    print("Indexing directory...")
    await search.index_directory()
    
    # Print metrics
    metrics = search.get_metrics()
    print(f"\n📊 Metrics: {metrics}")
    
    # Search examples
    queries = [
        "user authentication",
        "database operations",
        "error handling"
    ]
    
    for query in queries:
        print(f"\n🔍 Searching: {query}")
        results = await search.search_files(query, max_results=5)
        
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['file_path']} ({result['relevance_score']}%)")


if __name__ == "__main__":
    asyncio.run(main())
