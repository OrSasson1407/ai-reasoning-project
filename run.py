import uvicorn
from ai_reasoning.config import SystemConfig

if __name__ == "__main__":
    print("=====================================================")
    print(" AI Reasoning Project - Architecture v2.0 Initialize")
    print("=====================================================")
    print(f" Strict Contract Enforcement: {SystemConfig.STRICT_CONTRACT_ENFORCEMENT}")
    print(f" Confidence Floor Rule UP-10: {SystemConfig.CONFIDENCE_FLOOR}")
    print("=====================================================")
    
    # Starts the FastAPI application defined in API interface contracts
    uvicorn.run("ai_reasoning.api.main:app", host="0.0.0.0", port=8000, reload=True)
