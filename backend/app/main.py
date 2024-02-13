from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
import io
from PIL import Image
import cv2
import tensorflow as tf
import os 

app = FastAPI()

origins = ["*",
    "http://frontend:3000",
    "http://frontend:3006"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
async def ping() :
    return "Server is alive"

path = os.path.dirname(__file__)
# path = path[:len(path) - 3]        # removing api from path
MODEL = tf.keras.models.load_model( path + "/TL")
# MODEL = tf.keras.models.load_model( "../saved_models/TL")
CLASS_NAMES = ["Random", "Monument"]

def read_file_as_image(data) :
    img = Image.open(io.BytesIO(data)).convert('RGB')
    image = np.array(img)
    image = cv2.resize(image, (224,224))/255
    image = image.reshape(1,224, 224, 3)
    # image = Image.convert('RGB')
    # type(image)
    return image

@app.post("/predict")
async def predict(file: UploadFile = File(...)) :
    image = read_file_as_image(await file.read())
    prediction = float(MODEL.predict(image))
    # print(f" pre = {prediction}")
    
    predicted_class = CLASS_NAMES[1 if prediction > 0.5 else 0]
    prediction = 1 - prediction if prediction < 0.5 else prediction
    
    return {
        'class' : predicted_class,
        'confidence' : prediction
    }

# if __name__ == "__main__" :
#     uvicorn.run(app, host = 'localhost', port = 8000)