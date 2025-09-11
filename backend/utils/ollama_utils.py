import requests, base64, os, json
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
            response = requests.post(OLLAMA_URL, json=payload, timeout=250)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"[OLLAMA ERROR] Attempt {attempt+1}: {e}")
    return "[ERROR] No se pudo obtener descripción"

def limpiar_salida(raw: str) -> str:
    """
    Limpia la salida del modelo eliminando ```json ... ```
    y dejando solo el JSON crudo.
    """
    if not raw:
        return "{}"
    clean = raw.strip()

    # Si empieza con bloque markdown
    if clean.startswith("```"):
        clean = clean.strip("`")  # quita backticks
        clean = clean.replace("json", "", 1).strip()

    # En caso de que haya texto antes/después del JSON, intentamos aislar llaves
    if "{" in clean and "}" in clean:
        clean = clean[clean.find("{"): clean.rfind("}")+1]

    return clean

def ollama_analyze_images(image_paths: list, prompt: str) -> dict:
    """
    Analiza una lista de imágenes de una misma persona usando Ollama
    y devuelve un JSON consolidado con la información detectada.
    """
    # JSON inicial vacío
    consolidated_info = {
        "genero": "desconocido",
        "edad_aproximada": "desconocido",
        "color_piel": "desconocido",
        "ropa_principal": "desconocido",
        "ropa_inferior": "desconocido",
        "accesorio_cabeza": "ninguno"
    }

    for i, img_path in enumerate(image_paths):
        if i == 0:
            current_prompt = prompt
        else:
            # Para siguientes imágenes, pasamos la descripción anterior
            current_prompt = f"""
            Analiza la siguiente imagen de la misma persona y revisa si la descripción anterior es correcta.
            Imagen previa analizada: {json.dumps(consolidated_info)}

            Corrige o confirma la información según la nueva imagen.

            ⚠️ IMPORTANTE: 
            - Devuelve SOLO un JSON válido.
            - No repitas claves.
            - No escribas explicaciones ni texto adicional.
            - No uses ```.
            """

        # Llamada a Ollama
        result_json = ollama_analyze_image(current_prompt, img_path)
        # print(f"Resultados crudos imagen {i+1}:\n{result_json}\n")

        # Limpieza
        clean_json = limpiar_salida(result_json)

        # Parseo y actualización
        try:
            consolidated_info = json.loads(clean_json)
        except Exception as e:
            print(f"⚠️ Error al parsear JSON de la imagen {img_path}: {e}")
            print(f"Contenido recibido (limpio):\n{clean_json}\n")
            continue

        print(f"✅ Resultado tras imagen {i+1}:", consolidated_info, "\n")

    return consolidated_info
