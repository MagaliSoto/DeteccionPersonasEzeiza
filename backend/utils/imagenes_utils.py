import cv2, os, datetime, shutil, numpy as np

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

def eliminar_carpeta(ruta_carpeta):
    """
    Elimina una carpeta entera con todo su contenido.
    
    Parámetros:
        ruta_carpeta (str): Ruta de la carpeta a eliminar.
    
    Retorna:
        bool: True si se eliminó correctamente, False en caso de error.
    """
    try:
        if os.path.exists(ruta_carpeta):
            shutil.rmtree(ruta_carpeta)
            print(f"[OK] Carpeta eliminada: {ruta_carpeta}")
            return True
        else:
            print(f"[WARN] La carpeta no existe: {ruta_carpeta}")
            return False
    except Exception as e:
        print(f"[ERROR] No se pudo eliminar la carpeta {ruta_carpeta}: {e}")
        return False

def collage_4_desde_rutas_guardar(rutas, id_persona, carpeta_salida="Personas_Detectadas", tamaño_final=(800, 800)):
    """
    Crea un collage 2x2 a partir de 4 rutas de imágenes y lo guarda en Personas_Detectadas/persona_{id}.

    Parámetros:
        rutas (list of str): Lista de 4 rutas de imágenes.
        id_persona (str | int): ID de la persona.
        carpeta_salida (str): Carpeta raíz donde se guardará el collage.
        tamaño_final (tuple): Tamaño final del collage (ancho, alto).

    Retorna:
        str | None: Ruta del collage guardado o None si hubo error.
    """
    if len(rutas) != 4:
        print("[ERROR] Se necesitan exactamente 4 rutas de imágenes")
        return None

    ancho, alto = tamaño_final
    ancho_celda = ancho // 2
    alto_celda = alto // 2

    celdas = []
    for ruta in rutas:
        if not os.path.exists(ruta):
            print(f"[WARN] Imagen no encontrada: {ruta}. Se usa un recuadro negro.")
            img = np.zeros((alto_celda, ancho_celda, 3), dtype=np.uint8)
        else:
            img = cv2.imread(ruta)
            if img is None or img.size == 0:
                print(f"[WARN] Imagen vacía: {ruta}. Se usa un recuadro negro.")
                img = np.zeros((alto_celda, ancho_celda, 3), dtype=np.uint8)
            else:
                img = cv2.resize(img, (ancho_celda, alto_celda))
        celdas.append(img)

    # Combinar las imágenes
    fila1 = np.hstack((celdas[0], celdas[1]))
    fila2 = np.hstack((celdas[2], celdas[3]))
    collage = np.vstack((fila1, fila2))

    # Crear carpeta de salida: Personas_Detectadas/persona_{id}
    carpeta_persona = os.path.join(carpeta_salida, f"persona_{id_persona}")
    os.makedirs(carpeta_persona, exist_ok=True)

    # Nombre de archivo con timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    nombre_archivo = f"collage_{id_persona}_{timestamp}.jpg"
    ruta_completa = os.path.join(carpeta_persona, nombre_archivo)

    # Guardar collage
    if not cv2.imwrite(ruta_completa, collage):
        print(f"[ERROR] No se pudo guardar el collage para ID {id_persona}")
        return None

    print(f"[INFO] Collage guardado: {ruta_completa}")
    return ruta_completa

