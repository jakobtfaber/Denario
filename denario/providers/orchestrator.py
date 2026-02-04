"""Premium mathematical computation orchestrator."""

from typing import Dict, List, Optional, Any
import os
import subprocess
from .base import MathematicalProvider, ComputationResult, ComputationError
from .matlab_provider import MATLABProvider
from .python_provider import PythonProvider


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
        matrix = {
            'matlab': {
                'symbolic': 6,
                'numeric': 10,
                'visualization': 8, # Downgraded in favor of Python/SciencePlots
                'knowledge': 4,
                'optimization': 10,
                'differential_equations': 8,
                'number_theory': 5,
                'algebra': 8,
                'calculus': 8,
                'signal_processing': 10,
                'linear_algebra': 10,
                'statistics': 10
            },
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
                'statistics': 6
            },
            'python_scienceplots': {
                'symbolic': 2,
                'numeric': 9,
                'visualization': 10, # Highest score for visualization
                'knowledge': 0,
                'optimization': 8,
                'differential_equations': 6,
                'number_theory': 4,
                'algebra': 4,
                'calculus': 4,
                'signal_processing': 9,
                'linear_algebra': 9,
                'statistics': 9
            }
        }

        # Dynamically adjust MATLAB capabilities based on available toolboxes
        try:
            mcfg = self.config.get('matlab', {})
            backend = mcfg.get('backend') or os.getenv('MATLAB_BACKEND', '')
            container = (
                mcfg.get('container_name')
                or os.getenv('MATLAB_DOCKER_CONTAINER', 'matlab_r2025a')
            )
            if backend == 'docker':
                # Prefer cached capabilities JSON if present
                caps = self._load_cached_capabilities()
                tb_map = {}
                oper = {}
                if caps:
                    licensed = caps.get('toolboxes', {}).get('licensed', {})
                    oper = caps.get('toolboxes', {}).get('operational', {})
                    # Normalize keys for licensed map (remove spaces)
                    tb_map = {
                        'Symbolic_Toolbox': bool(
                            licensed.get(
                                'SymbolicMathToolbox', False)), 'Optimization_Toolbox': bool(
                            licensed.get(
                                'OptimizationToolbox', False)), 'Statistics_and_Machine_Learning_Toolbox': bool(
                            licensed.get(
                                'StatisticsAndMachineLearningToolbox', False)), 'Signal_Processing_Toolbox': bool(
                            licensed.get(
                                'SignalProcessingToolbox', False)), 'Image_Processing_Toolbox': bool(
                            licensed.get(
                                'ImageProcessingToolbox', False)), 'Parallel_Computing_Toolbox': bool(
                            licensed.get(
                                'ParallelComputingToolbox', False)), 'Control_System_Toolbox': bool(
                            licensed.get(
                                'ControlSystemToolbox', False)), 'Curve_Fitting_Toolbox': bool(
                            licensed.get(
                                'CurveFittingToolbox', False)), }
                else:
                    tb_map = self._probe_matlab_toolboxes(container)
                # Lower capability scores when toolbox missing
                if not (
                    tb_map.get(
                        'Symbolic_Toolbox',
                        False) or oper.get(
                        'Symbolic',
                        False)):
                    matrix['matlab']['symbolic'] = 0
                if not (
                    tb_map.get(
                        'Optimization_Toolbox',
                        False) or oper.get(
                        'Optimization',
                        False)):
                    matrix['matlab']['optimization'] = 5
                if not (
                    tb_map.get(
                        'Statistics_and_Machine_Learning_Toolbox',
                        False) or oper.get(
                        'Statistics',
                        False)):
                    matrix['matlab']['statistics'] = 5
                if not (
                    tb_map.get(
                        'Signal_Processing_Toolbox',
                        False) or oper.get(
                        'Signal',
                        False)):
                    matrix['matlab']['signal_processing'] = 6
                if not tb_map.get('Linear_Algebra_Toolbox', True):
                    # not an actual toolbox; keep default
                    pass
        except Exception:
            # Best-effort; keep defaults on probe failure
            pass

        return matrix

    def _load_cached_capabilities(self) -> Optional[Dict[str, Any]]:
        """Load cached capability JSON written by preflight if present.

        Looks for path in env MATLAB_CAPABILITIES_JSON, else a default
        DenarioApp location.
        """
        import json as _json
        paths = [
            os.getenv('MATLAB_CAPABILITIES_JSON', ''),
            '/data/cmbagents/DenarioApp/data/matlab_capabilities.json',
        ]
        for p in paths:
            if not p:
                continue
            try:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        return _json.load(f)
            except Exception:
                continue
        return None

    def _probe_matlab_toolboxes(self, container: str) -> Dict[str, bool]:
        """Probe selected MATLAB toolboxes in a docker container.

        Returns a dict mapping toolbox IDs to booleans.
        """
        toolboxes = [
            'Symbolic_Toolbox',
            'Optimization_Toolbox',
            'Statistics_and_Machine_Learning_Toolbox',
            'Signal_Processing_Toolbox',
            'Parallel_Computing_Toolbox',
            'Image_Processing_Toolbox',
            'Control_System_Toolbox',
            'Curve_Fitting_Toolbox',
        ]
        status: Dict[str, bool] = {}
        for tb in toolboxes:
            try:
                cmd = [
                    'docker', 'exec', container, 'matlab', '-batch',
                    f"disp(license(''test'',''{tb}''))",
                ]
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=6,
                )
                status[tb] = (
                    proc.returncode == 0 and proc.stdout.strip() == '1')
            except Exception:
                status[tb] = False
        return status

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
            'unit_conversion': 'wolfram_alpha',
            'symbolic_math': 'wolfram_alpha', # New explicit routing
            'visualization': 'python_scienceplots' # Explicit routing
        }

    def _initialize_providers(self):
        """Initialize available mathematical computation providers."""

        # Python Provider (Always enabled, high priority for visualization)
        self.providers['python_scienceplots'] = PythonProvider(
            work_dir=self.config.get('python', {}).get('work_dir', '/tmp/denario_plots')
        )

        # MATLAB provider (supports docker backend)
        if self.config.get('matlab', {}).get('enabled', True):
            mcfg = self.config.get('matlab', {})
            self.providers['matlab'] = MATLABProvider(
                matlab_path=mcfg.get('path'),
                license_file=mcfg.get('license_file'),
                backend=mcfg.get('backend'),
                container_name=mcfg.get('container_name'),
                work_mount=mcfg.get('work_mount'),
                entrypoint=mcfg.get('entrypoint'),
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
                'integrate',
                'solve',
                'derivative',
                'limit',
                'series',
                'integral',
                'simplify',
                'expand',
                'factor',
                'taylor',
                'maclaurin',
                'laplace',
                'inverse',
                'sum',
                'product',
                'antiderivative',
                'diff']):
            domain = "symbolic_math" # New domain for explicit symbolic requests
        elif any(
            keyword in query_lower for keyword in [
                'signal',
                'fft',
                'filter',
                'spectrum']):
            domain = "signal_processing"
        elif any(keyword in query_lower for keyword in ['plot', 'visualize', 'graph', 'chart', 'figure']):
             domain = "visualization"
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

    def healthcheck(self) -> Dict[str, Any]:
        """Return health and capability info for providers (lightweight)."""
        info: Dict[str, Any] = {}
        # MATLAB docker quick probe
        if 'matlab' in self.providers:
            p = self.providers['matlab']
            status = {'backend': getattr(p, 'backend', 'engine')}
            if getattr(p, 'backend', None) == 'docker':
                status['container'] = getattr(p, 'container_name', None)
                status['work_mount'] = getattr(p, 'work_mount', None)
                # Do not exec docker here; just surface config
            info['matlab'] = status
        if 'wolfram_alpha' in self.providers:
            info['wolfram_alpha'] = {'enabled': True}
        return info

    def list_providers(self) -> List[str]:
        """List available providers."""
        return list(self.providers.keys())

    def add_provider(self, name: str, provider: MathematicalProvider):
        """Add a new provider."""
        self.providers[name] = provider
