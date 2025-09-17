"""Premium mathematical computation orchestrator."""

from typing import Dict, List, Optional, Any
from .base import MathematicalProvider, ComputationResult, ComputationError
from .matlab_provider import MATLABProvider
from ..utils import WolframAlphaClient


class QueryAnalysis:
    """Analysis of a mathematical query."""

    def __init__(self,
                 complexity: str,
                 domain: str,
                 required_capabilities: List[str],
                 estimated_cost: float,
                 time_sensitivity: str = "normal"):
        self.complexity = complexity
        self.domain = domain
        self.required_capabilities = required_capabilities
        self.estimated_cost = estimated_cost
        self.time_sensitivity = time_sensitivity


class PremiumMathematicalOrchestrator:
    """Orchestrates multiple mathematical computation providers with intelligent routing."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.providers = {}
        self.capability_matrix = self._build_capability_matrix()
        self.domain_routing = self._build_domain_routing()
        self._initialize_providers()

    def _build_capability_matrix(self) -> Dict[str, Dict[str, int]]:
        """Build capability scoring matrix for all providers."""
        return {
            'matlab': {
                'symbolic': 6,
                'numeric': 10,
                'visualization': 10,
                'knowledge': 4,
                'optimization': 10,
                'differential_equations': 8,
                'number_theory': 5,
                'algebra': 8,
                'calculus': 8,
                'signal_processing': 10,
                'linear_algebra': 10,
                'statistics': 10},
            'wolfram_alpha': {
                'symbolic': 8,
                'numeric': 8,
                'visualization': 7,
                'knowledge': 10,
                'optimization': 6,
                'differential_equations': 7,
                'number_theory': 6,
                'algebra': 8,
                'calculus': 8,
                'signal_processing': 4,
                'linear_algebra': 7,
                'statistics': 6}}

    def _build_domain_routing(self) -> Dict[str, str]:
        """Build domain-based routing rules."""
        return {
            'numerical_computation': 'matlab',
            'signal_processing': 'matlab',
            'data_analysis': 'matlab',
            'statistics': 'matlab',
            'optimization': 'matlab',
            'linear_algebra': 'matlab',
            'knowledge_queries': 'wolfram_alpha',
            'real_time_data': 'wolfram_alpha',
            'unit_conversion': 'wolfram_alpha'
        }

    def _initialize_providers(self):
        """Initialize available mathematical computation providers."""

        # MATLAB provider
        if self.config.get('matlab', {}).get('enabled', True):
            self.providers['matlab'] = MATLABProvider(
                matlab_path=self.config.get('matlab', {}).get('path'),
                license_file=self.config.get('matlab', {}).get('license_file')
            )

        # Wolfram Alpha provider (existing)
        if self.config.get('wolfram_alpha', {}).get('enabled', True):
            from .wolfram_provider import WolframAlphaProvider
            self.providers['wolfram_alpha'] = WolframAlphaProvider(
                app_id=self.config.get(
                    'wolfram_alpha', {}).get('api_key'), enable_hitl=self.config.get(
                    'wolfram_alpha', {}).get(
                    'enable_hitl', False))

    def compute(self,
                query: str,
                context: Dict[str,
                              Any] = None) -> ComputationResult:
        """Route query to optimal provider based on intelligent analysis."""

        # Analyze query characteristics
        query_analysis = self._analyze_query(query)

        # Select optimal provider
        provider_name = self._select_optimal_provider(query_analysis, context)

        if provider_name not in self.providers:
            raise ComputationError(f"Provider '{provider_name}' not available")

        provider = self.providers[provider_name]

        # Execute computation with selected provider
        try:
            result = provider.compute(query)
            result.provider = provider_name
            return result
        except Exception as e:
            # Fallback to alternative provider
            fallback_provider = self._get_fallback_provider(
                provider_name, query_analysis)
            if fallback_provider and fallback_provider in self.providers:
                result = self.providers[fallback_provider].compute(query)
                result.provider = fallback_provider
                return result
            else:
                raise ComputationError(f"All providers failed: {e}")

    def _analyze_query(self, query: str) -> QueryAnalysis:
        """Analyze query to determine optimal provider."""
        query_lower = query.lower()

        # Determine complexity
        complexity = "low"
        if any(
            keyword in query_lower for keyword in [
                'integrate',
                'solve',
                'optimize',
                'eigen']):
            complexity = "high"
        elif any(keyword in query_lower for keyword in ['derivative', 'matrix', 'plot']):
            complexity = "medium"

        # Determine domain
        domain = "general"
        if any(
            keyword in query_lower for keyword in [
                'signal',
                'fft',
                'filter',
                'spectrum']):
            domain = "signal_processing"
        elif any(keyword in query_lower for keyword in ['statistics', 'mean', 'variance', 'correlation']):
            domain = "statistics"
        elif any(keyword in query_lower for keyword in ['optimize', 'minimize', 'maximize']):
            domain = "optimization"
        elif any(keyword in query_lower for keyword in ['matrix', 'eigen', 'linear']):
            domain = "linear_algebra"
        elif any(keyword in query_lower for keyword in ['convert', 'miles', 'kilometers', 'temperature', 'units']):
            domain = "unit_conversion"
        elif any(keyword in query_lower for keyword in ['weather', 'current', 'today', 'temperature']):
            domain = "real_time_data"
        elif any(keyword in query_lower for keyword in ['knowledge', 'what is', 'define', 'population', 'capital']):
            domain = "knowledge_queries"

        # Determine required capabilities
        required_capabilities = []
        if any(
            keyword in query_lower for keyword in [
                'plot',
                'graph',
                'visualize']):
            required_capabilities.append('visualization')
        if any(
            keyword in query_lower for keyword in [
                'symbolic',
                'algebraic']):
            required_capabilities.append('symbolic')
        if any(
            keyword in query_lower for keyword in [
                'numeric',
                'calculate',
                'compute']):
            required_capabilities.append('numeric')

        # Estimate cost
        estimated_cost = 0.0
        if 'wolfram_alpha' in self.providers:
            estimated_cost += 0.01  # Wolfram Alpha cost

        return QueryAnalysis(
            complexity=complexity,
            domain=domain,
            required_capabilities=required_capabilities,
            estimated_cost=estimated_cost
        )

    def _select_optimal_provider(self,
                                 query_analysis: QueryAnalysis,
                                 context: Dict[str,
                                               Any] = None) -> str:
        """Select optimal provider based on query analysis."""

        # Check domain-based routing first
        if query_analysis.domain in self.domain_routing:
            preferred_provider = self.domain_routing[query_analysis.domain]
            if preferred_provider in self.providers:
                return preferred_provider

        # Score providers based on capabilities
        provider_scores = {}
        for provider_name, provider in self.providers.items():
            if provider_name not in self.capability_matrix:
                continue

            capabilities = self.capability_matrix[provider_name]
            score = 0

            # Score based on required capabilities
            for capability in query_analysis.required_capabilities:
                if capability in capabilities:
                    score += capabilities[capability]

            # Bonus for complexity match
            if query_analysis.complexity == "high" and capabilities.get(
                    'numeric', 0) >= 9:
                score += 2
            elif query_analysis.complexity == "medium" and capabilities.get('numeric', 0) >= 7:
                score += 1

            provider_scores[provider_name] = score

        if not provider_scores:
            raise ComputationError("No suitable providers available")

        # Select highest scoring provider
        return max(provider_scores.items(), key=lambda x: x[1])[0]

    def _get_fallback_provider(
            self,
            failed_provider: str,
            query_analysis: QueryAnalysis) -> Optional[str]:
        """Get fallback provider when primary provider fails."""
        available_providers = [
            name for name in self.providers.keys() if name != failed_provider]

        if not available_providers:
            return None

        # Return first available provider as fallback
        return available_providers[0]

    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics for all providers."""
        stats = {}
        for name, provider in self.providers.items():
            if hasattr(provider, 'get_performance_stats'):
                stats[name] = provider.get_performance_stats()
            else:
                stats[name] = {'status': 'active', 'queries': 0}
        return stats

    def list_providers(self) -> List[str]:
        """List available providers."""
        return list(self.providers.keys())

    def add_provider(self, name: str, provider: MathematicalProvider):
        """Add a new provider."""
        self.providers[name] = provider
