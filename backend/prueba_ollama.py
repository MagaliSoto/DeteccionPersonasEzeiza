from utils.ollama_utils import ollama_analyze_images

prompt = """
Analiza la imagen de una persona y devuelve SOLO un JSON válido con este formato:

{
  "genero": "masculino | femenino | desconocido",
  "edad_aproximada": "niño | adolescente | adulto_joven | adulto | adulto_mayor | desconocido",
  "ropa_principal": "breve descripción (ej: 'buzo negro', 'camisa blanca') máx 25 caracteres",
  "ropa_inferior": "breve descripción (ej: 'pantalón azul', 'jean negro') máx 25 caracteres",
  "rasgos_visibles": "ninguno | barba | bigote | tatuajes | gorro | gorra | capucha | sombrero | lentes | anteojos de sol | otro"
}

Reglas estrictas:
1. Devuelve TODOS los campos. Si no es posible detectar alguno, usa "desconocido" para ropa y edad, "ninguno" para rasgos.
2. Cada descripción de ropa debe tener máximo 25 caracteres; si es más larga, acórtala respetando palabras clave.
3. Usa SOLO los valores permitidos para "genero", "edad_aproximada" y "rasgos_visibles". Si no encaja, usa "desconocido" o "otro".
4. No repitas claves, no agregues campos extra, no expliques nada, no uses ``` ni markdown.
5. Devuelve únicamente un JSON válido, listo para parsear.
"""

rutas_guardadas = [
    "backend/Personas_Detectadas/persona_167/Cuerpo/Cuerpo_167_2025-09-01__13-58-29.jpg",
    "backend/Personas_Detectadas/persona_167/Cuerpo/Cuerpo_167_2025-09-01__13-58-30.jpg",
    "backend/Personas_Detectadas/persona_167/Cuerpo/Cuerpo_167_2025-09-01__13-58-32.jpg",
    "backend/Personas_Detectadas/persona_167/Cuerpo/Cuerpo_167_2025-09-01__13-58-33.jpg"
]
rta = ollama_analyze_images(rutas_guardadas, prompt)

print(rta)