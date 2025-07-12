#!/usr/bin/env python3
"""
Test script for AI Product Intelligence Tool - Phase 3
Tests analysis, matching, and live price aggregation functionality
"""

import asyncio
import time
from backend.ai_services import AIProductProcessor
from backend.google_shopping_service import GoogleShoppingService
from backend.product_database import product_db
from config import Config

# Test data
TEST_TEXT = "Outdoor string lights with 50 LED bulbs, waterproof, warm white light"
TEST_PRODUCT_DESCRIPTION = "Smart ceiling fan with remote control and LED lighting"
TEST_PRICE_SEARCH = "Edison bulb string lights outdoor"

async def test_text_analysis():
    """Test text-based product analysis"""
    print("🔍 Testing text-based analysis...")
    
    try:
        processor = AIProductProcessor(Config.OPENAI_API_KEY)
        features = await processor.extract_features_from_text(TEST_TEXT)
        
        print(f"✅ Text analysis successful!")
        print(f"   Product type: {features.product_type}")
        print(f"   Category: {features.category}")
        print(f"   Key features: {features.key_features}")
        return True
    except Exception as e:
        print(f"❌ Text analysis failed: {e}")
        return False

async def test_product_matching():
    """Test product matching functionality"""
    print("\n🔍 Testing product matching...")
    
    try:
        processor = AIProductProcessor(Config.OPENAI_API_KEY)
        
        # First extract features
        features = await processor.extract_features_from_text(TEST_PRODUCT_DESCRIPTION)
        
        # Find similar products
        matches = await processor.find_similar_products(
            input_features=features,
            max_results=5
        )
        
        print(f"✅ Product matching successful!")
        print(f"   Found {len(matches)} similar products")
        
        if matches:
            print(f"   Top match: {matches[0].name}")
            print(f"   Similarity score: {matches[0].similarity_score:.2f}")
            print(f"   Combined score: {matches[0].combined_score:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Product matching failed: {e}")
        return False

async def test_google_shopping_service():
    """Test Google Shopping service functionality"""
    print("\n🛍️ Testing Google Shopping service...")
    
    try:
        shopping_service = GoogleShoppingService(Config.GOOGLE_SHOPPING_API_KEY)
        processor = AIProductProcessor(Config.OPENAI_API_KEY)
        
        # Extract features for search
        features = await processor.extract_features_from_text(TEST_PRICE_SEARCH)
        
        # Test search query generation
        search_query = shopping_service.create_search_query(features)
        print(f"   Generated search query: '{search_query}'")
        
        # Test live product search
        live_products = await shopping_service.search_products(features, max_results=3)
        
        print(f"✅ Google Shopping search successful!")
        print(f"   Found {len(live_products)} live products")
        
        if live_products:
            print(f"   Top result: {live_products[0]['title'][:50]}...")
            if live_products[0]['price']:
                print(f"   Price: ${live_products[0]['price']:.2f}")
            print(f"   Match score: {live_products[0]['match_score']:.2f}")
            print(f"   Source: {live_products[0]['source']}")
        
        return True
    except Exception as e:
        print(f"❌ Google Shopping test failed: {e}")
        return False

