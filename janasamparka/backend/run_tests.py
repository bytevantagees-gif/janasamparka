#!/usr/bin/env python3
"""
Test runner script for Janasamparka
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print("Output:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print("Error:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Janasamparka tests")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "all"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--coverage", action="store_true", 
                       help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, default=1,
                       help="Number of parallel processes")
    parser.add_argument("--failfast", "-x", action="store_true",
                       help="Stop on first failure")
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test type selection
    if args.type == "unit":
        cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        cmd.extend(["-m", "integration"])
    elif args.type == "e2e":
        cmd.extend(["-m", "e2e"])
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term"])
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add parallel execution
    if args.parallel > 1:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add failfast
    if args.failfast:
        cmd.append("-x")
    
    # Run tests
    success = run_command(cmd, f"Running {args.type} tests")
    
    if success:
        print("\n🎉 All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("  - HTML: htmlcov/index.html")
            print("  - Terminal: See above")
        
        # Show test summary
        summary_cmd = ["python", "-m", "pytest", "--tb=no", "-q"]
        if args.type != "all":
            summary_cmd.extend(["-m", args.type])
        
        run_command(summary_cmd, "Test summary")
        
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
