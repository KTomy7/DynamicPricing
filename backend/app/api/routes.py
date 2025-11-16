from fastapi import APIRouter
from app.services.dynamic_pricing_service import simulate_dynamic_pricing, run_and_analyze_simulations

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

@router.get("/analyze")
async def analyze_multiple_runs(runs: int = 100):
    try:
        print("run_and_analyze_simulations")
        summary = run_and_analyze_simulations(n_runs=runs)
        return summary
    except Exception as e:
        import traceback
        print("❌ ERROR in /analyze endpoint:", e)
        traceback.print_exc()
        return {"error": str(e)}
