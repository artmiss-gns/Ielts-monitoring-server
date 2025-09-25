#!/usr/bin/env python3
"""Test the fixed URL construction logic against sample URLs."""

import sys
import os
sys.path.append('/Users/artmissg/Documents/Projects/Ielts-monitoring2/src')

from urllib.parse import parse_qs, urlparse, unquote_plus
from ielts_monitor.scraper.client import IELTSClient
from ielts_monitor.config import default_config


class TestURLConstruction:
    """Test class for URL construction logic."""

    def __init__(self):
        """Initialize with default config."""
        self.client = IELTSClient(default_config)

    def test_sample_urls(self):
        """Test URL construction against the provided sample URLs."""
        print("Testing URL Construction Against Sample URLs")
        print("=" * 50)

        # Sample URLs from the user
        sample_urls = [
            "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=01",
            "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&city%5B%5D=shiraz&model%5B%5D=cdielts&month%5B%5D=01",
            "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=life+skills&model%5B%5D=cdielts&month%5B%5D=01",
            "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=09",
            "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=06"
        ]

        # Test cases - each test case should produce one of the sample URLs
        test_cases = [
            {
                "name": "Single city, single model, single month",
                "cities": ["isfahan"],
                "models": ["cdielts"],
                "months": ["01"]
            },
            {
                "name": "Multiple cities, single model, single month",
                "cities": ["isfahan", "shiraz"],
                "models": ["cdielts"],
                "months": ["01"]
            },
            {
                "name": "Single city, multiple models, single month",
                "cities": ["isfahan"],
                "models": ["life+skills", "cdielts"],
                "months": ["01"]
            },
            {
                "name": "Single city, single model, single month (09)",
                "cities": ["isfahan"],
                "models": ["cdielts"],
                "months": ["09"]
            },
            {
                "name": "Single city, single model, single month (06)",
                "cities": ["isfahan"],
                "models": ["cdielts"],
                "months": ["06"]
            }
        ]

        all_passed = True

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['name']}")

            # Generate URL using our fixed logic
            generated_url = self.client._construct_url(
                test_case["cities"],
                test_case["models"],
                test_case["months"] if test_case["months"] else None
            )

            # Find the corresponding sample URL
            sample_url = sample_urls[i-1]

            print(f"Generated: {generated_url}")
            print(f"Expected:  {sample_url}")

            # Compare the URLs
            if generated_url == sample_url:
                print("✅ PASS")
            else:
                print("❌ FAIL")
                all_passed = False

                # Show detailed comparison
                self._compare_urls(generated_url, sample_url)

        return all_passed

    def _compare_urls(self, generated: str, expected: str):
        """Compare two URLs and show differences."""
        gen_parsed = urlparse(generated)
        exp_parsed = urlparse(expected)

        print("  Detailed comparison:")

        if gen_parsed.scheme != exp_parsed.scheme:
            print(f"    Scheme: {gen_parsed.scheme} != {exp_parsed.scheme}")
        if gen_parsed.netloc != exp_parsed.netloc:
            print(f"    Netloc: {gen_parsed.netloc} != {exp_parsed.netloc}")
        if gen_parsed.path != exp_parsed.path:
            print(f"    Path: {gen_parsed.path} != {exp_parsed.path}")

        gen_params = parse_qs(gen_parsed.query)
        exp_params = parse_qs(exp_parsed.query)

        if gen_params != exp_params:
            print(f"    Query params differ:")
            print(f"      Generated: {gen_params}")
            print(f"      Expected:  {exp_params}")

    def test_multiple_months(self):
        """Test URL construction with multiple months."""
        print("\nTesting Multiple Months")
        print("=" * 30)

        # Test multiple months
        cities = ["isfahan"]
        models = ["cdielts"]
        months = ["09", "06"]

        generated_url = self.client._construct_url(cities, models, months)
        print(f"Generated URL: {generated_url}")

        parsed = urlparse(generated_url)
        params = parse_qs(parsed.query)

        expected_months = ["09", "06"]
        actual_months = params.get('month[]', [])

        if set(actual_months) == set(expected_months):
            print("✅ PASS: Multiple months handled correctly")
        else:
            print(f"❌ FAIL: Expected {expected_months}, got {actual_months}")

    def test_url_encoding(self):
        """Test that URL encoding is correct."""
        print("\nTesting URL Encoding")
        print("=" * 25)

        cities = ["isfahan"]
        models = ["cdielts"]
        months = ["01"]

        generated_url = self.client._construct_url(cities, models, months)

        # Check that brackets are properly encoded
        if "city%5B%5D" in generated_url:
            print("✅ PASS: Brackets are properly URL encoded")
        else:
            print("❌ FAIL: Brackets are not properly URL encoded")

        # Check that spaces in model names are handled
        models_with_space = ["life+skills"]
        generated_url_space = self.client._construct_url(cities, models_with_space, months)

        if "life+skills" in generated_url_space:
            print("✅ PASS: Spaces in model names are handled correctly")
        else:
            print("❌ FAIL: Spaces in model names are not handled correctly")


def main():
    """Run all tests."""
    tester = TestURLConstruction()

    print("URL Construction Test Suite")
    print("=" * 40)

    # Run tests
    sample_test_passed = tester.test_sample_urls()
    tester.test_multiple_months()
    tester.test_url_encoding()

    print("\n" + "=" * 40)
    if sample_test_passed:
        print("🎉 All sample URL tests PASSED!")
        print("The URL construction logic has been successfully fixed.")
    else:
        print("❌ Some tests FAILED.")
        print("The URL construction logic still needs work.")

    return 0 if sample_test_passed else 1


if __name__ == "__main__":
    sys.exit(main())
