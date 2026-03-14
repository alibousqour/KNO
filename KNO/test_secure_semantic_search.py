"""
Test Suite for Secure Semantic Search System
=============================================

اختبارات شاملة لنظام البحث الدلالي الآمن

Comprehensive tests for:
- Security filtering
- LLM Coordinator integration
- Pydantic validation
- Audit trails

Author: KNO Architecture
License: MIT
"""

import asyncio
import json
import logging
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
import pytest

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('KNO.SecureSearchTests')

# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def mock_search_engine():
    """Create a mock search engine"""
    engine = AsyncMock()
    engine.initialized = True
    engine.search_files_secure = AsyncMock(return_value=[])
    engine.get_security_audit = Mock(return_value={
        'total_files_scanned': 100,
        'files_filtered': 10,
        'restricted_files_blocked': 5
    })
    return engine


@pytest.fixture
def mock_ignore_manager():
    """Create a mock ignore manager"""
    manager = Mock()
    manager.should_include_file = Mock(return_value=True)
    manager.should_ignore_file = Mock(return_value={
        'ignored': False,
        'sensitivity': 'low'
    })
    manager.get_rules_summary = Mock(return_value={
        'total_rules': 50,
        'restricted_patterns': 15
    })
    return manager


@pytest.fixture
def sample_search_result():
    """Create a sample search result"""
    return {
        'file_path': 'KNO/agent.py',
        'file_type': '.py',
        'relevance_score': 0.85,
        'summary': 'Main agent file',
        'keywords': ['agent', 'async', 'websocket']
    }


# ============================================================================
# SECURITY FILTER TESTS
# ============================================================================

class TestSecurityFilter:
    """Test security filtering functionality"""
    
    def test_ignore_git_files(self):
        """Test that .git files are filtered"""
        from security_filter import IgnoreListManager
        
        manager = IgnoreListManager("./test")
        
        result = manager.should_ignore_file(".git/config")
        assert result['ignored'] == True
        assert result['sensitivity'] == 'restricted'
    
    def test_ignore_env_files(self):
        """Test that .env files are filtered"""
        from security_filter import IgnoreListManager
        
        manager = IgnoreListManager("./test")
        
        test_cases = [
            ".env",
            ".env.local",
            ".env.production",
            ".env.staging"
        ]
        
        for file_path in test_cases:
            result = manager.should_ignore_file(file_path)
            assert result['ignored'] == True
    
    def test_ignore_encrypted_keys(self):
        """Test that encrypted keys are filtered"""
        from security_filter import IgnoreListManager
        
        manager = IgnoreListManager("./test")
        
        test_cases = [
            "private_key.pem",
            "secret.key",
            "certificate.p12",
            "keystore.jks"
        ]
        
        for file_path in test_cases:
            result = manager.should_ignore_file(file_path)
            assert result['ignored'] == True
    
    def test_allow_safe_files(self):
        """Test that safe files are allowed"""
        from security_filter import IgnoreListManager
        
        manager = IgnoreListManager("./test")
        
        test_cases = [
            "agent.py",
            "config.json",
            "README.md",
            "package.json"
        ]
        
        for file_path in test_cases:
            result = manager.should_ignore_file(file_path)
            assert result['ignored'] == False
    
    def test_sensitivity_levels(self):
        """Test sensitivity level classification"""
        from security_filter import IgnoreListManager
        
        manager = IgnoreListManager("./test")
        
        # Restricted
        result = manager.should_ignore_file("secrets.json")
        assert result['sensitivity'] == 'restricted'
        
        # Sensitive
        result = manager.should_ignore_file(".aws/credentials")
        assert result['sensitivity'] == 'sensitive'
        
        # Internal
        result = manager.should_ignore_file("__pycache__/module.pyc")
        assert result['sensitivity'] == 'internal'


# ============================================================================
# PYDANTIC VALIDATION TESTS
# ============================================================================

