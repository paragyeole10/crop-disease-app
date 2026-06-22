# 🌱 AgriVision AI - System Architecture, ML Data Flow & Judge Q&A Guide

Welcome to the **AgriVision AI** technical guide. This document details the exact flow of data from a farmer's smartphone to our deep learning model, outlines our technical stack, and provides answers to questions that hackathon judges are likely to ask.

---

## 1. High-Level System Architecture

AgriVision AI utilizes a decoupled client-server architecture designed to run high-performance AI inference while maintaining a lightweight mobile client.

```text
       MOBILE CLIENT (React Native + Expo)
         │  (Captures image, manages local state, speaks audio)
         ▼
     [ HTTPS ]  <-- Secure Multi-Part Form Upload
         ▼
       FASTAPI BACKEND (Uvicorn Server)
         │  (Validates, pre-processes image, rate-limits)
         ├────────────────────────────────────────┐
         ▼                                        ▼
   TENSORFLOW ENGINE                      INTEGRATIONS LAYER
     └─ MobileNetV2 (17 classes)            ├─ Supabase (PostgreSQL & Storage)
                                            ├─ Gemini AI (Agricultural Chatbot)
                                            └─ Google TTS & Whisper STT (Voice AI)
```

---

## 2. Step-by-Step Mobile-to-Model Data Flow

Here is the exact journey of a leaf image, from the camera sensor to the neural network's classification result.

### Step 1: Capture or Selection on Mobile
* **Source**: The user opens the **ScanScreen** in the mobile app.
* **Mechanism**: 
  * They capture a live photo of a crop leaf using `expo-camera` via `<CameraView />`.
  * Or, they upload an existing photo from their gallery using `expo-image-picker`.
* **Output**: The mobile operating system stores the image in a local temporary cache folder and returns a local file URI (e.g., `file:///data/user/0/.../cache/ImagePicker/xyz.jpg`).

### Step 2: Preparing and Serializing Data (Client-Side)
* **The React Native Challenge**: Uploading local file URIs as raw streams directly can cause binary-to-string encoding errors on different devices.
* **The Solution (`uriToBlob`)**: 
  * The mobile app runs a local HTTP request using `XMLHttpRequest` with `responseType = 'blob'` targeting the local file URI.
  * This reads the raw file bytes directly from device storage and compiles them into a standard JavaScript `Blob`.
* **Form Submission**: 
  * The app creates a `FormData` container (standard for file uploads).
  * The binary Blob is appended under the key `"file"`, with a safe filename (e.g., `upload.jpg`).
  * A `POST` request is dispatched to `/api/v1/predict` with the `multipart/form-data` payload.

### Step 3: Backend Reception & Security Validation (FastAPI)
* **Endpoint**: `/api/v1/predict` receives the file stream.
* **Rate Limiting**: **SlowAPI** tracks the client's IP. The route enforces a limit of **20 prediction requests/minute** to protect the server from Denial of Service (DoS) attacks.
* **Extension Check**: The server rejects any file that does not end in `.jpg`, `.jpeg`, or `.png`.
* **Size Enforcement**: The server terminates the stream and throws a `400 Bad Request` error if the file payload exceeds **5 MB**.

### Step 4: Digital Image Preprocessing (Numpy & PIL)
Before the neural network can process the image, it must match the format of the training dataset:
1. **Raw Byte Loading**: The backend reads the incoming upload stream into memory using Python’s `io.BytesIO` and opens it with the Python Imaging Library (`PIL.Image`).
2. **Color Mode Alignment**: The image is converted using `.convert("RGB")` to strip any alpha (transparency) channels, ensuring a consistent 3-channel structure.
3. **Resizing**: The image is resized to **224 × 224 pixels** (the exact input dimensions required by MobileNetV2).
4. **Normalization**: Raw pixel values in the range `[0, 255]` are normalized to `[-1, 1]` using the formula:
   $$\text{Normalized Pixel} = \left(\frac{\text{Pixel Value}}{127.5}\right) - 1.0$$
