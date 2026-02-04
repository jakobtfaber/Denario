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
    
    BASE_URL = "https://api.adsabs.harvard.edu/v1"
    
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
                f"{self.BASE_URL}/search/query", 
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

    def export_bibtex(self, bibcodes: List[str]) -> str:
        """
        Export BibTeX entries for a list of bibcodes.
        
        Args:
            bibcodes: List of ADS bibcodes.
            
        Returns:
            A string containing all BibTeX entries.
        """
        payload = {"bibcode": bibcodes}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/export/bibtex",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining:
                print(f"ADS Export Rate Limit Remaining: {remaining}")
                
            response.raise_for_status()
            return response.json().get("export", "")
            
        except requests.exceptions.RequestException as e:
            print(f"ADS BibTeX Export failed: {e}")
            return ""

    def get_metrics(self, bibcodes: List[str]) -> Dict[str, Any]:
        """
        Get citation metrics for a list of bibcodes.
        
        Args:
            bibcodes: List of ADS bibcodes.
            
        Returns:
            Dictionary containing metrics (citation stats, histograms, etc.)
        """
        payload = {"bibcodes": bibcodes}
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/metrics",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"ADS Metrics failed: {e}")
            return {}

    def get_bibcode_from_arxiv(self, arxiv_id: str) -> Optional[str]:
        """
        Find the ADS bibcode corresponding to an arXiv ID.
        
        Args:
            arxiv_id: The arXiv identifier (e.g., "1602.03837").
            
        Returns:
            The ADS bibcode if found, else None.
        """
        # Search for identifier:arxiv_id
        # Note: ADS indexes arxiv IDs often with 'arXiv:' prefix in identifier field
        query = f"identifier:arxiv:{arxiv_id} OR identifier:{arxiv_id}"
        results = self.search(query, rows=1)
        if results:
            return results[0].get("bibcode")
        return None

    def get_paper_by_bibcode(self, bibcode: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific paper by its bibcode."""
        results = self.search(f"bibcode:{bibcode}", rows=1)
        return results[0] if results else None
