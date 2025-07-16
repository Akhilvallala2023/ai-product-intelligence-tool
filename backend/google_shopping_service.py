import asyncio
import logging
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
from backend.models import ProductFeatures
import re
from difflib import SequenceMatcher
import json
import base64

logger = logging.getLogger(__name__)

class GoogleShoppingService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.location = "Boca Raton, Florida, United States"
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
        
        # Add ALL specifications to the search query
        if features.specifications:
            for key, value in features.specifications.items():
                if value and len(str(value).strip()) > 0:
                    # Skip very common/generic values
                    if str(value).lower() not in ['standard', 'regular', 'basic', 'normal', 'default', 'yes', 'no']:
                        query_parts.append(str(value))
        
        # Add top 3 key features
        if features.key_features:
            for feature in features.key_features[:3]:
                if len(feature) > 3 and feature.lower() not in ['durable', 'quality', 'good']:
                    query_parts.append(feature)
        
        # Join and clean up the query
        query = " ".join(query_parts)
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Limit query length for better results (increased limit to accommodate more specs)
        if len(query) > 200:
            query = query[:200].rsplit(' ', 1)[0]
        
        logger.info(f"Generated search query: '{query}'")
        return query
    
    def similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def fuzzy_match_product(self, extracted_features: ProductFeatures, shopping_result: Dict[str, Any], 
                           matching_criteria: Optional[Dict[str, bool]] = None) -> float:
        """Calculate fuzzy match score between extracted features and shopping result"""
        score = 0.0
        weight_sum = 0.0
        
        # Use default matching if no criteria provided
        if matching_criteria is None:
            matching_criteria = {
                "titleMatching": True,
                "brandMatching": True,
                "colorMatching": True,
                "sizeMatching": True,
                "specificationsMatching": True
            }
        
        # Product title matching (high weight)
        if matching_criteria.get("titleMatching", True) and 'title' in shopping_result:
            title_score = self.similarity_score(
                extracted_features.product_type or "",
                shopping_result['title']
            )
            score += title_score * 0.3
            weight_sum += 0.3
        
        # Brand matching (high weight)
        if matching_criteria.get("brandMatching", True) and extracted_features.brand and 'title' in shopping_result:
            brand_score = 1.0 if extracted_features.brand.lower() in shopping_result['title'].lower() else 0.0
            score += brand_score * 0.25
            weight_sum += 0.25
        
        # Color matching (medium weight)
        if matching_criteria.get("colorMatching", True) and extracted_features.color and 'title' in shopping_result:
            color_score = 1.0 if extracted_features.color.lower() in shopping_result['title'].lower() else 0.0
            score += color_score * 0.1
            weight_sum += 0.1
        
        # Size matching (medium weight)
        if matching_criteria.get("sizeMatching", True) and extracted_features.size and 'title' in shopping_result:
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
            
            score += size_score * 0.1
            weight_sum += 0.1
        
        # Specifications matching
        if matching_criteria.get("specificationsMatching", True) and extracted_features.specifications and 'title' in shopping_result:
            spec_score = 0.0
            spec_count = 0
            
            # Important specifications that would likely appear in product titles
            important_specs = ["Light Source Type", "Power Source", "Special Feature", "Light Color", "Theme"]
            
            for spec_key in important_specs:
                if spec_key in extracted_features.specifications:
                    spec_value = extracted_features.specifications[spec_key]
                    if spec_value and len(spec_value) > 2:
                        spec_count += 1
                        if spec_value.lower() in shopping_result['title'].lower():
                            spec_score += 1.0
            
            if spec_count > 0:
                final_spec_score = spec_score / spec_count
                score += final_spec_score * 0.25
                weight_sum += 0.25
        
        # Normalize score
        if weight_sum > 0:
            return score / weight_sum
        else:
            return 0.0
    
    async def search_products(self, features: ProductFeatures, max_results: int = 10, 
                            matching_criteria: Optional[Dict[str, bool]] = None) -> List[Dict[str, Any]]:
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
                    match_score = self.fuzzy_match_product(features, result, matching_criteria)
                    
                    # Extract price information
                    price = self.extract_price(result)
                    
                    # Extract pack quantity and calculate unit price
                    pack_quantity = None
                    unit_price = None
                    if price and 'title' in result:
                        pack_quantity = self.extract_pack_quantity(result['title'])
                        if pack_quantity:
                            unit_price = self.calculate_unit_price(price, pack_quantity)
                    
                    # Clean and structure the result
                    original_price = result.get("extracted_price")
                    if original_price is not None:
                        original_price = str(original_price)
                    
                    processed_result = {
                        "title": result.get("title", ""),
                        "price": price,
                        "unit_price": unit_price,
                        "pack_quantity": pack_quantity,
                        "original_price": original_price,
                        "link": result.get("product_link", result.get("link")),
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
    
    async def search_products_by_image(self, image_base64: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for products using Bing Images API based on an image"""
        try:
            logger.info("Searching Bing Images with image")
            
            # Prepare search parameters for image search
            params = {
                "engine": "bing_images",
                "api_key": self.api_key,
            }
            
            # First get image search results
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "images_results" not in results or not results["images_results"]:
                logger.warning("No image results found")
                return []
            
            # Get the first few results as potential matches
            image_results = results["images_results"][:max_results]
            logger.info(f"Found {len(image_results)} image results")
            
            # Process results
            processed_results = []
            for result in image_results:
                try:
                    # Create a structured result
                    processed_result = {
                        "title": result.get("title", "Unknown Product"),
                        "link": result.get("link", ""),
                        "source": result.get("source", ""),
                        "thumbnail": result.get("thumbnail", ""),
                        "original_image": result.get("original", ""),
                        "match_score": 0.7,  # Default score for image matches
                    }
                    
                    processed_results.append(processed_result)
                except Exception as e:
                    logger.error(f"Error processing image result: {e}")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in Bing Images search: {e}")
            return []
    
    async def search_products_by_extracted_features(self, features: ProductFeatures, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for products using Bing Images API based on extracted features"""
        try:
            logger.info("Searching Bing Images with extracted features")
            
            # Create a search query from the features
            query = self.create_search_query(features)
            
            # Prepare search parameters
            params = {
                "engine": "bing_images",
                "q": query,
                "api_key": self.api_key,
            }
            
            # Perform the search
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "images_results" not in results or not results["images_results"]:
                logger.warning("No image results found")
                return []
            
            # Get the results
            image_results = results["images_results"][:max_results]
            logger.info(f"Found {len(image_results)} image results for query: {query}")
            
            # Process results
            processed_results = []
            for result in image_results:
                try:
                    # Create a structured result
                    processed_result = {
                        "title": result.get("title", "Unknown Product"),
                        "link": result.get("link", ""),
                        "source": result.get("source", ""),
                        "thumbnail": result.get("thumbnail", ""),
                        "original_image": result.get("original", ""),
                        "match_score": 0.8,  # Higher score for feature-based matches
                    }
                    
                    processed_results.append(processed_result)
                except Exception as e:
                    logger.error(f"Error processing image result: {e}")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in Bing Images search with features: {e}")
            return []
    
    def extract_pack_quantity(self, title: str) -> Optional[int]:
        """Extract pack quantity from product title (e.g., '12-pack', '8-pack', etc.)"""
        try:
            # Look for patterns like "12-pack", "8-pack", "2-pack", "4-pack", etc.
            pack_pattern = r'(\d+)-pack'
            match = re.search(pack_pattern, title, re.IGNORECASE)
            
            if match:
                quantity = int(match.group(1))
                logger.info(f"Detected pack quantity: {quantity} from title: {title}")
                return quantity
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting pack quantity: {e}")
            return None
    
    def calculate_unit_price(self, total_price: float, pack_quantity: int) -> float:
        """Calculate unit price by dividing total price by pack quantity"""
        try:
            if pack_quantity > 0:
                unit_price = total_price / pack_quantity
                logger.info(f"Calculated unit price: ${total_price:.2f} / {pack_quantity} = ${unit_price:.2f}")
                return unit_price
            return total_price
            
        except Exception as e:
            logger.warning(f"Error calculating unit price: {e}")
            return total_price

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
    
    async def get_price_comparison(self, features: ProductFeatures, 
                                 matching_criteria: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
        """Get comprehensive price comparison data"""
        results = await self.search_products(features, max_results=20, matching_criteria=matching_criteria)
        
        if not results:
            return {
                "products": [],
                "price_stats": {},
                "total_found": 0,
                "search_query": self.create_search_query(features)
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