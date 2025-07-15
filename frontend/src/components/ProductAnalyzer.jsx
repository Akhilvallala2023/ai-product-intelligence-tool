import React, { useState, useRef } from 'react';
import { Upload, X, Search, Zap, Star, DollarSign, Globe, ExternalLink } from 'lucide-react';
import ResultsDisplay from './ResultsDisplay';

const ProductAnalyzer = () => {
  const [textInput, setTextInput] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGettingPrices, setIsGettingPrices] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [livePriceResults, setLivePriceResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('analyze'); // 'analyze', 'prices'
  const fileInputRef = useRef(null);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!textInput.trim() && !imageFile) {
      setError('Please provide either a text description or an image.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResults(null);

    try {
      const formData = new FormData();
      
      if (textInput.trim()) {
        formData.append('text_description', textInput.trim());
      }
      
      if (imageFile) {
        formData.append('image', imageFile);
      }

      const response = await fetch('/api/analyze-form', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setAnalysisResults(result);
        setActiveTab('analyze');
      } else {
        setError(result.error_message || 'Analysis failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Analysis error:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };



  const handleGetLivePrices = async () => {
    if (!textInput.trim() && !imageFile) {
      setError('Please provide either a text description or an image.');
      return;
    }

    setIsGettingPrices(true);
    setError(null);
    setLivePriceResults(null);

    try {
      const formData = new FormData();
      
      if (textInput.trim()) {
        formData.append('text_description', textInput.trim());
      }
      
      if (imageFile) {
        formData.append('image', imageFile);
      }

      formData.append('max_results', '10');
      formData.append('include_price_stats', 'true');

      const response = await fetch('/api/live-prices-form', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        console.log('Live prices result:', result);
        setLivePriceResults(result);
        setActiveTab('prices');
      } else {
        setError(result.error_message || 'Live price search failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Live price error:', err);
    } finally {
      setIsGettingPrices(false);
    }
  };



  const clearAll = () => {
    setTextInput('');
    setImageFile(null);
    setImagePreview(null);
    setAnalysisResults(null);
    setLivePriceResults(null);
    setError(null);
    setActiveTab('analyze');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const isLoading = isAnalyzing || isGettingPrices;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center gap-3 mb-6">
          <Zap className="text-blue-600 h-8 w-8" />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">AI Product Intelligence Tool</h1>
            <p className="text-sm text-gray-600">Phase 3: Live Price Aggregation & Product Matching</p>
          </div>
        </div>
        
        <div className="space-y-6">
          {/* Text Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product Description
            </label>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Describe the product you want to analyze (e.g., 'Outdoor string lights with warm white LED bulbs')"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows="3"
            />
          </div>

          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product Image
            </label>
            <div className="flex items-start gap-4">
              <div className="flex-1">
                <div 
                  className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors cursor-pointer"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <p className="text-sm text-gray-600 mb-2">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">
                    PNG, JPG, GIF up to 10MB
                  </p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
              </div>
              
              {imagePreview && (
                <div className="relative">
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    className="w-32 h-32 object-cover rounded-lg border border-gray-300"
                  />
                  <button
                    onClick={removeImage}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              onClick={handleAnalyze}
              disabled={isLoading}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            >
              <Search className="h-4 w-4" />
              {isAnalyzing ? 'Analyzing...' : 'Analyze'}
            </button>
            
            <button
              onClick={handleGetLivePrices}
              disabled={isLoading}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
            >
              <Globe className="h-4 w-4" />
              {isGettingPrices ? 'Searching...' : 'Get Live Prices'}
            </button>
          </div>

          <button
            onClick={clearAll}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <X className="h-5 w-5" />
            Clear All
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <X className="h-5 w-5 text-red-500" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Results Tabs */}
      {(analysisResults || livePriceResults) && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex border-b border-gray-200 mb-6 overflow-x-auto">
            <button
              onClick={() => setActiveTab('analyze')}
              className={`px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === 'analyze'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Analysis Results
            </button>
            <button
              onClick={() => setActiveTab('prices')}
              className={`px-6 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
                activeTab === 'prices'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Live Prices
            </button>
          </div>

          {activeTab === 'analyze' && analysisResults && (
            <ResultsDisplay results={analysisResults} type="analysis" />
          )}

          {activeTab === 'prices' && livePriceResults && (
            <LivePriceResults results={livePriceResults} />
          )}
        </div>
      )}
    </div>
  );
};



// New component for displaying live price results (Phase 3)
const LivePriceResults = ({ results }) => {
  const { input_features, products, price_stats, total_found, search_query, processing_time } = results;
  
  console.log('LivePriceResults rendering with:', { products: products?.length, total_found });

  return (
    <div className="space-y-6">
      {/* Search Info */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-purple-800 mb-2">Live Price Search</h3>
        <div className="space-y-2 text-sm">
          <div>
            <span className="font-medium text-gray-700">Search Query:</span>
            <span className="ml-2 text-gray-600">"{search_query}"</span>
          </div>
          {input_features && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <span className="font-medium text-gray-700">Type:</span>
                <span className="ml-2 text-gray-600">{input_features.product_type}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Category:</span>
                <span className="ml-2 text-gray-600">{input_features.category}</span>
              </div>
              {input_features.brand && (
                <div>
                  <span className="font-medium text-gray-700">Brand:</span>
                  <span className="ml-2 text-gray-600">{input_features.brand}</span>
                </div>
              )}
              {input_features.color && (
                <div>
                  <span className="font-medium text-gray-700">Color:</span>
                  <span className="ml-2 text-gray-600">{input_features.color}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Price Statistics */}
      {price_stats && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-800 mb-3">Price Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">${price_stats.min_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Lowest Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">${price_stats.avg_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Average Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">${price_stats.median_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Median Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">${price_stats.max_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Highest Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">${price_stats.price_range.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Price Range</div>
            </div>
          </div>
        </div>
      )}

      {/* Results Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-800">
          Found {total_found} Live Products
        </h3>
        <div className="text-sm text-gray-500">
          Processing time: {processing_time?.toFixed(2)}s
        </div>
      </div>

      {/* Live Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product, index) => {
          return (
          <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="aspect-w-16 aspect-h-12 mb-4">
              {product.thumbnail ? (
                <img
                  src={product.thumbnail}
                  alt={product.title}
                  className="w-full h-48 object-cover rounded-lg"
                  onError={(e) => {
                    e.target.src = `https://via.placeholder.com/400x300?text=${encodeURIComponent(product.title)}`;
                  }}
                />
              ) : (
                <div className="w-full h-48 bg-gray-200 rounded-lg flex items-center justify-center">
                  <span className="text-gray-500 text-sm">No Image</span>
                </div>
              )}
            </div>
            
            <h4 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
              {product.title}
            </h4>
            
            <div className="flex justify-between items-center mb-2">
              {product.price ? (
                <span className="text-2xl font-bold text-green-600">
                  ${parseFloat(product.price).toFixed(2)}
                </span>
              ) : (
                <span className="text-lg text-gray-500">Price not available</span>
              )}
              <span className="text-sm text-gray-500">
                {product.source}
              </span>
            </div>
            
            <div className="flex items-center gap-4 mb-3">
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                <span className="text-sm text-gray-600">
                  {(product.match_score * 100).toFixed(0)}% match
                </span>
              </div>
              {product.rating && (
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 text-yellow-400 fill-current" />
                  <span className="text-sm text-gray-600">
                    {product.rating} ({product.reviews || 0} reviews)
                  </span>
                </div>
              )}
            </div>
            
            {product.shipping && (
              <div className="text-sm text-gray-600 mb-3">
                <span className="font-medium">Shipping:</span> {product.shipping}
              </div>
            )}
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              {product.link ? (
                <a
                  href={product.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                >
                  <ExternalLink className="h-4 w-4" />
                  View Product
                </a>
              ) : (
                <div className="flex items-center justify-center gap-2 w-full px-4 py-2 bg-gray-400 text-white rounded-lg cursor-not-allowed text-sm">
                  <ExternalLink className="h-4 w-4" />
                  Link Unavailable
                </div>
              )}
            </div>
          </div>
        );
        })}
      </div>
    </div>
  );
};



export default ProductAnalyzer; 