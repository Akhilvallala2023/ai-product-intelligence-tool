import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
from typing import Optional

from backend.models import (
    ProductAnalysisRequest, 
    ProductAnalysisResponse, 
    ProductMatchingRequest, 
    ProductMatchingResponse,
    LivePriceRequest,
    LivePriceResponse,
    CombinedSearchRequest,
    CombinedProductResponse,
    ProductFeatures,
    LiveProduct,
    PriceStatistics
)
from backend.ai_services import AIProductProcessor
from backend.google_shopping_service import GoogleShoppingService
from backend.product_database import product_db
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global AI processor and shopping service instances
ai_processor = None
shopping_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_processor, shopping_service
    try:
        # Validate configuration
        Config.validate_config()
        
        # Initialize services
        ai_processor = AIProductProcessor(Config.OPENAI_API_KEY)
        shopping_service = GoogleShoppingService(Config.GOOGLE_SHOPPING_API_KEY)
        
        logger.info("✅ Configuration validated successfully")
        logger.info("✅ AI processor and Google Shopping service initialized")
        yield
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    finally:
        # Cleanup if needed
        pass

app = FastAPI(
    title="AI Product Intelligence Tool",
    description="Multi-modal product analysis, matching, and live price aggregation system",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Product Intelligence Tool API", 
        "version": "2.0.0",
        "phase": "3 - Live Price Aggregation",
        "features": ["Product Analysis", "Smart Matching", "Live Price Aggregation"]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": time.time(),
        "services": {
            "ai_processor": ai_processor is not None,
            "shopping_service": shopping_service is not None,
            "database": len(product_db.get_all_products()) > 0
        }
    }

