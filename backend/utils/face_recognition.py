# utils/detector_faces.py
import cv2
import numpy as np
import mediapipe as mp
from insightface.app import FaceAnalysis
from numpy.linalg import norm
from typing import List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Modelos ---
face_model = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
face_model.prepare(ctx_id=0)

mp_pose = mp.solutions.pose
pose_model = mp_pose.Pose(static_image_mode=True)

# --- Galerías internas ---
gallery: dict[int, List[np.ndarray]] = {}
pose_gallery: dict[int, float] = {}

# --- Funciones auxiliares ---
def mejorar_imagen(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if img.ndim == 3 else img

def obtener_orientacion_y_pose(img: np.ndarray) -> Tuple[str, Optional[float]]:
    res = pose_model.process(img)
    if not res.pose_landmarks:
        return "desconocido", None
    lm = res.pose_landmarks.landmark
    nariz = lm[mp_pose.PoseLandmark.NOSE]
    izq  = lm[mp_pose.PoseLandmark.LEFT_SHOULDER]
    der  = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    if nariz.visibility < 0.5 or izq.visibility < 0.5 or der.visibility < 0.5:
        return "desconocido", None
    centro_h = (izq.x + der.x) / 2
    cuerpo_x = centro_h
    if nariz.visibility < 0.2:
        return "espaldas", cuerpo_x
    if abs(nariz.x - centro_h) > 0.1:
        return "perfil", cuerpo_x
    return "frente", cuerpo_x

def distancia_coseno(a: np.ndarray, b: np.ndarray) -> float:
    return 1 - np.dot(a, b) / (norm(a) * norm(b))

def embedding_medio(embs: List[np.ndarray]) -> np.ndarray:
    m = np.mean(np.stack(embs), axis=0)
    return m / norm(m)

# --- Función principal ---
def detectar_rostro_local(imagen: np.ndarray, track_id: int) -> Tuple[Optional[List[int]], str]:
    """
    Detecta el rostro y orientación directamente en local (sin FastAPI).
    Retorna:
        - box: [x1, y1, x2, y2] o None si no hay rostro
        - orientacion: 'frente', 'perfil', 'espaldas', 'desconocido', 'error'
    """
    if imagen is None:
        return None, "error"

    orient, cuerpo_x = obtener_orientacion_y_pose(imagen)
    if orient == "espaldas":
        return None, orient

    faces = face_model.get(imagen)
    if not faces:
        return None, orient

    if track_id not in gallery:
        f0 = faces[0]
        gallery[track_id] = [f0.normed_embedding]
        if cuerpo_x is not None:
            pose_gallery[track_id] = cuerpo_x
        x1, y1, x2, y2 = map(int, f0.bbox)
        return [x1, y1, x2, y2], orient

    target = embedding_medio(gallery[track_id])
    best_face = min(faces, key=lambda f: distancia_coseno(f.normed_embedding, target))
    best_dist = distancia_coseno(best_face.normed_embedding, target)

    th_perfil = 0.6
    th_frente = 0.5

    if orient == "perfil":
        if best_dist > th_perfil:
            return None, orient
        x1, y1, x2, y2 = map(int, best_face.bbox)
        return [x1, y1, x2, y2], orient

    elif orient == "frente":
        prev_pose = pose_gallery.get(track_id)
        accept = best_dist <= th_frente or (cuerpo_x is not None and prev_pose is not None and abs(cuerpo_x - prev_pose) < 0.05)
        if accept:
            x1, y1, x2, y2 = map(int, best_face.bbox)
            gallery[track_id].append(best_face.normed_embedding)
            if len(gallery[track_id]) > 5:
                gallery[track_id].pop(0)
            if cuerpo_x is not None:
                pose_gallery[track_id] = cuerpo_x
            return [x1, y1, x2, y2], orient
        return None, orient

    return None, "desconocido"
