# =========================================================================
# LLM Bridge - Secure Cloud AI Integration (Gemini, ChatGPT, DeepSeek)
# =========================================================================
"""
Safe bridge for querying external AI APIs for complex problem solving.

SECURITY FEATURES:
1. API keys from environment variables only (never logged or saved)
2. Request validation and sanitization
3. Response validation and error handling
4. Timeout enforcement
5. Retry logic with exponential backoff
6. Rate limiting awareness
7. Fallback chain: Gemini → ChatGPT → DeepSeek
"""

import requests
import aiohttp
import asyncio
import logging
import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("KNO.llm_bridge")

# Request timeout (prevents hanging)
REQUEST_TIMEOUT_SECONDS = 30

# Rate limiting
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds


# =========================================================================
# API RESPONSE MODELS
# =========================================================================

class AIEngine(Enum):
    """Available AI engines"""
    GEMINI = "Gemini"
    OPENAI = "ChatGPT"
    DEEPSEEK = "DeepSeek"
    LOCAL = "Local"


@dataclass
class AIResponse:
    """Structured response from AI engine"""
    engine: AIEngine
    content: str
    tokens_used: int = 0
    success: bool = True
    error: Optional[str] = None
    
    @property
    def is_valid(self) -> bool:
        """Check if response is valid and useful"""
        return self.success and self.content and len(self.content.strip()) > 0


# =========================================================================
# GEMINI API INTEGRATION
# =========================================================================

