import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI,Form
from pydantic import BaseModel
from agents.reasoning_agent import reason_about_user

app = FastAPI()

class RequestData(BaseModel):
    text: str

@app.post("/process")
async def process(user_text:str=Form(...)):
    result = reason_about_user(
        user_text=user_text,
        summary="",
        entities={}
    )
    return result