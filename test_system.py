#!/usr/bin/env python3
"""
Test script for AI Product Intelligence Tool - Phase 2
Tests both analysis and matching functionality
"""

import asyncio
import time
from backend.ai_services import AIProductProcessor
from backend.product_database import product_db
from config import Config

# Test data
TEST_TEXT = "Outdoor string lights with 50 LED bulbs, waterproof, warm white light"
TEST_PRODUCT_DESCRIPTION = "Smart ceiling fan with remote control and LED lighting"

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
            print("✅ Health endpoint working")
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

async def main():
    """Run all tests"""
    print("🚀 Starting AI Product Intelligence Tool - Phase 2 Tests")
    print("=" * 60)
    
    # Configuration check
    if not Config.OPENAI_API_KEY:
        print("❌ OpenAI API key not configured!")
        return
    
    tests = [
        ("Product Database", test_product_database),
        ("Text Analysis", test_text_analysis),
        ("Product Matching", test_product_matching),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        
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
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 2 is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    asyncio.run(main()) 