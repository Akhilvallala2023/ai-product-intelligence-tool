import React from 'react'
import ProductAnalyzer from './components/ProductAnalyzer'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <ProductAnalyzer />
      
      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              AI Product Intelligence Tool - Phase 2: Matching Engine
            </p>
            <p className="text-sm text-gray-500">
              Powered by OpenAI GPT-4o Vision + Embeddings
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App 