class TestPydanticValidation:
    """Test Pydantic model validation"""
    
    def test_search_query_validation(self):
        """Test SearchQuery validation"""
        try:
            from llm_coordinator_secure import SearchQuery
            
            # Valid query
            query = SearchQuery(
                query="test search",
                max_results=10,
                min_relevance=0.5
            )
            assert query.query == "test search"
            assert query.max_results == 10
        except ImportError:
            pytest.skip("Pydantic not installed")
    
    def test_invalid_empty_query(self):
        """Test that empty query is rejected"""
        try:
            from llm_coordinator_secure import SearchQuery
            
            with pytest.raises(ValueError):
                SearchQuery(query="")
        except ImportError:
            pytest.skip("Pydantic not installed")
    
    def test_invalid_max_results(self):
        """Test that invalid max_results is rejected"""
        try:
            from llm_coordinator_secure import SearchQuery
            
            # Too high
            with pytest.raises(ValueError):
                SearchQuery(query="test", max_results=100)
            
            # Too low
            with pytest.raises(ValueError):
                SearchQuery(query="test", max_results=0)
        except ImportError:
            pytest.skip("Pydantic not installed")
    
    def test_invalid_relevance(self):
        """Test that invalid relevance score is rejected"""
        try:
            from llm_coordinator_secure import SearchQuery
            
            # Too high
            with pytest.raises(ValueError):
                SearchQuery(query="test", min_relevance=1.5)
            
            # Negative
            with pytest.raises(ValueError):
                SearchQuery(query="test", min_relevance=-0.1)
        except ImportError:
            pytest.skip("Pydantic not installed")
    
    def test_search_result_model(self):
        """Test SearchResultModel"""
        try:
            from llm_coordinator_secure import SearchResultModel
            
            result = SearchResultModel(
                file_path="agent.py",
                file_type=".py",
                relevance_score=0.85,
                summary="Test",
                keywords=["test", "module"]
            )
            
            assert result.file_path == "agent.py"
            assert result.relevance_score == 0.85
            assert result.restricted == False
        except ImportError:
            pytest.skip("Pydantic not installed")
    
    def test_search_response_model(self):
        """Test SearchResponse model"""
        try:
            from llm_coordinator_secure import SearchResponse, SearchResultModel
            
            response = SearchResponse(
                success=True,
                query="test",
                total_results=1,
                results=[
                    SearchResultModel(
                        file_path="test.py",
                        file_type=".py",
                        relevance_score=0.9
                    )
                ],
                execution_time_ms=100.0
            )
            
            assert response.success == True
            assert response.total_results == 1
            assert response.total_results == len(response.results)
        except ImportError:
            pytest.skip("Pydantic not installed")


# ============================================================================
# LLM COORDINATOR TESTS
# ============================================================================

class TestLLMCoordinator:
    """Test LLM Coordinator integration"""
    
    def test_function_schema(self):
        """Test function schema generation"""
        from llm_coordinator_secure import get_semantic_search_function_schema
        
        schema = get_semantic_search_function_schema()
        
        assert schema['name'] == 'semantic_search'
        assert 'parameters' in schema
        assert 'query' in schema['parameters']['properties']
        assert 'max_results' in schema['parameters']['properties']
        assert 'scope' in schema['parameters']['properties']
    
    def test_semantic_search_tool(self):
        """Test SemanticSearchTool"""
        from llm_coordinator_secure import SemanticSearchTool
        
        tool = SemanticSearchTool()
        
        schema = tool.get_function_schema()
        assert schema['name'] == 'semantic_search'
        assert len(schema['parameters']['required']) > 0
    
    @pytest.mark.asyncio
    async def test_tool_execute_success(self, mock_search_engine, sample_search_result):
        """Test successful tool execution"""
        from llm_coordinator_secure import SemanticSearchTool
        
        # Mock the search engine
        mock_search_engine.search_files_secure = AsyncMock(
            return_value=[sample_search_result]
        )
        
        tool = SemanticSearchTool(search_engine=mock_search_engine)
        
        result = await tool.execute(
            query="test",
            max_results=10
        )
        
        assert result['success'] == True
        assert result['total_results'] == 1
        assert 'execution_time_ms' in result
    
    @pytest.mark.asyncio
    async def test_tool_execute_invalid_query(self):
        """Test tool with invalid query"""
        from llm_coordinator_secure import SemanticSearchTool
        
        tool = SemanticSearchTool()
        
        result = await tool.execute(
            query="",  # Empty query
            max_results=10
        )
        
        assert result['success'] == False
        assert 'message' in result
    
    @pytest.mark.asyncio
    async def test_integration_process_llm_call(self, mock_search_engine):
        """Test LLM integration process_llm_call"""
        from llm_coordinator_secure import SemanticSearchLLMIntegration
        
        integration = SemanticSearchLLMIntegration(
            search_engine=mock_search_engine
        )
        
        mock_search_engine.search_files_secure = AsyncMock(return_value=[])
        
        result = await integration.process_llm_call(
            "semantic_search",
            {"query": "test"}
        )
        
        assert isinstance(result, dict)
        assert 'success' in result
    
    def test_integration_get_available_tools(self):
        """Test getting available tools"""
        from llm_coordinator_secure import SemanticSearchLLMIntegration
        
        integration = SemanticSearchLLMIntegration()
        
        tools = integration.get_available_tools()
        
        assert len(tools) > 0
        assert tools[0]['name'] == 'semantic_search'


