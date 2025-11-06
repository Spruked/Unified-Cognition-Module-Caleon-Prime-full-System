# api.py - FastAPI interface for Resonator
from fastapi import FastAPI, Request
from pydantic import BaseModel
from resonator_core.resonator import Resonator
import uvicorn
import json

app = FastAPI()
resonator = Resonator()

class InputData(BaseModel):
    input: dict
    telemetry: bool = True

@app.post("/reasonate")
def reasonate(data: InputData):
    result = resonator.process(data.input, telemetry=data.telemetry)
    return result

@app.get("/")
def root():
    return {"status": "Resonator API is running"}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
