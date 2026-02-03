"""Wolfram Alpha provider wrapper for mathematical computations."""

import time
from typing import Dict, List, Optional, Any
from .base import MathematicalProvider, ComputationResult, ComputationError
from ..utils import WolframAlphaClient


class WolframAlphaProvider(MathematicalProvider):
    """Provider using Wolfram Alpha API for mathematical computations."""

    def __init__(self,
                 app_id: Optional[str] = None,
                 enable_hitl: bool = False,
                 **kwargs):
        super().__init__(
            capabilities=[
                'symbolic', 'numeric', 'visualization', 'knowledge',
                'optimization', 'differential_equations', 'number_theory',
                'algebra', 'calculus', 'unit_conversion', 'real_time_data'
            ],
            cost_per_query=0.01,  # Wolfram Alpha API cost
            max_complexity='high',
            priority=2,
            **kwargs
        )
        self.client = WolframAlphaClient(
            app_id=app_id,
            enable_hitl=enable_hitl
        )

    def compute(self, query: str) -> ComputationResult:
        """Execute computation using Wolfram Alpha."""
        start_time = time.time()

        try:
            # Execute Wolfram Alpha query
            wa_result = self.client.query(query)

            # Extract structured results
            structured = self.client.extract_structured_results(wa_result)

            execution_time = time.time() - start_time
            self._record_execution(execution_time, self.cost_per_query)

            return ComputationResult(
                plaintext=structured.get('plaintext', ''),
                latex=structured.get('latex', ''),
                mathml=structured.get('mathml', ''),
                images=structured.get('images', []),
                assumptions=structured.get('assumptions', []),
                sources=structured.get('sources', []),
                provider='wolfram_alpha',
                cost=self.cost_per_query,
                execution_time=execution_time,
                query=query
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_execution(execution_time, self.cost_per_query)
            raise ComputationError(f"Wolfram Alpha computation failed: {e}")

    def needs_hitl_review(self, query: str) -> bool:
        """Check if query result needs human-in-the-loop review."""
        try:
            wa_result = self.client.query(query)
            return self.client.needs_hitl_review(wa_result)
        except Exception:
            return False

    def get_hitl_prompt(self, query: str) -> str:
        """Get HITL review prompt for query."""
        try:
            wa_result = self.client.query(query)
            return self.client.get_hitl_prompt(query, wa_result)
        except Exception as e:
            return f"Error generating HITL prompt: {e}"
