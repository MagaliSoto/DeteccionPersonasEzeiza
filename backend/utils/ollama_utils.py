import requests, base64, os
import dotenv
dotenv.load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

def ollama_analyze_image(prompt, image_path, retries=2):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "images": [img_b64],
        "stream": False
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"[OLLAMA ERROR] Attempt {attempt+1}: {e}")
    return "[ERROR] No se pudo obtener descripción"
