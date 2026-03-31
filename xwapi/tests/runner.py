#!/usr/bin/env python3
"""
#exonware/xwapi/tests/runner.py
Main test runner for xwapi.
Coordinates all test layers and records a single Markdown summary under docs/tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 18-Dec-2025
Usage:
 python tests/runner.py # Run all tests
 python tests/runner.py --core # Run only core tests
 python tests/runner.py --unit # Run only unit tests
 python tests/runner.py --integration # Run only integration tests
 python tests/runner.py --advance # Run only advance tests (v1.0.0+)
 python tests/runner.py --security # Run only security tests
 python tests/runner.py --performance # Run only performance tests
Output:
 - Terminal: Colored, formatted output
 - File: docs/tests/TEST_<timestamp>_SUMMARY.md (Markdown-friendly format)
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def _find_monorepo_root(start: Path) -> Path:
    """Find the monorepo root (folder that contains xwapi + xwsystem)."""
    for p in [start] + list(start.parents):
        if (p / "xwapi").is_dir() and (p / "xwsystem").is_dir():
            return p
    return start.parent.parent.parent


def _add_monorepo_src_paths() -> None:
    """Add all required sibling package src/ folders to sys.path for monorepo testing."""
    test_dir = Path(__file__).parent
    monorepo_root = _find_monorepo_root(test_dir.resolve())
    for pkg in (
        "xwapi",
        "xwsystem",
        "xwentity",
        "xwauth",
        "xwstorage",
        "xwaction",
        "xwschema",
        "xwdata",
        "xwnode",
        "xwquery",
        "xwjson",
        "xwsyntax",
    ):
        src = monorepo_root / pkg / "src"
        if src.is_dir():
            sys.path.insert(0, str(src))
# Add src to path before importing xwsystem
_add_monorepo_src_paths()
# ⚠️ CRITICAL: Configure UTF-8 encoding for Windows console using xwsystem utility (GUIDE_TEST.md)
from exonware.xwsystem.console.cli import ensure_utf8_console
ensure_utf8_console()


class DualOutput:
    """Capture output for both terminal and Markdown file."""

    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.terminal_lines = []
        self.markdown_lines = []

    def print(self, text: str, markdown_format: str = None):
        """Print to terminal and capture for Markdown."""
        # Terminal output
        print(text)
        self.terminal_lines.append(text)
        # Markdown output (use markdown_format if provided, else clean terminal output)
        if markdown_format:
            self.markdown_lines.append(markdown_format)
        else:
            # Clean emoji and special chars for Markdown
            cleaned = text.replace("="*80, "---")
            self.markdown_lines.append(cleaned)

    def save(self):
        """Save Markdown output to file."""
        now = datetime.now()
        header = f"""# Test Runner Output
