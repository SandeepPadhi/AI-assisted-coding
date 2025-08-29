#!/usr/bin/env python3
"""
Test runner for the Voting System.

This script provides comprehensive test execution with various options:
- Run all tests
- Run specific test categories
- Generate coverage reports
- Run tests in parallel
- Run with different verbosity levels

Usage:
    python tests/run_tests.py                    # Run all tests
    python tests/run_tests.py --unit            # Run only unit tests
    python tests/run_tests.py --integration     # Run only integration tests
    python tests/run_tests.py --coverage        # Run with coverage report
    python tests/run_tests.py --parallel        # Run tests in parallel
    python tests/run_tests.py --verbose         # Verbose output
    python tests/run_tests.py --entities        # Run only entity tests
    python tests/run_tests.py --repositories    # Run only repository tests
    python tests/run_tests.py --managers        # Run only manager tests
    python tests/run_tests.py --slow            # Include slow tests
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Voting System Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--functional", action="store_true", help="Run only functional tests")
    parser.add_argument("--entities", action="store_true", help="Run only entity tests")
    parser.add_argument("--repositories", action="store_true", help="Run only repository tests")
    parser.add_argument("--managers", action="store_true", help="Run only manager tests")
    parser.add_argument("--orchestrator", action="store_true", help="Run only orchestrator tests")
    parser.add_argument("--design-patterns", action="store_true", help="Run only design pattern tests")
    parser.add_argument("--concurrency", action="store_true", help="Run only concurrency tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--slow", action="store_true", help="Include slow tests")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument("--test", help="Run specific test file or class")

    args = parser.parse_args()

    # Add the project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]

    # Add test directory
    if args.test:
        cmd.append(args.test)
    else:
        cmd.append("tests/")

    # Add markers and filters
    markers = []

    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.functional:
        markers.append("functional")
    if args.entities:
        markers.append("entities")
    if args.repositories:
        markers.append("repositories")
    if args.managers:
        markers.append("managers")
    if args.orchestrator:
        markers.append("orchestrator")
    if args.design_patterns:
        markers.append("design_patterns")
    if args.concurrency:
        markers.append("concurrency")

    if not args.slow:
        markers.append("not slow")

    if markers:
        cmd.extend(["-m", " and ".join(markers)])

    # Add coverage options
    if args.coverage:
        cmd.extend([
            "--cov=voting_system",
            "--cov-report=term-missing",
            "--cov-report=html:tests/coverage_html" if args.html else "--cov-report=html",
            "--cov-fail-under=80"
        ])

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", "auto"])

    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add fail-fast
    if args.fail_fast:
        cmd.append("--tb=short")
        cmd.append("-x")

    # Add other useful options
    cmd.extend([
        "--strict-markers",
        "--disable-warnings",
        "--tb=short",
        "-ra"
    ])

    print("=" * 60)
    print("🧪 VOTING SYSTEM TEST SUITE")
    print("=" * 60)
    print(f"Command: {' '.join(cmd)}")
    print()

    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=project_root)
        exit_code = result.returncode

        print("\n" + "=" * 60)
        if exit_code == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED!")
        print("=" * 60)

        return exit_code

    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
