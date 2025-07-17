import React, { useState, useRef } from 'react';
import { Upload, X, Search, Zap, Star, DollarSign, Globe, ExternalLink, Settings, Filter, Check, ChevronRight, Image as ImageIcon } from 'lucide-react';
import ResultsDisplay from './ResultsDisplay';

// API Configuration
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const ProductAnalyzer = () => {
  const [textInput, setTextInput] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGettingPrices, setIsGettingPrices] = useState(false);
  const [isSearchingByImage, setIsSearchingByImage] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [livePriceResults, setLivePriceResults] = useState(null);
  const [imageSearchResults, setImageSearchResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('prices'); // Changed default to 'prices'
  const [extractionMethod, setExtractionMethod] = useState('both'); // 'image', 'text', 'both'
  const [showExtractedFeatures, setShowExtractedFeatures] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [priceThreshold, setPriceThreshold] = useState('');
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [isFiltering, setIsFiltering] = useState(false);
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

  const analyzeInput = async () => {
    if ((extractionMethod === 'text' || extractionMethod === 'both') && !textInput.trim() && 
        (extractionMethod === 'image' || extractionMethod === 'both') && !imageFile) {
      setError('Please provide input based on your selected extraction method.');
      return null;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      
      if ((extractionMethod === 'text' || extractionMethod === 'both') && textInput.trim()) {
        formData.append('text_description', textInput.trim());
      }
      
      if ((extractionMethod === 'image' || extractionMethod === 'both') && imageFile) {
        formData.append('image', imageFile);
      }

      const response = await fetch(`${BASE_URL}/api/analyze-form`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setAnalysisResults(result);
        setShowExtractedFeatures(true);
        return result;
      } else {
        setError(result.error_message || 'Analysis failed');
        return null;
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Analysis error:', err);
      return null;
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleGetLivePrices = async () => {
    console.log('handleGetLivePrices called');
    setIsGettingPrices(true);
    setError(null);
    setLivePriceResults(null);

    try {
      if ((extractionMethod === 'text' || extractionMethod === 'both') && !textInput.trim() && 
          (extractionMethod === 'image' || extractionMethod === 'both') && !imageFile) {
        throw new Error('Please provide input based on your selected extraction method.');
      }

      const formData = new FormData();
      
      if ((extractionMethod === 'text' || extractionMethod === 'both') && textInput.trim()) {
        formData.append('text_description', textInput.trim());
      }
      
      if ((extractionMethod === 'image' || extractionMethod === 'both') && imageFile) {
        formData.append('image', imageFile);
      }

      // Include extracted features from analysis
      if (analysisResults?.features?.specifications) {
        formData.append('extracted_specifications', JSON.stringify(analysisResults.features.specifications));
      }

      // Include other extracted features
      if (analysisResults?.features) {
        const { brand, product_type, color, size, material, style, key_features, category } = analysisResults.features;
        
        if (brand) formData.append('extracted_brand', brand);
        if (product_type) formData.append('extracted_product_type', product_type);
        if (color) formData.append('extracted_color', color);
        if (size) formData.append('extracted_size', size);
        if (material) formData.append('extracted_material', material);
        if (style) formData.append('extracted_style', style);
        if (category) formData.append('extracted_category', category);
        
        if (key_features && key_features.length > 0) {
          formData.append('extracted_key_features', JSON.stringify(key_features));
        }
      }

      // Add matching criteria
      formData.append('matching_criteria', JSON.stringify({})); // Removed matching criteria
      formData.append('max_results', '10');
      formData.append('include_price_stats', 'true');

      console.log('Sending live prices request with form data');
      
      const response = await fetch(`${BASE_URL}/api/live-prices-form`, {
        method: 'POST',
        body: formData,
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        throw new Error(`Server returned ${response.status}: ${errorText}`);
      }

      const result = await response.json();
      console.log('Live prices result:', result);

      if (result.success) {
        console.log('Setting live price results:', result);
        setLivePriceResults(result);
        setActiveTab('prices');
      } else {
        throw new Error(result.error_message || 'Failed to get live prices');
      }
    } catch (err) {
      console.error('Error getting live prices:', err);
      setError(`Error getting live prices: ${err.message}`);
      
      // Create a minimal result object to prevent blank screen
      setLivePriceResults({
        success: false,
        products: [],
        total_found: 0,
        search_query: '',
        processing_time: 0,
        error_message: err.message
      });
    } finally {
      setIsGettingPrices(false);
    }
  };

  const handleImageSearch = async () => {
    if (!imageFile) {
      setError('Please upload an image to search');
      return;
    }

    setIsSearchingByImage(true);
    setError(null);
    setImageSearchResults(null);

    try {
      const formData = new FormData();
      formData.append('image', imageFile);
      formData.append('max_results', '10');

      const response = await fetch(`${BASE_URL}/api/image-search-form`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        console.log('Image search results:', result);
        setImageSearchResults(result);
        setActiveTab('image-search');
        setShowExtractedFeatures(false);
      } else {
        setError(result.error_message || 'Image search failed');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Image search error:', err);
    } finally {
      setIsSearchingByImage(false);
    }
  };

  const handlePriceFilter = () => {
    if (!livePriceResults || !livePriceResults.products || livePriceResults.products.length === 0) {
      setError("No products available to filter");
      return;
    }

    setIsFiltering(true);
    
    try {
      const threshold = parseFloat(priceThreshold);
      
      if (isNaN(threshold) || threshold <= 0) {
        setError("Please enter a valid price");
        setIsFiltering(false);
        return;
      }
      
      // Filter products that are either less than the threshold or up to 20% more
      const upperLimit = threshold * 1.2; // 20% more than the threshold
      
      const filtered = livePriceResults.products.filter(product => {
        // Skip products without price
        if (!product.price) return false;
        
        const productPrice = parseFloat(product.price);
        return productPrice <= upperLimit;
      });
      
      // Sort by price (lowest first)
      filtered.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
      
      setFilteredProducts(filtered);
      setError(null);
    } catch (err) {
      setError("Error filtering products: " + err.message);
    } finally {
      setIsFiltering(false);
    }
  };

  const clearFilters = () => {
    setPriceThreshold('');
    setFilteredProducts([]);
  };

  const clearAll = () => {
    setTextInput('');
    setImageFile(null);
    setImagePreview(null);
    setAnalysisResults(null);
    setLivePriceResults(null);
    setError(null);
    setActiveTab('prices');
    setShowExtractedFeatures(false);
    setSearchQuery('');
    setPriceThreshold('');
    setFilteredProducts([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const isLoading = isAnalyzing || isGettingPrices || isSearchingByImage;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center gap-3 mb-6">
          <Zap className="text-blue-600 h-8 w-8" />
          <div>
            <h1 className="text-3xl font-bold text-gray-800">AI Product Intelligence Tool</h1>
            <p className="text-sm text-gray-600">Phase 4: Searching with extracted features</p>
          </div>
        </div>
        
        {/* Error Message Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <div className="flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Error</span>
            </div>
            <p className="mt-2 text-sm">{error}</p>
          </div>
        )}
        
        <div className="space-y-6">
          {/* Extraction Method Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Feature Extraction Method
            </label>
            <select
              value={extractionMethod}
              onChange={(e) => setExtractionMethod(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="both">Both Text & Image</option>
              <option value="text">Text Description Only</option>
              <option value="image">Image Only</option>
            </select>
          </div>

          {/* Text Input */}
          {(extractionMethod === 'text' || extractionMethod === 'both') && (
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
          )}

          {/* Image Upload */}
          {(extractionMethod === 'image' || extractionMethod === 'both') && (
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
          )}

          {/* Action Buttons */}
          <div className="flex flex-wrap gap-3 mt-6">
            <button
              onClick={analyzeInput}
              disabled={isLoading}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Zap className="h-5 w-5" />
                  <span>Analyze Product</span>
                </>
              )}
            </button>
            
            {imageFile && (
              <button
                onClick={handleImageSearch}
                disabled={isLoading}
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-3 px-6 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSearchingByImage ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <ImageIcon className="h-5 w-5" />
                    <span>Search by Image</span>
                  </>
                )}
              </button>
            )}
          </div>
          
          {/* Clear Button */}
          <div className="text-center">
            <button
              onClick={clearAll}
              disabled={isLoading}
              className="text-sm text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Clear All
            </button>
          </div>
          
        </div>
      </div>
      
      {/* Extracted Features Section */}
      {showExtractedFeatures && analysisResults && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Extracted Product Features</h2>
            <div className="text-sm text-gray-500">
              Confidence: {Math.round(analysisResults.confidence_score * 100)}%
            </div>
          </div>
          
          <ResultsDisplay results={analysisResults} type="analysis" />
          
          {/* Preview of Search Query */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Predicted Search Query</h3>
            <p className="text-sm text-gray-600 italic">
              {analysisResults.features ? 
                `${analysisResults.features.product_type || ''} ${analysisResults.features.brand || ''} ${analysisResults.features.color || ''} ${analysisResults.features.size || ''} ${analysisResults.features.material || ''} ${analysisResults.features.key_features?.slice(0, 2).join(' ') || ''}`.trim() 
                : 'No features extracted'}
            </p>
            <p className="text-xs text-gray-500 mt-2">
              This is an approximation of the search query that will be used to find similar products.
            </p>
            
            {/* Find Similar Products Button */}
            <div className="mt-4">
              <button
                onClick={handleGetLivePrices}
                disabled={isLoading}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isGettingPrices ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Finding Similar Products...</span>
                  </>
                ) : (
                  <>
                    <DollarSign className="h-5 w-5" />
                    <span>Find Similar Products</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Results Section */}
      {(analysisResults?.success || livePriceResults?.success || imageSearchResults?.success) && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {livePriceResults?.success && (
                <button
                  onClick={() => setActiveTab('prices')}
                  className={`py-3 px-4 text-sm font-medium ${
                    activeTab === 'prices'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Live Prices
                </button>
              )}
              {analysisResults?.success && (
                <button
                  onClick={() => setActiveTab('analysis')}
                  className={`py-3 px-4 text-sm font-medium ${
                    activeTab === 'analysis'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Analysis Results
                </button>
              )}
              {imageSearchResults?.success && (
                <button
                  onClick={() => setActiveTab('image-search')}
                  className={`py-3 px-4 text-sm font-medium ${
                    activeTab === 'image-search'
                      ? 'border-b-2 border-blue-500 text-blue-600'
                      : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  Image Search Results
                </button>
              )}
            </nav>
          </div>

          <div className="mt-6">
            {activeTab === 'prices' && livePriceResults && (
              <>
                {/* Price Filter Section */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Price Filter</h3>
                  <div className="flex flex-wrap items-end gap-4">
                    <div className="flex-1">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Target Price ($)
                      </label>
                      <input
                        type="number"
                        value={priceThreshold}
                        onChange={(e) => setPriceThreshold(e.target.value)}
                        placeholder="Enter price threshold"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        min="0"
                        step="0.01"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Shows products less than this price or up to 20% more
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handlePriceFilter}
                        disabled={isFiltering || !priceThreshold}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {isFiltering ? (
                          <div className="flex items-center gap-2">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Filtering...</span>
                          </div>
                        ) : (
                          <div className="flex items-center gap-2">
                            <Filter className="h-4 w-4" />
                            <span>Apply Filter</span>
                          </div>
                        )}
                      </button>
                      {filteredProducts.length > 0 && (
                        <button
                          onClick={clearFilters}
                          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                  {filteredProducts.length > 0 && (
                    <div className="mt-3 text-sm text-gray-600">
                      Showing {filteredProducts.length} of {livePriceResults.products.length} products
                      {priceThreshold && (
                        <span> (price ≤ ${parseFloat(priceThreshold).toFixed(2)} or up to ${(parseFloat(priceThreshold) * 1.2).toFixed(2)})</span>
                      )}
                    </div>
                  )}
                </div>
                <LivePriceResults 
                  results={livePriceResults} 
                  filteredProducts={filteredProducts.length > 0 ? filteredProducts : null} 
                />
              </>
            )}
            {activeTab === 'analysis' && analysisResults && (
              <ResultsDisplay results={analysisResults} type="analysis" />
            )}
            {activeTab === 'image-search' && imageSearchResults && (
              <ImageSearchResults results={imageSearchResults} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// New component for displaying live price results (Phase 3)
const LivePriceResults = ({ results, filteredProducts }) => {
  console.log('LivePriceResults rendering with:', { results, filteredProducts });
  
  if (!results) {
    console.error('LivePriceResults: No results provided');
    return (
      <div className="p-8 text-center bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-600 mb-2">No results data available.</p>
        <p className="text-sm text-gray-500">Please try searching again.</p>
      </div>
    );
  }

  const { input_features, products, price_stats, total_found, search_query, processing_time } = results;
  
  // Use filtered products if available, otherwise use all products
  const displayProducts = filteredProducts || products || [];
  
  console.log('LivePriceResults: displayProducts length:', displayProducts.length);
  
  // Calculate dynamic price statistics based on currently displayed products
  const calculatePriceStats = (products) => {
    if (!products || products.length === 0) return null;
    
    try {
      const prices = products
        .filter(p => p.price !== null && p.price !== undefined)
        .map(p => {
          // Handle both numeric and string price formats
          if (typeof p.price === 'number') return p.price;
          if (typeof p.price === 'string') {
            // Remove currency symbols and parse as float
            const cleanPrice = p.price.replace(/[^0-9.]/g, '');
            return parseFloat(cleanPrice);
          }
          return null;
        })
        .filter(price => price !== null && !isNaN(price));
      
      if (prices.length === 0) return null;
      
      const sortedPrices = [...prices].sort((a, b) => a - b);
      
      return {
        min_price: sortedPrices[0],
        max_price: sortedPrices[sortedPrices.length - 1],
        avg_price: prices.reduce((sum, price) => sum + price, 0) / prices.length,
        median_price: sortedPrices[Math.floor(sortedPrices.length / 2)],
        price_range: sortedPrices[sortedPrices.length - 1] - sortedPrices[0]
      };
    } catch (error) {
      console.error('Error calculating price stats:', error);
      return null;
    }
  };
  
  // Get dynamic price statistics based on displayed products
  const dynamicPriceStats = calculatePriceStats(displayProducts);
  
  console.log('LivePriceResults rendering with:', { 
    products: products?.length, 
    filteredProducts: filteredProducts?.length, 
    total_found,
    displayProducts: displayProducts?.length,
    dynamicPriceStats
  });

  // Handle case where there's no data to display
  if (!displayProducts || displayProducts.length === 0) {
    return (
      <div className="p-8 text-center bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-600 mb-2">No product data available.</p>
        <p className="text-sm text-gray-500">Try adjusting your search criteria or try another product.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search Info */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-purple-800 mb-2">Live Price Search</h3>
        <div className="space-y-2 text-sm">
          <div>
            <span className="font-medium text-gray-700">Search Query:</span>
            <span className="ml-2 text-gray-600">"{search_query || 'No query'}"</span>
          </div>
          {input_features && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <span className="font-medium text-gray-700">Type:</span>
                  <span className="ml-2 text-gray-600">{input_features.product_type || 'Not specified'}</span>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Category:</span>
                  <span className="ml-2 text-gray-600">{input_features.category || 'Not specified'}</span>
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
              
              {/* Display specifications if available */}
              {input_features.specifications && Object.keys(input_features.specifications).length > 0 && (
                <div className="mt-3 pt-3 border-t border-purple-200">
                  <h4 className="font-medium text-gray-700 mb-2">Specifications Used:</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {Object.entries(input_features.specifications).map(([key, value]) => (
                      <div key={key} className="bg-white rounded-md p-2 text-xs">
                        <span className="font-medium text-gray-700">{key}:</span>
                        <span className="ml-1 text-gray-600">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Display key features if available */}
              {input_features.key_features && input_features.key_features.length > 0 && (
                <div className="mt-3 pt-3 border-t border-purple-200">
                  <h4 className="font-medium text-gray-700 mb-2">Key Features Used:</h4>
                  <div className="flex flex-wrap gap-2">
                    {input_features.key_features.map((feature, index) => (
                      <span key={index} className="bg-white rounded-full px-3 py-1 text-xs text-purple-700 border border-purple-200">
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Price Statistics */}
      {dynamicPriceStats && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-800 mb-3">
            Price Statistics 
            <span className="text-sm font-normal ml-2 text-gray-600">
              (Based on {displayProducts.filter(p => p.price !== null && p.price !== undefined).length} displayed products)
            </span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">${dynamicPriceStats.min_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Lowest Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">${dynamicPriceStats.avg_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Average Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">${dynamicPriceStats.median_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Median Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">${dynamicPriceStats.max_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Highest Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">${dynamicPriceStats.price_range.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Price Range</div>
            </div>
          </div>
        </div>
      )}

      {/* Results Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-800">
          {filteredProducts ? `Showing ${displayProducts.length} Filtered Products` : `Found ${total_found} Live Products`}
        </h3>
        <div className="text-sm text-gray-500">
          Processing time: {processing_time?.toFixed(2)}s
        </div>
      </div>

      {/* Live Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {displayProducts.map((product, index) => {
          try {
            // Debug logging for products with unit_price
            if (product.unit_price || product.pack_quantity) {
              console.log('Product with pack info:', {
                title: product.title,
                price: product.price,
                unit_price: product.unit_price,
                unit_price_type: typeof product.unit_price,
                pack_quantity: product.pack_quantity,
                pack_quantity_type: typeof product.pack_quantity
              });
            }
            
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
                  <div className="flex flex-col">
                    <span className="text-2xl font-bold text-green-600">
                      ${parseFloat(product.price).toFixed(2)}
                    </span>
                    {product.unit_price && product.pack_quantity && (
                      <span className="text-sm text-blue-600 font-medium">
                        {(() => {
                          try {
                            const unitPrice = typeof product.unit_price === 'number' 
                              ? product.unit_price 
                              : parseFloat(product.unit_price);
                            if (isNaN(unitPrice)) {
                              return null;
                            }
                            return `$${unitPrice.toFixed(2)} each (${product.pack_quantity}-pack)`;
                          } catch (error) {
                            console.error('Error formatting unit price:', error, product);
                            return null;
                          }
                        })()}
                      </span>
                    )}
                  </div>
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
          } catch (error) {
            console.error('Error rendering product:', error, product);
            return (
              <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-600">Error rendering product</p>
                <p className="text-sm text-red-500">{error.message}</p>
              </div>
            );
          }
        })}
      </div>
      
      {/* No Results Message */}
      {displayProducts.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No products match the current filter criteria.</p>
        </div>
      )}
    </div>
  );
};

// Add the ImageSearchResults component
const ImageSearchResults = ({ results }) => {
  if (!results || !results.success || !results.products) {
    return (
      <div className="p-8 text-center bg-gray-50 rounded-lg border border-gray-200">
        <p className="text-gray-600 mb-2">No image search results available.</p>
        <p className="text-sm text-gray-500">Try uploading a different image or adjusting your search criteria.</p>
      </div>
    );
  }

  const { products, search_query, processing_time, total_found } = results;
  
  // Calculate dynamic price statistics for image search results
  const calculatePriceStats = (products) => {
    if (!products || products.length === 0) return null;
    
    const prices = products
      .filter(p => p.price !== null && p.price !== undefined)
      .map(p => {
        // Handle both numeric and string price formats
        if (typeof p.price === 'number') return p.price;
        if (typeof p.price === 'string') {
          // Remove currency symbols and parse as float
          const cleanPrice = p.price.replace(/[^0-9.]/g, '');
          return parseFloat(cleanPrice);
        }
        return null;
      })
      .filter(price => price !== null && !isNaN(price));
    
    if (prices.length === 0) return null;
    
    const sortedPrices = [...prices].sort((a, b) => a - b);
    
    return {
      min_price: sortedPrices[0],
      max_price: sortedPrices[sortedPrices.length - 1],
      avg_price: prices.reduce((sum, price) => sum + price, 0) / prices.length,
      median_price: sortedPrices[Math.floor(sortedPrices.length / 2)],
      price_range: sortedPrices[sortedPrices.length - 1] - sortedPrices[0]
    };
  };
  
  // Get price statistics for displayed products
  const priceStats = calculatePriceStats(products);
  
  console.log('ImageSearchResults rendering with:', {
    products: products?.length,
    total_found,
    priceStats
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Image Search Results</h2>
          <p className="text-sm text-gray-500">
            Found {total_found} results in {processing_time.toFixed(2)} seconds
          </p>
        </div>
      </div>

      {search_query && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="text-sm font-medium text-gray-700 mb-1">Predicted Search Query</h3>
          <p className="text-sm text-blue-800 font-mono bg-blue-100 p-2 rounded">{search_query}</p>
        </div>
      )}
      
      {/* Price Statistics for Image Search Results */}
      {priceStats && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-800 mb-3">
            Price Statistics 
            <span className="text-sm font-normal ml-2 text-gray-600">
              (Based on {products.filter(p => p.price !== null && p.price !== undefined).length} products with price data)
            </span>
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">${priceStats.min_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Lowest Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">${priceStats.avg_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Average Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">${priceStats.median_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Median Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">${priceStats.max_price.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Highest Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">${priceStats.price_range.toFixed(2)}</div>
              <div className="text-xs text-gray-600">Price Range</div>
            </div>
          </div>
        </div>
      )}

      {products.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No products found matching your image.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product, index) => (
            <div key={index} className="border rounded-lg overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow">
              <div className="h-48 overflow-hidden bg-gray-100">
                {product.thumbnail && (
                  <img 
                    src={product.thumbnail} 
                    alt={product.title} 
                    className="w-full h-full object-contain"
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = 'https://via.placeholder.com/300x300?text=No+Image';
                    }}
                  />
                )}
              </div>
              <div className="p-4">
                <h3 className="text-sm font-medium text-gray-900 line-clamp-2 h-10">{product.title}</h3>
                {product.price && (
                  <div className="mt-2 text-lg font-bold text-green-600">
                    ${typeof product.price === 'number' ? product.price.toFixed(2) : product.price}
                  </div>
                )}
                <div className="mt-2 flex items-center justify-between">
                  <div className="flex items-center">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Match: {Math.round(product.match_score * 100)}%
                    </span>
                  </div>
                  <a 
                    href={product.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 flex items-center gap-1 text-sm"
                  >
                    <span>View</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                {product.source && (
                  <p className="mt-2 text-xs text-gray-500 truncate">Source: {product.source}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


export default ProductAnalyzer; 