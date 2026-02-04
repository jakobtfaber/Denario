"""ADS (Astrophysics Data System) Provider."""

import requests
import time
from typing import Dict, List, Optional, Any
from .base import MathematicalProvider, ComputationResult, ComputationError

class ADSProvider:
    """
    Provider for the Astrophysics Data System (ADS) API.
    Used for searching astronomical literature.
    """
    
    BASE_URL = "https://api.adsabs.harvard.edu/v1/search/query"
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("ADS API key is required")
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def search(self, query: str, rows: int = 5) -> List[Dict[str, Any]]:
        """
        Execute a search query against the ADS API.
        
        Args:
            query: The search query string (Solr syntax).
            rows: Number of results to return.
            
        Returns:
            List of paper dictionaries.
        """
        params = {
            "q": query,
            "fl": "title,author,abstract,bibcode,pubdate,year,citation_count",
            "rows": rows,
            "sort": "citation_count desc" 
        }
        
        try:
            response = requests.get(
                self.BASE_URL, 
                headers=self.headers, 
                params=params,
                timeout=30
            )
            
            # Log rate limits if available
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining:
                print(f"ADS Rate Limit Remaining: {remaining}")
                
            response.raise_for_status()
            data = response.json()
            
            docs = data.get("response", {}).get("docs", [])
            return docs
            
        except requests.exceptions.RequestException as e:
            print(f"ADS Search failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return []

    def get_paper_by_bibcode(self, bibcode: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific paper by its bibcode."""
        results = self.search(f"bibcode:{bibcode}", rows=1)
        return results[0] if results else None
