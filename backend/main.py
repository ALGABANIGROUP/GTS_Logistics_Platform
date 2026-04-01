# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import sys

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

# استيراد الـ routes
from routes import auth  # هذا السطر مهم جداً!

app = FastAPI(
    title='GTS Logistics Platform',
    version='2.0.0',
    docs_url='/docs'
)

# CORS
ALLOWED_ORIGINS = os.getenv('GTS_CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# إضافة الـ routes - هذا هو المفتاح!
app.include_router(auth.router, prefix='/api/v1')

@app.get('/')
async def root():
    return {
        'message': 'GTS Logistics Platform API',
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'version': '2.0.0'
    }

@app.get('/health')
async def health():
    return {
        'status': 'healthy',
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'timestamp': datetime.now().isoformat()
    }
