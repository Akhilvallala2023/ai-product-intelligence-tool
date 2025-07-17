# AI Product Intelligence Tool - Frontend

## Environment Configuration

### Local Development

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_DEV_MODE=true
```

### Production Deployment

For production deployment (e.g., Netlify), set the following environment variables:

```env
VITE_API_URL=https://your-backend-service.onrender.com
VITE_DEV_MODE=false
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `https://your-backend.onrender.com` |
| `VITE_DEV_MODE` | Development mode flag | `true` or `false` |

## Deployment Instructions

### Netlify Deployment

1. **Set Environment Variables in Netlify:**
   - Go to Site Settings > Environment Variables
   - Add `VITE_API_URL` with your backend URL
   - Add `VITE_DEV_MODE` set to `false`

2. **Build Settings:**
   - Build command: `npm run build`
   - Publish directory: `dist`

### Backend Deployment

The backend should be deployed to a service like:
- Render (recommended)
- Railway
- Heroku
- DigitalOcean App Platform

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## API Endpoints

The frontend communicates with the following backend endpoints:

- `POST /api/analyze-form` - Product analysis
- `POST /api/live-prices-form` - Live price search
- `POST /api/image-search-form` - Image-based search 