async def test_price_comparison():
    """Test comprehensive price comparison functionality"""
    print("\n💰 Testing price comparison...")
    
    try:
        shopping_service = GoogleShoppingService(Config.GOOGLE_SHOPPING_API_KEY)
        processor = AIProductProcessor(Config.OPENAI_API_KEY)
        
        # Extract features
        features = await processor.extract_features_from_text(TEST_PRICE_SEARCH)
        
        # Get price comparison
        price_data = await shopping_service.get_price_comparison(features)
        
        print(f"✅ Price comparison successful!")
        print(f"   Total products found: {price_data['total_found']}")
        print(f"   Search query used: '{price_data['search_query']}'")
        
        if price_data['price_stats']:
            stats = price_data['price_stats']
            print(f"   Price range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
            print(f"   Average price: ${stats['avg_price']:.2f}")
            print(f"   Median price: ${stats['median_price']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Price comparison test failed: {e}")
        return False

def test_product_database():
    """Test product database functionality"""
    print("\n🔍 Testing product database...")
    
    try:
        # Get all products
        all_products = product_db.get_all_products()
        print(f"✅ Database loaded: {len(all_products)} products")
        
        # Test category filtering
        lighting_products = product_db.get_products_by_category("lighting")
        fan_products = product_db.get_products_by_category("fans")
        
        print(f"   Lighting products: {len(lighting_products)}")
        print(f"   Fan products: {len(fan_products)}")
        
        # Test search
        search_results = product_db.search_products("LED")
        print(f"   LED search results: {len(search_results)}")
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    try:
        import requests
        
        # Test health endpoint
        health_response = requests.get("http://localhost:8000/api/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ Health endpoint working")
            print(f"   Services status: {health_data.get('services', {})}")
        else:
            print("❌ Health endpoint failed")
            return False
        
        # Test products endpoint
        products_response = requests.get("http://localhost:8000/api/products")
        if products_response.status_code == 200:
            data = products_response.json()
            print(f"✅ Products endpoint working: {data['total']} products")
        else:
            print("❌ Products endpoint failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

async def test_combined_search():
    """Test combined search functionality (local + live)"""
    print("\n🔄 Testing combined search...")
    
    try:
        processor = AIProductProcessor(Config.OPENAI_API_KEY)
        shopping_service = GoogleShoppingService(Config.GOOGLE_SHOPPING_API_KEY)
        
        # Extract features
        features = await processor.extract_features_from_text("LED string lights")
        
        # Get local matches
        local_matches = await processor.find_similar_products(
            input_features=features,
            max_results=3
        )
        
        # Get live products
        price_data = await shopping_service.get_price_comparison(features)
        live_products = price_data["products"][:3]
        
        print(f"✅ Combined search successful!")
        print(f"   Local matches: {len(local_matches)}")
        print(f"   Live products: {len(live_products)}")
        print(f"   Search query: '{price_data['search_query']}'")
        
        if local_matches:
            print(f"   Best local match: {local_matches[0].name} (${local_matches[0].price:.2f})")
        
        if live_products:
            live_product = live_products[0]
            price_str = f"${live_product['price']:.2f}" if live_product['price'] else "N/A"
            print(f"   Best live match: {live_product['title'][:50]}... ({price_str})")
        
        return True
    except Exception as e:
        print(f"❌ Combined search test failed: {e}")
        return False

async def test_fuzzy_matching():
    """Test fuzzy matching logic"""
    print("\n🎯 Testing fuzzy matching...")
    
    try:
        shopping_service = GoogleShoppingService(Config.GOOGLE_SHOPPING_API_KEY)
        processor = AIProductProcessor(Config.OPENAI_API_KEY)
        
        # Create test features
        features = await processor.extract_features_from_text("50ft LED string lights")
        
        # Create mock shopping result
        mock_result = {
            "title": "50 Foot LED String Light Set - Outdoor Patio Lights",
            "price": "$29.99",
            "source": "TestStore"
        }
        
        # Test fuzzy matching
        match_score = shopping_service.fuzzy_match_product(features, mock_result)
        
        print(f"✅ Fuzzy matching test successful!")
        print(f"   Input: {features.product_type} ({features.size})")
        print(f"   Result: {mock_result['title']}")
        print(f"   Match score: {match_score:.3f}")
        
        return True
    except Exception as e:
        print(f"❌ Fuzzy matching test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting AI Product Intelligence Tool - Phase 3 Tests")
    print("=" * 70)
    
    # Configuration check
    try:
        Config.validate_config()
        print("✅ Configuration validation successful")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return
    
    tests = [
        ("Product Database", test_product_database),
        ("Text Analysis", test_text_analysis),
        ("Product Matching", test_product_matching),
        ("Google Shopping Service", test_google_shopping_service),
        ("Price Comparison", test_price_comparison),
        ("Fuzzy Matching", test_fuzzy_matching),
        ("Combined Search", test_combined_search),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        start_time = time.time()
        if asyncio.iscoroutinefunction(test_func):
            success = await test_func()
        else:
            success = test_func()
        
        elapsed = time.time() - start_time
        results[test_name] = success
        
        if success:
            print(f"✅ {test_name} completed in {elapsed:.2f}s")
        else:
            print(f"❌ {test_name} failed after {elapsed:.2f}s")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 3 is ready to use.")
        print("\n🚀 Phase 3 Features Available:")
        print("   • Multi-modal product analysis (text + image)")
        print("   • Local database product matching")
        print("   • Live price aggregation via Google Shopping")
        print("   • Combined search (local + live results)")
        print("   • Fuzzy matching and price statistics")
        print("   • Beautiful web interface with real product links")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    asyncio.run(main()) 