import streamlit as st
import cv2
import pandas as pd
from pyzbar.pyzbar import decode
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps

# Configuración del Dashboard
st.set_page_config(page_title="AeroStock - IA Avanzada", layout="wide")
st.title("🚁 AeroStock: Auditor Cognitivo (IA Real)")
st.markdown("🚨 **Doble Verificación: Lector QR + Red Neuronal (TensorFlow)**")

# Cargar Modelo de IA (Se guarda en caché para no volver a cargar en cada foto)
@st.cache_resource
def load_tm_model():
    model = load_model("keras_model.h5", compile=False)
    with open("labels.txt", "r", encoding="utf-8") as f:
        # Quitar los números del inicio de las etiquetas (ej. "0 CAJA GALAK" -> "CAJA GALAK")
        class_names = [line.strip().split(" ", 1)[1] if " " in line.strip() else line.strip() for line in f.readlines()]
    return model, class_names

try:
    model, class_names = load_tm_model()
    ia_lista = True
except Exception as e:
    st.error(f"Error cargando el modelo: {e}")
    ia_lista = False

# Función para predecir con la imagen
def classify_image(img_buffer):
    image = Image.open(img_buffer).convert("RGB")
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array
    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    return class_name, confidence_score

# Base de datos del Historial
if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Cerebro_QR", "Cerebro_IA_Visual", "Confianza", "Decision_Operativa"])

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📷 Feed del Dron (Toma la foto)")
    img_file_buffer = st.camera_input("Escanea la caja (con o sin QR)")
    
    if img_file_buffer is not None and ia_lista:
        # 1. PASAR POR EL CEREBRO DE IA (Visión Artificial)
        st.info("🧠 Procesando frame con Inteligencia Artificial...")
        ia_clase, ia_confianza = classify_image(img_file_buffer)
        
        # 2. PASAR POR EL CEREBRO DE CÓDIGOS (Lector QR)
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        decoded_objects = decode(cv2_img)
        
        qr_leido = "NO DETECTADO"
        if decoded_objects:
            qr_leido = decoded_objects[0].data.decode("utf-8")

        # 3. EL JUEZ: LÓGICA DE DOBLE VERIFICACIÓN
        decision = ""
        estado_color = "success"

        # Caso A: No hay nada en la imagen
        if "VACIO" in ia_clase.upper():
            decision = "PASILLO DESPEJADO. Continuar patrullaje."
            estado_color = "info"
            
        # Caso B: Hay un QR y hay un producto (Verificar Desalineación)
        elif qr_leido != "NO DETECTADO":
            # Demostración del error de Filippo (Simulado por un QR que diga "ERROR-HUMANO")
            if "ERROR" in qr_leido.upper() or qr_leido.upper() != ia_clase.upper()[:len(qr_leido)]:
                decision = f"🚨 DESALINEACIÓN ASRS: El QR dice '{qr_leido}', pero la caja física es '{ia_clase}'. Bloqueando envío por error humano."
                estado_color = "error"
            else:
                decision = "✅ DOBLE VERIFICACIÓN OK: Código y Empaque físico coinciden."
                estado_color = "success"
                
        # Caso C: Hay un producto pero NO HAY QR (Etiqueta dañada por film/roto)
        else:
            decision = f"⚠️ ETIQUETA DAÑADA/AUSENTE: Producto '{ia_clase}' recuperado por IA visual. Ordenar re-etiquetado."
            estado_color = "warning"

        # Mostrar Resultados al usuario
        st.markdown(f"**Lector QR:** {qr_leido}")
        st.markdown(f"**IA Visual:** {ia_clase} ({ia_confianza:.0%} confianza)")
        
        if estado_color == "success": st.success(decision)
        elif estado_color == "error": st.error(decision)
        elif estado_color == "warning": st.warning(decision)
        else: st.info(decision)

        # Guardar en base de datos
        nuevo_registro = pd.DataFrame([{
            "Cerebro_QR": qr_leido,
            "Cerebro_IA_Visual": ia_clase,
            "Confianza": f"{ia_confianza:.0%}",
            "Decision_Operativa": decision
        }])
        st.session_state.db = pd.concat([nuevo_registro, st.session_state.db], ignore_index=True)

with col2:
    st.subheader("📊 Panel de Inteligencia Operativa")
    st.markdown("Registro en tiempo real de decisiones autónomas del dron:")
    st.dataframe(st.session_state.db, use_container_width=True)
