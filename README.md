# 🚀 AI-Powered Product Intelligence Tool

A multi-modal product intelligence system that extracts features from product images and text descriptions using AI vision and NLP capabilities.

## 🎯 Project Overview

This tool accepts:
- Product images (JPEG, PNG, WEBP)
- Product specifications (text descriptions)
- Or both combined

It then:
- Extracts product features using AI (OpenAI GPT-4 Vision, Gemini Vision, OpenAI GPT-4)
- Normalizes features into structured JSON format
- Displays results in a beautiful, responsive UI

## 📦 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI Models**: 
  - OpenAI GPT-4o (image analysis with vision)
  - OpenAI GPT-4 (text analysis)
- **Database**: SQLite (for future phases)
- **File Processing**: Pillow, aiofiles

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **UI**: Modern, responsive design with drag-and-drop

## 🏗️ Project Structure

```
AI-powered Product Intelligence Tool/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── ai_services.py       # AI processing services
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductAnalyzer.jsx
│   │   │   └── ResultsDisplay.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
└── README.md
```

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+ installed
- Node.js 16+ installed
- OpenAI API Key (required for both text and vision processing)

### 2. Environment Setup

Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=development
```

### 3. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at: `http://localhost:5173`

## 🧪 Testing Phase 1 - Base System

### Test Cases

#### 1. Text-Only Analysis
1. Navigate to `http://localhost:5173`
2. Enter a product description: `"Red Nike Air Max sneakers size 10 with air cushioning"`
3. Click "Analyze Product"
4. Verify extracted features include:
   - Brand: Nike
   - Product Type: sneakers
   - Color: Red
   - Size: 10
   - Key Features: air cushioning

#### 2. Image-Only Analysis
1. Upload a product image (drag & drop or click upload)
2. Leave text description empty
3. Click "Analyze Product"
4. Verify features are extracted from the image

#### 3. Combined Analysis (Text + Image)
1. Enter a product description
2. Upload a product image
3. Click "Analyze Product"
4. Verify features are combined from both sources
5. Check that extraction method shows "Combined Analysis"

#### 4. API Testing
Test the API endpoints directly:

```bash
# Health check
curl http://localhost:8000/api/health

# Text analysis
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{"product_text": "Blue Samsung Galaxy S24 smartphone 256GB"}'

# Form-based analysis (with file upload)
curl -X POST "http://localhost:8000/api/analyze-form" \
  -F "product_text=iPhone 15 Pro" \
  -F "image=@/path/to/your/image.jpg"
```

### Expected Performance
- **Latency**: Under 2 seconds for most requests
- **Accuracy**: High confidence scores (>80%) for clear inputs
- **Error Handling**: Graceful handling of invalid inputs

## 📊 Features Extracted

The system extracts structured product information:

```json
{
  "brand": "Nike",
  "model": "Air Max 90",
  "product_type": "sneakers",
  "color": "red",
  "size": "10",
  "material": "leather and mesh",
  "style": "athletic",
  "category": "footwear",
  "key_features": ["air cushioning", "retro design", "durable"],
  "specifications": {
    "sole_type": "rubber",
    "closure": "lace-up"
  },
  "confidence_score": 0.85,
  "extraction_method": "combined"
}
```

## 🔍 API Endpoints

### `POST /api/analyze`
Analyze product from JSON request
- **Body**: `{"product_text": "...", "image_base64": "..."}`
- **Response**: Product analysis with extracted features

### `POST /api/analyze-form`
Analyze product from form data (multipart)
- **Form Data**: `product_text` (string), `image` (file)
- **Response**: Product analysis with extracted features

### `GET /api/health`
Health check endpoint
- **Response**: API status and configuration info

### `GET /`
API information and available endpoints

## 🚨 Troubleshooting

### Common Issues

1. **"Configuration Error: OpenAI API key required"**
   - Ensure `.env` file exists with valid `OPENAI_API_KEY`
   - Check that the environment variable is loaded

2. **"CORS Error" in browser**
   - Ensure backend is running on port 8000
   - Check CORS configuration in `backend/main.py`

3. **"Module not found" errors**
   - Run `pip install -r requirements.txt`
   - Ensure Python path includes the project directory

4. **Frontend build errors**
   - Run `npm install` in the frontend directory
   - Check Node.js version (16+ required)

5. **Image upload fails**
   - Check file size (max 10MB)
   - Verify image format (JPEG, PNG, WEBP)
   - Ensure proper file permissions

## 🔮 Next Phases

### Phase 2 - Matching Engine (Static)
- Create dummy product database
- Implement similarity scoring with embeddings
- Add product matching and ranking

### Phase 3 - Live Price Aggregation
- Integrate shopping APIs
- Add web scraping capabilities
- Display real-time prices and links

### Phase 4 - Advanced Features
- Price tracking over time
- Review summarization
- Product variant clustering
- Enhanced filtering and sorting

## 📝 Development Notes

### Code Quality
- Modular, testable architecture
- Type hints and documentation
- Error handling and validation
- Clean separation of concerns

### Performance Considerations
- Async/await for API calls
- Efficient image processing
- Caching strategies for future phases
- Rate limiting for API calls

### Security
- Input validation and sanitization
- File upload restrictions
- API key management
- CORS configuration

## 🤝 Contributing

1. Follow the phase-by-phase development approach
2. Test thoroughly before advancing to next phase
3. Maintain clean, modular code
4. Document all changes and new features

## 📄 License

This project is for educational and development purposes. 