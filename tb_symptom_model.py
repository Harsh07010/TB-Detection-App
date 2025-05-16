from flask import Blueprint, request, jsonify
import joblib

symptom_app = Blueprint("symptom_app", __name__)
model = joblib.load("models/final_text_model.pkl")

@symptom_app.route("/predict_symptom", methods=["POST"])
def predict_tb():
    data = request.json
    features = data.get("features")
    prediction = model.predict([features])[0]
    return jsonify({"result": "Likely" if prediction == 1 else "Unlikely"})
