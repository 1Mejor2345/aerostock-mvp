import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import streamlit as st
import cv2
import pandas as pd
from pyzbar.pyzbar import decode
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D
from tensorflow.keras.utils import custom_object_scope
from PIL import Image, ImageOps

# ==========================================
# CONFIGURACIÓN DE PÁGINA (UI/UX)
# ==========================================
st.set_page_config(page_title="AeroStock OS | Nestlé", page_icon="🚁", layout="wide")

# CSS Personalizado para darle look de "Dashboard Profesional"
st.markdown("""
<style>
    /* Estilos de tarjetas métricas (Power BI feel) */
    div[data-testid="metric-container"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00529B; /* Azul Nestlé */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    /* Títulos principales */
    .main-title { color: #00529B; font-weight: bold; }
    /* Estilo del botón táctico */
    .stButton>button {
        background-color: #E32322; /* Rojo Maggi */
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# Carga de Modelos y Datos
# ==========================================
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs:
            del kwargs['groups']
        super().__init__(**kwargs)

@st.cache_resource
def load_tm_model():
    with custom_object_scope({'DepthwiseConv2D': CustomDepthwiseConv2D}):
        model = load_model("keras_model.h5", compile=False)
    with open("labels.txt", "r", encoding="utf-8") as f:
        class_names = [line.strip().split(" ", 1)[1] if " " in line.strip() else line.strip() for line in f.readlines()]
    return model, class_names

try:
    model, class_names = load_tm_model()
    ia_lista = True
except Exception as e:
    ia_lista = False
    st.sidebar.error(f"Error AI: {e}")

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
    return class_names[index], prediction[0][index]

if "db" not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=["Timestamp", "Cerebro_QR", "Cerebro_IA_Visual", "Confianza", "Estado", "Decision_Operativa"])

# ==========================================
# MENÚ LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("docs/images/nestle_logo.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #00529B;'>AeroStock OS</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    menu = st.radio(
        "Navegación Táctica",
        ["📊 Dashboard Analytics", "🚁 Escáner Táctico (IA)", "ℹ️ Contexto y Equipo"]
    )
    
    st.markdown("---")
    st.caption("Hackathon InnoLabs Nestlé ESPOL 2026")
    st.caption("Desarrollado por: J. Carreño & J. Paladines")

# ==========================================
# PÁGINA 1: DASHBOARD ANALYTICS (POWER BI)
# ==========================================
if menu == "📊 Dashboard Analytics":
    st.markdown("<h1 class='main-title'>📊 Dashboard de Inteligencia Operativa</h1>", unsafe_allow_html=True)
    st.markdown("Monitor de KPIs en tiempo real para control de inventarios y toma de decisiones (PEPS/FEFO).")
    
    # Métricas Superiores
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pallets Auditados Hoy", "1,245", "+15% vs ayer")
    c2.metric("Desalineaciones ASRS Evitadas", "12", "-2 casos")
    c3.metric("Recuperación Etiquetas (IA)", "48", "+5 casos")
    c4.metric("Eficiencia de Rotación PEPS", "98.5%", "+1.2%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos simulados
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tendencia de Anomalías (Últimos 7 días)")
        chart_data = pd.DataFrame(
            np.random.randint(2, 15, size=(7, 2)),
            columns=['Desalineación ASRS', 'Etiquetas Dañadas/Frío'],
            index=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        )
        st.line_chart(chart_data)
        
    with col2:
        st.subheader("Distribución de Inventario Recuperado por IA")
        pie_data = pd.DataFrame({
            'Categoría': ['Maggi', 'Nescafé', 'Galletas', 'Lácteos'],
            'Recuperados': [45, 20, 15, 20]
        }).set_index('Categoría')
        st.bar_chart(pie_data)
        
    st.markdown("---")
    st.subheader("Historial de Decisiones Autónomas del Dron")
    st.dataframe(st.session_state.db, use_container_width=True)

# ==========================================
# PÁGINA 2: ESCÁNER TÁCTICO (IA)
# ==========================================
elif menu == "🚁 Escáner Táctico (IA)":
    st.markdown("<h1 class='main-title'>🚁 Escáner Táctico y Doble Verificación</h1>", unsafe_allow_html=True)
    st.markdown("Interfaz del Montacarguista / Operador Edge para patrullaje y auditoría de excepciones.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.info("📡 **Terminal Activa:** Montacargas 04 | **Ubicación:** Pasillo B - Rack 3")
        img_file_buffer = st.camera_input("Capturar pallet objetivo")
        
        if img_file_buffer is not None and ia_lista:
            with st.spinner("Procesando Doble Verificación Cognitiva..."):
                # 1. IA VISUAL
                ia_clase, ia_confianza = classify_image(img_file_buffer)
                
                # 2. LECTOR QR (Con mejora óptica)
                bytes_data = img_file_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
                ampliado = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                decoded_objects = decode(ampliado)
                if not decoded_objects:
                    decoded_objects = decode(cv2_img)
                
                qr_leido = "NO DETECTADO"
                if decoded_objects:
                    qr_leido = decoded_objects[0].data.decode("utf-8")

                # 3. LÓGICA DE DECISIÓN
                decision = ""
                estado = ""
                estado_color = "success"

                if "VACIO" in ia_clase.upper():
                    decision = "PASILLO DESPEJADO. Continuar patrullaje."
                    estado = "Info"
                    estado_color = "info"
                elif qr_leido != "NO DETECTADO":
                    if "ERROR" in qr_leido.upper() or qr_leido.upper() != ia_clase.upper()[:len(qr_leido)]:
                        decision = f"DESALINEACIÓN ASRS: QR indica '{qr_leido}' pero IA detecta '{ia_clase}'. Envío bloqueado por error humano."
                        estado = "Crítico"
                        estado_color = "error"
                    else:
                        decision = "DOBLE VERIFICACIÓN OK: SAP y físico coinciden."
                        estado = "Aprobado"
                        estado_color = "success"
                else:
                    decision = f"ETIQUETA DAÑADA: Producto '{ia_clase}' identificado por IA. Emitir orden de re-etiquetado."
                    estado = "Advertencia"
                    estado_color = "warning"
                
                import datetime
                nuevo_registro = pd.DataFrame([{
                    "Timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "Cerebro_QR": qr_leido,
                    "Cerebro_IA_Visual": ia_clase,
                    "Confianza": f"{ia_confianza:.0%}",
                    "Estado": estado,
                    "Decision_Operativa": decision
                }])
                st.session_state.db = pd.concat([nuevo_registro, st.session_state.db], ignore_index=True)

    with col2:
        if img_file_buffer is not None and ia_lista:
            st.subheader("Resultados de Auditoría")
            st.markdown(f"**Lector Óptico (QR):** `{qr_leido}`")
            st.markdown(f"**Reconocimiento Visual (IA):** `{ia_clase}` (Precisión: {ia_confianza:.0%})")
            
            if estado_color == "success": 
                st.success(f"✅ {decision}")
            elif estado_color == "error": 
                st.error(f"🚨 {decision}")
            elif estado_color == "warning": 
                st.warning(f"⚠️ {decision}")
            else: 
                st.info(f"ℹ️ {decision}")
                
            st.markdown("### Historial Reciente")
            st.dataframe(st.session_state.db.head(3), use_container_width=True)
        else:
            st.warning("Esperando conexión de video... Encienda la cámara para auditar.")

# ==========================================
# PÁGINA 3: CONTEXTO Y EQUIPO
# ==========================================
elif menu == "ℹ️ Contexto y Equipo":
    st.markdown("<h1 class='main-title'>🏭 Sobre AeroStock</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("""
        ### Dron Táctico con Inteligencia Operativa
        **AeroStock** no es un dron de inventario tradicional; es un auditor cognitivo. 
        Desarrollado para el **Hackathon InnoLabs Nestlé ESPOL 2026**, resuelve tres cuellos de botella críticos:
        
        1. **Ceguera Logística (Etiquetas dañadas):** Las etiquetas ASRS se dañan con la manipulación y el film de las cámaras de frío (-20°C). AeroStock reconoce el empaque gracias a Computer Vision aunque no haya QR.
        2. **Error Humano ASRS:** Cuando un operario arregla una falla en el rack automatizado, suele tipear mal el producto en SAP. AeroStock hace **Doble Verificación** (QR vs Foto Física) y detecta esta desalineación.
        3. **Control Térmico y PEPS:** Mediante integración de IA, valida que los productos mantengan la estiba correcta y previene el bloqueo de lotes próximos a vencer.
        """)
    with c2:
        st.image("docs/images/logo_espol.png", width=150)
        st.markdown("""
        **Equipo Desarrollador:**
        * John Maximiliano Carreño Robalino
        * José Luis Paladines Sánchez
        
        **Reto 02:** Gestión Inteligente de Inventarios
        """)
