import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from pathlib import Path
import fitz
import urllib3
import json
import time
from commonUtils import configParams
import internetdownloadmanager as idm

def pdf_to_images(pdf_file, destinationFile, dpi = 300):
    doc = fitz.open(pdf_file)

    for p in doc:
        pix = p.get_pixmap(dpi=dpi)
        pix.save(destinationFile)

def preprocess(image):
    image = image / 255.0
    return image

def SpotColorExtractor (cimDocURL):
    
    http = urllib3.PoolManager()
    headers_data = {"Content-Type": "application/json", "Authorization": f"Bearer {params['token']}"}
    status = ""
    resultURL = ""

    data = {"DocumentReferenceUrl": f"{cimDocURL}",
        "Parameters": {
            "type": "PrintPrep.V2.Parameters",
            "outputFormat": "PDF",
            "customPreflightProfileUrl": f"{params['SpotColorExtractorURL']}"
            }
        }
    encoded_data = json.dumps(data).encode('utf-8')
    response = http.request('POST', params['printPrepURL'], body=encoded_data, headers=headers_data)
    # Manage response from remote API for access errors
    print(f"POST URL {cimDocURL} response {response.status}")

    if response.status == 200:
        data = json.loads(response.data)
        status = data['Status']

        if status != 'Failed':
            
            resultURL = data['ResultUrl']
            
            # Poll the status URL until the job is completed
            start_time = time.time()
            while True:
                # Check if the timeout has been exceeded
                elapsed_time = time.time() - start_time
                if elapsed_time > 60:
                    print('Job completion check timed out.')
                    break
                
                response = http.request('GET', resultURL)
                
                # Check the status of the job
                if response.status == 200:
                    cbData = json.loads(response.data)
                    
                    # If the job is completed, print the results and break the loop
                    status = cbData['Status']
                    if  status == 'Completed':
                        resultURL = cbData['Output']
                        print(f"Result URL received: {resultURL}")
                        break
                else:
                    print(f'Status check failed with status code {response.status}')
                    break

                # Wait before polling again
                time.sleep(10)
    else:
        print(f'Job failed to start with status code {response.status}')
        status = "Failed"

    return status, resultURL

def downloadPDF(url, output):
    pydownloader = idm.Downloader(worker=20, part_size=1024*1024*10, resumable=False)
    pydownloader .download(url, output)


# Import Configuration Parameters
config = configParams()
params = config.loadConfig()

# Set the parameters for training the model
target_size = (500, 500)  # Target size for resizing the images.
image_path = 'C:\\Users\\conrado.camacho\\OneDrive\\Personal Projects\\ML Projects\\Managing PDF\\SourcePDFs\\11345.pdf'
modelFile = "CutContour_val_loss 20230702-2 Sigmoid.hdf5"
image_path = "temp.pdf"
tempFile = "temp.png"

# Extract the CutContour file
origURL="https://uploads.documents.cimpress.io/v1/uploads/72bb3580-8a21-4116-8f22-886e944e03c3~100?tenant=prepress-uploads"
status, resultURL = SpotColorExtractor(origURL)
if status != "Completed": exit()

# Download PDF to local
downloadPDF(resultURL, image_path)
########################################

# Convert PDF to PNG
pdf_to_images(image_path, tempFile, 300)

# Convert PNG to Greyscale
img = Image.open(tempFile)
grey_img = ImageOps.grayscale(img)
grey_img.save(tempFile)

image = tf.keras.utils.load_img(tempFile, color_mode="grayscale", target_size = target_size)
image_arr = tf.keras.utils.img_to_array(image)
image_arr = preprocess(image_arr)
input_arr = np.array([image_arr])  # Convert single image to a batch.

model = tf.keras.models.load_model(modelFile)
prediction = model.predict(input_arr)

predicted_class = 'approved' if prediction[0] > 0.5 else 'rejected'

# Display the predicted class
print(f"Prediction: {predicted_class} ({prediction[0][0]:.4f})")
Path(image_path).unlink()
Path(tempFile).unlink()