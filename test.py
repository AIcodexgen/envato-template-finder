#!/usr/bin/env python3
"""
Test script for Envato Template Finder
Run this to verify all components are working correctly.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyzer import ReferenceAnalyzer
from scraper import EnvatoScraper
from ai_matcher import GeminiMatcher

async def test_analyzer():
    """Test the website analyzer"""
    print("\n🧪 Testing Website Analyzer...")
    print("-" * 50)

    analyzer = ReferenceAnalyzer()

    # Test with a known website
    test_url = "https://wordpress.org"

    try:
        result = await analyzer.analyze_website(test_url)

        print(f"✅ Analysis completed for {test_url}")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Detected CMS: {result.get('detected_cms', 'None')}")
        print(f"   Industry: {result.get('industry', 'Unknown')}")
        print(f"   Keywords: {', '.join(result.get('keywords', [])[:3])}")
        print(f"   Colors: {', '.join(result.get('color_palette', [])[:3])}")

        # Verify WordPress detection
        if result.get('detected_cms') == 'WordPress':
            print("   ✅ CMS detection working correctly")
        else:
            print("   ⚠️  CMS detection may need adjustment")

        return True

    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False

async def test_scraper():
    """Test the Envato scraper"""
    print("\n🧪 Testing Envato Scraper...")
    print("-" * 50)

    scraper = EnvatoScraper()

    try:
        # Test search with filters
        templates = await scraper.search_templates(
            industry="Corporate",
            cms="WordPress",
            max_results=5
        )

        print(f"✅ Scraping completed")
        print(f"   Found {len(templates)} templates")

        if templates:
            print(f"\n   Sample template:")
            print(f"   - Title: {templates[0].get('title', 'N/A')}")
            print(f"   - ID: {templates[0].get('id', 'N/A')}")
            print(f"   - Tags: {', '.join(templates[0].get('tags', [])[:3])}")
            return True
        else:
            print("   ⚠️  No templates found (Envato may be blocking)")
            return False

    except Exception as e:
        print(f"❌ Scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ai_matcher():
    """Test the AI matcher"""
    print("\n🧪 Testing AI Matcher...")
    print("-" * 50)

    matcher = GeminiMatcher()

    # Mock data
    reference = {
        "url": "https://example.com",
        "title": "Example SaaS Site",
        "industry": "SaaS/Technology",
        "detected_cms": "WordPress",
        "color_palette": ["#2563eb", "#ffffff"],
        "layout_features": {
            "has_hero": True,
            "has_pricing": True
        },
        "keywords": ["software", "cloud", "solution"]
    }

    templates = [
        {
            "id": "test-1",
            "title": "Tech Startup Pro",
            "url": "https://elements.envato.com/test-1",
            "preview_image": "",
            "tags": ["wordpress", "saas", "technology"],
            "description": "Perfect for tech startups"
        },
        {
            "id": "test-2",
            "title": "Corporate Business",
            "url": "https://elements.envato.com/test-2",
            "preview_image": "",
            "tags": ["wordpress", "corporate"],
            "description": "General business template"
        }
    ]

    try:
        matches = await matcher.find_similar_templates(reference, templates, top_n=2)

        print(f"✅ Matching completed")
        print(f"   Returned {len(matches)} matches")

        if matches:
            print(f"\n   Top match:")
            print(f"   - Title: {matches[0].get('title')}")
            print(f"   - Score: {matches[0].get('similarity_score')}%")
            print(f"   - Confidence: {matches[0].get('confidence')}")

            if matcher.enabled:
                print("   ✅ AI matching is active")
            else:
                print("   ℹ️  Using fallback matching (no API key)")

        return True

    except Exception as e:
        print(f"❌ AI matcher test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment setup"""
    print("\n🧪 Testing Environment...")
    print("-" * 50)

    checks = []

    # Check Python version
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        checks.append(True)
    else:
        print(f"❌ Python {version.major}.{version.minor} (requires 3.8+)")
        checks.append(False)

    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")

        # Check for API key
        with open('.env', 'r') as f:
            content = f.read()
            if 'GOOGLE_API_KEY' in content and 'your_' not in content:
                print("✅ Google API key configured")
                checks.append(True)
            else:
                print("⚠️  Google API key not configured (optional)")
                checks.append(True)
    else:
        print("⚠️  .env file not found (will use defaults)")
        checks.append(True)

    # Check required files
    required_files = ['main.py', 'scraper.py', 'analyzer.py', 'ai_matcher.py', 'requirements.txt']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
            checks.append(True)
        else:
            print(f"❌ {file} missing")
            checks.append(False)

    return all(checks)

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Envato Template Finder - Test Suite")
    print("=" * 60)

    # Environment tests
    env_ok = test_environment()

    if not env_ok:
        print("\n❌ Environment checks failed. Please fix the issues above.")
        return

    # Component tests
    results = []

    # Test analyzer
    results.append(("Analyzer", await test_analyzer()))

    # Test scraper
    results.append(("Scraper", await test_scraper()))

    # Test AI matcher
    results.append(("AI Matcher", await test_ai_matcher()))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:.<30} {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 All tests passed! The application is ready to use.")
        print("   Run: python main.py")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   Note: Scraper tests may fail due to network restrictions.")

if __name__ == "__main__":
    asyncio.run(main())
