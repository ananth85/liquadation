"""
LLM Client for OpenAI API Integration
Handles secure communication with language models
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response data structure from LLM"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    success: bool = True
    error: Optional[str] = None


class LLMClient:
    """Secure LLM client with memory cleanup and error handling supporting multiple providers"""
    
    def __init__(self, config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._active_requests = set()
        self.current_provider = self._determine_primary_provider()
        logger.info(f"LLM Client initialized with primary provider: {self.current_provider}")
    
    def _determine_primary_provider(self) -> str:
        """Determine which LLM provider to use as primary"""
        openai_available = (
            self.config.openai_api_key and 
            not self.config.openai_api_key.startswith('your_')
        )
        internal_available = (
            self.config.internal_llm_enabled and
            self.config.internal_llm_api_key and 
            not self.config.internal_llm_api_key.startswith('your_')
        )
        
        if self.config.primary_llm_provider == 'internal' and internal_available:
            return 'internal'
        elif openai_available:
            return 'openai'
        elif internal_available:
            return 'internal'
        else:
            logger.warning("No LLM provider configured - operations may fail")
            return 'openai'  # fallback default
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup"""
        await self._cleanup()
    
    async def _initialize_session(self):
        """Initialize HTTP session with security headers for current provider"""
        timeout_value = (
            self.config.internal_llm_timeout if self.current_provider == 'internal' 
            else 120
        )
        timeout = aiohttp.ClientTimeout(total=timeout_value)
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'{self.config.agent_name}/{self.config.agent_version}'
        }
        
        # Add provider-specific authorization
        if self.current_provider == 'openai':
            headers['Authorization'] = f'Bearer {self.config.openai_api_key}'
        elif self.current_provider == 'internal':
            headers['Authorization'] = f'Bearer {self.config.internal_llm_api_key}'
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers
        )
    
    async def _cleanup(self):
        """Clean up resources and memory"""
        # Cancel any active requests
        for task in self._active_requests:
            if not task.done():
                task.cancel()
        
        # Wait for cleanup with timeout
        if self._active_requests:
            await asyncio.wait(self._active_requests, timeout=5.0)
        
        # Close session
        if self.session:
            await self.session.close()
            self.session = None
        
        # Clear sensitive data from memory
        self._active_requests.clear()
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generate response from LLM with secure handling and automatic fallback
        
        Args:
            prompt: User prompt
            system_message: Optional system message for context
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            LLMResponse object with content and metadata
        """
        # Try primary provider first
        response = await self._attempt_request(
            prompt, system_message, max_tokens, temperature, self.current_provider
        )
        
        # If primary fails and fallback is enabled, try alternative provider
        if not response.success and self.config.auto_fallback_enabled:
            fallback_provider = 'internal' if self.current_provider == 'openai' else 'openai'
            
            if self._is_provider_available(fallback_provider):
                logger.warning(f"Primary provider {self.current_provider} failed, trying {fallback_provider}")
                
                # Switch to fallback provider temporarily
                old_provider = self.current_provider
                self.current_provider = fallback_provider
                
                # Close existing session and reinitialize for new provider
                if self.session:
                    await self.session.close()
                    self.session = None
                
                try:
                    response = await self._attempt_request(
                        prompt, system_message, max_tokens, temperature, fallback_provider
                    )
                    if response.success:
                        logger.info(f"Successfully switched to fallback provider: {fallback_provider}")
                    else:
                        logger.error(f"Fallback provider {fallback_provider} also failed")
                        self.current_provider = old_provider  # restore original
                except Exception as e:
                    logger.error(f"Fallback attempt failed: {e}")
                    self.current_provider = old_provider  # restore original
        
        return response
    
    def _is_provider_available(self, provider: str) -> bool:
        """Check if a provider is available and configured"""
        if provider == 'openai':
            return (
                self.config.openai_api_key and 
                not self.config.openai_api_key.startswith('your_')
            )
        elif provider == 'internal':
            return (
                self.config.internal_llm_enabled and
                self.config.internal_llm_api_key and 
                not self.config.internal_llm_api_key.startswith('your_')
            )
        return False
    
    async def _attempt_request(
        self, 
        prompt: str, 
        system_message: Optional[str],
        max_tokens: int,
        temperature: float,
        provider: str
    ) -> LLMResponse:
        """Attempt to make request with specified provider"""
        if not self.session:
            await self._initialize_session()
        
        try:
            # Prepare messages
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            # Get provider-specific configuration
            model, max_tokens_config, temp_config = self._get_provider_config(provider, max_tokens, temperature)
            
            # Prepare request payload
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens_config,
                "temperature": temp_config,
                "stream": False
            }
            
            # Make API request
            task = asyncio.create_task(self._make_request(payload, provider))
            self._active_requests.add(task)
            
            try:
                response_data = await task
                return self._parse_response(response_data, provider)
            finally:
                self._active_requests.discard(task)
                
        except Exception as e:
            logger.error(f"LLM request failed with {provider}: {e}")
            return LLMResponse(
                content="",
                model=model if 'model' in locals() else provider,
                usage={},
                finish_reason="error",
                success=False,
                error=str(e)
            )
    
    def _get_provider_config(self, provider: str, max_tokens: int, temperature: float):
        """Get provider-specific configuration"""
        if provider == 'openai':
            return (
                self.config.openai_model,
                min(max_tokens, self.config.openai_max_tokens),
                temperature
            )
        elif provider == 'internal':
            return (
                self.config.internal_llm_model,
                min(max_tokens, self.config.internal_llm_max_tokens),
                temperature
            )
        else:
            return "unknown", max_tokens, temperature
    
    async def _make_request(self, payload: Dict[str, Any], provider: str) -> Dict[str, Any]:
        """Make secure API request to specified provider"""
        if provider == 'openai':
            endpoint = f"{self.config.openai_api_base}/chat/completions"
        elif provider == 'internal':
            endpoint = f"{self.config.internal_llm_api_base}/chat/completions"
        else:
            raise Exception(f"Unknown provider: {provider}")
        
        async with self.session.post(endpoint, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"API request failed ({provider}): {response.status} - {error_text}")
            
            return await response.json()
    
    def _parse_response(self, data: Dict[str, Any], provider: str) -> LLMResponse:
        """Parse API response safely for specified provider"""
        try:
            choice = data['choices'][0]
            content = choice['message']['content']
            
            return LLMResponse(
                content=content,
                model=data.get('model', f"{provider}_model"),
                usage=data.get('usage', {}),
                finish_reason=choice.get('finish_reason', 'unknown')
            )
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse LLM response from {provider}: {e}")
            fallback_model = (
                self.config.openai_model if provider == 'openai' 
                else self.config.internal_llm_model
            )
            return LLMResponse(
                content="",
                model=fallback_model,
                usage={},
                finish_reason="parse_error",
                success=False,
                error=f"Response parsing failed ({provider}): {e}"
            )
    
    async def switch_provider(self, provider: str) -> bool:
        """
        Manually switch to a different LLM provider
        
        Args:
            provider: Provider to switch to ('openai' or 'internal')
            
        Returns:
            bool: True if switch was successful, False otherwise
        """
        if not self._is_provider_available(provider):
            logger.error(f"Provider {provider} is not available or not configured")
            return False
        
        if provider == self.current_provider:
            logger.info(f"Already using provider: {provider}")
            return True
        
        # Close existing session
        if self.session:
            await self.session.close()
            self.session = None
        
        # Switch provider
        old_provider = self.current_provider
        self.current_provider = provider
        
        try:
            # Initialize new session
            await self._initialize_session()
            logger.info(f"Successfully switched from {old_provider} to {provider}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to provider {provider}: {e}")
            self.current_provider = old_provider  # restore original
            return False
    
    def get_current_provider(self) -> str:
        """Get the currently active provider"""
        return self.current_provider
    
    def get_available_providers(self) -> List[str]:
        """Get list of available and configured providers"""
        providers = []
        if self._is_provider_available('openai'):
            providers.append('openai')
        if self._is_provider_available('internal'):
            providers.append('internal')
        return providers


class LLMService:
    """High-level LLM service for document generation tasks"""
    
    def __init__(self, config):
        self.config = config
        self.client = LLMClient(config)
    
    async def analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze user prompt to determine required actions"""
        system_message = """
        You are an AI assistant that analyzes user prompts to determine what actions are needed.
        Analyze the prompt and return a JSON object with:
        - task_type: (document_generation, web_search, api_query, mixed)
        - document_types: list of document types to generate
        - search_queries: list of web search queries needed
        - api_endpoints: list of APIs to query
        - organizations: list of organizations mentioned
        - urgency: (low, medium, high)
        - complexity: (simple, moderate, complex)
        """
        
        async with self.client as llm:
            response = await llm.generate_response(
                prompt=f"Analyze this prompt: {prompt}",
                system_message=system_message,
                temperature=0.3
            )
            
            if response.success:
                try:
                    return json.loads(response.content)
                except json.JSONDecodeError:
                    # Fallback to simple analysis
                    return {
                        "task_type": "mixed",
                        "document_types": ["general"],
                        "search_queries": [],
                        "api_endpoints": [],
                        "organizations": [],
                        "urgency": "medium",
                        "complexity": "moderate"
                    }
            else:
                raise Exception(f"Prompt analysis failed: {response.error}")
    
    async def generate_document_content(
        self, 
        document_type: str, 
        context: Dict[str, Any],
        organization: Optional[str] = None
    ) -> str:
        """Generate document content based on type and context"""
        system_message = f"""
        You are a legal document specialist generating {document_type} documents.
        Follow Australian legal standards and liquidation procedures.
        Ensure compliance with regulatory requirements.
        Use professional legal language and proper formatting.
        """
        
        prompt = f"""
        Generate a {document_type} document with the following context:
        {json.dumps(context, indent=2)}
        
        Organization: {organization or 'Generic Organization'}
        
        Requirements:
        - Follow Australian legal standards
        - Include all required legal clauses
        - Use professional formatting
        - Ensure regulatory compliance
        - Include appropriate legal disclaimers
        """
        
        async with self.client as llm:
            response = await llm.generate_response(
                prompt=prompt,
                system_message=system_message,
                max_tokens=3000,
                temperature=0.4
            )
            
            if response.success:
                return response.content
            else:
                raise Exception(f"Document generation failed: {response.error}")
    
    async def validate_document(self, content: str, document_type: str) -> Dict[str, Any]:
        """Validate generated document for compliance and completeness"""
        system_message = """
        You are a legal document validator. Check documents for:
        - Legal compliance
        - Required sections and clauses
        - Professional formatting
        - Regulatory requirements
        - Completeness
        
        Return JSON with: {valid: boolean, issues: [list], suggestions: [list]}
        """
        
        prompt = f"""
        Validate this {document_type} document:
        
        {content}
        
        Check for Australian legal compliance and completeness.
        """
        
        async with self.client as llm:
            response = await llm.generate_response(
                prompt=prompt,
                system_message=system_message,
                temperature=0.2
            )
            
            if response.success:
                try:
                    return json.loads(response.content)
                except json.JSONDecodeError:
                    return {
                        "valid": True,
                        "issues": [],
                        "suggestions": ["Manual review recommended"]
                    }
            else:
                return {
                    "valid": False,
                    "issues": [f"Validation failed: {response.error}"],
                    "suggestions": ["Manual review required"]
                } 