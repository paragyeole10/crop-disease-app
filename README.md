# AgriVision AI: An AI-Powered Multilingual Smart Crop Disease Detection & Agricultural Assistant

```
     AgriVision AI Project Group Technical Report
     IEEE Layout Reference & System Documentation
     Version 1.0 — June 2026
```

---

### **Abstract**
**Crop pathogens and diseases present a major threat to global food security and the livelihoods of smallholder farmers. Early and precise detection is critical, yet rural farmers frequently lack access to agricultural experts, encounter language barriers, and suffer from delayed diagnoses. This paper presents AgriVision AI, a comprehensive mobile-cloud ecosystem designed to democratize access to crop disease diagnosis and agricultural advice. The proposed system features a cross-platform mobile application developed using React Native and Expo, which interfaces with a high-performance FastAPI backend. A convolutional neural network (CNN) model based on the MobileNetV2 architecture is deployed on the server, capable of classifying 17 distinct crop states across 5 critical crops (Corn, Potato, Rice, Wheat, Sugarcane) with an initial validation accuracy of 87%. To address regional accessibility, the system incorporates IndicTrans2 translation for multilingual output (English, Hindi, Marathi) and incorporates voice-based interaction via Whisper-based speech-to-text (STT) and text-to-speech (TTS) interfaces. Experimental results indicate a prediction response time of under 3 seconds, fulfilling the requirement for real-time field operations.**

***Index Terms*—Computer Vision, Deep Learning, MobileNetV2, Crop Disease Diagnosis, Multilingual Translation, Speech-to-Text, FastAPI, Agri-Tech.**

---

## I. Introduction
Agriculture remains the backbone of the global economy, employing billions of people and supplying essential food products. However, crop yield optimization is severely hindered by plant pathogens, fungal infections, and bacterial pests. Traditional disease identification methods rely on visual inspection by agricultural experts, which is slow, expensive, and logistically unfeasible for millions of farmers in remote rural regions. 

With the rapid proliferation of mobile hardware, camera-equipped smartphones, and wireless connectivity, mobile-based Artificial Intelligence (AI) solutions have emerged as a viable bridge. By combining computer vision, natural language processing, and cloud services, AgriVision AI delivers instant, expert-level crop diagnosis directly to the field. 

The remainder of this document outlines the architecture, implementation details, data flow, and performance metrics of the AgriVision AI platform.

---

## II. Problem Statement & Motivation
Smallholder farmers, particularly in developing economies, encounter several compounding challenges when dealing with crop health:
1. **Ineffective Expert Outreach:** The ratio of agricultural extension officers to active farmers is extremely low, leading to delayed or absent human consultations.
2. **Delayed Diagnosis:** Fungal infections such as *Late Blight* in potatoes or *Rice Blast* can destroy entire fields within days if not identified and treated early.
3. **Language and Literacy Barriers:** Most scientific agricultural resources and treatment guidelines are published in English, making them inaccessible to local farmers speaking regional dialects.
4. **Indiscriminate Chemical Usage:** Without precise diagnostic tools, farmers often misapply chemical fungicides or pesticides, leading to increased costs, environmental degradation, and chemical resistance.
5. **Lack of Digital Integration:** Existing AI models often remain isolated in academic repositories or web tools, lacking the integration of offline historical tracking, voice interfaces, and direct supply-chain product advisory.

AgriVision AI solves these problems by providing a unified, localized, voice-enabled mobile assistant capable of image-based crop disease diagnosis, local language translation, and direct treatment and chemical product recommendations.

---

## III. System Architecture & Design
The system uses a client-server architecture tailored for low-latency inference and cross-platform mobile compatibility. The mobile client acts as the data acquisition interface (camera, microphone) and visualization layer, while the FastAPI server hosts the deep learning model and coordinates external APIs.

