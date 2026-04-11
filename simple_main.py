from fastapi import FastAPI
from backend.routes.invoices import router as invoices_router

app = FastAPI(title="GTS Logistics API", version="1.0.0")

# Include the invoice router
app.include_router(invoices_router, prefix="/api/v1/invoices")

@app.get("/")
async def root():
    return {"message": "GTS Logistics API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8006)