# ============================================================================
# SECURE SEMANTIC SEARCH TESTS
# ============================================================================

class TestSecureSemanticSearch:
    """Test SecureSemanticSearchEngine"""
    
    def test_secure_engine_initialization(self, mock_search_engine, mock_ignore_manager):
        """Test engine initialization"""
        try:
            from secure_semantic_search import SecureSemanticSearchEngine
            
            engine = SecureSemanticSearchEngine(
                base_engine=mock_search_engine,
                ignore_manager=mock_ignore_manager
            )
            
            assert engine.engine == mock_search_engine
            assert engine.ignore_manager == mock_ignore_manager
        except ImportError:
            pytest.skip("Base engine not available")
    
    def test_security_audit(self, mock_search_engine, mock_ignore_manager):
        """Test security audit tracking"""
        try:
            from secure_semantic_search import SecureSemanticSearchEngine
            
            engine = SecureSemanticSearchEngine(
                base_engine=mock_search_engine,
                ignore_manager=mock_ignore_manager
            )
            
            audit = engine.get_security_audit()
            
            assert 'total_files_scanned' in audit
            assert 'files_filtered' in audit
            assert 'restricted_files_blocked' in audit
        except ImportError:
            pytest.skip("Base engine not available")
    
    def test_ignore_summary(self, mock_search_engine, mock_ignore_manager):
        """Test getting ignore summary"""
        try:
            from secure_semantic_search import SecureSemanticSearchEngine
            
            engine = SecureSemanticSearchEngine(
                base_engine=mock_search_engine,
                ignore_manager=mock_ignore_manager
            )
            
            summary = engine.get_ignore_summary()
            
            assert isinstance(summary, dict)
        except ImportError:
            pytest.skip("Base engine not available")
    
    def test_security_status(self, mock_search_engine, mock_ignore_manager):
        """Test getting security status"""
        try:
            from secure_semantic_search import SecureSemanticSearchEngine
            
            engine = SecureSemanticSearchEngine(
                base_engine=mock_search_engine,
                ignore_manager=mock_ignore_manager
            )
            
            status = engine.get_security_status()
            
            assert 'ignore_manager' in status
            assert 'audit' in status
            assert 'engine_initialized' in status
        except ImportError:
            pytest.skip("Base engine not available")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests for complete system"""
    
    @pytest.mark.asyncio
    async def test_full_search_pipeline(self, mock_search_engine, mock_ignore_manager):
        """Test full search pipeline"""
        try:
            from secure_semantic_search import SecureKNOSemanticSearch
            from llm_coordinator_secure import SemanticSearchLLMIntegration
            
            # This would require full initialization
            # Skipping for now as it requires model downloads
            pytest.skip("Full integration test requires model downloads")
        except ImportError:
            pytest.skip("Required modules not available")
    
    def test_ignore_list_loading(self):
        """Test loading ignore list from JSON"""
        import json
        from pathlib import Path
        
        ignore_file = Path("./KNO/ignore_list.json")
        
        if ignore_file.exists():
            with open(ignore_file, 'r') as f:
                config = json.load(f)
            
            assert 'ignore_list' in config
            assert 'sensitivity_levels' in config
            assert 'allowed_extensions' in config
        else:
            pytest.skip("ignore_list.json not found")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.asyncio
    async def test_tool_execution_time(self, mock_search_engine):
        """Test tool execution performance"""
        from llm_coordinator_secure import SemanticSearchTool
        import time
        
        mock_search_engine.search_files_secure = AsyncMock(return_value=[])
        
        tool = SemanticSearchTool(search_engine=mock_search_engine)
        
        start = time.time()
        result = await tool.execute(query="test")
        elapsed = time.time() - start
        
        assert elapsed < 5.0  # Should complete in under 5 seconds
        assert result['execution_time_ms'] > 0


# ============================================================================
# MANUAL TEST RUNNER
# ============================================================================

async def manual_tests():
    """Run manual tests without pytest"""
    
    print("\n" + "=" * 70)
    print("Manual Test Suite - Secure Semantic Search System".center(70))
    print("=" * 70)
    
    # Test 1: Security Filter
    print("\n1️⃣  Security Filter Tests")
    print("-" * 70)
    
    try:
        from security_filter import IgnoreListManager
        
        manager = IgnoreListManager("./")
        
        test_cases = [
            (".git/config", True, "Git files"),
            (".env", True, "Env files"),
            ("agent.py", False, "Python files"),
            ("README.md", False, "Markdown files")
        ]
        
        for file_path, should_ignore, desc in test_cases:
            result = manager.should_ignore_file(file_path)
            status = "✓" if result['ignored'] == should_ignore else "✗"
            print(f"   {status} {desc}: {file_path}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Pydantic Validation
    print("\n2️⃣  Pydantic Validation Tests")
    print("-" * 70)
    
    try:
        from llm_coordinator_secure import SearchQuery
        
        # Valid query
        try:
            query = SearchQuery(query="test", max_results=10)
            print(f"   ✓ Valid query accepted")
        except:
            print(f"   ✗ Valid query rejected")
        
        # Invalid query (empty)
        try:
            query = SearchQuery(query="")
            print(f"   ✗ Empty query accepted (should reject)")
        except ValueError:
            print(f"   ✓ Empty query rejected")
        
        # Invalid max_results
        try:
            query = SearchQuery(query="test", max_results=100)
            print(f"   ✗ Over-limit max_results accepted")
        except ValueError:
            print(f"   ✓ Over-limit max_results rejected")
    
    except ImportError:
        print("   ⚠ Pydantic not installed")
    
    # Test 3: Function Schema
    print("\n3️⃣  LLM Function Schema Tests")
    print("-" * 70)
    
    try:
        from llm_coordinator_secure import get_semantic_search_function_schema
        
        schema = get_semantic_search_function_schema()
        
        print(f"   ✓ Schema name: {schema['name']}")
        print(f"   ✓ Parameters: {len(schema['parameters']['properties'])}")
        print(f"   ✓ Required fields: {schema['parameters']['required']}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Ignore List Config
    print("\n4️⃣  Ignore List Configuration Tests")
    print("-" * 70)
    
    try:
        import json
        from pathlib import Path
        
        config_file = Path("./KNO/ignore_list.json")
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print(f"   ✓ Config loaded")
            print(f"   ✓ Ignore patterns: {len(config['ignore_list'])}")
            print(f"   ✓ Sensitivity levels: {len(config['sensitivity_levels'])}")
            print(f"   ✓ Allowed extensions: {len(config['allowed_extensions'])}")
        else:
            print(f"   ⚠ Config file not found")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Manual Tests Completed".center(70))
    print("=" * 70)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if "--manual" in sys.argv:
        asyncio.run(manual_tests())
    else:
        print("Run with pytest:")
        print("  pytest test_secure_semantic_search.py -v")
        print("\nOr run manual tests:")
        print("  python test_secure_semantic_search.py --manual")
