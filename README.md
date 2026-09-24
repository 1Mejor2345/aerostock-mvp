# AeroStock OS - MVP (Hackathon Edition) 🚀

AeroStock es un prototipo de **Sistema Automático de Almacenamiento y Recuperación (ASRS)** basado en Visión Artificial. Utiliza un dron (simulado con DroidCam y una red neuronal) para auditar el inventario, escanear pallets y detectar caducidades o errores de logística en tiempo real.

## 🌟 Características del Prototipo

1. **Inteligencia Artificial Visual:** Modelo entrenado en **Teachable Machine (Keras)** capaz de clasificar productos de Nestlé (Cajas de Taco, Cereal, Cocoa, etc.).
2. **Navegación Espacial (SLAM):** Uso de **AprilTags** (Marcadores Fiduciales) y **OpenCV** para identificar Racks específicos (Rack A1, Rack A2, Rack A3) y calcular la distancia focal al pallet.
3. **Lectura de Códigos de Barras (PyZbar):** Escaneo de LPNs (License Plate Numbers) en formato CODE-128 integrados a los pallets.
4. **Validación Logística Dinámica (ERP Mock):** 
   - Verifica que el producto físico cuadre con el LPN de la caja.
   - Analiza las fechas de caducidad en tiempo real y alerta automáticamente si un producto está vencido (prioridad sanitaria).
5. **AeroStock OS (Dashboard):** Una aplicación Web (Single-Page Application con Tailwind CSS) para comandar al dron, ver su transmisión en vivo (HUD) y recibir el historial de auditorías.

## 📂 Arquitectura del Repositorio

- `/flask_terminator`: Contiene el código fuente del servidor **Flask** (`app_flask.py`) y la interfaz **Web** (`templates/index.html`). También incluye los scripts generadores de códigos de barras.
- `/docs/legacy`: Diseños conceptuales antiguos y códigos QR obsoletos.
- `/streamlit_legacy`: Primera versión del prototipo construida en Streamlit (descontinuada a favor de la arquitectura asíncrona de Flask).
- `keras_model.h5` y `labels.txt`: El cerebro (red neuronal) del sistema. Entrenado con 8 clases base.

## 🛠️ Requisitos e Instalación

### 1. Clonar e Instalar Dependencias
Asegúrate de tener **Python 3.10+**. Ejecuta:
```bash
pip install -r requirements.txt
```

### 2. Configurar Cámara (DroidCam)
Si usas DroidCam para simular el dron, asegúrate de colocar la IP correcta de la app de DroidCam dentro de la interfaz web, o selecciona la cámara de tu laptop en el menú.

### 3. Ejecutar el Servidor
Inicia la terminal, ve a la carpeta del proyecto y corre:
```bash
python flask_terminator/app_flask.py
```
> **NOTA:** El servidor Flask debe correrse desde la carpeta raíz para poder detectar el archivo `keras_model.h5`.

Abre `http://localhost:5000` en tu navegador para ingresar a **AeroStock OS**.

---
*Prototipo desarrollado para validación técnica en el Hackathon.*