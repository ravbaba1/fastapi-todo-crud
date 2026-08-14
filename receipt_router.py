import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

# We use APIRouter instead of FastAPI() so it can be plugged into your existing file
router = APIRouter(tags=["Receipt AI Parser"])

# 1. THE SCHEMA: Forces the AI to output exactly this format
class ReceiptAnalysis(BaseModel):
    store_name: str = Field(description="The clean name of the store or restaurant")
    total_amount: float = Field(description="The total price paid as a decimal number")
    currency: str = Field(description="The 3-letter currency code, e.g., USD, EUR, NGN")

class ReceiptInput(BaseModel):
    raw_text: str

# 2. RETRIES: Automatically handles network glitches or rate limits
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.NetworkError)),
    reraise=True
)
def call_ai_with_retry(client: Groq, text: str) -> str:
    # 3. TIMEOUT: Cuts off the connection if the AI takes longer than 5 seconds
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user", 
                "content": f"Extract store_name, total_amount, and currency from this receipt text and return them as a JSON object:\n\n{text}"
            }
        ],
        response_format={"type": "json_object"},
        timeout=5.0 
    )
    return response.choices[0].message.content

# Our new isolated endpoint
@router.post("/analyze-receipt", response_model=ReceiptAnalysis)
async def analyze_receipt(payload: ReceiptInput):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is missing")
        
    client = Groq(api_key=api_key)
    
    try:
        ai_raw_response = call_ai_with_retry(client, payload.raw_text)
        validated_data = ReceiptAnalysis.model_validate_json(ai_raw_response)
        return validated_data

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI model took too long to respond.")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to process receipt: {str(e)}")