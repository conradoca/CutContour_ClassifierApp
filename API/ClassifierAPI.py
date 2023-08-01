# Launch with: 
# uvicorn ClassifierAPI:app --reload

import asyncio
import uuid
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from urllib.parse import urlparse
from urllib.request import urlopen
from io import BytesIO
from PIL import Image, ImageOps
import tensorflow as tf
import numpy as np

app = FastAPI()

results = {}
target_size = (500, 500)  # Target size for resizing the images.
modelFile = "CutContour_val_loss 20230702-2 Sigmoid.hdf5"
model = tf.keras.models.load_model(modelFile)

class Item(BaseModel):
    Url: str
    Threshold: Optional[float] = 0.5

async def checkSpotColor(handler_id, artworkURL, threshold = 0.5):
    # Loading the Image from URL
    with urlopen(artworkURL) as response:
        image_data = response.read()
    image_stream = BytesIO(image_data)

    # Converting the image in a PIL object and preprocess it
    img = Image.open(image_stream)
    grey_img = ImageOps.grayscale(img)
    grey_img_resized = grey_img.resize(target_size)
    image_arr = tf.keras.utils.img_to_array(grey_img_resized)
    image_arr /= 255.

    input_arr = np.array([image_arr])  # Convert single image to a batch.
    prediction = model.predict(input_arr)
    predictionValue = float(prediction[0][0])
    outcome = "approved" if predictionValue > threshold else "rejected"

    # Create a dictionary to store the response
    result_dict = {
        "artworkURL": artworkURL,
        "threshold": threshold,
        "predictionValue": predictionValue,
        "outcome" : outcome
    }


    results[handler_id] = result_dict


@app.post("/check_file/")
async def check_file(requestJSON: Item, background_tasks: BackgroundTasks, request: Request):
    print(f"Received request: {request.method} {request.url.path}")
    print(f"Request url: {request.base_url}")
    print(f"Request headers: {request.headers}")
    print(f"Request body: {await request.json()}")
    
    request_JSON = requestJSON.dict()
    handler_id = str(uuid.uuid4())  # Generate a unique handler ID
    background_tasks.add_task(checkSpotColor, handler_id, request_JSON["Url"], request_JSON["Threshold"])

    # Normalize the received base_url
    requestBaseURL= str(request.base_url)
    parsed_url = urlparse(requestBaseURL)
    normalized_url = parsed_url._replace(path='/', query='', fragment='')
    baseURL = normalized_url.geturl()

    # Prepare the response
    response ={}
    response["Status"] = "Running"
    response["ResultName"] = f"{handler_id}"
    response["ResultURL"] = f"{baseURL}result/{handler_id}"

    return JSONResponse(content=response, status_code=201)


@app.get("/result/{handler_id}")
async def get_result(handler_id: str):

    if handler_id not in results:
        return {"status": "Running"}
    result = results[handler_id]
    # Prepare the response
    response ={}
    response["Status"] = "Completed"
    response["Result"] = result
    return JSONResponse(content=response, status_code=200)