"""
KNO Semantic File System (SFS) v1.0
===================================
Intelligent file management system with semantic indexing and search capabilities.

Features:
- Asynchronous file indexing using Sentence-Transformers
- Vector database storage (ChromaDB/FAISS)
- Semantic search functionality
- eDEX-UI integration for progress tracking
- Security-aware file filtering (ignores sensitive files)
- Modular design for LLMCoordinator integration

Author: KNO Architecture
License: MIT
"""

import os
import sys
import json
import asyncio
import hashlib
import logging
import threading
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Third-party imports with fallbacks
try:
    import numpy as np
except ImportError:
    np = None

try:
    from sentence_transformers import SentenceTransformer
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
# CONFIGURATION & CONSTANTS
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
    '.pdf': FileType.PDF,
    '.json': FileType.JSON,
}

# Default ignore patterns (security-aware)
DEFAULT_IGNORE_PATTERNS = [
    '.git', '.gitignore', '__pycache__', '.venv', 'venv',
    '.env', '.env.local', '.env.*.local',
    'node_modules', 'dist', 'build', '.DS_Store',
    '*.exe', '*.dll', '*.so', '*.dylib',
    '.idea', '.vscode', '*.swp', '*.swo',
    'private', 'secret', 'password', 'key',
    '*.pyc', '*.pyo', '*.egg-info',
    'Cookies', 'Cache', 'cookies-journal',
]

# Chunk size for text processing (tokens ~= words * 1.3)
TEXT_CHUNK_SIZE = 500  # words
TEXT_OVERLAP = 50  # words for context

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
    metadata: Dict[str, Any]

@dataclass
class SearchResult:
    """Result from semantic search"""
    file_path: str
    file_type: str
    chunk_index: int
    relevance_score: float
    content_excerpt: str
    matched_query: str

# ============================================================================
# LOGGER SETUP
# ============================================================================

