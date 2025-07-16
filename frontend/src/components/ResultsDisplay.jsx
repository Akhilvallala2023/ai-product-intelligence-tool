import React from 'react'
import { 
  Package, 
  Tag, 
  Palette, 
  Ruler, 
  ShoppingBag, 
  Star, 
  Info, 
  Eye,
  FileText,
  Image,
  Zap,
  Search,
  Scan,
  Layers,
  Text
} from 'lucide-react'

const ResultsDisplay = ({ results, type = 'analysis' }) => {
  if (!results || !results.success || !results.features) {
    return null
  }

  const { features, confidence_score, processing_time } = results

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getConfidenceLabel = (score) => {
    if (score >= 0.8) return 'High'
    if (score >= 0.6) return 'Medium'
    return 'Low'
  }

  const FeatureItem = ({ icon, label, value, className = '' }) => {
    if (!value) return null
    
    return (
      <div className={`flex items-center space-x-3 p-3 bg-gray-50 rounded-lg ${className}`}>
        <div className="flex-shrink-0">
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-700">{label}</p>
          <p className="text-sm text-gray-600">{value}</p>
        </div>
      </div>
    )
  }

  // Group specifications into categories for better organization
  const groupSpecifications = () => {
    if (!features.specifications || Object.keys(features.specifications).length === 0) {
      return {};
    }

    const groups = {
      'Light Properties': ['Light Source Type', 'Light Color', 'Brightness', 'Wattage', 'Bulb Type'],
      'Power & Installation': ['Power Source', 'Installation Type', 'Voltage', 'Connection Type'],
      'Physical Properties': ['Shape', 'Finish', 'Dimensions', 'Weight', 'Material Type'],
      'Features & Usage': ['Special Feature', 'Indoor/Outdoor Usage', 'Theme', 'Occasion', 'Compatibility'],
      'Other': []
    };

    const result = {};
    const processedKeys = new Set();

    // First pass: assign specs to specific groups
    Object.entries(features.specifications).forEach(([key, value]) => {
      for (const [groupName, groupKeys] of Object.entries(groups)) {
        if (groupKeys.some(groupKey => key.toLowerCase().includes(groupKey.toLowerCase()))) {
          if (!result[groupName]) result[groupName] = {};
          result[groupName][key] = value;
          processedKeys.add(key);
          break;
        }
      }
    });

    // Second pass: assign remaining specs to "Other"
    Object.entries(features.specifications).forEach(([key, value]) => {
      if (!processedKeys.has(key)) {
        if (!result['Other']) result['Other'] = {};
        result['Other'][key] = value;
      }
    });

    return result;
  };

  const groupedSpecs = groupSpecifications();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Scan className="w-6 h-6 text-blue-600" />
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Google Lens-like Analysis</h2>
            <p className="text-xs text-gray-500">Visual feature extraction & object recognition</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`px-3 py-1 rounded-full text-xs font-medium ${getConfidenceColor(confidence_score)}`}>
            {getConfidenceLabel(confidence_score)} ({Math.round(confidence_score * 100)}%)
          </div>
        </div>
      </div>

      {/* Visual Analysis Stages */}
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Visual Analysis Process</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-2">
          <div className="bg-white rounded-lg p-3 flex flex-col items-center text-center">
            <Layers className="w-5 h-5 text-blue-500 mb-2" />
            <h4 className="text-xs font-medium text-gray-700">Feature Extraction</h4>
            <p className="text-xs text-gray-500">Shapes, patterns, colors</p>
          </div>
          <div className="bg-white rounded-lg p-3 flex flex-col items-center text-center">
            <Eye className="w-5 h-5 text-purple-500 mb-2" />
            <h4 className="text-xs font-medium text-gray-700">Object Recognition</h4>
            <p className="text-xs text-gray-500">Product type & model</p>
          </div>
          <div className="bg-white rounded-lg p-3 flex flex-col items-center text-center">
            <Text className="w-5 h-5 text-green-500 mb-2" />
            <h4 className="text-xs font-medium text-gray-700">Text Recognition</h4>
            <p className="text-xs text-gray-500">Labels & markings</p>
          </div>
          <div className="bg-white rounded-lg p-3 flex flex-col items-center text-center">
            <Zap className="w-5 h-5 text-yellow-500 mb-2" />
            <h4 className="text-xs font-medium text-gray-700">Context Analysis</h4>
            <p className="text-xs text-gray-500">Visual cues & inference</p>
          </div>
          <div className="bg-white rounded-lg p-3 flex flex-col items-center text-center">
            <Search className="w-5 h-5 text-red-500 mb-2" />
            <h4 className="text-xs font-medium text-gray-700">Matching</h4>
            <p className="text-xs text-gray-500">Finding similar products</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FeatureItem
            icon={<Tag className="w-5 h-5 text-blue-500" />}
            label="Brand"
            value={features.brand}
          />
          <FeatureItem
            icon={<Package className="w-5 h-5 text-green-500" />}
            label="Model"
            value={features.model}
          />
          <FeatureItem
            icon={<ShoppingBag className="w-5 h-5 text-purple-500" />}
            label="Product Type"
            value={features.product_type}
          />
          <FeatureItem
            icon={<Palette className="w-5 h-5 text-pink-500" />}
            label="Color"
            value={features.color}
          />
        </div>

        {/* Additional Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FeatureItem
            icon={<Ruler className="w-5 h-5 text-orange-500" />}
            label="Size"
            value={features.size}
          />
          <FeatureItem
            icon={<Star className="w-5 h-5 text-yellow-500" />}
            label="Material"
            value={features.material}
          />
          <FeatureItem
            icon={<Info className="w-5 h-5 text-gray-500" />}
            label="Style"
            value={features.style}
          />
          <FeatureItem
            icon={<ShoppingBag className="w-5 h-5 text-indigo-500" />}
            label="Category"
            value={features.category}
          />
        </div>

        {/* Key Features */}
        {features.key_features && features.key_features.length > 0 && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
              <Star className="w-4 h-4 text-blue-500 mr-2" />
              Key Features
            </h3>
            <div className="flex flex-wrap gap-2">
              {features.key_features.map((feature, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full"
                >
                  {feature}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Specifications - Grouped by category */}
        {Object.keys(groupedSpecs).length > 0 && (
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-4 flex items-center">
              <Info className="w-4 h-4 text-green-500 mr-2" />
              Detailed Specifications
            </h3>
            
            <div className="space-y-4">
              {Object.entries(groupedSpecs).map(([groupName, specs]) => (
                Object.keys(specs).length > 0 && (
                  <div key={groupName} className="bg-white rounded-lg p-3">
                    <h4 className="text-sm font-medium text-gray-700 mb-2 border-b pb-2">{groupName}</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {Object.entries(specs).map(([key, value]) => (
                        <div key={key} className="flex justify-between items-center p-1">
                          <span className="text-sm font-medium text-gray-600 capitalize">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="text-sm text-gray-900 bg-gray-50 px-2 py-1 rounded">{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              ))}
            </div>
          </div>
        )}

        {/* Analysis Summary */}
        <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Analysis Summary</h3>
          <p className="text-sm text-gray-600">
            Successfully extracted product features using Google Lens-like visual analysis with {getConfidenceLabel(confidence_score).toLowerCase()} confidence 
            ({Math.round(confidence_score * 100)}%). 
            Processing completed in {processing_time?.toFixed(2) || 'N/A'} seconds.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ResultsDisplay 