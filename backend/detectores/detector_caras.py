import os, numpy as np
from ultralytics import YOLO
from utils.face_recognition import detectar_rostro_local
from utils.ollama_utils import ollama_analyze_image
from utils import imagenes_utils as iu

class DetectorCaras:
    def __init__(self, db, carpeta_salida, columna_db, ruta_modelo="models/yolov11m-face.pt"):
        """
        Inicializa el detector de caras con un modelo YOLO específico,
        una ruta para guardar imágenes, y un ejecutor para tareas en segundo plano.
        """
        self.modelo = YOLO(ruta_modelo)
        self.carpeta_salida = carpeta_salida
        os.makedirs(self.carpeta_salida, exist_ok=True)

        self.db = db
        self.columna_db = columna_db

    def detectar_caras_en_imagen(self, imagen, id_persona):
        """
        Dado un frame y un ID de persona, detecta el rostro si existe y lo guarda local, en la base de datos y en S3.

        Retorna:
            - Coordenadas del recorte de rostro (x1, y1, x2, y2) o None si no se detectó.
        """         
        # Convertir Image a numpy array
        if not isinstance(imagen, np.ndarray):
            img_np = np.array(imagen)
        else:
            img_np = imagen

        coordenadas, orientacion = detectar_rostro_local(img_np, id_persona)

        if coordenadas is None:
            print(f"[INFO] ID {id_persona}: Sin rostro detectado (orientación: {orientacion})")
            return None

        # Ajustar coordenadas al tamaño de la imagen
        x1, y1, x2, y2 = coordenadas
        h, w = img_np.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        recorte = img_np[y1:y2, x1:x2]

        if recorte.size == 0:
            print(f"[ADVERTENCIA] ID {id_persona}: recorte vacío")
            return None

        # Guardar imagen (cara) localmente
        ruta_guardada = iu.guardar_imagen(recorte, id_persona, self.carpeta_salida, tipo="Cara")

        if ruta_guardada:
            carpeta_id = os.path.dirname(ruta_guardada)
            # Guardar ruta en base de datos
            self.db.guardar_datos(id_persona, {self.columna_db: carpeta_id})
            print(f"[INFO] ID {id_persona}: Cara guardada en {ruta_guardada} (orientación: {orientacion})")
        else:
            print(f"[ERROR] ID {id_persona}: No se pudo guardar el rostro")

        return x1, y1, x2, y2

