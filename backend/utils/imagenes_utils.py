import cv2, os, datetime, numpy as np

def mejorar_imagen(img):
    """
    Convierte la imagen a RGB si es necesario.

    Parámetros:
        img (np.array): Imagen en formato BGR o RGB.

    Retorna:
        np.array: Imagen en formato RGB.
    """
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img

def guardar_imagen(imagen, id_persona, carpeta_salida, tipo):
    """
    Guarda una imagen (Cuerpo o Cara) en la carpeta correspondiente con un nombre único.

    Parámetros:
        imagen (ndarray o PIL.Image): Imagen a guardar.
        id_persona (str): ID único de la persona.
        carpeta_salida (str): Carpeta raíz donde guardar imágenes.
        tipo (str): 'Cuerpo' o 'Caras'. Define la subcarpeta y nombre del archivo.

    Retorna:
        str | None: Ruta del archivo guardado o None si hubo error.
    """
    if imagen is None:
        print(f"[ADVERTENCIA] Imagen vacía para ID {id_persona}")
        return None

    # Convertir a np.array si no lo es
    if not isinstance(imagen, np.ndarray):
        img_np = np.array(imagen)
    else:
        img_np = imagen

    # Verificar que la imagen no esté vacía
    if img_np.size == 0:
        print(f"[ADVERTENCIA] Imagen vacía para ID {id_persona}")
        return None

    # Convertir RGB a BGR si tiene 3 canales
    if img_np.ndim == 3 and img_np.shape[2] == 3:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # Carpeta: personas/persona_X/Cuerpo o Caras
    carpeta_persona = os.path.join(carpeta_salida, f"persona_{id_persona}", tipo)
    os.makedirs(carpeta_persona, exist_ok=True)

    # Nombre único con timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    nombre_archivo = f"{tipo}_{id_persona}_{timestamp}.jpg"
    ruta_completa = os.path.join(carpeta_persona, nombre_archivo)

    # Guardar imagen
    if not cv2.imwrite(ruta_completa, img_np):
        print(f"[ERROR] No se pudo guardar la imagen para ID {id_persona}")
        return None

    print(f"[INFO] Imagen guardada: {ruta_completa}")
    return ruta_completa