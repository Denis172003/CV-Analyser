#!/usr/bin/env python3
"""
Test runner for AI Resume Analyzer.

Runs all test suites with proper reporting and error handling.
"""

import sys
import os
import subprocess
import time
from pathlib import Path


def run_test_suite(test_file, description):
    """Run a specific test suite and return results."""
    print(f"🧪 Running {description}...")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} PASSED ({duration:.1f}s)")
            return True, result.stdout
        else:
            print(f"❌ {description} FAILED ({duration:.1f}s)")
            print("STDOUT:", result.stdout[-500:] if result.stdout else "None")
            print("STDERR:", result.stderr[-500:] if result.stderr else "None")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} TIMED OUT (5 minutes)")
        return False, "Test timed out"
    except Exception as e:
        print(f"💥 {description} ERROR: {str(e)}")
        return False, str(e)


def main():
    """Run all test suites."""
    print("🚀 AI RESUME ANALYZER - TEST RUNNER")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Please run this script from the AI Resume Analyzer root directory")
        sys.exit(1)
    
    # Test suites to run
    test_suites = [
        ("test_parsing.py", "Text Extraction Tests"),
        ("test_ai_integration.py", "AI Integration Tests"),
        ("test_tts_video.py", "Video Generation Tests"),
        ("test_new_integrations.py", "Database & Gemini Tests"),
        ("test_integration.py", "Integration Tests"),
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_file, description in test_suites:
        if os.path.exists(test_file):
            success, output = run_test_suite(test_file, description)
            results.append((description, success, output))
        else:
            print(f"⚠️  {test_file} not found, skipping {description}")
            results.append((description, False, f"{test_file} not found"))
        
        print()
    
    # Summary
    total_duration = time.time() - total_start_time
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print("=" * 60)
    print(f"📊 TEST SUMMARY")
    print(f"Total Duration: {total_duration:.1f} seconds")
    print(f"Test Suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print()
    
    if passed == total:
        print("🎉 ALL TEST SUITES PASSED!")
        print("Your AI Resume Analyzer is ready for deployment!")
    else:
        print("⚠️  Some test suites failed:")
        for description, success, output in results:
            if not success:
                print(f"   • {description}")
        print()
        print("Please review the failed tests and fix any issues.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)