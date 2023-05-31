# Import necessary modules
# import firebase_admin
from PIL import Image
import io
import requests
import numpy as np
import os
import tensorflow as tf


from PIL import Image
from flask import Flask, request, jsonify, json
# from firebase_admin import credentials, firestore
from keras.models import load_model
from werkzeug.utils import secure_filename

# Load Firebase service account credentials
app = Flask(__name__)

# Load model
model = tf.keras.models.load_model('app/models/Model_1.h5')

# Load penyakit data
with open('app/myPlant-json/penyakit.json') as json_file:
    contoh = json.load(json_file)


# Tes Utama
@app.route('/', methods=['GET'])
def welcome():
    return "Response Success!"


# Endpoint untuk menampilkan semua penyakit
@app.route('/penyakit', methods=['GET'])
def pagePenyakit():
    try:
        filtered_data = [{"nama": penyakit['nama'], "deskripsi": penyakit['deskripsi']} for penyakit in contoh]
    except:
        return jsonify({'Nama penyakit tidak ditemukan'})
    return jsonify(filtered_data), 200


# Endpoint menampilkan penyakit berdasarkan id
@app.route('/penyakit/<string:penyakit>', methods=['GET'])
def namaPenyakit(penyakit):
    penyakit_id = penyakit
    for penyakit_data in contoh:
        if penyakit_data['id'] == penyakit_id:
            return jsonify(penyakit_data), 200
    return jsonify({'message': 'Penyakit tidak ditemukan!'}), 400


# Preprocessing Gambar
def read_image(img):
    img = Image.open(io.BytesIO(img))
    img = img.resize((224, 224))
    img_tensor = tf.keras.preprocessing.image.img_to_array(img)
    img_tensor = np.expand_dims(img_tensor, axis=0)
    img_tensor /= 255.0
    return img_tensor


# Prediksi Penyakit Tanaman
@app.route("/predict", methods=['POST'])
def predict():
    if 'file' not in request.files:
        return "Please try again. The Image doesn't exist"
    
    file = request.files.get('file')

    if not file:
        return

    # Membaca input file
    img_bytes = file.read()

    basepath = os.path.dirname(__file__)
    file_path = os.path.join(
        basepath, 'uploads', secure_filename(file.filename))
    file.save(file_path)

    # File image untuk prediksi
    images = read_image(img_bytes)


    try:
        prediction_labels = [
            "Apple Scab",
            "Apple Black Rot",
            "Apple Cedar rust",
            "Apple Healthy",
            "Corn Cercospora Leaf Spot | Gray Leaf Spot",
            "Corn Common Rust",
            "Corn Northern Leaf Blight",
            "Corn Healthy",
            "Grape Black Rot",
            "Grape Esca | Black Measles",
            "Grape Leaf Blight | Isariopsis Leaf Spot",
            "Grape Healthy",
            "Potato Early Blight",
            "Potato Late Blight",
            "Potato Healthy",
            "Strawberry Leaf Scorch",
            "Strawberry Healthy"
        ]

        prediction = np.argmax(model.predict(images)[0])
        result = prediction_labels[prediction]

        return {
            'prediction': result
        }
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__=="__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)