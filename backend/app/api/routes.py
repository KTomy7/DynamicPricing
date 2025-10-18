from fastapi import APIRouter
from app.services.dynamic_pricing_service import simulate_dynamic_pricing

router = APIRouter()

@router.get("/simulate")
async def simulate_dynamic_pricing():
    results = simulate_dynamic_pricing()
    return results