5. **Tensor Shaping (Batch Expansion)**: An extra dimension is added using `np.expand_dims(img_array, axis=0)`, transforming the array shape from `(224, 224, 3)` to `(1, 224, 224, 3)`. This matches the batch shape Keras expects.

### Step 5: Model Inference (TensorFlow)
* **Model Selection**: During backend startup, the compiled TensorFlow Keras model `mobilenet_crop_disease.keras` is loaded into GPU/CPU memory via `tf.keras.models.load_model()`.
* **Execution**: The server executes `predictions = model(input_tensor, training=False).numpy()`. 
  * *Note: Using the model as a direct callable `model(...)` runs inference much faster than `model.predict(...)` for single-sample inference because it bypasses dataset pipeline overhead.*
* **Softmax Probability**: The model outputs a 2D array of shape `(1, 17)`. Each value corresponds to the probability distribution across our 17 supported classes.
* **Argmax Classification**: The backend extracts the index of the highest probability:
  $$\text{predicted\_idx} = \arg\max(\text{predictions}[0])$$
  $$\text{confidence} = \text{predictions}[0][\text{predicted\_idx}] \times 100$$

### Step 6: Parallel Database Logging & Detailed Diagnostics
* **JSON Delivery**: The backend returns the class name and confidence score to the mobile app in under 2 seconds.
* **Parallel Execution**: Once the client receives the prediction, it triggers two concurrent asynchronous network requests to minimize UI latency:
  1. **Get Disease Profile**: Requests `/api/v1/disease/{name}` to fetch actionable control remedies (organic and chemical), causes, and symptoms translated into the farmer's language.
  2. **Save to History**: Calls `dbService.savePrediction` to save the prediction metadata (disease, confidence, image path, timestamp) in the Supabase PostgreSQL database.
* **UI Transition**: The app navigates to the **AnalysisScreen**, rendering a detailed diagnostic report, confidence meter, and language-specific text-to-speech audio guidance.

---

## 3. Deep Learning Model Profile

| Parameter | Details |
| :--- | :--- |
| **Base Architecture** | **MobileNetV2** (with pre-trained ImageNet weights) |
| **Output Classes** | **17 Classes** (covering Corn, Potato, Rice, Wheat, and Sugarcane) |
| **Validation Accuracy** | **87%** |
| **Input Shape** | `(1, 224, 224, 3)` (RGB) |
| **Inference Time** | **< 50 milliseconds** (excluding network transmission) |
| **Model Size** | **~22.1 MB** (Keras single-file format) |

### Supported Diagnostic Classes
* 🌽 **Corn**: Common Rust, Gray Leaf Spot, Northern Leaf Blight, Healthy
* 🥔 **Potato**: Early Blight, Late Blight, Healthy
* 🌾 **Rice**: Leaf Blast, Neck Blast, Brown Spot, Healthy
* 🎋 **Sugarcane**: Bacterial Blight, Red Rot, Healthy
* 🌾 **Wheat**: Brown Rust, Yellow Rust, Healthy

---

## 4. Key Questions & Defenses for Judges

Be prepared to answer these technical questions during the demo or Q&A session:

### Q1: Why did you run the model on a FastAPI backend instead of compiling it to TensorFlow Lite (TFLite) to run locally on the phone?
* **Defense Points**:
  1. **Dynamic Model Updates**: If we compile the model into the app bundle, we have to publish a new app store release every time we retrain the model or add new crops. With a FastAPI backend, we can update or swap the model on the fly without the user needing to update their app.
  2. **Minimal App Footprint**: The `.keras` model file is ~22 MB, and the TensorFlow library is huge. Running it locally would increase the app download size to over 100 MB, which is a major barrier for rural farmers with limited cellular data.
  3. **Low-Spec Phone Compatibility**: Farmers often use older, low-spec smartphones. Running large convolutional neural networks locally drains the battery and can cause out-of-memory crashes. The backend server shoulders all the heavy computation.
  4. **Analytics Logging**: Having the model on the backend allows us to log predictions and flag emerging agricultural disease outbreaks in real time on our dashboard.

