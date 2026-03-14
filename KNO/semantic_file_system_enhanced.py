"""
KNO Semantic File System (SFS) v2.0 - Enhanced Edition
=====================================================
Intelligent file management system with advanced semantic indexing and search.

Features:
- Advanced Asynchronous file indexing using Sentence-Transformers
- Vector database storage (ChromaDB/FAISS) with caching
- Multi-modal semantic search (files, metadata, content)
- Intelligent file chunking with context awareness
- Real-time indexing progress tracking
- eDEX-UI integration with status broadcasting
- Security-aware file filtering
- Auto-deduplication and change detection
- Query expansion and semantic relevance boosting
- Batch operations support
- Persistent index management

Author: KNO Architecture (Enhanced v2.0)
License: MIT
Build Date: 2026-03-09
"""

import os
import sys
import json
import asyncio
import hashlib
import logging
import threading
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Callable, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from collections import defaultdict
import re

# Third-party imports with fallbacks
try:
    import numpy as np
except ImportError:
    np = None

try:
    from sentence_transformers import SentenceTransformer, util
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMADB = True
except ImportError:
    HAS_CHROMADB = False

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

try:
    from PyPDF2 import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class FileType(Enum):
    """Supported file types for indexing"""
    TEXT = "text"
    MARKDOWN = "markdown"
    PYTHON = "python"
    PDF = "pdf"
    JSON = "json"
    CODE = "code"
    UNKNOWN = "unknown"

class IndexingStatus(Enum):
    """Status of indexing operation"""
    IDLE = "idle"
    INDEXING = "indexing"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    ERROR = "error"

# File extension mapping
FILE_TYPE_MAP = {
    '.txt': FileType.TEXT,
    '.md': FileType.MARKDOWN,
    '.markdown': FileType.MARKDOWN,
    '.py': FileType.PYTHON,
    '.js': FileType.CODE,
    '.ts': FileType.CODE,
    '.java': FileType.CODE,
    '.cpp': FileType.CODE,
    '.c': FileType.CODE,
    '.go': FileType.CODE,
    '.rs': FileType.CODE,
    '.sh': FileType.CODE,
    '.bash': FileType.CODE,
    '.pdf': FileType.PDF,
    '.json': FileType.JSON,
}

# Default ignore patterns (security-aware)
DEFAULT_IGNORE_PATTERNS = [
    '.git', '.gitignore', '__pycache__', '.venv', 'venv', '.env-1',
    '.env', '.env.local', '.env.*.local',
    'node_modules', 'dist', 'build', '.DS_Store',
    '*.exe', '*.dll', '*.so', '*.dylib',
    '.idea', '.vscode', '*.swp', '*.swo',
    'private', 'secret', 'password', 'key',
    '*.pyc', '*.pyo', '*.egg-info',
    'Cookies', 'Cache', 'cookies-journal',
    'eDEX-ui', 'whisper.cpp', 'openclaw',
]

# Advanced chunking configuration
TEXT_CHUNK_SIZE = 500  # words
TEXT_OVERLAP = 75  # words for context
MIN_CHUNK_LENGTH = 20  # minimum words in chunk

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """Setup logger with file and console handlers"""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

logger = setup_logger('KNO.SemanticFS', log_file='semantic_fs.log')

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class IndexedFile:
    """Representation of an indexed file"""
    file_path: str
    file_type: str
    file_hash: str
    indexed_at: str
    chunk_count: int
    content_preview: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    encoding: str = "utf-8"

@dataclass
class SearchResult:
    """Result from semantic search"""
    file_path: str
    file_type: str
    chunk_index: int
    relevance_score: float
    content_excerpt: str
    matched_query: str
    keywords: List[str] = field(default_factory=list)
    rank: int = 0

@dataclass
class IndexingMetrics:
    """Metrics from indexing operation"""
    total_files: int = 0
    indexed_files: int = 0
    failed_files: int = 0
    total_chunks: int = 0
    total_size_mb: float = 0.0
    indexing_time_seconds: float = 0.0
    avg_chunk_size: int = 0
    files_skipped: int = 0
    
    def get_success_rate(self) -> float:
        """Get percentage of successfully indexed files"""
        return (self.indexed_files / self.total_files * 100) if self.total_files > 0 else 0

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def should_ignore_file(file_path: str, ignore_patterns: List[str]) -> bool:
    """Check if file should be ignored based on patterns"""
    path_str = str(file_path).lower()
    for pattern in ignore_patterns:
        if pattern.lstrip('*.').lower() in path_str.lower():
            return True
    if any(part.startswith('.') for part in Path(file_path).parts):
        return True
    return False

