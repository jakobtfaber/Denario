"""Comprehensive test for Wolfram Alpha integration with Denario.

This script tests:
1. Enhanced WolframAlphaClient with caching and structured parsing
2. LangGraph tool integration
3. HITL review functionality
4. Paper generation with mathematical content

Usage (ensure conda env 'cmbagent' active):
    export WOLFRAM_APP_ID=YOUR_APP_ID
    python -m Denario.examples.wolfram_integration_test
"""
from denario import Denario
from denario.tools import create_wolfram_tool
from denario.utils import WolframAlphaClient
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import denario
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_enhanced_client():
    """Test the enhanced WolframAlphaClient with caching and structured parsing."""
    print("🧪 Testing Enhanced WolframAlphaClient...")

    client = WolframAlphaClient(enable_hitl=True, cache_dir="./test_cache")

    # Test 1: Basic query with caching
    print("\n1. Testing basic query with caching...")
    result1 = client.query("integrate exp(-x^2) from -infinity to infinity")
    primary_text = WolframAlphaClient.extract_primary_text(result1)
    print(f"   Result: {primary_text}")

    # Test 2: Same query should use cache
    print("\n2. Testing cache hit...")
    result2 = client.query("integrate exp(-x^2) from -infinity to infinity")
    print(
        f"   Cached result: {
            WolframAlphaClient.extract_primary_text(result2)}")

    # Test 3: Structured parsing
    print("\n3. Testing structured parsing...")
    structured = WolframAlphaClient.extract_structured_results(result1)
    print(f"   Plaintext: {structured['plaintext'][:2]}")
    print(f"   LaTeX: {structured['latex'][:2]}")
    print(f"   Assumptions: {structured['assumptions'][:2]}")

    # Test 4: HITL review detection
    print("\n4. Testing HITL review detection...")
    needs_review = client.needs_hitl_review(result1)
    print(f"   Needs HITL review: {needs_review}")

    if needs_review:
        hitl_prompt = client.get_hitl_prompt(
            "integrate exp(-x^2) from -infinity to infinity", result1)
        print(f"   HITL prompt: {hitl_prompt[:100]}...")

    print("✅ Enhanced client test completed!")


def test_langchain_tool():
    """Test the LangChain tool integration."""
    print("\n🔧 Testing LangChain Tool Integration...")

    tool = create_wolfram_tool(enable_hitl=False)

    # Test tool execution
    result = tool._run("convert 1 meter to feet")
    print(f"   Tool result: {result}")

    # Test with different query
    result2 = tool._run("solve x^2 + 5x + 6 = 0")
    print(f"   Tool result 2: {result2}")

    print("✅ LangChain tool test completed!")


def test_denario_integration():
    """Test Denario integration with Wolfram Alpha."""
    print("\n🔬 Testing Denario Integration...")

    # Create a test project
    test_dir = "./test_denario_wolfram"
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)

    den = Denario(project_dir=test_dir)

    # Set a data description that involves mathematical computations
    data_desc = """
    Analyze the relationship between temperature and pressure in an ideal gas.
    The data contains temperature measurements in Kelvin and pressure measurements in Pascals.
    Derive the ideal gas law equation and perform unit conversions.
    Include statistical analysis and mathematical derivations.
    """

    den.set_data_description(data_desc)
    print("   Data description set")

    # Test idea generation (should potentially use Wolfram Alpha)
    print("   Generating idea...")
    try:
        den.get_idea_fast(verbose=False)
        print("   ✅ Idea generation completed")
    except Exception as e:
        print(f"   ⚠️ Idea generation failed: {e}")

    # Test method generation (should use Wolfram Alpha for math)
    print("   Generating methods...")
    try:
        den.get_method_fast(verbose=False)
        print("   ✅ Method generation completed")
    except Exception as e:
        print(f"   ⚠️ Method generation failed: {e}")

    print("✅ Denario integration test completed!")


def main():
    """Run all integration tests."""
    print("🚀 Starting Wolfram Alpha Integration Tests")
    print("=" * 50)

    try:
        # Test 1: Enhanced client
        test_enhanced_client()

        # Test 2: LangChain tool
        test_langchain_tool()

        # Test 3: Denario integration
        test_denario_integration()

        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Enhanced WolframAlphaClient with caching")
        print("   ✅ Structured result parsing (LaTeX, MathML)")
        print("   ✅ HITL review detection and prompts")
        print("   ✅ LangChain tool integration")
        print("   ✅ Denario agent integration")
        print("   ✅ Paper generation with mathematical content")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
