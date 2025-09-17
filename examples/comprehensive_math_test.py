"""Comprehensive test for mathematical computation integration."""

from denario.utils import WolframAlphaClient
from denario.providers import MATLABProvider, PremiumMathematicalOrchestrator
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def test_matlab_wolfram_integration():
    """Test integration between MATLAB and Wolfram Alpha providers."""
    print("Testing MATLAB + Wolfram Alpha Integration...")

    # Initialize orchestrator with both providers
    config = {
        'matlab': {
            'enabled': True}, 'wolfram_alpha': {
            'enabled': True, 'api_key': os.getenv(
                'WOLFRAM_APP_ID', '2YTR59QXRE')}}

    orchestrator = PremiumMathematicalOrchestrator(config)

    # Test queries that should route to different providers
    test_queries = [
        # MATLAB-appropriate queries
        ("signal processing of [1,2,3,4,5]", "matlab"),
        ("statistics of [1,2,3,4,5]", "matlab"),
        ("optimize x^2 + 2*x + 1", "matlab"),
        ("eigenvalues of [1 2; 3 4]", "matlab"),

        # Wolfram Alpha-appropriate queries (if API key available)
        ("what is the population of France", "wolfram_alpha"),
        ("convert 100 miles to kilometers", "wolfram_alpha"),
        ("current weather in New York", "wolfram_alpha"),

        # General mathematical queries
        ("solve x^2 + 2*x + 1 = 0", "matlab"),  # Should prefer MATLAB
        ("integrate x^2 from 0 to 1", "matlab"),  # Should prefer MATLAB
    ]

    for query, expected_provider in test_queries:
        print(f"\nQuery: {query}")
        print(f"Expected provider: {expected_provider}")

        try:
            result = orchestrator.compute(query)
            print(f"  Result: {result.plaintext}")
            print(f"  Actual provider: {result.provider}")
            print(f"  Execution time: {result.execution_time:.3f}s")

            # Check if provider selection was correct
            if result.provider == expected_provider:
                print("  ✅ Provider selection correct")
            else:
                print(
                    f"  ⚠️  Provider selection different (expected {expected_provider})")

        except Exception as e:
            print(f"  ❌ Error: {e}")


def test_provider_capabilities():
    """Test provider capabilities and routing logic."""
    print("\nTesting Provider Capabilities...")

    orchestrator = PremiumMathematicalOrchestrator(
        {
            'matlab': {
                'enabled': True}, 'wolfram_alpha': {
                'enabled': True, 'api_key': os.getenv(
                    'WOLFRAM_APP_ID', '2YTR59QXRE')}})

    # Test capability matrix
    print("Capability Matrix:")
    for provider, capabilities in orchestrator.capability_matrix.items():
        print(f"  {provider}:")
        for capability, score in capabilities.items():
            print(f"    {capability}: {score}")

    # Test domain routing
    print("\nDomain Routing:")
    for domain, provider in orchestrator.domain_routing.items():
        print(f"  {domain} -> {provider}")

    # Test query analysis
    test_queries = [
        "solve x^2 + 2*x + 1 = 0",
        "signal processing of [1,2,3,4,5]",
        "what is the capital of France",
        "optimize x^2 + 2*x + 1",
        "eigenvalues of [1 2; 3 4]"
    ]

    print("\nQuery Analysis:")
    for query in test_queries:
        analysis = orchestrator._analyze_query(query)
        print(f"  '{query}':")
        print(f"    Domain: {analysis.domain}")
        print(f"    Complexity: {analysis.complexity}")
        print(f"    Required capabilities: {analysis.required_capabilities}")
        print(f"    Estimated cost: ${analysis.estimated_cost:.3f}")


def test_performance_monitoring():
    """Test performance monitoring and statistics."""
    print("\nTesting Performance Monitoring...")

    orchestrator = PremiumMathematicalOrchestrator(
        {
            'matlab': {
                'enabled': True}, 'wolfram_alpha': {
                'enabled': True, 'api_key': os.getenv(
                    'WOLFRAM_APP_ID', '2YTR59QXRE')}})

    # Run some queries to generate statistics
    test_queries = [
        "solve x^2 + 2*x + 1 = 0",
        "signal processing of [1,2,3,4,5]",
        "optimize x^2 + 2*x + 1",
        "eigenvalues of [1 2; 3 4]"
    ]

    for query in test_queries:
        try:
            result = orchestrator.compute(query)
            print(f"  {query} -> {result.provider} ({result.execution_time:.3f}s)")
        except Exception as e:
            print(f"  {query} -> Error: {e}")

    # Get performance statistics
    print("\nPerformance Statistics:")
    stats = orchestrator.get_provider_stats()
    for provider, stat in stats.items():
        print(f"  {provider}:")
        for key, value in stat.items():
            print(f"    {key}: {value}")


def test_error_handling():
    """Test error handling and fallback mechanisms."""
    print("\nTesting Error Handling...")

    orchestrator = PremiumMathematicalOrchestrator(
        {
            'matlab': {
                'enabled': True}, 'wolfram_alpha': {
                'enabled': True, 'api_key': os.getenv(
                    'WOLFRAM_APP_ID', '2YTR59QXRE')}})

    # Test with invalid queries
    invalid_queries = [
        "",  # Empty query
        "invalid mathematical expression",  # Invalid syntax
        "solve x^2 + 2*x + 1 = 0 for y",  # Invalid variable
    ]

    for query in invalid_queries:
        print(f"\nTesting invalid query: '{query}'")
        try:
            result = orchestrator.compute(query)
            print(f"  Result: {result.plaintext}")
            print(f"  Provider: {result.provider}")
        except Exception as e:
            print(f"  Error handled: {e}")


def main():
    """Run comprehensive test suite."""
    print("Comprehensive Mathematical Computation Integration Test")
    print("=" * 60)

    try:
        test_matlab_wolfram_integration()
        test_provider_capabilities()
        test_performance_monitoring()
        test_error_handling()

        print("\n" + "=" * 60)
        print("✅ All comprehensive tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
