from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes

app = FastAPI(title="Dynamic Pricing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",  # frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api/DynamicPricing")

@app.get("/")
async def root():
    return {"message": "Dynamic Pricing API is running."}