### Q2: How does the app handle spotty internet connection in remote agricultural fields?
* **Defense Points**:
  1. **Image Caching & Offline History**: The app records past predictions, descriptions, and treatment guidelines locally. A farmer can access their entire history of diagnostic results without an internet connection.
  2. **Optimized Payloads**: The mobile app allows resizing or compressing the camera captures before uploading, reducing cellular bandwidth usage.
  3. **Future Offline Quantized Model**: Our roadmap includes implementing a highly quantized, ultra-lightweight TFLite model (~4MB) built directly into the app for basic offline detection, falling back to the higher-accuracy cloud API when internet connectivity is restored.

### Q3: What measures did you implement to ensure accessibility for illiterate or non-technical farmers?
* **Defense Points**:
  1. **Tri-lingual Interface & Local Translations**: The entire app supports **English, Hindi, and Marathi**. The disease definitions, symptoms, and organic/chemical remedies are completely translated locally.
  2. **One-Tap Text-to-Speech (Audio Playback)**: Every analysis screen has an audio speaker button. Clicking it streams localized voice recordings generated by our backend **gTTS (Google Text-to-Speech)** pipeline, allowing farmers to listen to descriptions and treatments in their native language.
  3. **Voice Queries (Speech-to-Text)**: Farmers can click a microphone icon to record their symptoms. The audio is sent to the backend `/api/v1/speech-to-text` service (Whisper AI) to transcribe the query, permitting hands-free natural-language interactions.

### Q4: How do you handle scalability and protect the backend from abuse?
* **Defense Points**:
  1. **Asynchronous Architecture**: FastAPI is built on top of `Starlette` and `Pydantic`, which run on an asynchronous event loop (ASGI). This allows it to handle thousands of concurrent requests with minimal CPU overhead.
  2. **Strict Rate Limiting**: We use **SlowAPI** to rate-limit the `/api/v1/predict` endpoint to 20 requests/minute per IP, stopping malicious scripts and bots from overloading our machine learning engine.
  3. **Direct Inference Callables**: In our backend code, we call `model(input_tensor, training=False)` as a direct mathematical function rather than wrapping it in the high-overhead `model.predict()`, which cuts down inference latency by over 70% per image.

### Q5: How do you prevent incorrect diagnoses from leading to crop loss or pesticide overuse?
* **Defense Points**:
  1. **Confidence Thresholding**: If the model's confidence is low (e.g., under 65%), the app displays a warning: *"Uncertain Diagnosis. Please retake the photo with better lighting or consult an agronomist."*
  2. **Holistic Advice**: Our recommendations split treatments into **Organic/Preventative Control** and **Chemical Remedies**, emphasizing organic solutions first to discourage immediate chemical pesticide abuse.
  3. **Gemini AI Chat Integration**: If a farmer is unsure about a prediction, they can consult the built-in AI Agricultural Chatbot, which uses **Gemini 2.5 Flash** to provide contextual, specialized agricultural counseling.

### Q6: What is the plan for Explainable AI (XAI)? How can a farmer trust the model's diagnosis?
* **Defense Points**:
  * **Roadmap Feature (Grad-CAM)**: In Phase 2, we will integrate **Grad-CAM (Gradient-weighted Class Activation Mapping)** on our backend. Grad-CAM visualizes the gradients of the target class in the final convolutional layer of MobileNetV2. It generates a heatmap overlay on the leaf image, highlighting the exact spots (e.g., pustules, lesions) the neural network focused on. Showing this heatmap to agricultural experts and farmers helps demystify the "black box" of deep learning, building trust in our system.
