import json
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from backend.models import ProductFeatures
from backend.product_database import product_db
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class AIProductProcessor:
    def __init__(self, openai_api_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.embeddings_cache = {}  # Cache for product embeddings
    
    async def extract_features_from_image(self, image_base64: str) -> ProductFeatures:
        """Extract product features from image using OpenAI Vision API with Google Lens-like capabilities
        
        This method uses a Google Lens-inspired approach:
        1. Visual feature extraction - identifying shapes, patterns, colors, textures
        2. Object recognition - identifying the exact product type and model
        3. Text recognition - extracting visible text from the image
        4. Contextual understanding - inferring specifications from visual cues
        5. Comparative analysis - identifying distinctive features for matching
        """
        try:
            logger.info("Analyzing image using Google Lens-like visual processing...")
            return await self._process_image_openai(image_base64)
        except Exception as e:
            logger.error(f"Error in Google Lens-like image processing: {e}")
            raise e
    
    async def extract_features_from_text(self, text: str) -> ProductFeatures:
        """Extract product features from text using OpenAI API"""
        try:
            return await self._process_text_openai(text)
        except Exception as e:
            logger.error(f"Error in text processing: {e}")
            raise e
    
    async def _process_text_openai(self, text: str) -> ProductFeatures:
        """Process text using OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a product analyst. Extract structured product information from the given text.
                        Return a valid JSON object with these fields:
                        - brand (string or null)
                        - model (string or null)
                        - product_type (string, required)
                        - color (string or null)
                        - size (string or null)
                        - material (string or null)
                        - style (string or null)
                        - category (string, required)
                        - key_features (array of strings)
                        - specifications (object with key-value pairs)
                        
                        Only return the JSON object, no additional text."""
                    },
                    {
                        "role": "user",
                        "content": f"Extract product features from this text: {text}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            raw_response = response.choices[0].message.content
            logger.info(f"Raw OpenAI text response: {raw_response}")
            
            # Parse JSON response
            try:
                features_json = json.loads(raw_response)
            except json.JSONDecodeError:
                logger.error(f"JSON decode error for text: {raw_response}")
                # Try to extract JSON from response if it's wrapped in other text
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    features_json = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract valid JSON from OpenAI response")
            
            # Create ProductFeatures object
            features = ProductFeatures(**features_json)
            return features
            
        except Exception as e:
            logger.error(f"Error in OpenAI text processing: {e}")
            raise e
    
    async def _process_image_openai(self, image_base64: str) -> ProductFeatures:
        """Process image using OpenAI Vision API with Google Lens-like capabilities"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an advanced product image analyzer with capabilities similar to Google Lens. 
                        Analyze the product image in detail by:
                        
                        1. VISUAL FEATURE EXTRACTION: Identify distinctive visual elements like shapes, patterns, colors, textures, and design elements.
                        2. OBJECT RECOGNITION: Recognize the exact product type, model, and brand if visible.
                        3. TEXT RECOGNITION: Extract any visible text in the image, including brand names, model numbers, specifications, and features.
                        4. CONTEXTUAL UNDERSTANDING: Infer product specifications based on visual cues (e.g., material type from texture, size from proportions).
                        5. COMPARATIVE ANALYSIS: Identify distinctive features that would help match this product with similar items.
                        
                        Return a comprehensive JSON object with these fields:
                        - brand (string or null): Identify brand name from logos, text, or distinctive design elements
                        - model (string or null): Extract model name/number if visible
                        - product_type (string, required): Specific product type, be as precise as possible
                        - color (string or null): Dominant and secondary colors, be specific (e.g., "brushed nickel" not just "silver")
                        - size (string or null): Dimensions or size category if determinable
                        - material (string or null): Main materials used in construction
                        - style (string or null): Design style (modern, traditional, industrial, etc.)
                        - category (string, required): Product category (lighting, furniture, electronics, etc.)
                        - key_features (array of strings): 3-5 most distinctive visual or functional features
                        - specifications (object): Detailed key-value pairs of specifications visible in the image or inferred from visual cues
                          Include fields like:
                          - "Light Source Type" (e.g., LED, incandescent)
                          - "Power Source" (e.g., corded electric, battery)
                          - "Indoor/Outdoor Usage"
                          - "Special Feature" (e.g., dimmable, color changing)
                          - "Installation Type" (e.g., flush mount, hanging)
                          - "Theme" (e.g., modern, vintage)
                          - "Light Color" (e.g., warm white, cool white)
                          - "Shape" (e.g., round, square)
                          - "Finish" (e.g., matte, glossy)
                          - Any other visible or inferable specifications
                        
                        Only return the JSON object, no additional text. Be comprehensive and detailed in your analysis."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this product image like Google Lens would, extracting all visible details and specifications:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            raw_response = response.choices[0].message.content
            logger.info(f"Raw OpenAI response: {raw_response}")
            
            # Parse JSON response
            try:
                features_json = json.loads(raw_response)
            except json.JSONDecodeError:
                logger.error(f"JSON decode error: {raw_response}")
                logger.info(f"Trying to extract JSON from response: {raw_response}")
                # Try to extract JSON from response if it's wrapped in markdown or other text
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
                if json_match:
                    features_json = json.loads(json_match.group(1))
                else:
                    # Try to find any JSON object
                    json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                    if json_match:
                        features_json = json.loads(json_match.group())
                    else:
                        raise ValueError("Could not extract valid JSON from OpenAI response")
            
            # Ensure category is always set to prevent validation errors
            if not features_json.get('category'):
                # Try to infer category from product_type
                product_type = features_json.get('product_type', '').lower()
                if any(light_term in product_type for light_term in ['light', 'lamp', 'chandelier', 'bulb']):
                    features_json['category'] = 'lighting'
                elif any(furniture_term in product_type for furniture_term in ['chair', 'table', 'sofa', 'desk', 'bed']):
                    features_json['category'] = 'furniture'
                elif any(electronics_term in product_type for electronics_term in ['tv', 'phone', 'computer', 'laptop']):
                    features_json['category'] = 'electronics'
                else:
                    # Default fallback
                    features_json['category'] = 'home goods'
            
            # Create ProductFeatures object
            features = ProductFeatures(**features_json)
            return features
            
        except Exception as e:
            logger.error(f"Error in OpenAI image processing: {e}")
            raise e
    
    async def get_product_embedding(self, product_text: str) -> List[float]:
        """Get embedding for product text using OpenAI embeddings"""
        try:
            # Check cache first
            if product_text in self.embeddings_cache:
                return self.embeddings_cache[product_text]
            
            response = await self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=product_text
            )
            
            embedding = response.data[0].embedding
            # Cache the embedding
            self.embeddings_cache[product_text] = embedding
            return embedding
            
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise e
    
    def create_product_text(self, product: Dict[str, Any]) -> str:
        """Create a text representation of a product for embedding"""
        parts = []
        
        # Add basic info
        parts.append(f"Product: {product['name']}")
        parts.append(f"Category: {product['category']}")
        parts.append(f"Type: {product['product_type']}")
        
        if product.get('brand'):
            parts.append(f"Brand: {product['brand']}")
        if product.get('color'):
            parts.append(f"Color: {product['color']}")
        if product.get('size'):
            parts.append(f"Size: {product['size']}")
        if product.get('material'):
            parts.append(f"Material: {product['material']}")
        if product.get('style'):
            parts.append(f"Style: {product['style']}")
        
        # Add key features
        if product.get('key_features'):
            parts.append(f"Features: {', '.join(product['key_features'])}")
        
        # Add specifications
        if product.get('specifications'):
            specs = []
            for key, value in product['specifications'].items():
                specs.append(f"{key}: {value}")
            parts.append(f"Specifications: {', '.join(specs)}")
        
        # Add description
        if product.get('description'):
            parts.append(f"Description: {product['description']}")
        
        return " ".join(parts)
    
    def create_features_text(self, features: ProductFeatures) -> str:
        """Create a text representation of product features for embedding"""
        parts = []
        
        # Add basic info
        parts.append(f"Product: {features.product_type}")
        parts.append(f"Category: {features.category}")
        
        if features.brand:
            parts.append(f"Brand: {features.brand}")
        if features.color:
            parts.append(f"Color: {features.color}")
        if features.size:
            parts.append(f"Size: {features.size}")
        if features.material:
            parts.append(f"Material: {features.material}")
        if features.style:
            parts.append(f"Style: {features.style}")
        
        # Add key features
        if features.key_features:
            parts.append(f"Features: {', '.join(features.key_features)}")
        
        # Add specifications
        if features.specifications:
            specs = []
            for key, value in features.specifications.items():
                specs.append(f"{key}: {value}")
            parts.append(f"Specifications: {', '.join(specs)}")
        
        return " ".join(parts)
    
    def calculate_price_score(self, product_price: float, all_prices: List[float]) -> float:
        """Calculate a price competitiveness score
        
        Lower prices get higher scores, with diminishing returns for extremely low prices
        """
        if not all_prices:
            return 0.5  # Default score if no comparison prices
        
        max_price = max(all_prices)
        min_price = min(all_prices)
        price_range = max_price - min_price
        
        if price_range == 0:  # All prices are the same
            return 1.0
        
        # Normalize price (0 = cheapest, 1 = most expensive)
        normalized_price = (product_price - min_price) / price_range
        
        # Invert so lower prices get higher scores (0.5 to 1.0)
        # Using a curve that gives diminishing returns for extremely low prices
        price_score = 1.0 - (normalized_price ** 0.7) * 0.5
        
        return price_score
    
    async def find_similar_products(
        self, 
        input_features: ProductFeatures, 
        max_results: int = 10,
        category_filter: Optional[str] = None,
        price_weight: float = 0.3,
        similarity_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Find similar products based on input features"""
        try:
            # Get all products from database
            all_products = product_db.get_all_products()
            
            # Apply category filter if specified
            if category_filter:
                all_products = [p for p in all_products if p['category'].lower() == category_filter.lower()]
            
            if not all_products:
                return []
            
            # Create text representation of input features
            input_text = self.create_features_text(input_features)
            
            # Get embedding for input features
            input_embedding = await self.get_product_embedding(input_text)
            
            # Calculate embeddings and similarity scores for all products
            product_embeddings = []
            for product in all_products:
                product_text = self.create_product_text(product)
                product_embedding = await self.get_product_embedding(product_text)
                product_embeddings.append(product_embedding)
            
            # Convert to numpy arrays for cosine similarity
            input_embedding_np = np.array(input_embedding).reshape(1, -1)
            product_embeddings_np = np.array(product_embeddings)
            
            # Calculate cosine similarity scores
            similarity_scores = cosine_similarity(input_embedding_np, product_embeddings_np)[0]
            
            # Get all prices for price scoring
            all_prices = [p['price'] for p in all_products]
            
            # Calculate combined scores
            matched_products = []
            for i, product in enumerate(all_products):
                similarity_score = float(similarity_scores[i])
                price_score = self.calculate_price_score(product['price'], all_prices)
                
                # Combined score with weighting
                combined_score = (similarity_score * similarity_weight) + (price_score * price_weight)
                
                # Create matched product object
                matched_product = {
                    "id": product['id'],
                    "name": product['name'],
                    "price": product['price'],
                    "image_url": product['image_url'],
                    "category": product['category'],
                    "product_type": product['product_type'],
                    "brand": product.get('brand'),
                    "color": product.get('color'),
                    "size": product.get('size'),
                    "material": product.get('material'),
                    "style": product.get('style'),
                    "key_features": product.get('key_features', []),
                    "specifications": product.get('specifications', {}),
                    "description": product.get('description', ''),
                    "similarity_score": similarity_score,
                    "price_score": price_score,
                    "combined_score": combined_score
                }
                matched_products.append(matched_product)
            
            # Sort by combined score (descending)
            matched_products.sort(key=lambda x: x['combined_score'], reverse=True)
            
            # Return top results
            return matched_products[:max_results]
            
        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            raise e 