@app.post("/api/analyze", response_model=ProductAnalysisResponse)
async def analyze_product(request: ProductAnalysisRequest):
    """Analyze product from text description and/or image"""
    start_time = time.time()
    
    try:
        if not request.text_description and not request.image_base64:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        logger.info(f"📝 Analysis request - Text: {bool(request.text_description)}, Image: {bool(request.image_base64)}")
        
        # Extract features from available inputs
        features = None
        
        if request.text_description and request.image_base64:
            # Both text and image provided - combine results
            text_features = await ai_processor.extract_features_from_text(request.text_description)
            image_features = await ai_processor.extract_features_from_image(request.image_base64)
            
            # For now, prioritize text features but merge key information
            features = text_features
            if image_features.color and not features.color:
                features.color = image_features.color
            if image_features.material and not features.material:
                features.material = image_features.material
            if image_features.style and not features.style:
                features.style = image_features.style
            
            # Merge key features
            if image_features.key_features:
                features.key_features = list(set(features.key_features + image_features.key_features))
            
        elif request.text_description:
            # Text only
            features = await ai_processor.extract_features_from_text(request.text_description)
        elif request.image_base64:
            # Image only
            features = await ai_processor.extract_features_from_image(request.image_base64)
        
        processing_time = time.time() - start_time
        
        return ProductAnalysisResponse(
            success=True,
            features=features,
            confidence_score=0.85,  # Default confidence score
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ Error during product analysis: {e}")
        
        return ProductAnalysisResponse(
            success=False,
            features=None,
            confidence_score=0.0,
            processing_time=processing_time,
            error_message=str(e)
        )

@app.post("/api/analyze-form")
async def analyze_product_form(
    text_description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """Analyze product from form data (for file upload)"""
    try:
        if not text_description and not image:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        # Process image if provided
        image_base64 = None
        if image:
            image_content = await image.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Create request object
        request = ProductAnalysisRequest(
            text_description=text_description,
            image_base64=image_base64
        )
        
        # Use the main analyze function
        return await analyze_product(request)
        
    except Exception as e:
        logger.error(f"❌ Error during form analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match", response_model=ProductMatchingResponse)
async def match_products(request: ProductMatchingRequest):
    """Find similar products based on input description/image"""
    start_time = time.time()
    
    try:
        if not request.text_description and not request.image_base64:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        logger.info(f"🔍 Matching request - Text: {bool(request.text_description)}, Image: {bool(request.image_base64)}")
        
        # First, extract features from the input
        features = None
        
        if request.text_description and request.image_base64:
            # Both text and image provided - combine results
            text_features = await ai_processor.extract_features_from_text(request.text_description)
            image_features = await ai_processor.extract_features_from_image(request.image_base64)
            
            # For now, prioritize text features but merge key information
            features = text_features
            if image_features.color and not features.color:
                features.color = image_features.color
            if image_features.material and not features.material:
                features.material = image_features.material
            if image_features.style and not features.style:
                features.style = image_features.style
            
            # Merge key features
            if image_features.key_features:
                features.key_features = list(set(features.key_features + image_features.key_features))
            
        elif request.text_description:
            # Text only
            features = await ai_processor.extract_features_from_text(request.text_description)
        elif request.image_base64:
            # Image only
            features = await ai_processor.extract_features_from_image(request.image_base64)
        
        # Find similar products
        matched_products = await ai_processor.find_similar_products(
            input_features=features,
            max_results=request.max_results,
            category_filter=request.category_filter,
            price_weight=request.price_weight,
            similarity_weight=request.similarity_weight
        )
        
        processing_time = time.time() - start_time
        
        return ProductMatchingResponse(
            success=True,
            input_features=features,
            matched_products=matched_products,
            total_matches=len(matched_products),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ Error during product matching: {e}")
        
        return ProductMatchingResponse(
            success=False,
            input_features=None,
            matched_products=[],
            total_matches=0,
            processing_time=processing_time,
            error_message=str(e)
        )

# New Phase 3 endpoints for live price aggregation
@app.post("/api/live-prices", response_model=LivePriceResponse)
async def get_live_prices(request: LivePriceRequest):
    """Get live prices from Google Shopping API"""
    start_time = time.time()
    
    try:
        if not request.text_description and not request.image_base64:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        logger.info(f"🛍️ Live price request - Text: {bool(request.text_description)}, Image: {bool(request.image_base64)}")
        
        # Extract features first
        features = None
        
        if request.text_description and request.image_base64:
            # Both text and image provided - combine results
            text_features = await ai_processor.extract_features_from_text(request.text_description)
            image_features = await ai_processor.extract_features_from_image(request.image_base64)
            
            features = text_features
            if image_features.color and not features.color:
                features.color = image_features.color
            if image_features.material and not features.material:
                features.material = image_features.material
            if image_features.style and not features.style:
                features.style = image_features.style
            
            if image_features.key_features:
                features.key_features = list(set(features.key_features + image_features.key_features))
            
        elif request.text_description:
            features = await ai_processor.extract_features_from_text(request.text_description)
        elif request.image_base64:
            features = await ai_processor.extract_features_from_image(request.image_base64)
        
        # Get price comparison data
        price_data = await shopping_service.get_price_comparison(features)
        
        # Convert shopping results to LiveProduct models
        live_products = []
        for product_data in price_data["products"]:
            live_product = LiveProduct(**product_data)
            live_products.append(live_product)
        
        # Apply price range filter if specified
        if request.price_range and len(request.price_range) == 2:
            min_price, max_price = request.price_range
            live_products = [
                p for p in live_products 
                if p.price and min_price <= p.price <= max_price
            ]
        
        # Limit results
        live_products = live_products[:request.max_results]
        
        # Create price statistics if requested
        price_stats = None
        if request.include_price_stats and price_data["price_stats"]:
            price_stats = PriceStatistics(**price_data["price_stats"])
        
        processing_time = time.time() - start_time
        
        return LivePriceResponse(
            success=True,
            input_features=features,
            products=live_products,
            price_stats=price_stats,
            total_found=len(live_products),
            search_query=price_data["search_query"],
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ Error during live price search: {e}")
        
        return LivePriceResponse(
            success=False,
            input_features=None,
            products=[],
            price_stats=None,
            total_found=0,
            search_query="",
            processing_time=processing_time,
            error_message=str(e)
        )

@app.post("/api/search-combined", response_model=CombinedProductResponse)
async def search_combined(request: CombinedSearchRequest):
    """Combined search: local database + live online prices"""
    start_time = time.time()
    
    try:
        if not request.text_description and not request.image_base64:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        logger.info(f"🔄 Combined search request - Local: {request.include_local}, Live: {request.include_live}")
        
        # Extract features first
        features = None
        
        if request.text_description and request.image_base64:
            text_features = await ai_processor.extract_features_from_text(request.text_description)
            image_features = await ai_processor.extract_features_from_image(request.image_base64)
            
            features = text_features
            if image_features.color and not features.color:
                features.color = image_features.color
            if image_features.material and not features.material:
                features.material = image_features.material
            if image_features.style and not features.style:
                features.style = image_features.style
            
            if image_features.key_features:
                features.key_features = list(set(features.key_features + image_features.key_features))
            
        elif request.text_description:
            features = await ai_processor.extract_features_from_text(request.text_description)
        elif request.image_base64:
            features = await ai_processor.extract_features_from_image(request.image_base64)
        
        # Initialize results
        local_matches = []
        live_products = []
        price_stats = None
        search_query = ""
        
        # Get local database matches if requested
        if request.include_local:
            local_matches = await ai_processor.find_similar_products(
                input_features=features,
                max_results=request.max_local_results,
                category_filter=request.category_filter
            )
        
        # Get live online results if requested
        if request.include_live:
            price_data = await shopping_service.get_price_comparison(features)
            search_query = price_data["search_query"]
            
            # Convert to LiveProduct models
            for product_data in price_data["products"]:
                live_product = LiveProduct(**product_data)
                live_products.append(live_product)
            
            # Apply price range filter if specified
            if request.price_range and len(request.price_range) == 2:
                min_price, max_price = request.price_range
                live_products = [
                    p for p in live_products 
                    if p.price and min_price <= p.price <= max_price
                ]
            
            # Limit results
            live_products = live_products[:request.max_live_results]
            
            # Create price statistics
            if price_data["price_stats"]:
                price_stats = PriceStatistics(**price_data["price_stats"])
        
        processing_time = time.time() - start_time
        
        return CombinedProductResponse(
            success=True,
            input_features=features,
            local_matches=local_matches,
            local_total=len(local_matches),
            live_products=live_products,
            live_total=len(live_products),
            price_stats=price_stats,
            search_query=search_query,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ Error during combined search: {e}")
        
        return CombinedProductResponse(
            success=False,
            input_features=None,
            local_matches=[],
            local_total=0,
            live_products=[],
            live_total=0,
            price_stats=None,
            search_query="",
            processing_time=processing_time,
            error_message=str(e)
        )

# Form-based endpoints for Phase 3
@app.post("/api/live-prices-form")
async def get_live_prices_form(
    text_description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    max_results: int = Form(10),
    price_range_min: Optional[float] = Form(None),
    price_range_max: Optional[float] = Form(None),
    include_price_stats: bool = Form(True)
):
    """Get live prices from form data"""
    try:
        if not text_description and not image:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        # Process image if provided
        image_base64 = None
        if image:
            image_content = await image.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Create price range if both values provided
        price_range = None
        if price_range_min is not None and price_range_max is not None:
            price_range = [price_range_min, price_range_max]
        
        # Create request object
        request = LivePriceRequest(
            text_description=text_description,
            image_base64=image_base64,
            max_results=max_results,
            price_range=price_range,
            include_price_stats=include_price_stats
        )
        
        return await get_live_prices(request)
        
    except Exception as e:
        logger.error(f"❌ Error during form live price search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/search-combined-form")
async def search_combined_form(
    text_description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    max_local_results: int = Form(5),
    max_live_results: int = Form(10),
    include_local: bool = Form(True),
    include_live: bool = Form(True),
    price_range_min: Optional[float] = Form(None),
    price_range_max: Optional[float] = Form(None),
    category_filter: Optional[str] = Form(None)
):
    """Combined search from form data"""
    try:
        if not text_description and not image:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        # Process image if provided
        image_base64 = None
        if image:
            image_content = await image.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Create price range if both values provided
        price_range = None
        if price_range_min is not None and price_range_max is not None:
            price_range = [price_range_min, price_range_max]
        
        # Create request object
        request = CombinedSearchRequest(
            text_description=text_description,
            image_base64=image_base64,
            max_local_results=max_local_results,
            max_live_results=max_live_results,
            include_local=include_local,
            include_live=include_live,
            price_range=price_range,
            category_filter=category_filter
        )
        
        return await search_combined(request)
        
    except Exception as e:
        logger.error(f"❌ Error during form combined search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Existing endpoints (maintained for backward compatibility)
@app.post("/api/match-form")
async def match_products_form(
    text_description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    max_results: int = Form(10),
    category_filter: Optional[str] = Form(None),
    price_weight: float = Form(0.3),
    similarity_weight: float = Form(0.7)
):
    """Find similar products from form data (for file upload)"""
    try:
        if not text_description and not image:
            raise HTTPException(
                status_code=400, 
                detail="Either text description or image must be provided"
            )
        
        # Process image if provided
        image_base64 = None
        if image:
            image_content = await image.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Create request object
        request = ProductMatchingRequest(
            text_description=text_description,
            image_base64=image_base64,
            max_results=max_results,
            category_filter=category_filter,
            price_weight=price_weight,
            similarity_weight=similarity_weight
        )
        
        # Use the main match function
        return await match_products(request)
        
    except Exception as e:
        logger.error(f"❌ Error during form matching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
async def get_products(
    category: Optional[str] = None,
    product_type: Optional[str] = None,
    limit: int = 20
):
    """Get products from database with optional filtering"""
    try:
        if category:
            products = product_db.get_products_by_category(category)
        elif product_type:
            products = product_db.get_products_by_type(product_type)
        else:
            products = product_db.get_all_products()
        
        # Apply limit
        products = products[:limit]
        
        return {
            "success": True,
            "products": products,
            "total": len(products)
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Get a specific product by ID"""
    try:
        product = product_db.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "success": True,
            "product": product
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting product: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 