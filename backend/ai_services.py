import json
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
from backend.models import ProductFeatures, MatchedProduct
from backend.product_database import product_db
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class AIProductProcessor:
    def __init__(self, openai_api_key: str):
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.embeddings_cache = {}  # Cache for product embeddings
    
    async def extract_features_from_image(self, image_base64: str) -> ProductFeatures:
        """Extract product features from image using OpenAI Vision API"""
        try:
            return await self._process_image_openai(image_base64)
        except Exception as e:
            logger.error(f"Error in image processing: {e}")
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
        """Process image using OpenAI Vision API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a product analyst. Analyze the product image and extract detailed information.
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
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this product image and extract detailed product information:"
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
                max_tokens=500,
                temperature=0.3
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
            if specs:
                parts.append(f"Specifications: {', '.join(specs)}")
        
        # Add description
        if product.get('description'):
            parts.append(f"Description: {product['description']}")
        
        return " | ".join(parts)
    
    def create_features_text(self, features: ProductFeatures) -> str:
        """Create a text representation of extracted features for embedding"""
        parts = []
        
        parts.append(f"Type: {features.product_type}")
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
            if specs:
                parts.append(f"Specifications: {', '.join(specs)}")
        
        return " | ".join(parts)
    
    def calculate_price_score(self, product_price: float, all_prices: List[float]) -> float:
        """Calculate price competitiveness score (lower price = higher score)"""
        if not all_prices:
            return 0.5
        
        min_price = min(all_prices)
        max_price = max(all_prices)
        
        if min_price == max_price:
            return 1.0
        
        # Normalize price score (lower price gets higher score)
        normalized_score = 1.0 - (product_price - min_price) / (max_price - min_price)
        return max(0.0, min(1.0, normalized_score))
    
    async def find_similar_products(
        self, 
        input_features: ProductFeatures, 
        max_results: int = 10,
        category_filter: Optional[str] = None,
        price_weight: float = 0.3,
        similarity_weight: float = 0.7
    ) -> List[MatchedProduct]:
        """Find similar products using embeddings and similarity scoring"""
        try:
            # Get all products
            all_products = product_db.get_all_products()
            
            # Apply category filter if specified
            if category_filter:
                all_products = [p for p in all_products if p['category'].lower() == category_filter.lower()]
            
            if not all_products:
                return []
            
            # Create text representation of input features
            input_text = self.create_features_text(input_features)
            
            # Get input embedding
            input_embedding = await self.get_product_embedding(input_text)
            
            # Get embeddings for all products
            product_embeddings = []
            for product in all_products:
                product_text = self.create_product_text(product)
                embedding = await self.get_product_embedding(product_text)
                product_embeddings.append(embedding)
            
            # Calculate similarity scores
            input_embedding_array = np.array(input_embedding).reshape(1, -1)
            products_embedding_array = np.array(product_embeddings)
            
            similarity_scores = cosine_similarity(input_embedding_array, products_embedding_array)[0]
            
            # Calculate price scores
            all_prices = [p['price'] for p in all_products]
            
            # Create matched products with scores
            matched_products = []
            for i, (product, similarity_score) in enumerate(zip(all_products, similarity_scores)):
                price_score = self.calculate_price_score(product['price'], all_prices)
                
                # Combined score
                combined_score = (similarity_weight * similarity_score) + (price_weight * price_score)
                
                matched_product = MatchedProduct(
                    id=product['id'],
                    name=product['name'],
                    price=product['price'],
                    image_url=product['image_url'],
                    category=product['category'],
                    product_type=product['product_type'],
                    brand=product.get('brand'),
                    color=product.get('color'),
                    size=product.get('size'),
                    material=product.get('material'),
                    style=product.get('style'),
                    key_features=product.get('key_features', []),
                    specifications=product.get('specifications', {}),
                    description=product.get('description', ''),
                    similarity_score=float(similarity_score),
                    price_score=float(price_score),
                    combined_score=float(combined_score)
                )
                matched_products.append(matched_product)
            
            # Sort by combined score (descending)
            matched_products.sort(key=lambda x: x.combined_score, reverse=True)
            
            # Return top results
            return matched_products[:max_results]
            
        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            raise e 