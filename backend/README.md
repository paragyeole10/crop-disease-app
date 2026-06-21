# AgriVision AI Backend

This is the FastAPI backend for the AgriVision AI application. It loads a trained MobileNetV2 Keras model to classify crop leaf diseases.

## 🚀 How to Run the Backend Server

Follow these steps to run the server on your local machine:

### 1. Open Terminal & Navigate to Backend
Open your PowerShell or Command Prompt, and navigate to the backend directory:
```powershell
cd d:\Crop_app\backend
```

### 2. Create and Activate a Virtual Environment (Recommended)
A virtual environment keeps your Python packages isolated and clean.
```powershell
# Create the environment
python -m venv venv

# Activate it (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate it (Command Prompt / cmd)
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies
Install all required libraries listed in `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 4. Run the Server
Run the Uvicorn server. We bind it to `0.0.0.0` so it is accessible to other devices (like your mobile phone running Expo) on your local Wi-Fi network:
```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## ⚙️ Configuration details

* **Port**: Runs on port `8000`.
* **Model Path**: Loads the crop disease model from `d:\Crop_app\mobilenet_crop_disease.keras`.
* **Environment Variables**: Managed via the `.env` file in this directory.
* **Main API Endpoints**:
  * `POST /api/v1/predict` - Uploads a crop leaf image for disease diagnosis.
  * `GET /api/v1/disease/{name}` - Gets detailed description, causes, and treatments for a disease.
  * `POST /api/v1/translate` - Translates text between English, Hindi, and Marathi.
  * `POST /api/v1/text-to-speech` - Generates TTS audio for assistant replies.
  * `POST /api/v1/speech-to-text` - Transcribes voice messages.
