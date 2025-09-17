"""MATLAB installation verification script."""

import sys
import os
import subprocess
import shutil
from pathlib import Path


def check_matlab_installation():
    """Check if MATLAB is installed and accessible."""
    print("🔍 Checking MATLAB Installation...")

    # Check if matlab command is available
    matlab_exe = shutil.which('matlab')
    if matlab_exe:
        print(f"✅ MATLAB executable found: {matlab_exe}")

        # Get MATLAB version
        try:
            result = subprocess.run(['matlab', '-version'],
                                    capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ MATLAB version info:")
                print(f"   {result.stdout.strip()}")
            else:
                print(f"⚠️  MATLAB version check failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("⚠️  MATLAB version check timed out")
        except Exception as e:
            print(f"⚠️  Error checking MATLAB version: {e}")
    else:
        print("❌ MATLAB executable not found in PATH")
        return False

    return True


def check_matlab_root():
    """Check MATLAB_ROOT environment variable."""
    print("\n🔍 Checking MATLAB_ROOT Environment Variable...")

    matlab_root = os.environ.get('MATLAB_ROOT')
    if matlab_root:
        print(f"✅ MATLAB_ROOT set to: {matlab_root}")
        if os.path.exists(matlab_root):
            print(f"✅ MATLAB_ROOT path exists")
            return True
        else:
            print(f"❌ MATLAB_ROOT path does not exist: {matlab_root}")
            return False
    else:
        print("⚠️  MATLAB_ROOT environment variable not set")
        return False


def check_matlab_engine_api():
    """Check if MATLAB Engine API is available."""
    print("\n🔍 Checking MATLAB Engine API...")

    try:
        import matlab.engine
        print("✅ MATLAB Engine API module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ MATLAB Engine API not available: {e}")
        print("   To install: pip install matlabengine")
        return False


def test_matlab_engine_start():
    """Test starting MATLAB Engine."""
    print("\n🔍 Testing MATLAB Engine Start...")

    try:
        import matlab.engine
        print("   Starting MATLAB Engine...")
        eng = matlab.engine.start_matlab()
        print("✅ MATLAB Engine started successfully")

        # Test basic computation
        result = eng.sqrt(4.0)
        print(f"✅ Basic computation test: sqrt(4) = {result}")

        # Close engine
        eng.quit()
        print("✅ MATLAB Engine closed successfully")
        return True

    except Exception as e:
        print(f"❌ MATLAB Engine start failed: {e}")
        return False


def check_matlab_paths():
    """Check common MATLAB installation paths."""
    print("\n🔍 Checking Common MATLAB Installation Paths...")

    common_paths = [
        "/usr/local/MATLAB",
        "/opt/MATLAB",
        "/Applications/MATLAB_*.app",
        "/usr/local/bin/matlab",
        "/opt/bin/matlab"
    ]

    found_paths = []
    for pattern in common_paths:
        if '*' in pattern:
            import glob
            matches = glob.glob(pattern)
            found_paths.extend(matches)
        else:
            if os.path.exists(pattern):
                found_paths.append(pattern)

    if found_paths:
        print("✅ Found MATLAB installations:")
        for path in found_paths:
            print(f"   {path}")
        return True
    else:
        print("❌ No MATLAB installations found in common paths")
        return False


def test_denario_matlab_provider():
    """Test Denario MATLAB provider."""
    print("\n🔍 Testing Denario MATLAB Provider...")

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from denario.providers import MATLABProvider

        provider = MATLABProvider()
        print("✅ MATLABProvider created successfully")

        # Test basic computation
        result = provider.compute("solve x^2 + 2*x + 1 = 0")
        print(f"✅ MATLAB computation test: {result.plaintext}")
        print(f"   Provider: {result.provider}")
        print(f"   Execution time: {result.execution_time:.3f}s")

        return True

    except Exception as e:
        print(f"❌ Denario MATLAB provider test failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("MATLAB R2024a Installation Verification")
    print("=" * 50)

    checks = [
        ("MATLAB Installation", check_matlab_installation),
        ("MATLAB_ROOT Environment", check_matlab_root),
        ("MATLAB Engine API", check_matlab_engine_api),
        ("MATLAB Engine Start", test_matlab_engine_start),
        ("MATLAB Paths", check_matlab_paths),
        ("Denario MATLAB Provider", test_denario_matlab_provider)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check failed with exception: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:25} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! MATLAB integration is ready.")
    elif passed >= total - 1:
        print("⚠️  Most checks passed. MATLAB integration should work with minor issues.")
    else:
        print("❌ Multiple checks failed. Please review the setup guide.")
        print("   See: Denario/examples/matlab_setup_guide.md")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
