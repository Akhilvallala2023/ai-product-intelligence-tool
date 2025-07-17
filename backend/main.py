import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import base64
from typing import Optional
import json

from backend.models import (
    ProductAnalysisRequest, 
    ProductAnalysisResponse, 
    LivePriceRequest,
    LivePriceResponse,
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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174","https://idyllic-sorbet-caaa3d.netlify.app"],
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
        "phase": "4 - Searching with extracted features",
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

@app.post("/api/live-prices", response_model=LivePriceResponse)
async def get_live_prices(request: LivePriceRequest):
    """Get live prices from Google Shopping API"""
    start_time = time.time()
    
    try:
        if not request.text_description and not request.image_base64 and not request.extracted_data:
            raise HTTPException(
                status_code=400, 
                detail="Either text description, image, or extracted data must be provided"
            )
        
        logger.info(f"🛍️ Live price request - Text: {bool(request.text_description)}, Image: {bool(request.image_base64)}")
        
        # Extract features first
        features = None
        
        # Check if we have pre-extracted data from analysis
        if request.extracted_data:
            logger.info("Using pre-extracted data from analysis")
            
            # Create a ProductFeatures object from extracted data
            extracted = request.extracted_data
            features = ProductFeatures(
                brand=extracted.get("brand"),
                model=None,  # Not typically provided in extracted data
                product_type=extracted.get("product_type"),
                color=extracted.get("color"),
                size=extracted.get("size"),
                material=extracted.get("material"),
                style=extracted.get("style"),
                category=extracted.get("category") or "lighting",  # Default to "lighting" if category is None
                key_features=extracted.get("key_features", []),
                specifications=extracted.get("specifications", {})
            )
        
        # If no pre-extracted features or they're incomplete, use AI extraction
        if not features:
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
        # If we have pre-extracted features but they're missing some fields, supplement with AI
        elif request.text_description or request.image_base64:
            # Check if key fields are missing
            missing_key_fields = not features.product_type or len(features.key_features) == 0
            
            if missing_key_fields:
                logger.info("Supplementing pre-extracted features with AI extraction")
                ai_features = None
                
                if request.text_description:
                    ai_features = await ai_processor.extract_features_from_text(request.text_description)
                elif request.image_base64:
                    ai_features = await ai_processor.extract_features_from_image(request.image_base64)
                
                if ai_features:
                    # Fill in missing fields
                    if not features.product_type and ai_features.product_type:
                        features.product_type = ai_features.product_type
                    if not features.category and ai_features.category:
                        features.category = ai_features.category
                    if not features.brand and ai_features.brand:
                        features.brand = ai_features.brand
                    if not features.color and ai_features.color:
                        features.color = ai_features.color
                    if not features.size and ai_features.size:
                        features.size = ai_features.size
                    if not features.material and ai_features.material:
                        features.material = ai_features.material
                    if not features.style and ai_features.style:
                        features.style = ai_features.style
                    
                    # Merge key features
                    if ai_features.key_features:
                        features.key_features = list(set(features.key_features + ai_features.key_features))
        
        # Get price comparison data
        price_data = await shopping_service.get_price_comparison(features, matching_criteria=request.matching_criteria)
        
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

@app.post("/api/live-prices-form")
async def get_live_prices_form(
    text_description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    max_results: int = Form(10),
    price_range_min: Optional[float] = Form(None),
    price_range_max: Optional[float] = Form(None),
    include_price_stats: bool = Form(True),
    extracted_specifications: Optional[str] = Form(None),
    extracted_brand: Optional[str] = Form(None),
    extracted_product_type: Optional[str] = Form(None),
    extracted_color: Optional[str] = Form(None),
    extracted_size: Optional[str] = Form(None),
    extracted_material: Optional[str] = Form(None),
    extracted_style: Optional[str] = Form(None),
    extracted_category: Optional[str] = Form(None),
    extracted_key_features: Optional[str] = Form(None),
    matching_criteria: Optional[str] = Form(None)
):
    """Get live prices from form data"""
    try:
        if not text_description and not image and not (
            extracted_specifications or extracted_brand or extracted_product_type or 
            extracted_color or extracted_size or extracted_material or 
            extracted_style or extracted_category or extracted_key_features
        ):
            raise HTTPException(
                status_code=400, 
                detail="Either text description, image, or extracted features must be provided"
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
        
        # Parse extracted data if provided
        extracted_specs_dict = {}
        if extracted_specifications:
            try:
                extracted_specs_dict = json.loads(extracted_specifications)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse extracted specifications: {extracted_specifications}")
        
        key_features_list = []
        if extracted_key_features:
            try:
                key_features_list = json.loads(extracted_key_features)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse extracted key features: {extracted_key_features}")
        
        # Parse matching criteria if provided
        matching_criteria_dict = None
        if matching_criteria:
            try:
                matching_criteria_dict = json.loads(matching_criteria)
                logger.info(f"Using custom matching criteria: {matching_criteria_dict}")
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse matching criteria: {matching_criteria}")
        
        # Create request object
        request = LivePriceRequest(
            text_description=text_description,
            image_base64=image_base64,
            max_results=max_results,
            price_range=price_range,
            include_price_stats=include_price_stats,
            extracted_data={
                "specifications": extracted_specs_dict,
                "brand": extracted_brand,
                "product_type": extracted_product_type,
                "color": extracted_color,
                "size": extracted_size,
                "material": extracted_material,
                "style": extracted_style,
                "category": extracted_category,
                "key_features": key_features_list
            },
            matching_criteria=matching_criteria_dict
        )
        
        return await get_live_prices(request)
        
    except Exception as e:
        logger.error(f"❌ Error during form live price search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/image-search", response_model=LivePriceResponse)
async def search_by_image(
    image: UploadFile = File(...),
    max_results: int = Form(10)
):
    """Search for products using an image via Bing Images API"""
    start_time = time.time()
    
    try:
        # Read and encode the image
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        logger.info(f"🔍 Image search request - Image size: {len(image_content)} bytes")
        
        # First extract features from the image
        features = await ai_processor.extract_features_from_image(image_base64)
        
        # Use the extracted features to search for similar products
        similar_products = await shopping_service.search_products_by_extracted_features(features, max_results)
        
        processing_time = time.time() - start_time
        
        return LivePriceResponse(
            success=True,
            products=similar_products,
            search_query=shopping_service.create_search_query(features),
            processing_time=processing_time,
            total_found=len(similar_products)
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ Error during image search: {e}")
        
        return LivePriceResponse(
            success=False,
            products=[],
            search_query="",
            processing_time=processing_time,
            error_message=str(e),
            total_found=0
        )

@app.post("/api/image-search-form")
async def search_by_image_form(
    image: UploadFile = File(...),
    max_results: int = Form(10)
):
    """Search for products using an image via Bing Images API (form endpoint)"""
    return await search_by_image(image, max_results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 
