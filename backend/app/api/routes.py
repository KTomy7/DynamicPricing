from fastapi import APIRouter
from app.services.dynamic_pricing_service import simulate_dynamic_pricing

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Dynamic Pricing API is running."}

@router.get("/simulate")
def simulate_dynamic_pricing_endpoint():
    try:
        print("simulate_dynamic_pricing")
        results = simulate_dynamic_pricing()
        return results
    except Exception as e:
        import traceback
        print("❌ ERROR in /simulate endpoint:", e)
        traceback.print_exc()
        return {"error": str(e)}