**Library:** xwapi
**Generated:** {now.strftime("%d-%b-%Y %H:%M:%S")}.{now.microsecond // 1000:03d}
**Runner:** Main Orchestrator
---
"""
        content = header + "\n".join(self.markdown_lines) + "\n"
        self.output_file.write_text(content, encoding='utf-8')


def format_path(path: Path) -> str:
    """Format path to show full absolute path."""
    return str(path.resolve())


def run_sub_runner(runner_path: Path, description: str, output: DualOutput) -> int:
    """Run a sub-runner and return exit code."""
    separator = "="*80
    output.print(f"\n{separator}", f"\n## {description}\n")
    output.print(f"🚀 {description}", f"**Status:** Running...")
    output.print(f"{separator}\n", "")
    result = subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=runner_path.parent,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    # Print sub-runner output
    if result.stdout:
        output.print(result.stdout, f"```\n{result.stdout}\n```")
    if result.stderr:
        output.print(result.stderr, f"**Errors:**\n```\n{result.stderr}\n```")
    # Status
    status = "✅ PASSED" if result.returncode == 0 else "❌ FAILED"
    output.print(f"\n{status}", f"\n**Result:** {status}")
    return result.returncode


def main():
    """Main test runner function following GUIDE_TEST.md."""
    # Setup output logger
    test_dir = Path(__file__).parent
    reports_dir = test_dir.parent / "docs" / "tests"
    reports_dir.mkdir(parents=True, exist_ok=True)
    from exonware.xwsystem.utils.test_runner import timestamp_for_filename
    timestamp = timestamp_for_filename()
    output_file = reports_dir / f"TEST_{timestamp}_SUMMARY.md"
    output = DualOutput(output_file)
    # Add src to Python path for testing
    src_path = test_dir.parent / "src"
    sys.path.insert(0, str(src_path))
    # Header
    header = "="*80
    output.print(header, "# Test Execution Report")
    output.print("xwapi Test Runner",
            f"**Library:** xwapi \n**Type:** Main Orchestrator - Hierarchical Test Execution")
    output.print("Main Orchestrator - Hierarchical Test Execution", "")
    output.print(header, "---")
    # Parse arguments
    args = sys.argv[1:]
    # Define sub-runners (GUIDE_TEST.md hierarchy)
    core_runner = test_dir / "0.core" / "runner.py"
    unit_runner = test_dir / "1.unit" / "runner.py"
    integration_runner = test_dir / "2.integration" / "runner.py"
    advance_runner = test_dir / "3.advance" / "runner.py"
    exit_codes = []
    # Determine which tests to run
    if "--core" in args:
        if core_runner.exists():
            exit_codes.append(run_sub_runner(core_runner, "Core Tests", output))
    elif "--unit" in args:
        if unit_runner.exists():
            exit_codes.append(run_sub_runner(unit_runner, "Unit Tests", output))
    elif "--integration" in args:
        if integration_runner.exists():
            exit_codes.append(run_sub_runner(integration_runner, "Integration Tests", output))
    elif "--advance" in args:
        if advance_runner.exists():
            exit_codes.append(run_sub_runner(advance_runner, "Advance Tests", output))
        else:
            msg = "\n⚠️ Advance tests not available (requires v1.0.0)"
            output.print(msg, f"\n> {msg}")
    elif any(m in args for m in ("--security", "--performance", "--usability", "--maintainability", "--extensibility")):
        if advance_runner.exists():
            result = subprocess.run(
                [sys.executable, str(advance_runner)] + args,
                cwd=advance_runner.parent,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.stdout:
                output.print(result.stdout, f"```\n{result.stdout}\n```")
            if result.stderr:
                output.print(result.stderr, f"**Errors:**\n```\n{result.stderr}\n```")
            exit_codes.append(result.returncode)
        else:
            msg = "\n⚠️ Advance tests not available (requires v1.0.0)"
            output.print(msg, f"\n> {msg}")
    else:
        # Run all tests in sequence (GUIDE_TEST.md: 0.core, 1.unit, 2.integration, 3.advance)
        advance_tag = " ✅ 3.advance" if advance_runner.exists() else ""
        msg_header = "\n🚀 Running: ALL Tests"
        msg_layers = f" Layers: 0.core ✅ 1.unit ✅ 2.integration{advance_tag}"
        output.print(msg_header, "\n## Running All Test Layers")
        output.print(msg_layers, f"\n**Execution Order:** 0.core ✅ 1.unit ✅ 2.integration{advance_tag}\n")
        output.print("", "")
        if core_runner.exists():
            exit_codes.append(run_sub_runner(core_runner, "Layer 0: Core Tests", output))
        if unit_runner.exists():
            exit_codes.append(run_sub_runner(unit_runner, "Layer 1: Unit Tests", output))
        if integration_runner.exists():
            exit_codes.append(run_sub_runner(integration_runner, "Layer 2: Integration Tests", output))
        if advance_runner.exists():
            exit_codes.append(run_sub_runner(advance_runner, "Layer 3: Advance Tests", output))
    # Print summary
    summary_header = f"\n{'='*80}"
    output.print(summary_header, f"\n---\n\n## 📈 Test Execution Summary")
    output.print("📈 TEST EXECUTION SUMMARY", "")
    output.print(f"{'='*80}", "")
    total_runs = len(exit_codes)
    passed = sum(1 for code in exit_codes if code == 0)
    failed = total_runs - passed
    output.print(f"Total Layers: {total_runs}", f"- **Total Layers:** {total_runs}")
    output.print(f"Passed: {passed}", f"- **Passed:** {passed}")
    output.print(f"Failed: {failed}", f"- **Failed:** {failed}")
    # Final status
    if all(code == 0 for code in exit_codes):
        final_msg = "\n✅ ALL TESTS PASSED!"
        output.print(final_msg, f"\n### {final_msg}")
        # Save output
        output.save()
        print(f"\n💾 Test results saved to: {format_path(output_file)}")
        sys.exit(0)
    else:
        final_msg = "\n❌ SOME TESTS FAILED!"
        output.print(final_msg, f"\n### {final_msg}")
        # Save output
        output.save()
        print(f"\n💾 Test results saved to: {format_path(output_file)}")
        sys.exit(1)
if __name__ == "__main__":
    main()
