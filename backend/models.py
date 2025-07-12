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