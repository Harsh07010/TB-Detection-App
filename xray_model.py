from flask import Blueprint, request, jsonify
import joblib
from PIL import Image
import numpy as np
from torchvision import transforms

xray_app = Blueprint("xray_app", __name__)
model = joblib.load("models/resnet_model.pkl")  

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

@xray_app.route("/predict_xray", methods=["POST"])
def predict_xray():
    image = Image.open(request.files["image"]).convert("RGB")
    image = transform(image).numpy()
    image = np.transpose(image, (1, 2, 0))  # back to HWC
    image = image.flatten().reshape(1, -1)  # flatten image

    prediction = model.predict(image)[0]
    return jsonify({"result": "Consult doctor" if prediction == 1 else "Normal"})
