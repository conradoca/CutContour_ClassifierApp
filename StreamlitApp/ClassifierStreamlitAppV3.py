import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from pathlib import Path
import fitz
import urllib3
import json
import time
import internetdownloadmanager as idm
import validators
from commonUtils import configParams

config = configParams()
params = config.loadConfig()

# Set the parameters for training the model
target_size = (500, 500)  # Target size for resizing the images.
#image_path = 'C:\\Users\\conrado.camacho\\OneDrive\\Personal Projects\\ML Projects\\Managing PDF\\SourcePDFs\\11345.pdf'
modelFile = "CutContour_val_loss 20230702-2 Sigmoid.hdf5"
tempFile = "temp.png"
tempPDF = "temp.pdf"
model = tf.keras.models.load_model(modelFile)

def pdf_to_images(pdf_file, destinationFile, dpi = 300):
    doc = fitz.open(pdf_file)
    #Taking only the first page. Ignoring multipages documents.
    p=doc[0]
    pix = p.get_pixmap(dpi=dpi)
    pix.save(destinationFile)

def getPreview(cimDocURL):

    http = urllib3.PoolManager()
    headers_data = {"Content-Type": "application/json", "Authorization": f"Bearer {params['token']}"}
    width = 300
    previewURL = f"https://previews.cimpress.io/v2/preview?documentReferenceUri={cimDocURL}&width={width}&panelNumber=1"
    return previewURL

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
    st.write(f"POST URL {cimDocURL} response {response.status}")

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
                        st.write(f"Result URL received: {resultURL}")
                        break
                else:
                    st.write(f'Status check failed with status code {response.status}')
                    break

                # Wait before polling again
                time.sleep(8)
    else:
        print(f'Job failed to start with status code {response.status}')
        status = "Failed"

    return status, resultURL

def downloadPDF(url, output):
    pydownloader = idm.Downloader(worker=20, part_size=1024*1024*10, resumable=False)
    pydownloader .download(url, output)

def isValidURL(url):
    return validators.url(url)

# Create the app content
def main():
    st.title("CutContour Classification App")
    st.write("Please enter a valid CimDoc URL to identify if its CutContour can be produced")

    url = st.text_input("Enter a valid CimDoc URL:")

    if st.button("Validate"):
        if isValidURL(url) == False:
            st.error("Invalid URL!")
            st.stop()

        col1, col2, col3 = st.columns([1,3,1])

        previewURL=getPreview(url)
        col2.image(previewURL, channels="BGR", width = 25, use_column_width="auto")
        #st.image(previewURL, channels="BGR", width = 25, use_column_width="auto")

        status, resultURL = SpotColorExtractor(url)
        if status != "Completed": st.stop()

        # Download PDF to local
        downloadPDF(resultURL, tempPDF)

        #Convert the PDF to PNG
        pdf_to_images(tempPDF, tempFile, 300)

        # Convert PNG to Greyscale
        img = Image.open(tempFile)
        grey_img = ImageOps.grayscale(img)
        grey_img.save(tempFile)
     
        # Prediction
        image = tf.keras.utils.load_img(tempFile, color_mode="grayscale", target_size = target_size)
        image_arr = tf.keras.utils.img_to_array(image)
        image_arr = preprocess(image_arr)
        input_arr = np.array([image_arr])  # Convert single image to a batch.
        prediction = model.predict(input_arr)

        predicted_class = 'approved' if prediction[0] > 0.5 else 'rejected'

        # Display the predicted class
        col1, col2, col3 = st.columns([1,2,1])
        col2.write(f"Prediction: {predicted_class} ({prediction[0][0]:.4f})")

        # Display the uploaded image
        col2.image(grey_img, caption='CutContour Shape', channels="BGR", width = 25, use_column_width="auto")
        #st.image(grey_img, caption='CutContour Shape', channels="BGR", width = 25, use_column_width="auto")

        #Remove the temp file
        Path(tempFile).unlink()
        Path(tempPDF).unlink()

if __name__ == "__main__":
    main()