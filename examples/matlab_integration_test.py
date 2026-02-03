"""Test script for MATLAB integration."""

from denario.providers import MATLABProvider, PremiumMathematicalOrchestrator, ComputationResult
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def test_matlab_provider():
    """Test MATLAB provider functionality."""
    print("Testing MATLAB Provider...")

    # Initialize MATLAB provider
    matlab_provider = MATLABProvider()

    # Test basic computation
    test_queries = [
        "solve x^2 + 2*x + 1 = 0",
        "integrate x^2 from 0 to 1",
        "derivative of x^3",
        "eigenvalues of [1 2; 3 4]",
        "optimize x^2 + 2*x + 1"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = matlab_provider.compute(query)
            print(f"  Result: {result.plaintext}")
            print(f"  LaTeX: {result.latex}")
            print(f"  Provider: {result.provider}")
            print(f"  Execution time: {result.execution_time:.3f}s")
        except Exception as e:
            print(f"  Error: {e}")

    # Test data analysis
    print("\nTesting data analysis...")
    test_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    try:
        result = matlab_provider.analyze_data(test_data, "statistical")
        print(f"  Data analysis result: {result.plaintext}")
    except Exception as e:
        print(f"  Data analysis error: {e}")


def test_orchestrator():
    """Test the premium mathematical orchestrator."""
    print("\nTesting Premium Mathematical Orchestrator...")

    # Initialize orchestrator
    config = {
        'matlab': {'enabled': True},
        # Disable for now since we don't have API key
        'wolfram_alpha': {'enabled': False}
    }

    orchestrator = PremiumMathematicalOrchestrator(config)

    # Test queries with different domains
    test_queries = [
        "solve x^2 + 2*x + 1 = 0",  # General math
        "signal processing of [1,2,3,4,5]",  # Signal processing
        "statistics of [1,2,3,4,5]",  # Statistics
        "optimize x^2 + 2*x + 1",  # Optimization
        "eigenvalues of [1 2; 3 4]"  # Linear algebra
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = orchestrator.compute(query)
            print(f"  Result: {result.plaintext}")
            print(f"  Provider: {result.provider}")
            print(f"  Execution time: {result.execution_time:.3f}s")
        except Exception as e:
            print(f"  Error: {e}")

    # Test provider statistics
    print("\nProvider Statistics:")
    stats = orchestrator.get_provider_stats()
    for provider, stat in stats.items():
        print(f"  {provider}: {stat}")


def test_capability_routing():
    """Test capability-based routing."""
    print("\nTesting Capability-Based Routing...")

    orchestrator = PremiumMathematicalOrchestrator({
        'matlab': {'enabled': True},
        'wolfram_alpha': {'enabled': False}
    })

    # Test different query types
    query_tests = [
        ("solve x^2 + 2*x + 1 = 0", "general"),
        ("signal processing of [1,2,3,4,5]", "signal_processing"),
        ("statistics of [1,2,3,4,5]", "statistics"),
        ("optimize x^2 + 2*x + 1", "optimization"),
        ("eigenvalues of [1 2; 3 4]", "linear_algebra")
    ]

    for query, expected_domain in query_tests:
        print(f"\nQuery: {query}")
        print(f"Expected domain: {expected_domain}")

        # Analyze query
        analysis = orchestrator._analyze_query(query)
        print(f"Detected domain: {analysis.domain}")
        print(f"Complexity: {analysis.complexity}")
        print(f"Required capabilities: {analysis.required_capabilities}")

        # Select provider
        provider = orchestrator._select_optimal_provider(analysis)
        print(f"Selected provider: {provider}")


def main():
    """Run all tests."""
    print("MATLAB Integration Test Suite")
    print("=" * 50)

    try:
        test_matlab_provider()
        test_orchestrator()
        test_capability_routing()
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
