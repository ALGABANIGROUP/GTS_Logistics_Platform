"""
Integration guide for Transport Mapping System

Add these lines to your backend/main.py:

```python
# After other imports, add:
from backend.routes.transport_tracking_api import router as transport_router

# In your app setup, add:
app.include_router(transport_router)
```

All transport endpoints will be available at:
- Base URL: http://localhost:8000/api/v1/transport/*
- WebSocket: ws://localhost:8000/api/v1/transport/ws/*
"""

# Example implementation for main.py integration:

def setup_transport_routes(app):
    """
    Add transport routing to FastAPI application
    
    Usage in main.py:
        from backend.routes.setup import setup_transport_routes
        setup_transport_routes(app)
    """
    try:
        from backend.routes.transport_tracking_api import router as transport_router
        app.include_router(transport_router)
        print("✓ Transport tracking routes registered")
    except ImportError as e:
        print(f"Warning: Could not import transport routes: {e}")


def create_transport_tables(engine):
    """
    Create transport-related database tables
    
    Usage in main.py:
        from backend.models.truck_location import Base
        from backend.database import engine
        from backend.routes.setup import create_transport_tables
        
        create_transport_tables(engine)
    """
    try:
        from backend.models.truck_location import Base
        Base.metadata.create_all(bind=engine)
        print("✓ Transport tables created")
    except Exception as e:
        print(f"Warning: Could not create transport tables: {e}")
