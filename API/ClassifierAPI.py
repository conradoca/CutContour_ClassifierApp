# Launch with: 
# uvicorn ClassifierAPI:app --reload

import asyncio
import time
from fastapi import FastAPI, BackgroundTasks, Request
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

results = {}

class Item(BaseModel):
    url: str
    description: Optional[str] = None

async def perform_check(handler_id, url):
    # Simulating some time-consuming task
    await asyncio.sleep(5)
    # Simulating the result
    lines_count = len(url)
    results[handler_id] = lines_count


@app.post("/check_file/")
async def check_file(requestJSON: Item, background_tasks: BackgroundTasks, request: Request):
    print(f"Received request: {request.method} {request.url.path}")
    print(f"Request headers: {request.headers}")
    print(f"Request body: {await request.json()}")
    request_JSON = requestJSON.dict()
    handler_id = str(int(time.time()))  # Generate a unique handler ID
    background_tasks.add_task(perform_check, handler_id, request_JSON["url"])
    return {"handler_id": handler_id}


@app.get("/check_file/{handler_id}")
async def get_result(handler_id: str):
    if handler_id not in results:
        return {"status": "processing"}
    result = results[handler_id]
    return {"status": "completed", "result": result}