### A. Conceptual Architecture
```text
┌────────────────────────────────────────────────────────┐
│               Mobile Client (React Native + Expo)      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌──────────┐  │
│  │   Camera/Audio  │ │  Local History  │ │ UI Paper │  │
│  └────────┬────────┘ └─────────────────┘ └────▲─────┘  │
└───────────┼───────────────────────────────────┼────────┘
            │ Request                           │ Response
            ▼ (JSON / Multi-part Form Data)     │ (JSON / Audio Stream)
┌───────────┼───────────────────────────────────┼────────┐
│           │            FastAPI Backend        │        │
│  ┌────────▼────────┐                          │        │
│  │   CORS / Auth   │                          │        │
│  └────────┬────────┘                          │        │
│           ├───────────────┬───────────────────┤        │
│  ┌────────▼────────┐ ┌────▼────────────┐ ┌────▼─────┐  │
│  │  AI Predictor  │ │ Translation API │ │ Voice/TTS│  │
│  │ (MobileNetV2)   │ │  (IndicTrans2)  │ │ (gTTS)   │  │
│  └────────┬────────┘ └────────┬────────┘ └──────────┘  │
└───────────┼───────────────────┼────────────────────────┘
            ▼                   ▼
┌────────────────────────────────────────────────────────┐
│                     Cloud Database                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │      Supabase (PostgreSQL & Object Storage)      │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### B. Core Data Flow
The sequence below illustrates the execution flow when a user uploads an image for disease prediction:
1. **Acquisition:** The mobile client captures an image using `expo-camera` or selects it using `expo-image-picker`.
2. **Serialization:** The image is converted into a binary blob and appended to `FormData`.
3. **Transmission:** The client issues an HTTP POST request to `/api/v1/predict`.
4. **Preprocessing:** The backend receives the image stream, validates the file headers, and normalizes it to a shape of `224x224x3`.
5. **Inference:** The TensorFlow engine executes the feed-forward pass on the MobileNetV2 network.
6. **Lookup:** The predicted class label triggers a database query to retrieve localized disease details (Description, Symptoms, Actionable Treatments, and Chemical Products).
7. **Response:** The system packages the prediction confidence and agricultural advice into a JSON object and returns it to the client.

---

## IV. Technical Stack & Infrastructure
The application stack is selected to maximize execution speed, maintainability, and horizontal scaling.

### A. Frontend Layer (Mobile)
* **Framework:** React Native + Expo (SDK 51+), facilitating a single, clean TypeScript/JavaScript codebase for Android and iOS.
* **Component Library:** React Native Paper (Material Design compliant), providing high contrast UI elements optimized for high-glare field use.
* **Navigation:** React Navigation (Stack and Tab-based routing).
* **Hardware APIs:** `expo-camera` (viewfinder control), `expo-image-picker` (photo selection), `expo-av` (audio playback and recording).

### B. Backend Layer (Service Core)
* **Framework:** FastAPI (Python 3.10+), selected for its asynchronous (async/await) capability, automatically generated OpenAPI schemas, and speed.
* **ASGI Server:** Uvicorn.
* **Rate Limiting:** SlowAPI (Token bucket algorithm to defend against DoS attacks on the TensorFlow inference engine).
* **Network Client:** HTTPX for asynchronous external API requests.

### C. Artificial Intelligence & NLP
* **Deep Learning Engine:** TensorFlow 2.15 (Model format: `.keras` compiled binary).
* **Image Processing:** OpenCV and Pillow (PIL).
* **Translation Service:** IndicTrans2 model wrappers to translate descriptions between English, Hindi, and Marathi.
* **Audio Processing:** Whisper (future upgrade path for local dialect parsing) and gTTS (Google Text-to-Speech) for vocalization.

### D. Cloud Infrastructure
* **Relational Database:** Supabase PostgreSQL for storing structured user schema and user prediction history logs.
* **File Storage:** Supabase Storage (S3-compatible Object Storage) for caching crop images and audio assets.
* **User Authentication:** Firebase Auth, providing secure JWT token verification for Google and Email logins.

---

## V. Core System Features
AgriVision AI contains several main features tailored specifically for rural farming:

### 1. Crop Disease Detection
Provides real-time class predictions and confidence percentages by uploading leaf images from the camera interface.

### 2. Deep Information Cards
For every diagnosed disease, the app displays:
* **Description:** Scientific details translated into the farmer's preferred language.
* **Symptom Highlights:** Spotting patterns, discoloration, leaf-wilting thresholds.
* **Organic/Chemical Actionable Remedies:** Instant recommendations on crop rotation, pruning, and safe fungicide usage.

### 3. Integrated Product Advisory
Recommends exact, locally approved chemical products (e.g. Mancozeb, Copper Oxychloride, Tricyclazole) matching the diagnosed disease.

### 4. Multilingual & Voice Support
Translates text and provides text-to-speech output in English, Hindi, and Marathi, allowing low-literacy users to hear diagnoses in their native language.

### 5. Prediction History Logs
Retains past diagnostic data locally (via SecureStore/AsyncStorage) and in the cloud (Supabase), enabling tracking of seasonal disease patterns.

---

## VI. Application Screenshot Gallery
Here is a visual overview of the AgriVision AI mobile application:

| Welcome & Authentication | Dashboard Home | Camera Scanner |
| :---: | :---: | :---: |
| ![Welcome Screen](mobile\assets\Authentication_Screen.png) | ![Dashboard Screen](mobile\assets\Dashboard_Screen.png) | ![Scan Screen](mobile/assets/screenshots/scan.png) |

| Disease Analysis | History Logs | Voice Assistant |
| :---: | :---: | :---: |
| ![Analysis Screen](mobile/assets/screenshots/analysis.png) | ![History Screen](mobile/assets/screenshots/history.png) | ![Assistant Screen](mobile/assets/screenshots/assistant.png) |

| Marketplace Store | Product Details | Order Tracking |
| :---: | :---: | :---: |
| ![Marketplace Screen](mobile/assets/screenshots/marketplace.png) | ![Product Details](mobile/assets/screenshots/details.png) | ![Order Tracking](mobile/assets/screenshots/tracking.png) |

---

## VII. Deep Learning Classification Model
The primary ML system consists of a Convolutional Neural Network (CNN) fine-tuned using Transfer Learning.

### A. Model Selection: MobileNetV2
MobileNetV2 was chosen as the baseline model due to its light weight and low parameter footprint, making it ideal for edge server configurations and potential future on-device compilation. The model leverages depthwise separable convolutions to reduce computations while maintaining representation accuracy.

```text
Input (224x224x3) ──► [MobileNetV2 Base] ──► [GlobalAveragePooling2D] ──► [Dense 128 (ReLU)] ──► [Dense 17 (Softmax)]
```

### B. Supported Crop & Disease Classes
The system is trained and configured to diagnose the following 17 distinct classifications:

| Crop | Target Disease | Causative Agent / Class Type |
| :--- | :--- | :--- |
| **Corn** | Common Rust | *Puccinia sorghi* (Fungus) |
| | Gray Leaf Spot | *Cercospora zeae-maydis* (Fungus) |
| | Northern Leaf Blight | *Exserohilum turcicum* (Fungus) |
| | Healthy | Baseline Control |
| **Potato** | Early Blight | *Alternaria solani* (Fungus) |
| | Late Blight | *Phytophthora infestans* (Oomycete) |
| | Healthy | Baseline Control |
| **Rice** | Brown Spot | *Bipolaris oryzae* (Fungus) |
| | Leaf Blast | *Magnaporthe oryzae* (Fungus) |
| | Neck Blast | *Magnaporthe oryzae* (Fungus) |
| | Healthy | Baseline Control |
| **Sugarcane**| Bacterial Blight | *Xanthomonas albilineans* (Bacteria) |
| | Red Rot | *Colletotrichum falcatum* (Fungus) |
| | Healthy | Baseline Control |
| **Wheat** | Brown Rust | *Puccinia triticina* (Fungus) |
| | Yellow Rust | *Puccinia striiformis* (Fungus) |
| | Healthy | Baseline Control |

### C. Performance & Preprocessing
* **Input dimensions:** $224 \times 224$ pixels, 3 channels (RGB).
* **Scaling:** Normalized to $[-1, 1]$ range matching MobileNetV2 expectations.
* **Accuracy:** Current validation dataset accuracy is **87%**.
* **Inference optimization:** The backend loads the compiled Keras model using direct callable (`model(input_tensor, training=False).numpy()`) for faster single-image inference compared to the standard `model.predict()`.

---

## VIII. API Specifications & Endpoints
The backend exposes RESTful endpoints, documented automatically via Swagger UI.

### 1. Predict Disease
* **Endpoint:** `POST /api/v1/predict`
* **Content-Type:** `multipart/form-data`
* **Request Payload:**
  * `file`: Binary file stream (JPG, JPEG, PNG <= 5MB)
* **Response Payload (JSON):**
  ```json
  {
    "disease": "Rice___Leaf_Blast",
    "confidence": 94.30,
    "simulated": false
  }
  ```

### 2. Get Disease Details
* **Endpoint:** `GET /api/v1/disease/{name}`
* **Path Parameter:** `name` (URL-encoded class name, e.g. `Rice___Leaf_Blast`)
* **Query Parameter:** `lang` (Preferred language: `English`, `Hindi`, `Marathi`)
* **Response Payload (JSON):**
  ```json
  {
    "name": "Rice___Leaf_Blast",
    "description": "Leaf blast is a devastating fungal disease of rice...",
    "symptoms": [
      "Diamond-shaped lesions on leaves",
      "Gray or white centers in lesions",
      "Brown borders around lesions"
    ],
    "treatment": {
      "organic": "Apply neem oil sprays regularly and avoid excessive nitrogen fertilizer.",
      "chemical": "Spray Tricyclazole 75 WP at 0.6 g/liter of water."
    },
    "prevention": [
      "Use disease-resistant seeds",
      "Ensure proper plant spacing",
      "Avoid overhead irrigation"
    ],
    "products": [
      "Tricyclazole 75% WP",
      "Kitazin 48% EC",
      "Isoprothiolane 40% EC"
    ]
  }
  ```

### 3. Text to Speech (TTS)
* **Endpoint:** `GET /api/v1/text-to-speech`
* **Query Parameters:**
  * `text`: Text string to convert.
  * `language_code`: Lang identifier (`en`, `hi`, `mr`).
* **Response:** Streaming Binary Audio Data (`audio/mpeg`).

---

## IX. Security & Performance Verification

### A. Security Protocols
1. **Inference Protection:** Implemented using `SlowAPI` to prevent DoS attacks on `/api/v1/predict` (rate limited to 20 requests per minute).
2. **Payload Size Checks:** File uploads are limited to 5MB maximum to prevent server memory exhaustion.
3. **CORS Configuration:** Explicitly configured to allow cross-origin requests from web or native clients while blocking unauthorized referrers.
4. **Input Verification:** RegEx filters verify filename extensions (`.jpg`, `.jpeg`, `.png`) to mitigate file upload vulnerabilities.

### B. Performance Metrics
* **Average Inference Latency:** ~180ms on standard CPUs.
* **Total Network Round-Trip Time (RTT):** Under 2.4 seconds under simulated 3G networks.
* **App Cold Start:** Under 4.5 seconds on mid-range Android devices.

---

## X. Implementation Roadmap & Milestones

```text
┌────────────────────────┐      ┌────────────────────────┐      ┌────────────────────────┐
│        Phase 1         │      │        Phase 2         │      │        Phase 3         │
│  - ML Engine MVP       │ ───► │  - FastAPI Server      │ ───► │  - Translation Service │
│  - 17 Disease Classes  │      │  - React Native Client │      │  - Voice Integration   │
└────────────────────────┘      └────────────────────────┘      └────────────────────────┘
                                                                            │
