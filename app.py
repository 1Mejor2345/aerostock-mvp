import streamlit as st
import cv2
import pandas as pd
from pyzbar.pyzbar import decode
import numpy as np

# Configuración del Dashboard
st.set_page_config(page_title="AeroStock - Decisiones", layout="wide")
st.title("🚁 AeroStock: Centro de Decisiones Operativas")
st.markdown("🚨 **Conectado con Métodos PEPS y Stock de Seguridad (Nestlé)**")

# Base de datos simulada
if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame({
        "ID_Pallet": ["NESTLE-001", "NESTLE-FEFO", "SIN-QR-DETECTADO"],
        "Producto": ["Nescafé Tradición", "Chocapic (Lote Antiguo)", "Desconocido"],
        "Método_Aplicable": ["Stock de Seguridad", "Método PEPS", "Seguimiento de Lotes"],
        "Estado": ["Pendiente", "CRÍTICO - Riesgo Caducidad", "Requiere IA Visual"]
    })

if "decision_sugerida" not in st.session_state:
    st.session_state.decision_sugerida = "Esperando datos del dron..."

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("📷 Feed del Dron Táctico")
    
    img_file_buffer = st.camera_input("📸 Cámara del Dron (Escanear Pallet o Producto)")
    
    if img_file_buffer is not None:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        decoded_objects = decode(cv2_img)
        
        if decoded_objects:
            for obj in decoded_objects:
                data = obj.data.decode("utf-8")
                
                if data == "NESTLE-FEFO":
                    st.session_state.db.loc[st.session_state.db["ID_Pallet"] == data, "Estado"] = "Localizado"
                    st.session_state.decision_sugerida = "⚠️ DECISIÓN PEPS: El dron detectó el lote antiguo de Chocapic al fondo del pasillo. ACCIÓN: Enviar montacargas para rotar este pallet hacia el frente de despacho."
                    st.warning("Alerta FEFO Activada.")
                elif data == "NESTLE-001":
                    st.session_state.db.loc[st.session_state.db["ID_Pallet"] == data, "Estado"] = "Verificado"
                    st.session_state.decision_sugerida = "✅ DECISIÓN STOCK DE SEGURIDAD: Pallet verificado. Los niveles de Nescafé cumplen con la cuota de Justo a Tiempo (JIT)."
                    st.success("Pallet registrado correctamente.")
                else:
                    st.error("Código no reconocido.")
        else:
            # SIMULACIÓN DE MACHINE LEARNING VISUAL (Cuando no hay QR)
            st.error("❌ Código QR no detectado o Ilegible.")
            st.info("🧠 Activando Modelo de Machine Learning (Visión Artificial)...")
            st.success("👁️ Reconocimiento Visual: Empaque Rojo/Amarillo detectado -> **Probabilidad 98%: Caldo Maggi**")
            st.session_state.db.loc[st.session_state.db["ID_Pallet"] == "SIN-QR-DETECTADO", "Estado"] = "Identificado por IA"
            st.session_state.decision_sugerida = "🔍 DECISIÓN DE SEGUIMIENTO: El dron encontró inventario 'fantasma' de Maggi sin código. ACCIÓN: Generar nueva etiqueta desde el sistema y enviar operario para re-etiquetar (Recuperación de Stock)."

with col2:
    st.subheader("📊 Panel de Inteligencia Operativa")
    
    def color_status(val):
        if 'Localizado' in val or 'Verificado' in val or 'Identificado' in val: color = 'green'
        elif 'CRÍTICO' in val: color = 'red'
        else: color = 'orange'
        return f'color: {color}; font-weight: bold'
    
    st.dataframe(st.session_state.db.style.map(color_status, subset=['Estado']), use_container_width=True)

    # El corazón del reto: La Toma de Decisiones
    st.markdown("### 🎯 Toma de Decisiones (Recomendación del Sistema)")
    st.info(st.session_state.decision_sugerida)
