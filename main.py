from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import Controllers.Emailcontroller,Controllers.WhatsAppController,Controllers.TwitterController
# Create FastAPI app
app = FastAPI(
    title="Fresh FastAPI Project",
    description="A clean FastAPI application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Controllers.Emailcontroller.route)
app.include_router(Controllers.WhatsAppController.route)
app.include_router(Controllers.TwitterController.route)
# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Fresh FastAPI Project!", "status": "running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}

# Simple test endpoint
@app.get("/test")
async def test_endpoint():
    return {"message": "Test endpoint is working!", "data": {"test": True}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
