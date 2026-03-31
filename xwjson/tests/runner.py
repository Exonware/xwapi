#exonware/xwjson/tests/runner.py
"""
Main test runner for xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 2025-01-XX
Orchestrates all test layers following GUIDE_TEST.md 4-layer structure.
"""

import sys
import subprocess
from pathlib import Path
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console (GUIDE_TEST.md compliance)
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with default encoding


def run_tests():
    """Run all xwjson tests."""
    test_dir = Path(__file__).parent
    # Run tests in order: core -> unit -> integration -> advance
    layers = [
        ("0.core", "Core tests (20% for 80% value)"),
        ("1.unit", "Unit tests (component tests)"),
        ("2.integration", "Integration tests (scenario tests)"),
        ("3.advance", "Advance tests (production excellence)"),
    ]
    results = {}
    for layer_dir, description in layers:
        layer_path = test_dir / layer_dir
        if not layer_path.exists():
            print(f"⚠️  Layer {layer_dir} not found, skipping...")
            continue
        print(f"\n{'='*60}")
        print(f"Running {description} ({layer_dir})")
        print(f"{'='*60}")
        # Run pytest for this layer
        # ⚠️ CRITICAL: Following GUIDE_TEST.md - no forbidden flags
        # ❌ FORBIDDEN: --disable-warnings (hides real problems)
        # ✅ ALLOWED: -v, --tb=short, --strict-markers, -x (stop on first failure)
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                str(layer_path),
                "-v",
                "--tb=short",
                "--strict-markers",
                "-x",  # Stop on first failure (fast feedback)
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        results[layer_dir] = {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if result.returncode == 0:
            print(f"✅ {description} passed")
        else:
            print(f"❌ {description} failed")
    # Summary
    print(f"\n{'='*60}")
    print("Test Summary")
    print(f"{'='*60}")
    all_passed = True
    for layer_dir, result in results.items():
        status = "✅ PASSED" if result["returncode"] == 0 else "❌ FAILED"
        print(f"{layer_dir}: {status}")
        if result["returncode"] != 0:
            all_passed = False
    return 0 if all_passed else 1
if __name__ == "__main__":
    sys.exit(run_tests())
