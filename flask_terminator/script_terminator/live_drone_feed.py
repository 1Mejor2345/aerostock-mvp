import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D
from tensorflow.keras.utils import custom_object_scope
from PIL import Image, ImageOps

# Rutas a los modelos (Asume que se corre desde la raiz del proyecto)
MODEL_PATH = "keras_model.h5"
LABELS_PATH = "labels.txt"

class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs: del kwargs['groups']
        super().__init__(**kwargs)

print("[SISTEMA] Cargando IA Visión Cognitiva (Keras)...")
try:
    with custom_object_scope({'DepthwiseConv2D': CustomDepthwiseConv2D}):
        model = load_model(MODEL_PATH, compile=False)
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        class_names = [line.strip().split(" ", 1)[1] if " " in line.strip() else line.strip() for line in f.readlines()]
except Exception as e:
    print(f"Error cargando IA: {e}")
    exit()

# Configuración AprilTags
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
detector_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)
MARKER_SIZE = 0.078
MAPA_RACKS = {0: "Rack A1", 1: "Rack A2", 2: "Zona Picking"}

# Conexión Cámara
url_droidcam = "http://192.168.100.115:4747/video"
cap = cv2.VideoCapture(url_droidcam)
if not cap.isOpened():
    print("[ALERTA] No se pudo conectar a DroidCam. Intentando webcam local (0)...")
    cap = cv2.VideoCapture(0)

print("[SISTEMA] AeroStock OS (HUD Terminator) Inicializado. Presiona 'q' para salir.")

frame_count = 0
ia_result = "Analizando..."
ia_conf = 0.0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    # HUD UI Estética Terminator
    cv2.putText(frame, "AEROSTOCK OS - VISUAL AUDIT", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.rectangle(frame, (10, 10), (w-10, h-10), (0, 255, 0), 2)

    # 1. APRILTAGS (SLAM)
    corners, ids, rejected = detector.detectMarkers(frame)
    if ids is not None:
        camera_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float32)
        dist_coeffs = np.zeros((4,1))
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        for i in range(len(ids)):
            tag_id = int(np.ravel(ids[i])[0])
            ubicacion = MAPA_RACKS.get(tag_id, f"Tag {tag_id}")
            image_points = corners[i].reshape((4, 2))
            obj_points = np.array([
                [-MARKER_SIZE/2,  MARKER_SIZE/2, 0], [ MARKER_SIZE/2,  MARKER_SIZE/2, 0],
                [ MARKER_SIZE/2, -MARKER_SIZE/2, 0], [-MARKER_SIZE/2, -MARKER_SIZE/2, 0]
            ], dtype=np.float32)
            success, rvec, tvec = cv2.solvePnP(obj_points, image_points, camera_matrix, dist_coeffs)
            if success:
                distancia = tvec[2][0]
                texto_nav = f"NAV: {ubicacion} | Dist: {distancia:.2f}m"
                try: cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
                except AttributeError: cv2.aruco.drawAxis(frame, camera_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
            else:
                texto_nav = f"NAV: {ubicacion}"
            c = corners[i].reshape((-1, 2))
            cv2.putText(frame, texto_nav, (int(c[0][0]), int(c[0][1]) - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # 2. CÓDIGOS DE BARRAS (PyZbar)
    decoded_objects = decode(frame)
    barcode_data = "LPN: NO DETECTADO"
    barcode_color = (0, 0, 255)
    for obj in decoded_objects:
        barcode_data = f"LPN: {obj.data.decode('utf-8')}"
        barcode_color = (0, 255, 0)
        (x, y, bw, bh) = obj.rect
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
        cv2.putText(frame, barcode_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # 3. IA (Keras) - Solo 1 de cada 10 frames para evitar lag
    if frame_count % 10 == 0:
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        pil_img = ImageOps.fit(pil_img, (224, 224), Image.Resampling.LANCZOS)
        img_array = np.asarray(pil_img)
        normalized_img = (img_array.astype(np.float32) / 127.5) - 1
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_img
        prediction = model.predict(data, verbose=0)
        index = np.argmax(prediction)
        ia_result = class_names[index]
        ia_conf = prediction[0][index]
    frame_count += 1
    
    # 4. DATA EN PANTALLA (Bottom HUD)
    cv2.putText(frame, barcode_data, (20, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, barcode_color, 2)
    ia_text_color = (0, 255, 0) if ia_conf > 0.8 else (0, 165, 255)
    cv2.putText(frame, f"IA VISUAL: {ia_result} ({ia_conf:.0%})", (20, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, ia_text_color, 2)

    cv2.imshow("AeroStock Terminator HUD", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
