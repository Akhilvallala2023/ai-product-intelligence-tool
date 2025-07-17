// Test environment variables
console.log('Environment Variables Test:');
console.log('VITE_API_URL:', import.meta.env.VITE_API_URL);
console.log('VITE_DEV_MODE:', import.meta.env.VITE_DEV_MODE);
console.log('BASE_URL (computed):', import.meta.env.VITE_API_URL || 'http://localhost:8000'); 