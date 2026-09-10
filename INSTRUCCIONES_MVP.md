# Instrucciones para Correr el MVP en tu Computadora y Celular

Este MVP es una aplicación web responsiva construida con Streamlit. Utiliza la cámara del dispositivo para simular la "visión del dron" mediante Inteligencia Artificial (OpenCV y lectura de códigos) y actualiza una tabla en tiempo real.

## Requisitos previos
Debes tener instalado Python (preferiblemente la versión 3.9 o superior).

## 1. Instalar las dependencias
Abre una terminal (PowerShell o CMD) y navega hasta esta carpeta (`generados/app_celular`). Luego instala las librerías necesarias ejecutando:

```bash
pip install streamlit opencv-python pyzbar pandas pillow numpy
```
*(Nota para Windows: Para que `pyzbar` funcione correctamente, a veces se requiere tener instalados los redistribuibles de C++. Si lanza un error al leer códigos, la solución es instalar las herramientas de compilación de Visual Studio o descargar la librería zbar directamente).*

## 2. Ejecutar la aplicación
En la misma terminal, ejecuta el siguiente comando:

```bash
streamlit run app.py
```

## 3. Probar en el Celular (¡La mejor presentación para el Hackathon!)
Cuando ejecutes el comando anterior, verás en la terminal algo como esto:

```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.X.X:8501
```

1. Asegúrate de que tu celular y tu computadora estén conectados al **mismo WiFi**.
2. Abre el navegador de tu celular (Chrome, Safari).
3. Escribe la dirección que aparece en **Network URL** (ejemplo: `http://192.168.1.5:8501`).
4. ¡Listo! Verás la aplicación en la pantalla de tu celular. Podrás usar la cámara trasera del teléfono para tomar fotos de códigos QR y verás cómo se actualiza la tabla de inventario en vivo.

## 4. ¿Cómo probarlo?
Genera códigos QR gratis en internet con los textos exactos que programamos en la base de datos simulada:
* `NESTLE-001`
* `NESTLE-002`
* `NESTLE-003`

Puedes mostrarlos desde otro celular a la cámara o imprimirlos y pegarlos en cajitas de cartón. Al escanearlos, el estado en el dashboard cambiará mágicamente de "Pendiente" a "Verificado".
