import React, { useState, useRef } from 'react';
import { Upload, X, Search, Zap, ShoppingCart, Star, DollarSign } from 'lucide-react';
import ResultsDisplay from './ResultsDisplay';

const ProductAnalyzer = () => {
  const [textInput, setTextInput] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isMatching, setIsMatching] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [matchingResults, setMatchingResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('analyze'); // 'analyze' or 'match'
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

  const handleFindSimilar = async () => {
    if (!textInput.trim() && !imageFile) {
      setError('Please provide either a text description or an image.');
      return;
    }

    setIsMatching(true);
    setError(null);
    setMatchingResults(null);

    try {
      const formData = new FormData();
      
      if (textInput.trim()) {
        formData.append('text_description', textInput.trim());
      }
      
      if (imageFile) {
        formData.append('image', imageFile);
      }

      // Add matching parameters
      formData.append('max_results', '10');
      formData.append('price_weight', '0.3');
      formData.append('similarity_weight', '0.7');

      const response = await fetch('/api/match-form', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setMatchingResults(result);
        setActiveTab('match');
      } else {
        setError(result.error_message || 'Product matching failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Matching error:', err);
    } finally {
      setIsMatching(false);
    }
  };

  const clearAll = () => {
    setTextInput('');
    setImageFile(null);
    setImagePreview(null);
    setAnalysisResults(null);
    setMatchingResults(null);
    setError(null);
    setActiveTab('analyze');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center gap-3 mb-6">
          <Zap className="text-blue-600 h-8 w-8" />
          <h1 className="text-3xl font-bold text-gray-800">AI Product Intelligence Tool</h1>
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
          <div className="flex gap-4">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || isMatching}
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Search className="h-5 w-5" />
              {isAnalyzing ? 'Analyzing...' : 'Analyze Product'}
            </button>
            
            <button
              onClick={handleFindSimilar}
              disabled={isAnalyzing || isMatching}
              className="flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ShoppingCart className="h-5 w-5" />
              {isMatching ? 'Finding Similar...' : 'Find Similar Products'}
            </button>
            
            <button
              onClick={clearAll}
              disabled={isAnalyzing || isMatching}
              className="flex items-center gap-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <X className="h-5 w-5" />
              Clear All
            </button>
          </div>
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
      {(analysisResults || matchingResults) && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex border-b border-gray-200 mb-6">
            <button
              onClick={() => setActiveTab('analyze')}
              className={`px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'analyze'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Analysis Results
            </button>
            <button
              onClick={() => setActiveTab('match')}
              className={`px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === 'match'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Similar Products
            </button>
          </div>

          {activeTab === 'analyze' && analysisResults && (
            <ResultsDisplay results={analysisResults} type="analysis" />
          )}
          
          {activeTab === 'match' && matchingResults && (
            <MatchingResults results={matchingResults} />
          )}
        </div>
      )}
    </div>
  );
};

// New component for displaying matching results
const MatchingResults = ({ results }) => {
  const { input_features, matched_products, total_matches, processing_time } = results;

  return (
    <div className="space-y-6">
      {/* Input Features Summary */}
      {input_features && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-800 mb-2">Search Criteria</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
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
        </div>
      )}

      {/* Results Stats */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-800">
          Found {total_matches} Similar Products
        </h3>
        <div className="text-sm text-gray-500">
          Processing time: {processing_time?.toFixed(2)}s
        </div>
      </div>

      {/* Matched Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {matched_products.map((product) => (
          <div key={product.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="aspect-w-16 aspect-h-12 mb-4">
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-48 object-cover rounded-lg"
                onError={(e) => {
                  e.target.src = `https://via.placeholder.com/400x300?text=${encodeURIComponent(product.name)}`;
                }}
              />
            </div>
            
            <h4 className="text-lg font-semibold text-gray-800 mb-2 line-clamp-2">
              {product.name}
            </h4>
            
            <div className="flex justify-between items-center mb-2">
              <span className="text-2xl font-bold text-green-600">
                ${product.price.toFixed(2)}
              </span>
              <span className="text-sm text-gray-500 capitalize">
                {product.category}
              </span>
            </div>
            
            <div className="flex items-center gap-4 mb-3">
              <div className="flex items-center gap-1">
                <Star className="h-4 w-4 text-yellow-400 fill-current" />
                <span className="text-sm text-gray-600">
                  {(product.similarity_score * 100).toFixed(0)}% match
                </span>
              </div>
              <div className="flex items-center gap-1">
                <DollarSign className="h-4 w-4 text-green-500" />
                <span className="text-sm text-gray-600">
                  {(product.price_score * 100).toFixed(0)}% value
                </span>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex flex-wrap gap-1">
                {product.key_features.slice(0, 3).map((feature, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                  >
                    {feature}
                  </span>
                ))}
                {product.key_features.length > 3 && (
                  <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded-full">
                    +{product.key_features.length - 3} more
                  </span>
                )}
              </div>
              
              <p className="text-sm text-gray-600 line-clamp-2">
                {product.description}
              </p>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
              <div className="flex justify-between">
                <span>Combined Score:</span>
                <span className="font-semibold">
                  {(product.combined_score * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductAnalyzer; 