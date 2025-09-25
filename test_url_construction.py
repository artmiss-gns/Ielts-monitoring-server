#!/usr/bin/env python3
"""Test cases for URL construction logic."""

import pytest
from urllib.parse import parse_qs, urlparse, unquote_plus


def test_single_city_single_model_single_month():
    """Test URL construction for single city, single model, single month."""
    # Expected URL format from sample
    expected = "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=01"

    # Parse the expected URL to understand structure
    parsed = urlparse(expected)
    params = parse_qs(parsed.query)

    print("Single city, model, month test:")
    print(f"URL: {expected}")
    print(f"Parameters: {params}")
    print()


def test_multiple_cities_single_model_single_month():
    """Test URL construction for multiple cities, single model, single month."""
    expected = "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&city%5B%5D=shiraz&model%5B%5D=cdielts&month%5B%5D=01"

    parsed = urlparse(expected)
    params = parse_qs(parsed.query)

    print("Multiple cities, single model, single month test:")
    print(f"URL: {expected}")
    print(f"Parameters: {params}")
    print()


def test_single_city_multiple_models_single_month():
    """Test URL construction for single city, multiple models, single month."""
    expected = "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=life+skills&model%5B%5D=cdielts&month%5B%5D=01"

    parsed = urlparse(expected)
    params = parse_qs(parsed.query)

    print("Single city, multiple models, single month test:")
    print(f"URL: {expected}")
    print(f"Parameters: {params}")
    print()


def test_single_city_single_model_multiple_months():
    """Test URL construction for single city, single model, multiple months."""
    # This scenario isn't in the samples, but let's test the pattern
    expected = "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=09&month%5B%5D=06"

    parsed = urlparse(expected)
    params = parse_qs(parsed.query)

    print("Single city, single model, multiple months test:")
    print(f"URL: {expected}")
    print(f"Parameters: {params}")
    print()


def test_url_encoding_analysis():
    """Analyze URL encoding patterns in the sample URLs."""
    samples = [
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=01",
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&city%5B%5D=shiraz&model%5B%5D=cdielts&month%5B%5D=01",
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=life+skills&model%5B%5D=cdielts&month%5B%5D=01",
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=09",
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=06"
    ]

    print("URL Encoding Analysis:")
    print("=" * 50)

    for i, url in enumerate(samples, 1):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        print(f"\nSample {i}:")
        print(f"URL: {url}")
        print(f"Path: {parsed.path}")
        print("Parameters:")
        for key, values in params.items():
            decoded_key = unquote_plus(key)
            decoded_values = [unquote_plus(v) for v in values]
            print(f"  {decoded_key}: {decoded_values}")


def test_current_implementation_vs_expected():
    """Compare current implementation with expected URLs."""
    print("\nCurrent vs Expected URL Analysis:")
    print("=" * 50)

    # Current implementation (from the code)
    current_base = "https://irsafam.org/timetable"
    current_examples = [
        f"{current_base}/isfahan/cdielts",
        f"{current_base}/isfahan/cdielts/01",
        f"{current_base}/tehran/cdielts/01"
    ]

    # Expected URLs (from samples)
    expected_examples = [
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=cdielts&month%5B%5D=01",
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&city%5B%5D=shiraz&model%5B%5D=cdielts&month%5B%5D=01",
        "https://irsafam.org/ielts/timetable?city%5B%5D=isfahan&model%5B%5D=life+skills&model%5B%5D=cdielts&month%5B%5D=01"
    ]

    print("\nCurrent Implementation URLs:")
    for url in current_examples:
        print(f"  {url}")

    print("\nExpected URLs:")
    for url in expected_examples:
        print(f"  {url}")

    print("\nKey Differences:")
    print("1. Base URL: /timetable vs /ielts/timetable")
    print("2. Path parameters vs Query parameters")
    print("3. No URL encoding in current implementation")
    print("4. No support for multiple values in current implementation")


if __name__ == "__main__":
    test_single_city_single_model_single_month()
    test_multiple_cities_single_model_single_month()
    test_single_city_multiple_models_single_month()
    test_single_city_single_model_multiple_months()
    test_url_encoding_analysis()
    test_current_implementation_vs_expected()
