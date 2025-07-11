"""
Web Search Service for AI Agent
Provides internet search capabilities with multiple search engines
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import aiohttp
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Individual search result"""
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float = 0.0


@dataclass
class SearchResponse:
    """Search response with multiple results"""
    query: str
    results: List[SearchResult]
    total_results: int
    search_time: float
    success: bool = True
    error: Optional[str] = None


class WebSearchService:
    """Web search service with multiple search engine support"""
    
    def __init__(self, config):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._search_engines = {
            'duckduckgo': self._search_duckduckgo,
            'google': self._search_google_serp,
            'fallback': self._search_fallback
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _initialize_session(self):
        """Initialize HTTP session"""
        timeout = aiohttp.ClientTimeout(total=60)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
    
    async def search(
        self, 
        query: str, 
        max_results: int = 10,
        search_engine: Optional[str] = None
    ) -> SearchResponse:
        """
        Perform web search using specified or default search engine
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            search_engine: Specific search engine to use
            
        Returns:
            SearchResponse with results
        """
        if not self.session:
            await self._initialize_session()
        
        engine = search_engine or self.config.search_engine
        
        # Fallback chain for search engines
        engines_to_try = [engine]
        if engine != 'duckduckgo':
            engines_to_try.append('duckduckgo')
        if 'fallback' not in engines_to_try:
            engines_to_try.append('fallback')
        
        last_error = None
        
        for engine_name in engines_to_try:
            try:
                search_func = self._search_engines.get(engine_name)
                if search_func:
                    logger.info(f"Searching with {engine_name}: {query}")
                    result = await search_func(query, max_results)
                    if result.success and result.results:
                        return result
                    last_error = result.error
            except Exception as e:
                logger.warning(f"Search engine {engine_name} failed: {e}")
                last_error = str(e)
                continue
        
        # All engines failed
        return SearchResponse(
            query=query,
            results=[],
            total_results=0,
            search_time=0.0,
            success=False,
            error=f"All search engines failed. Last error: {last_error}"
        )
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> SearchResponse:
        """Search using DuckDuckGo Instant Answer API"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # DuckDuckGo Instant Answer API
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"DuckDuckGo API returned {response.status}")
                
                data = await response.json()
                results = []
                
                # Process instant answer
                if data.get('AbstractText'):
                    results.append(SearchResult(
                        title=data.get('Heading', 'Instant Answer'),
                        url=data.get('AbstractURL', ''),
                        snippet=data.get('AbstractText', ''),
                        source='DuckDuckGo',
                        relevance_score=1.0
                    ))
                
                # Process related topics
                for topic in data.get('RelatedTopics', [])[:max_results-len(results)]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append(SearchResult(
                            title=topic.get('Text', '').split(' - ')[0],
                            url=topic.get('FirstURL', ''),
                            snippet=topic.get('Text', ''),
                            source='DuckDuckGo',
                            relevance_score=0.8
                        ))
                
                search_time = asyncio.get_event_loop().time() - start_time
                
                return SearchResponse(
                    query=query,
                    results=results[:max_results],
                    total_results=len(results),
                    search_time=search_time
                )
                
        except Exception as e:
            search_time = asyncio.get_event_loop().time() - start_time
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=search_time,
                success=False,
                error=str(e)
            )
    
    async def _search_google_serp(self, query: str, max_results: int) -> SearchResponse:
        """Search using SerpAPI (Google) if API key is available"""
        start_time = asyncio.get_event_loop().time()
        
        if not self.config.serpapi_api_key or self.config.serpapi_api_key.startswith('your_'):
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=0.0,
                success=False,
                error="SerpAPI key not configured"
            )
        
        try:
            url = "https://serpapi.com/search"
            params = {
                'q': query,
                'engine': 'google',
                'api_key': self.config.serpapi_api_key,
                'num': min(max_results, 10)
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"SerpAPI returned {response.status}")
                
                data = await response.json()
                results = []
                
                for item in data.get('organic_results', []):
                    results.append(SearchResult(
                        title=item.get('title', ''),
                        url=item.get('link', ''),
                        snippet=item.get('snippet', ''),
                        source='Google',
                        relevance_score=0.9
                    ))
                
                search_time = asyncio.get_event_loop().time() - start_time
                
                return SearchResponse(
                    query=query,
                    results=results,
                    total_results=data.get('search_information', {}).get('total_results', 0),
                    search_time=search_time
                )
                
        except Exception as e:
            search_time = asyncio.get_event_loop().time() - start_time
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=search_time,
                success=False,
                error=str(e)
            )
    
    async def _search_fallback(self, query: str, max_results: int) -> SearchResponse:
        """Fallback search using Wikipedia API"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Wikipedia search API
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
            search_url = "https://en.wikipedia.org/w/api.php"
            
            # Search for pages
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': min(max_results, 5)
            }
            
            async with self.session.get(search_url, params=search_params) as response:
                if response.status != 200:
                    raise Exception(f"Wikipedia search failed: {response.status}")
                
                search_data = await response.json()
                results = []
                
                for item in search_data.get('query', {}).get('search', []):
                    title = item.get('title', '')
                    snippet = item.get('snippet', '').replace('<span class="searchmatch">', '').replace('</span>', '')
                    
                    results.append(SearchResult(
                        title=title,
                        url=f"https://en.wikipedia.org/wiki/{quote_plus(title)}",
                        snippet=snippet,
                        source='Wikipedia',
                        relevance_score=0.7
                    ))
                
                search_time = asyncio.get_event_loop().time() - start_time
                
                return SearchResponse(
                    query=query,
                    results=results,
                    total_results=len(results),
                    search_time=search_time
                )
                
        except Exception as e:
            search_time = asyncio.get_event_loop().time() - start_time
            return SearchResponse(
                query=query,
                results=[],
                total_results=0,
                search_time=search_time,
                success=False,
                error=str(e)
            )
    
    async def search_multiple_queries(self, queries: List[str], max_results_per_query: int = 5) -> Dict[str, SearchResponse]:
        """Search multiple queries concurrently"""
        tasks = []
        for query in queries:
            task = asyncio.create_task(self.search(query, max_results_per_query))
            tasks.append((query, task))
        
        results = {}
        for query, task in tasks:
            try:
                result = await task
                results[query] = result
            except Exception as e:
                logger.error(f"Search failed for query '{query}': {e}")
                results[query] = SearchResponse(
                    query=query,
                    results=[],
                    total_results=0,
                    search_time=0.0,
                    success=False,
                    error=str(e)
                )
        
        return results 