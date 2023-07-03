import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from pathlib import Path
import fitz

def pdf_to_images(pdf_file, destinationFile, dpi = 300):
    doc = fitz.open(pdf_file)

    for p in doc:
        pix = p.get_pixmap(dpi=dpi)
        pix.save(destinationFile)

def preprocess(image):
    image = image / 255.0
    return image

# Set the parameters for training the model
target_size = (500, 500)  # Target size for resizing the images.
image_path = 'C:\\Users\\conrado.camacho\\OneDrive\\Personal Projects\\ML Projects\\Managing PDF\\SourcePDFs\\11345.pdf'
modelFile = "CutContour_val_loss 20230702-2 Sigmoid.hdf5"
tempFile = "temp.png"

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
Path(tempFile).unlink()