import sys, os
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from db.db_manager import DBManager

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

carpeta_imagenes="Personas_Detectadas"
"""
Crea la app FastAPI inyectando la instancia de DBManager
"""
app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montamos la carpeta como pública para servir imágenes
app.mount(f"/static/{carpeta_imagenes}", StaticFiles(directory=carpeta_imagenes), name=carpeta_imagenes)

# Configuración DB
db_name = os.getenv("DB_NAME_TABLE")
db_struct_text = os.getenv("DB_STRUCT")

if not db_name or not db_struct_text:
    raise EnvironmentError("Variables de entorno DB_NAME_TABLE y/o DB_STRUCT no definidas.")

# Convertir string a diccionario
db_struct = dict(item.split(":") for item in db_struct_text.split(",") if item)

# Crear la instancia de DBManager (compartida)
db = DBManager(db_name, db_struct)

def listar_imagenes(carpeta: str):
    imagenes = []
    if carpeta and os.path.exists(carpeta):
        for archivo in sorted(os.listdir(carpeta)):
            if archivo.lower().endswith((".jpg", ".png")):
                rel_path = os.path.relpath(carpeta, carpeta_imagenes)
                url = f"http://192.168.0.105:8001/static/{carpeta_imagenes}/{rel_path}/{archivo}"
                imagenes.append(url.replace("\\", "/"))
    return imagenes

@app.get("/api/personas")
def get_personas():
    personas = db.obtener_datos()
    for persona in personas:
        # Convertir fecha a yyyy-mm-dd (filtrado)
        if persona.get("fecha"):
            try:
                fecha_obj = datetime.strptime(str(persona["fecha"]), "%Y-%m-%d")
                persona["fecha"] = fecha_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        persona["imagenes"] = []
        persona["imagenes"] += listar_imagenes(persona.get("ruta_cuerpo", ""))
        persona["imagenes"] += listar_imagenes(persona.get("ruta_cara", ""))
        
        # Ahora descripcion viene como dict, no string
        # Si quieres asegurarte que es dict, podrías hacer algo así:
        if persona.get("descripcion") and isinstance(persona["descripcion"], str):
            import json
            try:
                persona["descripcion"] = json.loads(persona["descripcion"])
            except Exception:
                # Si no es JSON válido, déjalo tal cual
                pass

    return personas

# uvicorn api.start_api:app --host 0.0.0.0 --port 8000 --reload