def setup_logger(name: str) -> logging.Logger:
    """Setup logger for the module"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = setup_logger('KNO.SemanticFS')

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def should_ignore_file(file_path: str, ignore_patterns: List[str]) -> bool:
    """Check if file should be ignored based on patterns"""
    path_str = str(file_path).lower()
    for pattern in ignore_patterns:
        if pattern.lower() in path_str:
            return True
    # Also ignore hidden files/folders on Unix
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
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        else:
            # TEXT, MARKDOWN, PYTHON, CODE, JSON
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        logger.warning(f"Failed to extract text from {file_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = TEXT_CHUNK_SIZE, 
               overlap: int = TEXT_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    return chunks if chunks else [text[:1000]]  # Fallback

# ============================================================================
# SEMANTIC FILE SYSTEM CLASS
# ============================================================================

class KNOFileSystem:
    """
    Intelligent Semantic File System for KNO
    
    Async operations for:
    - Vector indexing of files
    - Semantic search
    - Progress tracking
    - eDEX-UI integration
    """
    
    def __init__(self, 
                 index_dir: Optional[str] = None,
                 edex_status_file: Optional[str] = None,
                 use_chroma: bool = True,
                 model_name: str = "all-MiniLM-L6-v2",
                 ignore_patterns: List[str] = None):
        """
        Initialize KNO File System
        
        Args:
            index_dir: Directory to store indexes (default: ./sfs_index)
            edex_status_file: Path to edex_status.json for progress tracking
            use_chroma: Use ChromaDB (True) or FAISS (False)
            model_name: Name of Sentence-Transformer model
            ignore_patterns: Custom ignore patterns
        """
        self.index_dir = Path(index_dir or "./sfs_index")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.edex_status_file = edex_status_file
        self.use_chroma = use_chroma
        self.model_name = model_name
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS
        
        # State tracking
        self.indexed_files: Dict[str, IndexedFile] = {}
        self.embedding_model = None
        self.db = None
        self.embeddings = None
        self.chunk_to_file_map: Dict[int, str] = {}
        
        # Thread safety
        self._lock = asyncio.Lock() if sys.version_info >= (3, 10) else threading.Lock()
        self._indexing_in_progress = False
        
        # Statistics
        self.stats = {
            'total_files_indexed': 0,
            'total_chunks': 0,
            'index_size_mb': 0.0,
            'last_index_time': None,
            'model_loaded': False,
        }
        
        logger.info(f"KNOFileSystem initialized at {self.index_dir}")
        logger.info(f"Using {'ChromaDB' if self.use_chroma else 'FAISS'}")
        logger.info(f"Embedding model: {self.model_name}")
    
    async def initialize(self) -> bool:
        """
        Initialize and load models/databases
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing KNOFileSystem...")
            
            # Check dependencies
            if not HAS_SENTENCE_TRANSFORMERS:
                logger.error("sentence-transformers not installed")
                return False
            
            if self.use_chroma and not HAS_CHROMADB:
                logger.warning("ChromaDB not available, trying FAISS")
                self.use_chroma = False
            
            if not self.use_chroma and not HAS_FAISS:
                logger.error("Neither ChromaDB nor FAISS available")
                return False
            
            # Load embedding model
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            self.stats['model_loaded'] = True
            
            # Initialize database
            if self.use_chroma:
                await self._init_chromadb()
            else:
                await self._init_faiss()
            
            # Load existing indexes
            await self._load_indexes()
            
            logger.info("KNOFileSystem initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.stats['model_loaded'] = False
            return False
    
    async def _init_chromadb(self):
        """Initialize ChromaDB backend"""
        try:
            db_path = self.index_dir / "chroma_db"
            db_path.mkdir(parents=True, exist_ok=True)
            
            settings = Settings(
                chroma_db_impl="duckdb",
                persist_directory=str(db_path),
                anonymized_telemetry=False,
            )
            
            self.db = chromadb.Client(settings)
            logger.info(f"ChromaDB initialized at {db_path}")
        except Exception as e:
            logger.error(f"ChromaDB init failed: {e}")
            raise
    
    async def _init_faiss(self):
        """Initialize FAISS backend"""
        try:
            if not HAS_FAISS or np is None:
                raise ImportError("FAISS or NumPy not available")
            
            embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
            self.embeddings = faiss.IndexFlatL2(embedding_dim)
            logger.info(f"FAISS index initialized (dimension: {embedding_dim})")
        except Exception as e:
            logger.error(f"FAISS init failed: {e}")
            raise
    
    async def _load_indexes(self):
        """Load existing index metadata"""
        try:
            metadata_file = self.index_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    for file_path, file_data in metadata.items():
                        self.indexed_files[file_path] = IndexedFile(**file_data)
                logger.info(f"Loaded {len(self.indexed_files)} indexed files")
        except Exception as e:
            logger.warning(f"Failed to load indexes: {e}")
    
    async def _save_indexes(self):
        """Save index metadata"""
        try:
            metadata_file = self.index_dir / "metadata.json"
            metadata = {path: asdict(file_obj) 
                       for path, file_obj in self.indexed_files.items()}
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save indexes: {e}")
    
    async def index_directory(self, 
                             directory: str,
                             recursive: bool = True,
                             callback: Optional[callable] = None) -> Tuple[int, int]:
        """
        Index all files in a directory asynchronously
        
        Args:
            directory: Directory to index
            recursive: Index subdirectories
            callback: Callback function for progress (file_count, total_files)
        
        Returns:
            Tuple of (indexed_count, total_count)
        """
        if self._indexing_in_progress:
            logger.warning("Indexing already in progress")
            return 0, 0
        
        self._indexing_in_progress = True
        
        try:
            directory = Path(directory)
            
            # Collect all files
            files_to_index = []
            if recursive:
                files_to_index = [f for f in directory.rglob('*') 
                                 if f.is_file() and not should_ignore_file(f, self.ignore_patterns)]
            else:
                files_to_index = [f for f in directory.glob('*') 
                                 if f.is_file() and not should_ignore_file(f, self.ignore_patterns)]
            
            total = len(files_to_index)
            logger.info(f"Found {total} files to index in {directory}")
            
            indexed_count = 0
            for idx, file_path in enumerate(files_to_index):
                try:
                    # Update progress
                    if callback:
                        await callback(idx + 1, total)
                    
                    # Update eDEX status
                    await self._update_edex_progress(idx + 1, total)
                    
                    # Index file
                    if await self.index_file(str(file_path)):
                        indexed_count += 1
                    
                    # Yield control to event loop
                    await asyncio.sleep(0.01)
                    
                except Exception as e:
                    logger.warning(f"Failed to index {file_path}: {e}")
            
            # Save indexes
            await self._save_indexes()
            
            self.stats['last_index_time'] = datetime.now().isoformat()
            logger.info(f"Indexing complete: {indexed_count}/{total} files")
            
            return indexed_count, total
            
        finally:
            self._indexing_in_progress = False
    
    async def index_file(self, file_path: str) -> bool:
        """
        Index a single file
        
        Args:
            file_path: Path to file to index
        
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = str(Path(file_path).resolve())
            
            # Skip if shouldn't be indexed
            if should_ignore_file(file_path, self.ignore_patterns):
                return False
            
            # Determine file type
            ext = Path(file_path).suffix.lower()
            file_type = FILE_TYPE_MAP.get(ext, FileType.UNKNOWN)
            
            if file_type == FileType.UNKNOWN:
                return False
            
            # Calculate file hash
            file_hash = calculate_file_hash(file_path)
            
            # Check if already indexed with same hash
            if file_path in self.indexed_files:
                if self.indexed_files[file_path].file_hash == file_hash:
                    return False  # Already indexed, no changes
            
            # Extract text
            text = extract_text_from_file(file_path, file_type)
            
            if not text or len(text.strip()) < 10:
                logger.debug(f"Skipping {file_path}: content too short")
                return False
            
            # Chunk text
            chunks = chunk_text(text)
            
            # Generate embeddings
            if not self.embedding_model:
                logger.error("Embedding model not loaded")
                return False
            
            chunk_embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
            
            # Store in database
            if self.use_chroma:
                await self._store_in_chromadb(file_path, file_type, chunks, chunk_embeddings)
            else:
                await self._store_in_faiss(file_path, file_type, chunks, chunk_embeddings)
            
            # Update metadata
            preview = text[:200].replace('\n', ' ')
            indexed_file = IndexedFile(
                file_path=file_path,
                file_type=file_type.value,
                file_hash=file_hash,
                indexed_at=datetime.now().isoformat(),
                chunk_count=len(chunks),
                content_preview=preview,
                metadata={
                    'size_bytes': os.path.getsize(file_path),
                    'lines': len(text.split('\n')),
                }
            )
            
            self.indexed_files[file_path] = indexed_file
            self.stats['total_files_indexed'] = len(self.indexed_files)
            self.stats['total_chunks'] += len(chunks)
            
            logger.debug(f"Indexed {file_path} ({len(chunks)} chunks)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index {file_path}: {e}")
            return False
    
    async def _store_in_chromadb(self, file_path: str, file_type: FileType, 
                                 chunks: List[str], embeddings: np.ndarray):
        """Store chunks in ChromaDB"""
        try:
            collection = self.db.get_or_create_collection(
                name="kno_files",
                metadata={"hnsw:space": "cosine"}
            )
            
            doc_ids = [f"{file_path}_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    'file_path': file_path,
                    'file_type': file_type.value,
                    'chunk_index': i,
                }
                for i in range(len(chunks))
            ]
            
            collection.add(
                ids=doc_ids,
                documents=chunks,
                metadatas=metadatas,
                embeddings=embeddings.tolist() if np else embeddings,
            )
            
        except Exception as e:
            logger.error(f"ChromaDB storage failed: {e}")
            raise
    
    async def _store_in_faiss(self, file_path: str, file_type: FileType, 
                            chunks: List[str], embeddings: np.ndarray):
        """Store chunks in FAISS"""
        try:
            if not isinstance(embeddings, np.ndarray):
                embeddings = np.array(embeddings).astype('float32')
            else:
                embeddings = embeddings.astype('float32')
            
            chunk_id = len(self.chunk_to_file_map)
            
            for i, chunk in enumerate(chunks):
                self.chunk_to_file_map[chunk_id + i] = file_path
            
            self.embeddings.add(embeddings)
            
        except Exception as e:
            logger.error(f"FAISS storage failed: {e}")
            raise
    
    async def search_files(self, 
                          query: str, 
                          top_k: int = 5,
                          similarity_threshold: float = 0.3) -> List[SearchResult]:
        """
        Semantic search for files
        
        Args:
            query: Search query
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
        
        Returns:
            List of SearchResult objects
        """
        try:
            if not self.embedding_model:
                logger.error("Embedding model not loaded")
                return []
            
            # Encode query
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Search in database
            if self.use_chroma:
                results = await self._search_chromadb(query_embedding, query, top_k, similarity_threshold)
            else:
                results = await self._search_faiss(query_embedding, query, top_k, similarity_threshold)
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def _search_chromadb(self, embedding: np.ndarray, query: str, 
                              top_k: int, threshold: float) -> List[SearchResult]:
        """Search in ChromaDB"""
        try:
            collection = self.db.get_collection(name="kno_files")
            
            results_data = collection.query(
                query_embeddings=[embedding.tolist() if isinstance(embedding, np.ndarray) else embedding],
                n_results=top_k * 2,  # Get more to filter by threshold
            )
            
            results = []
            
            # Process results
            ids = results_data['ids'][0] if results_data['ids'] else []
            documents = results_data['documents'][0] if results_data['documents'] else []
            metadatas = results_data['metadatas'][0] if results_data['metadatas'] else []
            distances = results_data['distances'][0] if results_data['distances'] else []
            
            for doc_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
                # ChromaDB returns distance; convert to similarity
                similarity = 1.0 - distance
                
                if similarity >= threshold:
                    results.append(SearchResult(
                        file_path=metadata['file_path'],
                        file_type=metadata['file_type'],
                        chunk_index=metadata.get('chunk_index', 0),
                        relevance_score=similarity,
                        content_excerpt=document[:500],
                        matched_query=query,
                    ))
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []
    
    async def _search_faiss(self, embedding: np.ndarray, query: str, 
                           top_k: int, threshold: float) -> List[SearchResult]:
        """Search in FAISS"""
        try:
            if self.embeddings.ntotal == 0:
                return []
            
            # Ensure embedding is float32 and 2D
            if not isinstance(embedding, np.ndarray):
                embedding = np.array(embedding, dtype='float32')
            else:
                embedding = embedding.astype('float32')
            
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)
            
            # Search
            distances, indices = self.embeddings.search(embedding, min(top_k, self.embeddings.ntotal))
            
            results = []
            
            for idx, distance in zip(indices[0], distances[0]):
                # FAISS L2 distance; convert to similarity
                similarity = 1.0 / (1.0 + distance)
                
                if similarity >= threshold and idx in self.chunk_to_file_map:
                    # Reconstruct chunk content (note: we don't store chunks in FAISS)
                    file_path = self.chunk_to_file_map[idx]
                    
                    results.append(SearchResult(
                        file_path=file_path,
                        file_type=self.indexed_files.get(file_path, IndexedFile(
                            file_path=file_path,
                            file_type="unknown",
                            file_hash="",
                            indexed_at="",
                            chunk_count=0,
                            content_preview="",
                            metadata={}
                        )).file_type,
                        chunk_index=idx,
                        relevance_score=similarity,
                        content_excerpt="[Content not cached in FAISS]",
                        matched_query=query,
                    ))
                
                if len(results) >= top_k:
                    break
            
            return results
            
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []
    
    async def _update_edex_progress(self, current: int, total: int):
        """Update eDEX-UI progress bar"""
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
        """Get indexing statistics"""
        return {
            **self.stats,
            'indexed_files_count': len(self.indexed_files),
            'database_type': 'ChromaDB' if self.use_chroma else 'FAISS',
        }
    
    def get_indexed_files(self) -> Dict[str, IndexedFile]:
        """Get all indexed files"""
        return self.indexed_files.copy()
    
    async def clear_indexes(self) -> bool:
        """Clear all indexes"""
        try:
            if self.use_chroma and self.db:
                self.db.reset()
            else:
                embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.embeddings = faiss.IndexFlatL2(embedding_dim)
            
            self.indexed_files.clear()
            self.chunk_to_file_map.clear()
            
            # Remove metadata file
            metadata_file = self.index_dir / "metadata.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            self.stats['total_files_indexed'] = 0
            self.stats['total_chunks'] = 0
            
            logger.info("Indexes cleared")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear indexes: {e}")
            return False


# ============================================================================
# ASYNC WRAPPER FOR SYNCHRONOUS CONTEXTS
# ============================================================================

class KNOFileSystemSync:
    """
    Synchronous wrapper around KNOFileSystem
    For use in non-async contexts (e.g., GUI event handlers)
    """
    
    def __init__(self, *args, **kwargs):
        self.async_fs = KNOFileSystem(*args, **kwargs)
        self.loop = None
        self.thread = None
    
    def _ensure_loop(self):
        """Ensure event loop is running in background thread"""
        if self.loop is None or not self.thread.is_alive():
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
    
    def _run_loop(self):
        """Run event loop in background thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def initialize(self) -> bool:
        """Initialize synchronously"""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.async_fs.initialize(), 
            self.loop
        )
        return future.result(timeout=30)
    
    def index_directory(self, directory: str, recursive: bool = True) -> Tuple[int, int]:
        """Index directory synchronously"""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.async_fs.index_directory(directory, recursive),
            self.loop
        )
        return future.result(timeout=300)
    
    def search_files(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search files synchronously"""
        self._ensure_loop()
        future = asyncio.run_coroutine_threadsafe(
            self.async_fs.search_files(query, top_k),
            self.loop
        )
        return future.result(timeout=30)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics"""
        return self.async_fs.get_statistics()


# ============================================================================
# TOOL FUNCTION FOR LLM INTEGRATION
# ============================================================================

async def search_kno_files(query: str, filesystem: KNOFileSystem, top_k: int = 5) -> Dict[str, Any]:
    """
    Tool function for LLMCoordinator to call semantic file search
    
    Args:
        query: Search query
        filesystem: KNOFileSystem instance
        top_k: Number of results
    
    Returns:
        Dictionary with results suitable for LLM context
    """
    try:
        results = await filesystem.search_files(query, top_k)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                'file': result.file_path,
                'type': result.file_type,
                'relevance': f"{result.relevance_score:.2%}",
                'excerpt': result.content_excerpt,
            })
        
        return {
            'success': True,
            'query': query,
            'results_count': len(results),
            'results': formatted_results,
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
        }


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        print("Initializing KNOFileSystem...")
        fs = KNOFileSystem(
            index_dir="./test_sfs_index",
            edex_status_file="./edex_status.json",
            use_chroma=True,
        )
        
        if not await fs.initialize():
            print("Failed to initialize")
            return
        
        print("Indexing KNO directory...")
        indexed, total = await fs.index_directory("./KNO", recursive=True)
        print(f"Indexed {indexed}/{total} files")
        
        print("\nSearching for 'file management' files...")
        results = await fs.search_files("file management system", top_k=3)
        
        for result in results:
            print(f"  - {result.file_path} ({result.relevance_score:.2%})")
            print(f"    {result.content_excerpt[:100]}...")
        
        print("\nStatistics:")
        stats = fs.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    asyncio.run(main())
