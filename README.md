# Detección de Personas Ezeiza

**Sistema integral de detección, análisis y visualización de personas en video**

Este proyecto combina **NVIDIA DeepStream**, **Redis**, **MQTT**, **Ollama** y un **backend con API + frontend web** para crear una solución completa de detección y descripción de personas en tiempo real.  

El sistema está diseñado para:
- Detectar personas y rostros en video mediante **DeepStream**.  
- Procesar detecciones en un **backend inteligente** que genera descripciones y guarda información.  
- Exponer una **API REST** con las imágenes y descripciones.  
- Mostrar los resultados en un **frontend web** con filtros y galería visual.

---

## 🧠 Arquitectura General

### 1. **DeepStream + Redis + MQTT**
- Procesa el flujo de video (por RTSP u otra fuente).  
- Detecta personas en tiempo real usando **NVIDIA DeepStream**.  
- Publica las detecciones hacia **Redis** y **MQTT**, para que el backend reciba los eventos y datos asociados.  

### 2. **Backend**
- Detecta y analiza los **rostros** y **cuerpos** de todas las personas identificadas.  
- Realiza **recortes automáticos** de los rostros y cuerpos y los guarda localmente.  
- Usa **Ollama** para generar una **descripción textual** de cada persona detectada (ropa, rasgos, accesorios, etc.).  
- Guarda toda la información (imágenes, descripciones, fecha y hora) en una **base de datos**.  
- Expone una **API REST** que permite acceder desde el exterior a las imágenes y descripciones almacenadas.  
  - Ejemplo: `/api/personas` o `/api/imagenes/<id>`.

### 3. **Frontend**
- Aplicación web sencilla en **HTML, CSS y JavaScript**.  
- Se conecta a la API del backend para mostrar:
  - Álbumes con las imágenes de las personas detectadas.  
  - Descripción generada.  
  - Fecha y hora de detección.  
- Incluye una **barra de búsqueda y filtros**:
  - Por **fecha y hora**.
  - Por **palabras clave** dentro de la descripción.

---

## ⚙️ Clonar el repositorio

```bash
git clone git@github.com:MagaliSoto/DeteccionPersonasEzeiza.git
````

---

## 🚀 Ejecución del sistema

1. Permitir acceso a la sesión X11:

   ```bash
   xhost +
   ```

2. Iniciar los contenedores de **DeepStream**, **Redis** y **MQTT**:

   ```bash
   docker compose --profile deepstream up -d --build --force-recreate
   ```

> El backend y el frontend pueden levantarse desde Docker o manualmente, según la configuración de desarrollo.

---

## 🧩 Componentes Principales

| Componente                | Función                                                                              |
| ------------------------- | ------------------------------------------------------------------------------------ |
| **DeepStream**            | Detección de personas y extracción de frames en tiempo real.                         |
| **Redis**                 | Intermediario de datos entre DeepStream y el backend.                                |
| **MQTT**                  | Canal de mensajería para notificaciones y sincronización.                            |
| **Backend (Python)**      | Análisis de detecciones, recortes, descripciones y API REST.                         |
| **Ollama**                | Generación de descripciones automáticas de las personas detectadas.                  |
| **Base de Datos (MySQL)** | Almacenamiento de información estructurada: rostros, cuerpos, fechas, descripciones. |
| **Frontend (HTML + JS)**  | Interfaz visual para explorar las detecciones y filtrar resultados.                  |

---

## 🖼️ Ejemplo de flujo

1. DeepStream detecta una persona en el video.
2. El backend recibe la detección vía Redis/MQTT.
3. Se recortan las imágenes del rostro y del cuerpo.
4. Ollama genera una descripción textual.
5. Toda la información se guarda en la base de datos.
6. El frontend consulta la API y muestra los resultados filtrables.

---

## 🔧 Archivos de Configuración

* **Fuente RTSP:**

  ```
  /perception/cfg/sources.yml
  ```
* **Zonas de interés (ROI):**

  ```
  /perception/cfg/nvdsanalytics.txt
  ```
* **Configuración del backend (variables de entorno):**

  * Tokens de Ollama
  * Rutas locales de almacenamiento de imágenes
  * Credenciales de la base de datos

---

## 📦 Tecnologías

* **NVIDIA DeepStream SDK**
* **Docker Compose**
* **Redis**
* **MQTT**
* **Python (Flask / FastAPI)**
* **Ollama**
* **MySQL**
* **HTML + JavaScript (Frontend Web)**

---

## 📄 Licencia

Proyecto demostrativo desarrollado para detección, descripción y visualización de personas en tiempo real.
Uso permitido con fines de desarrollo, evaluación o investigación.
