import os
import requests, base64
from PIL import Image
OLLAMA_URL="http://127.0.0.1:11434/api/generate"

OLLAMA_MODEL = "qwen2.5vl:7b"

# Función para enviar prompt + imagen a Ollama
def ollama_analyze_image(prompt, image_path):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "images": [img_b64],
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"].strip()

def build_prompt(detections):
    if isinstance(detections, dict):  # caso único
        detections = [detections]
    detection_info = "\n".join(
        [f"- {d['label']} (confidence: {d['confidence']:.2f})" for d in detections]
    )
    return f"""
        You are analyzing a retail surveillance frame for suspicious activity.

        YOLOv8 object detection found:
        {detection_info}

        The scene appears to be inside a store where individuals are interacting with shelves or items.

        Please analyze the image and answer:
        1. What do you observe in terms of human behavior?
        2. Is any suspicious or shoplifting-like behavior visible?
        3. Are there any behavioral patterns or body language that stand out?
    """

# Process all frames
frame_dir = "Personas_Detectadas/persona_67/Cuerpo"
for frame_file in sorted(os.listdir(frame_dir)):
    frame_path = os.path.join(frame_dir, frame_file)
    print(f"\n🔍 Processing: {frame_file}")

    img = Image.open(frame_path)
    ollama_text = ollama_analyze_image("Describi lo que ves en la imagen.", frame_path)

    print("--- OLLAMA ANALYSIS ---")
    print(ollama_text)