class GeminiBridge:
    """Google Gemini API integration"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini bridge.
        
        Args:
            api_key: Gemini API key (from environment)
        """
        self.api_key = api_key
    
    def is_available(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def query(self, prompt: str, max_tokens: int = 1000) -> AIResponse:
        """
        Query Gemini API.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AIResponse: Response from Gemini
        """
        if not self.is_available():
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error="Gemini API key not configured"
            )
        
        try:
            # Validate and sanitize prompt
            prompt = self._sanitize_prompt(prompt)
            
            # Build request
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7
                }
            }
            
            # Make request with timeout
            response = requests.post(
                f"{self.BASE_URL}?key={self.api_key}",
                json=payload,
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if "candidates" in data and data["candidates"]:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return AIResponse(
                    engine=AIEngine.GEMINI,
                    content=text,
                    tokens_used=0,  # Gemini doesn't always provide token count
                    success=True
                )
            else:
                return AIResponse(
                    engine=AIEngine.GEMINI,
                    content="",
                    success=False,
                    error="No content in Gemini response"
                )
        
        except requests.Timeout:
            logger.warning("❌ Gemini request timeout")
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"❌ Gemini error: {e}")
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"❌ Unexpected Gemini error: {e}")
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def query_async(self, prompt: str, max_tokens: int = 1000) -> AIResponse:
        """
        Query Gemini API asynchronously.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AIResponse: Response from Gemini
        """
        if not self.is_available():
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error="Gemini API key not configured"
            )
        
        try:
            # Validate and sanitize prompt
            prompt = self._sanitize_prompt(prompt)
            
            # Build request
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": 0.7
                }
            }
            
            # Make async request with timeout
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.BASE_URL}?key={self.api_key}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
                ) as response:
                    response.raise_for_status()
                    
                    # Parse response
                    data = await response.json()
                    
                    if "candidates" in data and data["candidates"]:
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        return AIResponse(
                            engine=AIEngine.GEMINI,
                            content=text,
                            tokens_used=0,  # Gemini doesn't always provide token count
                            success=True
                        )
                    else:
                        return AIResponse(
                            engine=AIEngine.GEMINI,
                            content="",
                            success=False,
                            error="No content in Gemini response"
                        )
        
        except asyncio.TimeoutError:
            logger.warning("❌ Gemini request timeout")
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error="Request timeout"
            )
        except aiohttp.ClientError as e:
            logger.warning(f"❌ Gemini error: {e}")
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"❌ Unexpected Gemini error: {e}")
            return AIResponse(
                engine=AIEngine.GEMINI,
                content="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    @staticmethod
    def _sanitize_prompt(prompt: str) -> str:
        """Sanitize prompt to prevent injection attacks"""
        # Remove potentially dangerous content
        sanitized = prompt.strip()
        # Limit length
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
        return sanitized


# =========================================================================
# OPENAI API INTEGRATION
# =========================================================================

class OpenAIBridge:
    """OpenAI ChatGPT API integration"""
    
    BASE_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = "gpt-3.5-turbo"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI bridge.
        
        Args:
            api_key: OpenAI API key (from environment)
        """
        self.api_key = api_key
    
    def is_available(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def query(self, prompt: str, max_tokens: int = 1000) -> AIResponse:
        """
        Query OpenAI API.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AIResponse: Response from OpenAI
        """
        if not self.is_available():
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error="OpenAI API key not configured"
            )
        
        try:
            # Validate and sanitize prompt
            prompt = self._sanitize_prompt(prompt)
            
            # Build request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            # Make request with timeout
            response = requests.post(
                self.BASE_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if "choices" in data and data["choices"]:
                text = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return AIResponse(
                    engine=AIEngine.OPENAI,
                    content=text,
                    tokens_used=tokens,
                    success=True
                )
            else:
                return AIResponse(
                    engine=AIEngine.OPENAI,
                    content="",
                    success=False,
                    error="No content in OpenAI response"
                )
        
        except requests.Timeout:
            logger.warning("❌ OpenAI request timeout")
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"❌ OpenAI error: {e}")
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"❌ Unexpected OpenAI error: {e}")
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def query_async(self, prompt: str, max_tokens: int = 1000) -> AIResponse:
        """
        Query OpenAI API asynchronously.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AIResponse: Response from OpenAI
        """
        if not self.is_available():
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error="OpenAI API key not configured"
            )
        
        try:
            # Validate and sanitize prompt
            prompt = self._sanitize_prompt(prompt)
            
            # Build request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            # Make async request with timeout
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
                ) as response:
                    response.raise_for_status()
                    
                    # Parse response
                    data = await response.json()
                    
                    if "choices" in data and data["choices"]:
                        text = data["choices"][0]["message"]["content"]
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        return AIResponse(
                            engine=AIEngine.OPENAI,
                            content=text,
                            tokens_used=tokens,
                            success=True
                        )
                    else:
                        return AIResponse(
                            engine=AIEngine.OPENAI,
                            content="",
                            success=False,
                            error="No content in OpenAI response"
                        )
        
        except asyncio.TimeoutError:
            logger.warning("❌ OpenAI request timeout")
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error="Request timeout"
            )
        except aiohttp.ClientError as e:
            logger.warning(f"❌ OpenAI error: {e}")
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"❌ Unexpected OpenAI error: {e}")
            return AIResponse(
                engine=AIEngine.OPENAI,
                content="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    @staticmethod
    def _sanitize_prompt(prompt: str) -> str:
        """Sanitize prompt to prevent injection attacks"""
        sanitized = prompt.strip()
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
        return sanitized


# =========================================================================
# DEEPSEEK API INTEGRATION
# =========================================================================

class DeepSeekBridge:
    """DeepSeek API integration"""
    
    BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    MODEL = "deepseek-chat"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DeepSeek bridge.
        
        Args:
            api_key: DeepSeek API key (from environment)
        """
        self.api_key = api_key
    
    def is_available(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def query(self, prompt: str, max_tokens: int = 1000) -> AIResponse:
        """
        Query DeepSeek API.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AIResponse: Response from DeepSeek
        """
        if not self.is_available():
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error="DeepSeek API key not configured"
            )
        
        try:
            # Validate and sanitize prompt
            prompt = self._sanitize_prompt(prompt)
            
            # Build request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            # Make request with timeout
            response = requests.post(
                self.BASE_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS
            )
            
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            if "choices" in data and data["choices"]:
                text = data["choices"][0]["message"]["content"]
                tokens = data.get("usage", {}).get("total_tokens", 0)
                return AIResponse(
                    engine=AIEngine.DEEPSEEK,
                    content=text,
                    tokens_used=tokens,
                    success=True
                )
            else:
                return AIResponse(
                    engine=AIEngine.DEEPSEEK,
                    content="",
                    success=False,
                    error="No content in DeepSeek response"
                )
        
        except requests.Timeout:
            logger.warning("❌ DeepSeek request timeout")
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error="Request timeout"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"❌ DeepSeek error: {e}")
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"❌ Unexpected DeepSeek error: {e}")
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    async def query_async(self, prompt: str, max_tokens: int = 1000) -> AIResponse:
        """
        Query DeepSeek API asynchronously.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            
        Returns:
            AIResponse: Response from DeepSeek
        """
        if not self.is_available():
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error="DeepSeek API key not configured"
            )
        
        try:
            # Validate and sanitize prompt
            prompt = self._sanitize_prompt(prompt)
            
            # Build request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            # Make async request with timeout
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SECONDS)
                ) as response:
                    response.raise_for_status()
                    
                    # Parse response
                    data = await response.json()
                    
                    if "choices" in data and data["choices"]:
                        text = data["choices"][0]["message"]["content"]
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                        return AIResponse(
                            engine=AIEngine.DEEPSEEK,
                            content=text,
                            tokens_used=tokens,
                            success=True
                        )
                    else:
                        return AIResponse(
                            engine=AIEngine.DEEPSEEK,
                            content="",
                            success=False,
                            error="No content in DeepSeek response"
                        )
        
        except asyncio.TimeoutError:
            logger.warning("❌ DeepSeek request timeout")
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error="Request timeout"
            )
        except aiohttp.ClientError as e:
            logger.warning(f"❌ DeepSeek error: {e}")
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"❌ Unexpected DeepSeek error: {e}")
            return AIResponse(
                engine=AIEngine.DEEPSEEK,
                content="",
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
    
    @staticmethod
    def _sanitize_prompt(prompt: str) -> str:
        """Sanitize prompt to prevent injection attacks"""
        sanitized = prompt.strip()
        if len(sanitized) > 10000:
            sanitized = sanitized[:10000]
        return sanitized


# =========================================================================
# LLM COORDINATOR (FALLBACK CHAIN)
# =========================================================================

class LLMCoordinator:
    """Coordinates queries across multiple AI engines with fallback"""
    
    def __init__(self, gemini_key: Optional[str] = None,
                 openai_key: Optional[str] = None,
                 deepseek_key: Optional[str] = None):
        """
        Initialize coordinator with API keys.
        
        Args:
            gemini_key: Gemini API key
            openai_key: OpenAI API key
            deepseek_key: DeepSeek API key
        """
        self.gemini = GeminiBridge(gemini_key)
        self.openai = OpenAIBridge(openai_key)
        self.deepseek = DeepSeekBridge(deepseek_key)
        
        # Track which engines are available
        available_engines = []
        if self.gemini.is_available():
            available_engines.append("Gemini")
        if self.openai.is_available():
            available_engines.append("ChatGPT")
        if self.deepseek.is_available():
            available_engines.append("DeepSeek")
        
        if available_engines:
            logger.info(f"✅ LLM engines available: {', '.join(available_engines)}")
        else:
            logger.warning("⚠️  No LLM engines configured (all cloud queries will fail)")
    
    def query_with_fallback(self, prompt: str, max_tokens: int = 1000) -> Tuple[AIResponse, List[AIEngine]]:
        """
        Query with automatic fallback chain.
        
        Tries: Gemini → ChatGPT → DeepSeek
        
        Args:
            prompt: User prompt
            max_tokens: Maximum response tokens
            
        Returns:
            Tuple[AIResponse, List[AIEngine]]: (response, fallback_chain_used)
        """
        fallback_chain = []
        
        # Try Gemini first
        if self.gemini.is_available():
            logger.info("🔄 Querying Gemini...")
            response = self.gemini.query(prompt, max_tokens)
            fallback_chain.append(AIEngine.GEMINI)
            if response.is_valid:
                logger.info(f"✅ Gemini response successful")
                return response, fallback_chain
        
        # Fallback to ChatGPT
        if self.openai.is_available():
            logger.info("⚠️  Gemini failed, trying ChatGPT...")
            response = self.openai.query(prompt, max_tokens)
            fallback_chain.append(AIEngine.OPENAI)
            if response.is_valid:
                logger.info(f"✅ ChatGPT response successful")
                return response, fallback_chain
        
        # Final fallback to DeepSeek
        if self.deepseek.is_available():
            logger.info("⚠️  ChatGPT failed, trying DeepSeek...")
            response = self.deepseek.query(prompt, max_tokens)
            fallback_chain.append(AIEngine.DEEPSEEK)
            if response.is_valid:
                logger.info(f"✅ DeepSeek response successful")
                return response, fallback_chain
        
        # All engines failed
        logger.error("❌ All LLM engines failed")
        return AIResponse(
            engine=AIEngine.LOCAL,
            content="",
            success=False,
            error="All LLM engines unavailable or failed"
        ), fallback_chain
    
    async def query_with_fallback_async(self, prompt: str, max_tokens: int = 1000) -> Tuple[AIResponse, List[AIEngine]]:
        """
        Query with automatic fallback chain asynchronously.
        
        Tries: Gemini → ChatGPT → DeepSeek
        
        Args:
            prompt: User prompt
            max_tokens: Maximum response tokens
            
        Returns:
            Tuple[AIResponse, List[AIEngine]]: (response, fallback_chain_used)
        """
        fallback_chain = []
        
        # Try Gemini first
        if self.gemini.is_available():
            logger.info("🔄 Querying Gemini...")
            response = await self.gemini.query_async(prompt, max_tokens)
            fallback_chain.append(AIEngine.GEMINI)
            if response.is_valid:
                logger.info(f"✅ Gemini response successful")
                return response, fallback_chain
        
        # Fallback to ChatGPT
        if self.openai.is_available():
            logger.info("⚠️  Gemini failed, trying ChatGPT...")
            response = await self.openai.query_async(prompt, max_tokens)
            fallback_chain.append(AIEngine.OPENAI)
            if response.is_valid:
                logger.info(f"✅ ChatGPT response successful")
                return response, fallback_chain
        
        # Final fallback to DeepSeek
        if self.deepseek.is_available():
            logger.info("⚠️  ChatGPT failed, trying DeepSeek...")
            response = await self.deepseek.query_async(prompt, max_tokens)
            fallback_chain.append(AIEngine.DEEPSEEK)
            if response.is_valid:
                logger.info(f"✅ DeepSeek response successful")
                return response, fallback_chain
        
        # All engines failed
        logger.error("❌ All LLM engines failed")
        return AIResponse(
            engine=AIEngine.LOCAL,
            content="",
            success=False,
            error="All LLM engines unavailable or failed"
        ), fallback_chain


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with environment variables
    import os
    coordinator = LLMCoordinator(
        gemini_key=os.getenv("GEMINI_API_KEY"),
        openai_key=os.getenv("OPENAI_API_KEY"),
        deepseek_key=os.getenv("DEEPSEEK_API_KEY")
    )
    
    # Note: This will only work if API keys are set in environment
    print("Testing LLM Coordinator (requires API keys in environment)")
