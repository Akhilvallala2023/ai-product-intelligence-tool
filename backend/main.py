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
    ProductFeatures
)
from backend.ai_services import AIProductProcessor
from backend.product_database import product_db
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global AI processor instance
ai_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_processor
    try:
        # Validate configuration
        if not Config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        
        # Initialize AI processor
        ai_processor = AIProductProcessor(Config.OPENAI_API_KEY)
        logger.info("✅ Configuration validated successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    finally:
        # Cleanup if needed
        pass

app = FastAPI(
    title="AI Product Intelligence Tool",
    description="Multi-modal product analysis and matching system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Product Intelligence Tool API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

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
    start_time = time.time()
    
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
        processing_time = time.time() - start_time
        logger.error(f"❌ Error during form analysis: {e}")
        
        return ProductAnalysisResponse(
            success=False,
            features=None,
            confidence_score=0.0,
            processing_time=processing_time,
            error_message=str(e)
        )

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