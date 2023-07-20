import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from pathlib import Path
import fitz
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

    for p in doc:
        pix = p.get_pixmap(dpi=dpi)
        pix.save(destinationFile)

def preprocess(image):
    image = image / 255.0
    return image



# Create the app content
def main():
    st.title("CutContour Classification App")
    st.write("Upload a PDF to identify if its CutContour can be produced")

    # File uploader
    uploaded_file = st.file_uploader("Choose an image", type=["pdf"])

    if uploaded_file is not None:
        
        #image_file = {"FileName":uploaded_file.name,"FileType":uploaded_file.type}
        
        with open(tempPDF,"wb") as f: 
            f.write(uploaded_file.getbuffer()) 


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
        st.write(f"Prediction: {predicted_class} ({prediction[0][0]:.4f})")

        # Display the uploaded image
        st.image(grey_img, caption='Uploaded Image', channels="BGR", width = 25, use_column_width="auto")

        #Remove the temp file
        Path(tempFile).unlink()
        Path(tempPDF).unlink()

if __name__ == "__main__":
    main()