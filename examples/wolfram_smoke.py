"""Minimal smoke test for Wolfram Alpha adapter.

Usage (ensure conda env 'cmbagent' active):
    python -m Denario.examples.wolfram_smoke
"""
from denario.utils import WolframAlphaClient
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path so we can import denario
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
# Try to find .env file in common locations
env_paths = [
    Path(__file__).parent.parent.parent / "DenarioApp" / ".env",
    Path(__file__).parent.parent / ".env",
    Path.cwd() / ".env"
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break


def main():
    try:
        client = WolframAlphaClient()
        print("✅ Wolfram Alpha client initialized successfully")

        # Test query: integral of exp(-x^2) from -infinity to infinity
        print("🔍 Testing query: integrate exp(-x^2) from -infinity to infinity")
        result = client.query("integrate exp(-x^2) from -infinity to infinity")

        # Extract primary text
        text = WolframAlphaClient.extract_primary_text(result)
        print(f"📊 Primary result: {text[:200] if text else '<none>'}...")

        # Check if query was successful
        if result.get("queryresult", {}).get("success"):
            print("✅ Query successful!")
        else:
            print("❌ Query failed")
            print(
                f"Error: {
                    result.get(
                        'queryresult',
                        {}).get(
                        'error',
                        'Unknown error')}")

        # Test another query: unit conversion
        print("\n🔍 Testing query: convert 1 meter to feet")
        result2 = client.query("convert 1 meter to feet")
        text2 = WolframAlphaClient.extract_primary_text(result2)
        print(f"📊 Primary result: {text2[:200] if text2 else '<none>'}...")

        if result2.get("queryresult", {}).get("success"):
            print("✅ Unit conversion successful!")
        else:
            print("❌ Unit conversion failed")

        print("\n🎉 Wolfram Alpha integration test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
