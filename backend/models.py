from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

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

class LiveProduct(BaseModel):
    title: str = Field(..., description="Product title from online store")
    price: Optional[float] = Field(None, description="Current price (numeric)")
    unit_price: Optional[float] = Field(None, description="Unit price for pack products (price/quantity)")
    pack_quantity: Optional[int] = Field(None, description="Number of items in pack (e.g., 12 for 12-pack)")
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
    extracted_data: Optional[Dict[str, Any]] = Field(None, description="Pre-extracted product data from analysis")
    matching_criteria: Optional[Dict[str, bool]] = Field(None, description="Criteria to use for matching products") 