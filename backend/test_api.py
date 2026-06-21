import httpx
import os

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Starting API validation tests...")
    
    # 1. Test Root Endpoint
    try:
        r = httpx.get(f"{BASE_URL}/")
        print("Root Status:", r.status_code)
        print("Root Response:", r.json())
        assert r.status_code == 200
        assert r.json()["status"] == "online"
    except Exception as e:
        print("Failed root check. Is the server running? Details:", e)
        return

    # 2. Test Disease Details Endpoint (English)
    r = httpx.get(f"{BASE_URL}/api/v1/disease/Corn___Common_Rust?lang=English")
    print("Disease Details (EN):", r.status_code)
    assert r.status_code == 200
    assert r.json()["disease_name"] == "Common Rust"

    # 3. Test Disease Details Endpoint (Hindi)
    r = httpx.get(f"{BASE_URL}/api/v1/disease/Corn___Common_Rust?lang=Hindi")
    print("Disease Details (HI):", r.status_code)
    assert r.status_code == 200
    assert r.json()["disease_name"] == "सामान्य गेरूआ रोग (कॉमन रस्ट)"

    # 4. Test Translation Endpoint
    payload = {
        "text": "What fertilizer should I use for rice blast?",
        "target_language": "Marathi"
    }
    r = httpx.post(f"{BASE_URL}/api/v1/translate", json=payload)
    print("Translation Status:", r.status_code)
    assert r.status_code == 200
    print("Translated text successfully received!")
    assert "खत" in r.json()["translated_text"] or "करपा" in r.json()["translated_text"]

    # 5. Test Text to Speech Endpoint
    payload = {
        "text": "Detected Condition: Common Rust",
        "language_code": "en"
    }
    r = httpx.post(f"{BASE_URL}/api/v1/text-to-speech", json=payload)
    print("TTS Status:", r.status_code)
    assert r.status_code == 200
    assert r.headers["content-type"] == "audio/mpeg"
    print("TTS MP3 streaming audio successfully verified!")

    # 6. Test Prediction (Real Pipeline)
    # Create a valid 1x1 image file
    from PIL import Image
    dummy_img_path = "dummy_rice_blast_leaf.jpg"
    img = Image.new('RGB', (224, 224), color = 'green')
    img.save(dummy_img_path)
        
    try:
        with open(dummy_img_path, "rb") as f:
            files = {"file": ("dummy_rice_blast_leaf.jpg", f, "image/jpeg")}
            r = httpx.post(f"{BASE_URL}/api/v1/predict", files=files)
        print("Prediction Status:", r.status_code)
        assert r.status_code == 200
        print("Prediction result:", r.json())
        assert "disease" in r.json()
    finally:
        if os.path.exists(dummy_img_path):
            try:
                os.remove(dummy_img_path)
            except Exception as e:
                print("Failed to remove dummy file:", e)

    print("All backend API endpoints verified successfully!")

if __name__ == "__main__":
    test_api()
