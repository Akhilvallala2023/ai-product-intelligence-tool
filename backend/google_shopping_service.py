import asyncio
import logging
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
from backend.models import ProductFeatures
import re
from difflib import SequenceMatcher
import json

logger = logging.getLogger(__name__)

class GoogleShoppingService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.location = "Austin, Texas, United States"
        self.language = "en"
        self.country = "us"
    
    def create_search_query(self, features: ProductFeatures) -> str:
        """Create an optimized search query from extracted product features"""
        query_parts = []
        
        # Add product type (most important)
        if features.product_type:
            query_parts.append(features.product_type)
        
        # Add brand if available
        if features.brand:
            query_parts.append(features.brand)
        
        # Add key descriptive features
        if features.color and features.color.lower() not in ['black', 'white', 'clear', 'transparent']:
            query_parts.append(features.color)
        
        if features.size:
            query_parts.append(features.size)
        
        # Add material if it's distinctive
        if features.material and features.material.lower() not in ['plastic', 'metal']:
            query_parts.append(features.material)
        
        # Add style if it's specific
        if features.style and features.style.lower() not in ['standard', 'regular', 'basic']:
            query_parts.append(features.style)
        
        # Add top 2 key features
        if features.key_features:
            for feature in features.key_features[:2]:
                if len(feature) > 3 and feature.lower() not in ['durable', 'quality', 'good']:
                    query_parts.append(feature)
        
        # Join and clean up the query
        query = " ".join(query_parts)
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Limit query length for better results
        if len(query) > 100:
            query = query[:100].rsplit(' ', 1)[0]
        
        logger.info(f"Generated search query: '{query}'")
        return query
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def fuzzy_match_product(self, extracted_features: ProductFeatures, shopping_result: Dict[str, Any]) -> float:
        """Calculate fuzzy match score between extracted features and shopping result"""
        score = 0.0
        weight_sum = 0.0
        
        # Product title matching (high weight)
        if 'title' in shopping_result:
            title_score = self.similarity_score(
                extracted_features.product_type or "",
                shopping_result['title']
            )
            score += title_score * 0.4
            weight_sum += 0.4
        
        # Brand matching (high weight)
        if extracted_features.brand and 'title' in shopping_result:
            brand_score = 1.0 if extracted_features.brand.lower() in shopping_result['title'].lower() else 0.0
            score += brand_score * 0.3
            weight_sum += 0.3
        
        # Color matching (medium weight)
        if extracted_features.color and 'title' in shopping_result:
            color_score = 1.0 if extracted_features.color.lower() in shopping_result['title'].lower() else 0.0
            score += color_score * 0.15
            weight_sum += 0.15
        
        # Size matching (medium weight)
        if extracted_features.size and 'title' in shopping_result:
            # Extract size patterns from both
            size_pattern = r'\b\d+[\s]*(?:inch|in|ft|feet|cm|mm|"|\')\b'
            extracted_sizes = re.findall(size_pattern, extracted_features.size.lower(), re.IGNORECASE)
            result_sizes = re.findall(size_pattern, shopping_result['title'].lower(), re.IGNORECASE)
            
            size_score = 0.0
            if extracted_sizes and result_sizes:
                # Check if any sizes match
                for ext_size in extracted_sizes:
                    for res_size in result_sizes:
                        if self.similarity_score(ext_size, res_size) > 0.8:
                            size_score = 1.0
                            break
                    if size_score > 0:
                        break
            
            score += size_score * 0.15
            weight_sum += 0.15
        
        # Normalize score
        if weight_sum > 0:
            return score / weight_sum
        else:
            return 0.0
    
    async def search_products(self, features: ProductFeatures, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for products using Google Shopping API"""
        try:
            query = self.create_search_query(features)
            
            if not query.strip():
                logger.warning("Empty search query generated")
                return []
            
            # Prepare search parameters
            params = {
                "q": query,
                "location": self.location,
                "hl": self.language,
                "gl": self.country,
                "api_key": self.api_key,
                "engine": "google_shopping",
                "num": min(max_results * 2, 20)  # Get more results for better filtering
            }
            
            logger.info(f"Searching Google Shopping with params: {params}")
            
            # Perform the search
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "shopping_results" not in results:
                logger.warning("No shopping results found")
                return []
            
            shopping_results = results["shopping_results"]
            logger.info(f"Found {len(shopping_results)} raw shopping results")
            
            # Process and score results
            processed_results = []
            for result in shopping_results:
                try:
                    # Calculate fuzzy match score
                    match_score = self.fuzzy_match_product(features, result)
                    
                    # Extract price information
                    price = self.extract_price(result)
                    
                    # Clean and structure the result
                    original_price = result.get("extracted_price")
                    if original_price is not None:
                        original_price = str(original_price)
                    
                    processed_result = {
                        "title": result.get("title", ""),
                        "price": price,
                        "original_price": original_price,
                        "link": result.get("product_link", result.get("link")),  # Use product_link as primary, link as fallback
                        "product_link": result.get("product_link"),
                        "source": result.get("source", ""),
                        "thumbnail": result.get("thumbnail", ""),
                        "rating": result.get("rating"),
                        "reviews": result.get("reviews"),
                        "shipping": result.get("shipping", ""),
                        "match_score": float(match_score),
                        "position": result.get("position", 0)
                    }
                    
                    # Only include results with decent match scores
                    if match_score > 0.3:
                        processed_results.append(processed_result)
                
                except Exception as e:
                    logger.warning(f"Error processing shopping result: {e}")
                    continue
            
            # Sort by match score (descending) and limit results
            processed_results.sort(key=lambda x: x["match_score"], reverse=True)
            final_results = processed_results[:max_results]
            
            logger.info(f"Returning {len(final_results)} filtered and ranked results")
            return final_results
            
        except Exception as e:
            logger.error(f"Error searching Google Shopping: {e}")
            return []
    
    def extract_price(self, result: Dict[str, Any]) -> Optional[float]:
        """Extract numeric price from shopping result"""
        try:
            # Try different price fields
            price_fields = ["extracted_price", "price"]
            
            for field in price_fields:
                if field in result and result[field]:
                    price_str = str(result[field])
                    
                    # Remove currency symbols and extract number
                    price_match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
                    if price_match:
                        return float(price_match.group())
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting price: {e}")
            return None
    
    async def get_product_alternatives(self, features: ProductFeatures, price_range: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Get alternative products with optional price filtering"""
        results = await self.search_products(features, max_results=15)
        
        if price_range:
            min_price, max_price = price_range
            filtered_results = []
            
            for result in results:
                if result["price"] and min_price <= result["price"] <= max_price:
                    filtered_results.append(result)
            
            return filtered_results
        
        return results
    
    async def get_price_comparison(self, features: ProductFeatures) -> Dict[str, Any]:
        """Get comprehensive price comparison data"""
        results = await self.search_products(features, max_results=20)
        
        if not results:
            return {
                "products": [],
                "price_stats": {},
                "total_found": 0
            }
        
        # Extract prices for statistics
        prices = [r["price"] for r in results if r["price"] is not None]
        
        price_stats = {}
        if prices:
            price_stats = {
                "min_price": min(prices),
                "max_price": max(prices),
                "avg_price": sum(prices) / len(prices),
                "median_price": sorted(prices)[len(prices) // 2] if prices else 0,
                "price_range": max(prices) - min(prices) if len(prices) > 1 else 0
            }
        
        return {
            "products": results,
            "price_stats": price_stats,
            "total_found": len(results),
            "search_query": self.create_search_query(features)
        } 