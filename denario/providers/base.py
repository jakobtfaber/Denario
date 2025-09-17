"""Base classes for mathematical computation providers."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ComputationResult:
    """Result from a mathematical computation."""

    plaintext: str
    latex: Optional[str] = None
    mathml: Optional[str] = None
    images: List[str] = None
    assumptions: List[str] = None
    sources: List[str] = None
    provider: str = "unknown"
    cost: float = 0.0
    execution_time: float = 0.0
    error: Optional[str] = None
    query: Optional[str] = None

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.assumptions is None:
            self.assumptions = []
        if self.sources is None:
            self.sources = []


class ComputationError(Exception):
    """Exception raised when mathematical computation fails."""
    pass


class MathematicalProvider(ABC):
    """Abstract base class for mathematical computation providers."""

    def __init__(self,
                 capabilities: List[str] = None,
                 cost_per_query: float = 0.0,
                 max_complexity: str = "medium",
                 priority: int = 1,
                 **kwargs):
        self.capabilities = capabilities or []
        self.cost_per_query = cost_per_query
        self.max_complexity = max_complexity
        self.priority = priority
        self._execution_times = []
        self._total_cost = 0.0

    @abstractmethod
    def compute(self, query: str) -> ComputationResult:
        """Execute a mathematical computation query."""
        pass

    def can_handle(
            self,
            query: str,
            required_capabilities: List[str] = None) -> bool:
        """Check if this provider can handle the given query."""
        if required_capabilities:
            return all(
                cap in self.capabilities for cap in required_capabilities)
        return True

    def estimate_cost(self, query: str) -> float:
        """Estimate the cost of executing a query."""
        return self.cost_per_query

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for this provider."""
        if not self._execution_times:
            return {
                'avg_execution_time': 0.0,
                'total_queries': 0,
                'total_cost': self._total_cost
            }

        return {
            'avg_execution_time': sum(self._execution_times) / len(self._execution_times),
            'min_execution_time': min(self._execution_times),
            'max_execution_time': max(self._execution_times),
            'total_queries': len(self._execution_times),
            'total_cost': self._total_cost
        }

    def _record_execution(self, execution_time: float, cost: float = None):
        """Record execution statistics."""
        self._execution_times.append(execution_time)
        if cost is not None:
            self._total_cost += cost
        elif self.cost_per_query > 0:
            self._total_cost += self.cost_per_query
