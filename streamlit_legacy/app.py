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
import sqlite3
import datetime
import random

# ==========================================
# CONFIGURACIÓN DE PÁGINA (UI/UX)
# ==========================================
st.set_page_config(page_title="AeroStock OS | Nestlé", page_icon="🚁", layout="wide")

st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #f8fafc; border: 1px solid #e2e8f0;
        padding: 15px; border-radius: 10px; border-left: 5px solid #00529B;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .main-title { color: #00529B; font-weight: bold; }
    .stButton>button { background-color: #E32322; color: white; border-radius: 5px; font-weight: bold; }
    .telemetry-box {
        background-color: #1E293B; color: #10B981; font-family: monospace;
        padding: 10px; border-radius: 5px; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DATOS SQLITE (TRAZABILIDAD)
# ==========================================
def init_db():
    conn = sqlite3.connect("aerostock_trazabilidad.db")
    cursor = conn.cursor()
    # Dropping to ensure fresh schema with new LPN IDs
    cursor.execute('DROP TABLE IF EXISTS inventory_metadata')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_metadata (
            lpn_id TEXT PRIMARY KEY,
            producto TEXT,
            lote TEXT,
            fecha_ingreso TEXT,
            fecha_caducidad TEXT,
            proveedor TEXT,
            cantidad_recibida TEXT,
            condicion_empaque TEXT
        )
    ''')
    
    # Leer labels.txt para generar la BD dinámica
    datos_prueba = []
    try:
        with open("labels.txt", "r", encoding="utf-8") as f:
            labels = f.readlines()
            
        index = 1
        for line in labels:
            if not line.strip(): continue
            parts = line.strip().split(" ", 1)
            name = parts[1] if len(parts) > 1 else parts[0]
            if "VACIO" in name.upper(): continue
            
            # Formato simplificado para Códigos de Barras más fáciles de leer (líneas más gruesas)
            lpn_id = f"N{index:02d}"
            
            # Metadatos falsos realistas
            lote = f"L-2026-{index:03d}"
            fecha_ingreso = "2026-09-01"
            fecha_caducidad = "2027-01-15" if index % 2 == 0 else "2026-10-30"
            proveedor = "Fábrica Surindu" if "RICA" in name.upper() or "GALAK" in name.upper() else "Nestlé Ecuador"
            # Lógica para diferenciar Pallets (Cajas) de Productos Sueltos (Picking)
            if "SUELT" in name.upper() or "PICKING" in name.upper() or "UNIDAD" in name.upper():
                cantidad = f"{index * 5} unidades (Área de Picking)"
            else:
                cantidad = f"{100 * index} cajas (Pallet Completo)"
            
            datos_prueba.append((lpn_id, name, lote, fecha_ingreso, fecha_caducidad, proveedor, cantidad, "Óptima"))
            index += 1
    except:
        pass 
        
    # Trampa para el test de desalineación
    datos_prueba.append(("N99", "ERROR-HUMANO (Desalineación)", "L-2026-ERR", "2026-09-12", "2028-05-01", "Desconocido", "1 pallet", "Óptima"))
    
    cursor.executemany('''
        INSERT OR REPLACE INTO inventory_metadata (lpn_id, producto, lote, fecha_ingreso, fecha_caducidad, proveedor, cantidad_recibida, condicion_empaque)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', datos_prueba)
    
    conn.commit()
    conn.close()

init_db()

def get_metadata(lpn_id):
    conn = sqlite3.connect("aerostock_trazabilidad.db")
    cursor = conn.cursor()
    cursor.execute("SELECT producto, lote, fecha_ingreso, fecha_caducidad, proveedor, cantidad_recibida, condicion_empaque FROM inventory_metadata WHERE lpn_id=?", (lpn_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# ==========================================
# Carga de Modelos y Datos
# ==========================================
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs: del kwargs['groups']
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
    st.session_state.db = pd.DataFrame(columns=["Timestamp", "LPN_Leido", "IA_Visual", "Lote", "Estado", "Decision_Operativa"])

# ==========================================
# MENÚ LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("docs/images/nestle_logo.png", use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #00529B;'>AeroStock OS</h2>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navegación Táctica", ["📊 Dashboard Analytics", "💰 ROI & Business Case", "🚁 Escáner Táctico (IA)", "ℹ️ Contexto y Equipo"])
    st.markdown("---")
    st.caption("Hackathon InnoLabs Nestlé ESPOL 2026")
    st.caption("Desarrollado por: J. Carreño & J. Paladines")

# ==========================================
# PÁGINA 1: DASHBOARD ANALYTICS (POWER BI)
# ==========================================
if menu == "📊 Dashboard Analytics":
    st.markdown("<h1 class='main-title'>📊 Dashboard de Inteligencia Operativa</h1>", unsafe_allow_html=True)
    st.markdown("Monitor de KPIs en tiempo real para control de inventarios y trazabilidad alimentaria.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pallets Auditados", "1,245", "+15% vs ayer")
    c2.metric("Desalineaciones ASRS", "12", "-2 casos")
    c3.metric("Alertas de Trazabilidad", "8", "Falta Código de Barras")
    c4.metric("Eficiencia FEFO", "98.5%", "+1.2%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tendencia de Anomalías (Últimos 7 días)")
        chart_data = pd.DataFrame(
            np.random.randint(2, 15, size=(7, 2)),
            columns=['Desalineación ASRS', 'Pérdida Trazabilidad (Ilegible)'],
            index=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        )
        st.line_chart(chart_data)
    with col2:
        st.subheader("Estado de Auditorías")
        pie_data = pd.DataFrame({
            'Categoría': ['Match Perfecto', 'Desalineación ASRS', 'Sin Código (Alerta)'],
            'Casos': [85, 5, 10]
        }).set_index('Categoría')
        st.bar_chart(pie_data)
        
    st.markdown("---")
    st.subheader("Historial de Decisiones Autónomas del Dron")
    st.dataframe(st.session_state.db, use_container_width=True)

# ==========================================
# PÁGINA 2: ROI & BUSINESS CASE
# ==========================================
elif menu == "💰 ROI & Business Case":
    st.markdown("<h1 class='main-title'>💰 Retorno de Inversión (Caso de Negocio)</h1>", unsafe_allow_html=True)
    st.markdown("Proyección de ahorros operativos y mitigación de riesgos (Shrinkage) en Nestlé Ecuador (Surindu / Ceibos).")

    r1, r2, r3 = st.columns(3)
    r1.metric("Horas-Hombre Recuperadas / Mes", "1,200 hrs", "Evitando paro de 2h/día con 20 operarios")
    r2.metric("Reducción de Mermas (Spoilage)", "$ 45,000", "Prevención anual por control FEFO Térmico")
    r3.metric("ROI Estimado (12 meses)", "285 %", "Payback en 4.2 meses")

    st.markdown("### 🎯 Impacto Operativo")
    st.info("**Cero Parálisis en Bodega:** AeroStock realiza conteos cíclicos a demanda o en ventanas de baja actividad. Actualmente, Nestlé detiene la recepción/despacho durante 2 horas cada mañana.")
    st.warning("**Seguridad Laboral (Cero Accidentes):** Reduce la exposición humana a operaciones en altura (hasta 12 metros) y a temperaturas extremas (-20°C en cámaras de frío).")
    st.success("**Prevención de Desalineaciones (ASRS):** Al evitar errores de digitación o 'ceguera' del código de barras, protegemos la integridad del maestro de materiales en SAP S/4HANA.")


# ==========================================
# PÁGINA 3: ESCÁNER TÁCTICO (IA)
# ==========================================
elif menu == "🚁 Escáner Táctico (IA)":
    st.markdown("<h1 class='main-title'>🚁 Escáner Táctico: Doble Verificación Cognitiva</h1>", unsafe_allow_html=True)
    st.markdown("Validación cruzada entre reconocimiento físico (IA) y la etiqueta maestra EAN-128 del Pallet.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        # Telemetría Anticolisión (Simulada)
        altitud = random.uniform(2.0, 11.5)
        dist_obs = random.uniform(3.5, 8.0)
        st.markdown(f"""
        <div class="telemetry-box">
            📡 <b>TELEMETRÍA DRON AEROSTOCK</b><br>
            📍 <b>Ubicación:</b> Pasillo B - Rack 3<br>
            📏 <b>Altitud:</b> {altitud:.1f} m | <b>Velocidad:</b> 0.5 m/s<br>
            🛡️ <b>Sensor Anticolisión:</b> ACTIVO (Obstáculo a {dist_obs:.1f}m - Seguro)
        </div>
        """, unsafe_allow_html=True)

        img_file_buffer = st.camera_input("Capturar pallet objetivo (Enfocar Código de Barras y Empaque)")
        
        if img_file_buffer is not None and ia_lista:
            with st.spinner("Procesando Doble Verificación Cognitiva..."):
                # 1. IA VISUAL
                ia_clase, ia_confianza = classify_image(img_file_buffer)
                
                # 2. LECTOR DE CÓDIGO DE BARRAS
                bytes_data = img_file_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
                ampliado = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                decoded_objects = decode(ampliado)
                if not decoded_objects:
                    decoded_objects = decode(cv2_img)
                
                lpn_leido = "NO DETECTADO"
                if decoded_objects:
                    lpn_leido = decoded_objects[0].data.decode("utf-8")

                # 3. LÓGICA DE DECISIÓN Y TRAZABILIDAD (SQLITE)
                decision = ""
                estado = ""
                estado_color = "success"
                lote_detectado = "N/A"
                
                if "VACIO" in ia_clase.upper():
                    decision = "PASILLO DESPEJADO. Continuar patrullaje autónomo."
                    estado = "Info"
                    estado_color = "info"
                elif lpn_leido == "NO DETECTADO":
                    # REGLA ESPECIAL PARA EL ÁREA DE PICKING (Productos Sueltos)
                    if "SUELT" in ia_clase.upper() or "PICKING" in ia_clase.upper() or "UNIDAD" in ia_clase.upper():
                        decision = f"ZONA DE PICKING: Unidad de '{ia_clase}' detectada visualmente. Contabilizando para armado de pedido mixto (Sin LPN)."
                        estado = "Picking (OK)"
                        estado_color = "success"
                    # REGLA PARA PALLETS SIN CÓDIGO (Pérdida de Trazabilidad)
                    else:
                        decision = f"PÉRDIDA DE TRAZABILIDAD: IA detectó '{ia_clase}' (Pallet), pero no hay Código de Barras legible. Imposible certificar Lote. Re-etiquetar."
                        estado = "Alerta Trazabilidad"
                        estado_color = "error"
                else:
                    # Buscar ID en Base de Datos SQLite
                    metadata = get_metadata(lpn_leido)
                    if metadata:
                        db_producto, db_lote, db_ingreso, db_caducidad, db_proveedor, db_cantidad, db_condicion = metadata
                        lote_detectado = db_lote
                        
                        # Validar si el producto de la BD coincide con la IA
                        if ia_clase.upper() in db_producto.upper() or db_producto.upper() in ia_clase.upper():
                            decision = f"TRAZABILIDAD OK: Coincide físico '{ia_clase}' con BD. (Lote: {db_lote} | Vence: {db_caducidad})"
                            estado = "Aprobado"
                            estado_color = "success"
                        else:
                            decision = f"DESALINEACIÓN ASRS: LPN '{lpn_leido}' pertenece a '{db_producto}' (Lote {db_lote}), pero IA visualiza '{ia_clase}'. Bloqueando Pallet en WMS."
                            estado = "Crítico (ASRS)"
                            estado_color = "error"
                    else:
                        decision = f"LPN DESCONOCIDO: El código '{lpn_leido}' no existe en el maestro de materiales."
                        estado = "Advertencia"
                        estado_color = "warning"
                
                nuevo_registro = pd.DataFrame([{
                    "Timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "LPN_Leido": lpn_leido,
                    "IA_Visual": ia_clase,
                    "Lote": lote_detectado,
                    "Estado": estado,
                    "Decision_Operativa": decision
                }])
                st.session_state.db = pd.concat([nuevo_registro, st.session_state.db], ignore_index=True)

    with col2:
        if img_file_buffer is not None and ia_lista:
            st.subheader("Auditoría de Trazabilidad")
            st.markdown(f"**LPN Extraído (Barcode):** `{lpn_leido}`")
            st.markdown(f"**Validación Visual (IA):** `{ia_clase}` (Precisión: {ia_confianza:.0%})")
            
            if estado_color == "success": 
                st.success(f"✅ {decision}")
            elif estado_color == "error": 
                st.error(f"🚨 {decision}")
            elif estado_color == "warning": 
                st.warning(f"⚠️ {decision}")
            else: 
                st.info(f"ℹ️ {decision}")
                
            st.markdown("### Registro Diario")
            st.dataframe(st.session_state.db.head(4), use_container_width=True)
        else:
            st.warning("Esperando feed de video... Encienda la cámara para iniciar inspección.")

# ==========================================
# PÁGINA 4: CONTEXTO Y EQUIPO
# ==========================================
elif menu == "ℹ️ Contexto y Equipo":
    st.markdown("<h1 class='main-title'>🏭 Sobre AeroStock OS</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("""
        ### Plataforma Híbrida: Inteligencia Operativa y Trazabilidad
        **AeroStock** fue desarrollado para el **Hackathon InnoLabs Nestlé ESPOL 2026** resolviendo cuellos de botella en almacenes de gran altura (12m) y operaciones logísticas críticas:
        
        * **Fase 1 (Dron Táctico Guiado):** El dron actúa como herramienta del montacarguista para auditar pallets extraviados o zonas de picking. Se elimina el riesgo humano de trabajar en alturas dentro de cámaras de frío.
        * **Fase 2 (100% Autónomo / SLAM Térmico):** Patrullajes nocturnos sin intervención humana usando odometría visual (AprilTags). Integración con termohidrómetros IoT para detectar microclimas anómalos y prevenir mermas de producto.
        
        **Pilares del Auditor Cognitivo:**
        1. **Alerta de Trazabilidad Perdida:** Si la IA detecta cajas pero el código de barras LPN está destruido/tapado, lanza una alerta fotográfica para evitar inventario ciego.
        2. **Doble Verificación (ASRS):** Cruza el LPN con el maestro de materiales (SAP/SQLite). Si SAP dice "Nescafé" pero la cámara reconoce cajas de "Maggi", el sistema bloquea el error humano instantáneamente.
        """)
    with c2:
        st.image("docs/images/logo_espol.png", width=150)
        st.markdown("""
        **Equipo Desarrollador:**
        * John Maximiliano Carreño Robalino
        * José Luis Paladines Sánchez
        
        **Reto 02:** Gestión Inteligente de Inventarios
        """)
