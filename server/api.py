from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .search_api import router as search_router

app = FastAPI(
    title="Research Assistant API",
    description="API for the Research Assistant",
    version="0.1.0",
    contact={
        "name": "Research Assistant",
        "url": "https://github.com/research-assistant",
        "email": "saurabh.chauhan2298@gmail.com",
    },
    license_info={
        "name": "MIT License",
    },
    docs_url="/docs",
    debug=True,
    
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api", tags=["search"])


@app.get("/")
async def base_route():
    return {"message": "Welcome to the Research Assistant API"}
