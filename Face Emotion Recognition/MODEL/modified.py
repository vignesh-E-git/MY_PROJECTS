from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import cv2
from tensorflow import keras
import os
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='../../webapp', static_url_path='')
CORS(app)

# Emotion names for FER dataset
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]

# Load model at startup
MODEL_PATH = "D:/ANTIGRAVITY/project-1/FaceEmotion/source/experiments/FER_MINI-XCEPTION_RUN_00/model.hdf5"
print("Loading model...")
model = keras.models.load_model(MODEL_PATH)
print("Model loaded successfully!")

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """Preprocess image for emotion detection (same as predict.py)"""
    # Read image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image not found or unreadable: " + image_path)

    # Mini-Xception expects 48x48 grayscale
    image = cv2.resize(image, (48, 48))
    image = image.astype("float32") / 255.0

    # Expand dims: (48,48) → (48,48,1)
    image = np.expand_dims(image, axis=-1)

    # Batch dimension: (48,48,1) → (1,48,48,1)
    image = np.expand_dims(image, axis=0)
    return image

@app.route('/')
def index():
    """Serve the intro page"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/app.html')
def app_page():
    """Serve the main app page"""
    return send_from_directory(app.static_folder, 'app.html')

@app.route('/predict', methods=['POST'])
def predict():
    """API endpoint for emotion prediction"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400
        
        # Save file securely
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Preprocess and predict
        image = preprocess_image(filepath)
        preds = model.predict(image)
        
        # Get prediction results
        emotion_index = np.argmax(preds)
        emotion_label = EMOTIONS[emotion_index]
        confidence = float(preds[0][emotion_index])
        
        # Create confidence scores for all emotions
        all_confidences = {
            EMOTIONS[i]: float(preds[0][i]) for i in range(len(EMOTIONS))
        }
        
        # Clean up uploaded file
        os.remove(filepath)
        
        # Return results
        return jsonify({
            'success': True,
            'emotion': emotion_label,
            'confidence': confidence,
            'all_confidences': all_confidences
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Face Emotion Detection Server")
    print("="*50)
    print(f"Server running at: http://localhost:5000")
    print("Press CTRL+C to stop the server")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