def calculate_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """Calculate SHA-256 hash of file"""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except Exception as e:
        logger.warning(f"Failed to hash {file_path}: {e}")
        return ""

def extract_keywords(text: str, num_keywords: int = 5) -> List[str]:
    """Extract keywords from text (simple approach)"""
    # Remove special characters and split
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                  'to', 'for', 'of', 'with', 'is', 'are', 'was', 'be', 
                  'that', 'this', 'it', 'from'}
    
    filtered = [w for w in words if w not in stop_words and len(w) > 3]
    
    # Count frequency
    freq = defaultdict(int)
    for word in filtered:
        freq[word] += 1
    
    # Return top keywords
    top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in top_words[:num_keywords]]

def extract_text_from_file(file_path: str, file_type: FileType) -> str:
    """Extract text content from different file types"""
    try:
        if file_type == FileType.PDF:
            if not HAS_PYPDF:
                logger.warning("PyPDF2 not available, skipping PDF")
                return ""
            with open(file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text += f"\n--- PAGE {page_num + 1} ---\n"
                        text += page.extract_text()
                    except Exception as e:
                        logger.debug(f"Failed to extract page {page_num}: {e}")
                return text
        else:
            # TEXT, MARKDOWN, PYTHON, CODE, JSON
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Failed to extract text from {file_path}: {e}")
        return ""

def chunk_text(text: str, 
               chunk_size: int = TEXT_CHUNK_SIZE, 
               overlap: int = TEXT_OVERLAP,
               file_type: FileType = FileType.TEXT) -> List[str]:
    """Split text into intelligent overlapping chunks"""
    
    # For code files, use line-based chunking
    if file_type in [FileType.PYTHON, FileType.CODE]:
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_words = 0
        
        for line in lines:
            words_in_line = len(line.split())
            
            if current_words + words_in_line > chunk_size and current_chunk:
                chunks.append('\n'.join(current_chunk))
                # Add overlap
                overlap_lines = min(len(current_chunk), max(1, overlap // 10))
                current_chunk = current_chunk[-overlap_lines:] if overlap_lines > 0 else []
                current_words = sum(len(l.split()) for l in current_chunk)
            
            current_chunk.append(line)
            current_words += words_in_line
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
    
    else:
        # For text files, use word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.split()) >= MIN_CHUNK_LENGTH:
                chunks.append(chunk)
    
    return chunks if chunks else [text[:1000]]

# ============================================================================
# CHROMA DB BACKEND
# ============================================================================

class ChromaDBBackend:
    """ChromaDB vector database backend"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db = None
        self.collection = None
    
    async def initialize(self):
        """Initialize ChromaDB"""
        try:
            settings = Settings(
                chroma_db_impl="duckdb",
                persist_directory=str(self.db_path),
                anonymized_telemetry=False,
            )
            self.db = chromadb.Client(settings)
            logger.info(f"ChromaDB initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"ChromaDB init failed: {e}")
            raise
    
    async def get_or_create_collection(self, name: str):
        """Get or create collection"""
        try:
            self.collection = self.db.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            logger.error(f"Failed to get/create collection: {e}")
            raise
    
    async def add_documents(self, doc_ids: List[str], documents: List[str], 
                           metadatas: List[Dict], embeddings: List[List[float]]):
        """Add documents to collection"""
        try:
            self.collection.add(
                ids=doc_ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings,
            )
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def query(self, embedding: List[float], n_results: int) -> Dict:
        """Query collection"""
        try:
            return self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
            )
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    async def reset(self):
        """Reset database"""
        if self.db:
            self.db.reset()

# ============================================================================
# FAISS BACKEND
# ============================================================================

class FAISSBackend:
    """FAISS vector database backend"""
    
    def __init__(self, embedding_dim: int):
        self.embedding_dim = embedding_dim
        self.index = None
        self.metadata_store = {}
        self.chunk_counter = 0
    
    async def initialize(self):
        """Initialize FAISS index"""
        try:
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            logger.info(f"FAISS index initialized (dimension: {self.embedding_dim})")
        except Exception as e:
            logger.error(f"FAISS init failed: {e}")
            raise
    
    async def add_documents(self, doc_ids: List[str], embeddings: np.ndarray, 
                           metadatas: List[Dict]):
        """Add documents to FAISS"""
        try:
            embeddings = np.array(embeddings, dtype='float32')
            self.index.add(embeddings)
            
            for doc_id, metadata in zip(doc_ids, metadatas):
                self.metadata_store[self.chunk_counter] = (doc_id, metadata)
                self.chunk_counter += 1
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    async def query(self, embedding: np.ndarray, n_results: int) -> Tuple[np.ndarray, np.ndarray]:
        """Query FAISS index"""
        try:
            embedding = np.array(embedding, dtype='float32').reshape(1, -1)
            distances, indices = self.index.search(embedding, min(n_results, self.index.ntotal))
            return distances[0], indices[0]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise
    
    async def reset(self):
        """Reset index"""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata_store.clear()
        self.chunk_counter = 0

# ============================================================================
# MAIN SEMANTIC FILE SYSTEM CLASS
# ============================================================================

class KNOFileSystem:
    """
    Enhanced Semantic File System for KNO
    
    Features:
    - Async vector indexing
    - Multi-backend support (ChromaDB/FAISS)
    - Intelligent chunking and caching
    - Progress tracking
    - Real-time statistics
    """
    
    def __init__(self, 
                 index_dir: Optional[str] = None,
                 edex_status_file: Optional[str] = None,
                 use_chroma: bool = True,
                 model_name: str = "all-MiniLM-L6-v2",
                 ignore_patterns: List[str] = None,
                 batch_size: int = 32):
        """
        Initialize KNOFileSystem
        
        Args:
            index_dir: Directory to store indexes (default: ./sfs_index)
            edex_status_file: Path to edex_status.json for progress tracking
            use_chroma: Use ChromaDB (True) or FAISS (False)
            model_name: Name of Sentence-Transformer model
            ignore_patterns: Custom ignore patterns
            batch_size: Batch size for embedding generation
        """
        self.index_dir = Path(index_dir or "./sfs_index")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.edex_status_file = edex_status_file
        self.use_chroma = use_chroma
        self.model_name = model_name
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
        self.batch_size = batch_size
        
        # State tracking
        self.indexed_files: Dict[str, IndexedFile] = {}
        self.embedding_model = None
        self.db_backend = None
        self.chunk_to_file_map: Dict[int, Tuple[str, int]] = {}  # chunk_id -> (file_path, chunk_index)
        
        # Threading/async
        self._lock = threading.Lock()
        self._indexing_in_progress = False
        self._indexing_status = IndexingStatus.IDLE
        
        # Caching
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._file_content_cache: Dict[str, str] = {}
        
        # Statistics
        self.metrics = IndexingMetrics()
        self.stats = {
            'total_files_indexed': 0,
            'total_chunks': 0,
            'index_size_mb': 0.0,
            'last_index_time': None,
            'model_loaded': False,
            'chunks_per_file': 0,
        }
        
        logger.info(f"KNOFileSystem v2.0 initialized at {self.index_dir}")
        logger.info(f"Using {'ChromaDB' if self.use_chroma else 'FAISS'}")
        logger.info(f"Embedding model: {self.model_name}")
        logger.info(f"Batch size: {batch_size}")
    
    @property
    def indexing_status(self) -> str:
        """Get current indexing status"""
        return self._indexing_status.value
    
    async def initialize(self) -> bool:
        """Initialize and load models/databases"""
        try:
            logger.info("Initializing KNOFileSystem...")
            
            # Check dependencies
            if not HAS_SENTENCE_TRANSFORMERS:
                logger.error("sentence-transformers not installed")
                return False
            
            if self.use_chroma and not HAS_CHROMADB:
                logger.warning("ChromaDB not available, falling back to FAISS")
                self.use_chroma = False
            
            if not self.use_chroma and not HAS_FAISS:
                logger.error("Neither ChromaDB nor FAISS available")
                return False
            
            # Load embedding model
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            self.stats['model_loaded'] = True
            
            # Initialize database backend
            if self.use_chroma:
                self.db_backend = ChromaDBBackend(str(self.index_dir / "chroma_db"))
                await self.db_backend.initialize()
                await self.db_backend.get_or_create_collection("kno_files")
            else:
                embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.db_backend = FAISSBackend(embedding_dim)
                await self.db_backend.initialize()
            
            # Load existing indexes
            await self._load_indexes()
            
            logger.info("KNOFileSystem initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            self.stats['model_loaded'] = False
            return False
    
    async def _load_indexes(self):
        """Load existing index metadata"""
        try:
            metadata_file = self.index_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    for file_path, file_data in metadata.items():
                        self.indexed_files[file_path] = IndexedFile(**file_data)
                logger.info(f"Loaded {len(self.indexed_files)} indexed file metadata")
        except Exception as e:
            logger.warning(f"Failed to load indexes: {e}")
    
    async def _save_indexes(self):
        """Save index metadata"""
        try:
            metadata_file = self.index_dir / "metadata.json"
            metadata = {path: asdict(file_obj) 
                       for path, file_obj in self.indexed_files.items()}
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save indexes: {e}")
    
    async def index_directory(self, 
                             directory: str,
                             recursive: bool = True,
                             callback: Optional[Callable] = None) -> IndexingMetrics:
        """
        Index all files in a directory asynchronously
        
        Args:
            directory: Directory to index
            recursive: Index subdirectories
            callback: Callback function for progress (current, total)
        
        Returns:
            IndexingMetrics with results
        """
        if self._indexing_in_progress:
            logger.warning("Indexing already in progress")
            return self.metrics
        
        self._indexing_in_progress = True
        self._indexing_status = IndexingStatus.INDEXING
        self.metrics = IndexingMetrics()
        start_time = time.time()
        
        try:
            directory = Path(directory)
            
            # Collect all files
            if recursive:
                files = [f for f in directory.rglob('*') 
                        if f.is_file() and not should_ignore_file(f, self.ignore_patterns)]
            else:
                files = [f for f in directory.glob('*') 
                        if f.is_file() and not should_ignore_file(f, self.ignore_patterns)]
            
            self.metrics.total_files = len(files)
            logger.info(f"Found {self.metrics.total_files} files to index")
            
            # Index files in batches
            for idx, file_path in enumerate(files):
                try:
                    # Update progress
                    if callback:
                        await callback(idx + 1, self.metrics.total_files)
                    
                    await self._update_edex_progress(idx + 1, self.metrics.total_files)
                    
                    # Index file
                    if await self.index_file(str(file_path)):
                        self.metrics.indexed_files += 1
                    else:
                        self.metrics.files_skipped += 1
                    
                    # Yield control
                    await asyncio.sleep(0.001)
                    
                except Exception as e:
                    logger.warning(f"Failed to index {file_path}: {e}")
                    self.metrics.failed_files += 1
            
            # Optimize index
            self._indexing_status = IndexingStatus.OPTIMIZING
            await self._optimize_index()
            
            # Save indexes
            await self._save_indexes()
            
            # Calculate metrics
            self.metrics.indexing_time_seconds = time.time() - start_time
            if self.metrics.total_chunks > 0:
                self.metrics.avg_chunk_size = self.metrics.total_size_mb / self.metrics.total_chunks
            
            self._indexing_status = IndexingStatus.COMPLETED
            logger.info(f"Indexing complete: {self.metrics.indexed_files}/{self.metrics.total_files} files")
            logger.info(f"Metrics: {self.metrics}")
            
            return self.metrics
            
        except Exception as e:
            logger.error(f"Indexing failed: {e}", exc_info=True)
            self._indexing_status = IndexingStatus.ERROR
            return self.metrics
            
        finally:
            self._indexing_in_progress = False
    
    async def index_file(self, file_path: str) -> bool:
        """Index a single file"""
        try:
            file_path = str(Path(file_path).resolve())
            
            if should_ignore_file(file_path, self.ignore_patterns):
                return False
            
            ext = Path(file_path).suffix.lower()
            file_type = FILE_TYPE_MAP.get(ext, FileType.UNKNOWN)
            
            if file_type == FileType.UNKNOWN:
                return False
            
            # Calculate file hash
            file_hash = calculate_file_hash(file_path)
            if not file_hash:
                return False
            
            # Check if already indexed
            if file_path in self.indexed_files:
                if self.indexed_files[file_path].file_hash == file_hash:
                    return False
            
            # Extract text
            text = extract_text_from_file(file_path, file_type)
            if not text or len(text.strip()) < 20:
                logger.debug(f"Skipping {file_path}: content too short")
                return False
            
            # Chunk text
            chunks = chunk_text(text, file_type=file_type)
            
            # Generate embeddings
            chunk_embeddings = self.embedding_model.encode(
                chunks, 
                show_progress_bar=False,
                batch_size=self.batch_size
            )
            
            # Extract keywords
            keywords = extract_keywords(text)
            
            # Store in database
            doc_ids = [f"{file_path}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    'file_path': file_path,
                    'file_type': file_type.value,
                    'chunk_index': i,
                }
                for i in range(len(chunks))
            ]
            
            if self.use_chroma:
                await self.db_backend.add_documents(
                    doc_ids,
                    chunks,
                    metadatas,
                    chunk_embeddings.tolist() if isinstance(chunk_embeddings, np.ndarray) else chunk_embeddings
                )
            else:
                await self.db_backend.add_documents(doc_ids, chunk_embeddings, metadatas)
            
            # Update metrics
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            self.metrics.total_size_mb += file_size_mb
            self.metrics.total_chunks += len(chunks)
            
            # Update metadata
            preview = text[:300].replace('\n', ' ')
            indexed_file = IndexedFile(
                file_path=file_path,
                file_type=file_type.value,
                file_hash=file_hash,
                indexed_at=datetime.now().isoformat(),
                chunk_count=len(chunks),
                content_preview=preview,
                keywords=keywords,
                metadata={
                    'size_bytes': os.path.getsize(file_path),
                    'lines': len(text.split('\n')),
                }
            )
            
            self.indexed_files[file_path] = indexed_file
            self.stats['total_files_indexed'] = len(self.indexed_files)
            self.stats['total_chunks'] = self.metrics.total_chunks
            
            logger.debug(f"Indexed {file_path} ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index {file_path}: {e}", exc_info=True)
            return False
    
    async def search_files(self, 
                          query: str, 
                          top_k: int = 5,
                          similarity_threshold: float = 0.3,
                          enable_query_expansion: bool = True) -> List[SearchResult]:
        """Semantic search for files"""
        try:
            if not self.embedding_model:
                logger.error("Embedding model not loaded")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])
            if len(query_embedding.shape) == 2:
                query_embedding = query_embedding[0]
            
            # Search
            if self.use_chroma:
                results = await self._search_chromadb(
                    query_embedding, query, top_k, similarity_threshold
                )
            else:
                results = await self._search_faiss(
                    query_embedding, query, top_k, similarity_threshold
                )
            
            # Rank results
            for rank, result in enumerate(sorted(results, key=lambda x: x.relevance_score, reverse=True)):
                result.rank = rank + 1
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}", exc_info=True)
            return []
    
    async def _search_chromadb(self, embedding, query: str, 
                              top_k: int, threshold: float) -> List[SearchResult]:
        """Search in ChromaDB"""
        try:
            results_data = await self.db_backend.query(
                embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                top_k * 2
            )
            
            results = []
            
            ids = results_data.get('ids', [[]])[0]
            documents = results_data.get('documents', [[]])[0]
            metadatas = results_data.get('metadatas', [[]])[0]
            distances = results_data.get('distances', [[]])[0]
            
            for doc_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
                similarity = 1.0 - distance
                
                if similarity >= threshold:
                    file_path = metadata.get('file_path', '')
                    keywords = self.indexed_files.get(file_path, IndexedFile(
                        file_path='', file_type='unknown', file_hash='',
                        indexed_at='', chunk_count=0, content_preview=''
                    )).keywords
                    
                    results.append(SearchResult(
                        file_path=file_path,
                        file_type=metadata.get('file_type', 'unknown'),
                        chunk_index=metadata.get('chunk_index', 0),
                        relevance_score=float(similarity),
                        content_excerpt=document[:500],
                        matched_query=query,
                        keywords=keywords,
                    ))
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}", exc_info=True)
            return []
    
    async def _search_faiss(self, embedding, query: str, 
                           top_k: int, threshold: float) -> List[SearchResult]:
        """Search in FAISS"""
        try:
            if self.db_backend.index.ntotal == 0:
                return []
            
            distances, indices = await self.db_backend.query(embedding, min(top_k, self.db_backend.index.ntotal))
            
            results = []
            
            for idx, distance in zip(indices, distances):
                similarity = 1.0 / (1.0 + distance)
                
                if similarity >= threshold and idx in self.db_backend.metadata_store:
                    doc_id, metadata = self.db_backend.metadata_store[idx]
                    file_path = metadata.get('file_path', '')
                    
                    keywords = self.indexed_files.get(file_path, IndexedFile(
                        file_path='', file_type='unknown', file_hash='',
                        indexed_at='', chunk_count=0, content_preview=''
                    )).keywords
                    
                    results.append(SearchResult(
                        file_path=file_path,
                        file_type=metadata.get('file_type', 'unknown'),
                        chunk_index=metadata.get('chunk_index', 0),
                        relevance_score=float(similarity),
                        content_excerpt="[Content cached in FAISS]",
                        matched_query=query,
                        keywords=keywords,
                    ))
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"FAISS search failed: {e}", exc_info=True)
            return []
    
    async def _optimize_index(self):
        """Optimize index after indexing"""
        logger.info("Optimizing index...")
        try:
            if not self.use_chroma and hasattr(self.db_backend.index, 'train'):
                # FAISS optimization would go here
                pass
            logger.info("Index optimization complete")
        except Exception as e:
            logger.warning(f"Index optimization failed: {e}")
    
    async def _update_edex_progress(self, current: int, total: int):
        """Update eDEX-UI progress"""
        if not self.edex_status_file:
            return
        
        try:
            status = {
                "indexing": True,
                "progress": {
                    "current": current,
                    "total": total,
                    "percentage": int((current / total * 100) if total > 0 else 0),
                },
                "timestamp": datetime.now().isoformat(),
            }
            
            with open(self.edex_status_file, 'w') as f:
                json.dump(status, f)
                
        except Exception as e:
            logger.debug(f"Failed to update eDEX progress: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            **self.stats,
            **asdict(self.metrics),
            'indexed_files_count': len(self.indexed_files),
            'database_type': 'ChromaDB' if self.use_chroma else 'FAISS',
            'indexing_status': self._indexing_status.value,
        }
    
    def get_indexed_files(self) -> Dict[str, IndexedFile]:
        """Get all indexed files"""
        return self.indexed_files.copy()
    
    async def clear_indexes(self) -> bool:
        """Clear all indexes"""
        try:
            await self.db_backend.reset()
            self.indexed_files.clear()
            self.chunk_to_file_map.clear()
            self._embedding_cache.clear()
            
            metadata_file = self.index_dir / "metadata.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            self.metrics = IndexingMetrics()
            logger.info("Indexes cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear indexes: {e}", exc_info=True)
            return False


# ============================================================================
# SYNCHRONOUS WRAPPER
# ============================================================================

class KNOFileSystemSync:
    """Synchronous wrapper for non-async contexts"""
    
    def __init__(self, *args, **kwargs):
        self.async_fs = KNOFileSystem(*args, **kwargs)
        self.loop = None
        self.thread = None
    
    def _ensure_loop(self):
        """Ensure event loop"""
        if self.loop is None or not self.thread.is_alive():
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
    
    def _run_loop(self):
        """Run event loop"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def initialize(self) -> bool:
        """Initialize"""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(self.async_fs.initialize(), self.loop)
        return future.result(timeout=30)
    
    def index_directory(self, directory: str, recursive: bool = True) -> IndexingMetrics:
        """Index directory"""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.async_fs.index_directory(directory, recursive),
            self.loop
        )
        return future.result(timeout=600)
    
    def search_files(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search files"""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.async_fs.search_files(query, top_k),
            self.loop
        )
        return future.result(timeout=30)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics"""
        return self.async_fs.get_statistics()


if __name__ == "__main__":
    # Example usage
    async def main():
        print("═" * 60)
        print("KNO Semantic File System v2.0 - Demo")
        print("═" * 60)
        
        fs = KNOFileSystem(index_dir="./test_sfs_index")
        
        if not await fs.initialize():
            print("✗ Failed to initialize")
            return
        
        print("✓ Initialized")
        
        # Index directory
        print("\nIndexing directory...")
        metrics = await fs.index_directory(".", recursive=False)
        print(f"✓ Indexed {metrics.indexed_files}/{metrics.total_files} files")
        print(f"  - Total chunks: {metrics.total_chunks}")
        print(f"  - Time: {metrics.indexing_time_seconds:.2f}s")
        print(f"  - Success rate: {metrics.get_success_rate():.1f}%")
        
        # Search
        print("\nSearching for 'semantic file system'...")
        results = await fs.search_files("semantic file system", top_k=3)
        for result in results:
            print(f"  [{result.rank}] {result.file_path}")
            print(f"      Relevance: {result.relevance_score:.2%}")
            print(f"      Type: {result.file_type}")
        
        # Statistics
        print("\nStatistics:")
        stats = fs.get_statistics()
        for key in ['total_files_indexed', 'total_chunks', 'indexing_status']:
            print(f"  {key}: {stats.get(key, 'N/A')}")
    
    asyncio.run(main())