┌────────────────────────┐      ┌────────────────────────┐                  │
│        Phase 5         │      │        Phase 4         │                  │
│  - MLOps Pipeline      │ ◄─── │  - Render Deployment   │ ◄────────────────┘
│  - Docker / CI-CD      │      │  - Firebase Auth Setup │
└────────────────────────┘      └────────────────────────┘
```

* **Phase 1 (Completed):** Model training, accuracy validation (87%), and basic database configuration.
* **Phase 2 (Completed):** Mobile client implementation with React Native, FastAPI setup, and core endpoints.
* **Phase 3 (Current):** Voice integration (TTS + STT) and IndicTrans2 translation for regional languages.
* **Phase 4 (Pending):** Production deployment on Render and Firebase Authentication integration.
* **Phase 5 (Future):** EfficientNetB0 upgrade (expected accuracy 94%), Grad-CAM explainability, and automated Dockerized CI/CD pipelines.

---

## XI. Conclusion
AgriVision AI demonstrates a scalable and accessible approach to crop disease management. By leveraging MobileNetV2 for low-latency image classification and integrating multilingual translation and voice services, the platform addresses both the diagnostic and accessibility challenges faced by smallholder farmers. The current 87% prediction accuracy and robust client-server design establish a strong foundation for future upgrades, including explainable AI models and localized micro-service features.

---

## References
1. **Howard, A. G., et al.** "MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications," *arXiv preprint arXiv:1704.04861*, 2017.
2. **FastAPI Framework Developer Documentation.** Online: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com).
3. **IndicTrans2 Translation Engine Library.** AI4Bharat, IIT Madras. Online: [https://github.com/AI4Bharat/IndicTrans2](https://github.com/AI4Bharat/IndicTrans2).
4. **TF.Keras Model Deployment Guides.** Google TensorFlow. Online: [https://www.tensorflow.org/guide/keras](https://www.tensorflow.org/guide/keras).
