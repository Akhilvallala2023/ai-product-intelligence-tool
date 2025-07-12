from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class ProductAnalysisRequest(BaseModel):
    text_description: Optional[str] = Field(None, description="Text description of the product")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")

class ProductFeatures(BaseModel):
    brand: Optional[str] = Field(None, description="Product brand")
    model: Optional[str] = Field(None, description="Product model")
    product_type: str = Field(..., description="Type of product")
    color: Optional[str] = Field(None, description="Product color")
    size: Optional[str] = Field(None, description="Product size")
    material: Optional[str] = Field(None, description="Product material")
    style: Optional[str] = Field(None, description="Product style")
    category: str = Field(..., description="Product category")
    key_features: Optional[List[str]] = Field(default=[], description="List of key features")
    specifications: Optional[Dict[str, Any]] = Field(default={}, description="Product specifications")

class ProductAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Whether the analysis was successful")
    features: Optional[ProductFeatures] = Field(None, description="Extracted product features")
    confidence_score: float = Field(..., description="Confidence score of the analysis")
    processing_time: float = Field(..., description="Processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if analysis failed")

# New models for Phase 2 - Product Matching
class MatchedProduct(BaseModel):
    id: int = Field(..., description="Product ID")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    image_url: str = Field(..., description="Product image URL")
    category: str = Field(..., description="Product category")
    product_type: str = Field(..., description="Product type")
    brand: Optional[str] = Field(None, description="Product brand")
    color: Optional[str] = Field(None, description="Product color")
    size: Optional[str] = Field(None, description="Product size")
    material: Optional[str] = Field(None, description="Product material")
    style: Optional[str] = Field(None, description="Product style")
    key_features: List[str] = Field(default=[], description="List of key features")
    specifications: Dict[str, Any] = Field(default={}, description="Product specifications")
    description: str = Field(..., description="Product description")
    similarity_score: float = Field(..., description="Similarity score to the input product")
    price_score: float = Field(..., description="Price competitiveness score")
    combined_score: float = Field(..., description="Combined similarity and price score")

class ProductMatchingResponse(BaseModel):
    success: bool = Field(..., description="Whether the matching was successful")
    input_features: Optional[ProductFeatures] = Field(None, description="Input product features")
    matched_products: List[MatchedProduct] = Field(default=[], description="List of matched products")
    total_matches: int = Field(..., description="Total number of matches found")
    processing_time: float = Field(..., description="Processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if matching failed")

class ProductMatchingRequest(BaseModel):
    text_description: Optional[str] = Field(None, description="Text description of the product")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    max_results: int = Field(10, description="Maximum number of results to return")
    category_filter: Optional[str] = Field(None, description="Filter by category (lighting, fans)")
    price_weight: float = Field(0.3, description="Weight for price scoring (0.0 to 1.0)")
    similarity_weight: float = Field(0.7, description="Weight for similarity scoring (0.0 to 1.0)")

# New models for Phase 3 - Live Price Aggregation
class LiveProduct(BaseModel):
    title: str = Field(..., description="Product title from online store")
    price: Optional[float] = Field(None, description="Current price (numeric)")
    original_price: Optional[str] = Field(None, description="Original price string from source")
    link: str = Field(..., description="Direct link to product")
    product_link: Optional[str] = Field(None, description="Alternative product link")
    source: str = Field(..., description="Online store/source name")
    thumbnail: Optional[str] = Field(None, description="Product thumbnail image URL")
    rating: Optional[float] = Field(None, description="Product rating (if available)")
    reviews: Optional[int] = Field(None, description="Number of reviews")
    shipping: Optional[str] = Field(None, description="Shipping information")
    match_score: float = Field(..., description="Fuzzy match score (0.0 to 1.0)")
    position: int = Field(default=0, description="Position in search results")
    
    class Config:
        # Allow conversion of numeric original_price to string
        json_encoders = {
            float: lambda v: str(v) if v is not None else None
        }
    
    def __init__(self, **data):
        # Convert original_price to string if it's a number
        if 'original_price' in data and data['original_price'] is not None:
            data['original_price'] = str(data['original_price'])
        super().__init__(**data)

class PriceStatistics(BaseModel):
    min_price: float = Field(..., description="Minimum price found")
    max_price: float = Field(..., description="Maximum price found")
    avg_price: float = Field(..., description="Average price")
    median_price: float = Field(..., description="Median price")
    price_range: float = Field(..., description="Price range (max - min)")

class LivePriceResponse(BaseModel):
    success: bool = Field(..., description="Whether the search was successful")
    input_features: Optional[ProductFeatures] = Field(None, description="Input product features")
    products: List[LiveProduct] = Field(default=[], description="List of live products found")
    price_stats: Optional[PriceStatistics] = Field(None, description="Price statistics")
    total_found: int = Field(..., description="Total number of products found")
    search_query: str = Field(..., description="Generated search query used")
    processing_time: float = Field(..., description="Processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if search failed")

class LivePriceRequest(BaseModel):
    text_description: Optional[str] = Field(None, description="Text description of the product")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    max_results: int = Field(10, description="Maximum number of results to return")
    price_range: Optional[List[float]] = Field(None, description="Price range filter [min, max]")
    include_price_stats: bool = Field(True, description="Whether to include price statistics")

# Enhanced response combining local and live results
class CombinedProductResponse(BaseModel):
    success: bool = Field(..., description="Whether the search was successful")
    input_features: Optional[ProductFeatures] = Field(None, description="Input product features")
    
    # Local database results (Phase 2)
    local_matches: List[MatchedProduct] = Field(default=[], description="Local database matches")
    local_total: int = Field(default=0, description="Total local matches")
    
    # Live online results (Phase 3)
    live_products: List[LiveProduct] = Field(default=[], description="Live online products")
    live_total: int = Field(default=0, description="Total live products found")
    price_stats: Optional[PriceStatistics] = Field(None, description="Live price statistics")
    
    # Combined metadata
    search_query: str = Field(..., description="Generated search query")
    processing_time: float = Field(..., description="Total processing time in seconds")
    error_message: Optional[str] = Field(None, description="Error message if search failed")

class CombinedSearchRequest(BaseModel):
    text_description: Optional[str] = Field(None, description="Text description of the product")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image")
    max_local_results: int = Field(5, description="Maximum local results to return")
    max_live_results: int = Field(10, description="Maximum live results to return")
    include_local: bool = Field(True, description="Whether to include local database results")
    include_live: bool = Field(True, description="Whether to include live online results")
    price_range: Optional[List[float]] = Field(None, description="Price range filter [min, max]")
    category_filter: Optional[str] = Field(None, description="Filter by category") 