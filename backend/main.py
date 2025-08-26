import argparse, redis, base64, io, time, json, os, pytz, threading
import paho.mqtt.client as mqtt
from PIL import Image
from detectores.detector_caras import DetectorCaras
from utils import imagenes_utils as iu
from utils.ollama_utils import ollama_analyze_image
from db.db_manager import DBManager
from datetime import datetime

# Define MQTT broker settings
broker_address = "mosquitto-ezeiza"
broker_port = 1883
topic = "/perception/tracking"
# Create MQTT client instance
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Configuración DB
db_name = os.getenv("DB_NAME_TABLE")
db_struct_text = os.getenv("DB_STRUCT")
# Convertir string a diccionario
db_struct = dict(item.split(":") for item in db_struct_text.split(",") if item)

# Crear la instancia de DBManager (compartida)
db = DBManager(db_name, db_struct)

carpeta_salida = "Personas_Detectadas"
detector_caras = DetectorCaras(db, carpeta_salida, "ruta_cara")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    global topic
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe(topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global topic

    start_time = time.time()

    # Convert the bytes variable to a string
    payload_str = msg.payload.decode('utf-8')
    # Convert the string to a JSON object
    payload = json.loads(payload_str)

    redis_frame_key = f"{payload['camera_id']}_{payload['frame_num']}"
    redis_person_id = payload["object_id"]

    print(f"id person: {redis_person_id}")
    redis_crop_box = (
        payload["bbox_left"],
        payload["bbox_top"],
        payload["bbox_left"] + payload["bbox_width"],
        payload["bbox_top"] + payload["bbox_height"]
    )

    print(f'Frame key: {redis_frame_key}')
    
    threading.Thread(
        target=read_frame_from_redis,          # función a ejecutar
        args=(redis_frame_key, redis_crop_box, redis_person_id),  # argumentos posicionales
        kwargs={                              # argumentos nombrados
            'redis_host': 'redis-ezeiza',
            'redis_port': 6379,
            'redis_db': 0
        }
    ).start()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"on_message() took {elapsed_time:.6f} seconds on topic {msg.topic}: {payload['camera_id']} {payload['roi']} {payload['frame_num']}")

def read_frame_from_redis(frame_key, crop_box, person_id, redis_host='redis-ezeiza', redis_port=6379, redis_db=0):
    # Connect to Redis
    r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
    try:
        r.ping()
        print("Connected to Redis")
    except redis.ConnectionError:
        print("Could not connect to Redis")
        return
    print(f"Using Redis at {redis_host}:{redis_port}")

    image = None

    # Get the image data
    time.sleep(1)  # Wait for Redis to be ready
    image_data = r.get(frame_key)

    if image_data:
        print(f"Retrieved image data for key: {frame_key}")
        # If the data is base64 encoded, decode it
        try:
            # Try to decode as base64 first
            decoded_data = base64.b64decode(image_data)
            # If successful, create an image from the decoded data
            image = Image.open(io.BytesIO(decoded_data), formats=['JPEG'])            
        except Exception as e:
            print(f"Base64 decoding failed: {e}")
            # If base64 decoding fails, try direct binary data
            image = Image.open(io.BytesIO(image_data), formats=['JPEG'])
        
        cropped_image = image.crop(crop_box)
        ruta_guardada = iu.guardar_imagen(cropped_image, person_id, carpeta_salida, "Cuerpo")
        
        rta = ollama_analyze_image("Describi lo que ves en la imagen.", ruta_guardada)
        db.guardar_datos(person_id, {"descripcion": rta})
        
        if ruta_guardada:
            carpeta_id = os.path.dirname(ruta_guardada)
            # Guardar en base de datos en segundo plano (no espera)
            db.guardar_datos(person_id, {"ruta_cuerpo": carpeta_id})
            tz = pytz.timezone("America/Argentina/Buenos_Aires")
            ahora_local = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
            db.guardar_datos(person_id, {"fecha": ahora_local})
        else:
            print(f"[ERROR] ID {person_id}: No se pudo guardar el cuerpo")
        
        detector_caras.detectar_caras_en_imagen(cropped_image, person_id)

    return image

def main(args):
    global mqtt_client

    # MQTT Broker
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(broker_address, broker_port, 60)

    # Iniciar MQTT loop en el hilo principal (bloqueante)
    mqtt_client.loop_forever()

# ---------------------------------------------------------
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Example Backend - Read from REDIS and display image - Subscribe to mosquitto")
    # Redis
    parser.add_argument("--redis_host", type=str, default="redis-ezeiza", help="Redis host")
    parser.add_argument("--redis_port", type=int, default=6379, help="Redis port")
    parser.add_argument("--redis_db", type=int, default=0, help="Redis database number")
    # Mosquitto
    parser.add_argument("--mosquitto_host", type=str, default="mosquitto-ezeiza", help="Mosquitto host")
    parser.add_argument("--mosquitto_port", type=int, default=1883, help="Mosquitto port")
    #
    args = parser.parse_args()
    main(args)
    print("Done!")