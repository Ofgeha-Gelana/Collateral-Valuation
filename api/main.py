# api/main.py

from fastapi import FastAPI
from .models import ValuationRequest, ValuationResponse
from core.calculation_engine import run_full_valuation

app = FastAPI(
    title="CBO Property Valuation API",
    description="An API to perform property valuations based on the CBO manual.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Valuation API. Please use the /docs endpoint to see the API documentation."}

@app.post("/estimate", response_model=ValuationResponse)
def create_estimation(request: ValuationRequest):
    """
    Receives property and building data, performs a full valuation,
    and returns the estimated values.
    """
    # The Pydantic model is automatically converted to a dictionary
    valuation_results = run_full_valuation(request.dict())
    return valuation_results
