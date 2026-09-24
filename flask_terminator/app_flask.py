import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"
import cv2
import numpy as np
from flask import Flask, render_template, Response, jsonify, request
from pyzbar.pyzbar import decode
import tf_keras
from tf_keras.models import load_model
from tf_keras.layers import DepthwiseConv2D
from tf_keras.utils import custom_object_scope
from PIL import Image, ImageOps

app = Flask(__name__, static_folder="../docs/images", static_url_path="/images")
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Rutas asumiendo que corres desde la raiz del proyecto
BASE_DIR = r"c:\GitHub\aerostock-mvp"
MODEL_PATH = os.path.join(BASE_DIR, "keras_model.h5")
LABELS_PATH = os.path.join(BASE_DIR, "labels.txt")

class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, **kwargs):
        if 'groups' in kwargs: del kwargs['groups']
        super().__init__(**kwargs)

# Cargar IA
print("[SERVIDOR] Cargando Inteligencia Artificial...")
try:
    with custom_object_scope({'DepthwiseConv2D': CustomDepthwiseConv2D}):
        model = load_model(MODEL_PATH, compile=False)
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        class_names = [line.strip().split(" ", 1)[1] if " " in line.strip() else line.strip() for line in f.readlines()]
except Exception as e:
    print(f"Error AI: {e}")
    model = None
    class_names = []

# Configurar AprilTags
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
detector_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)
MARKER_SIZE = 0.078
MAPA_RACKS = {0: "Rack A1", 1: "Rack A2", 2: "Rack A3", 3: "Mesa Picking"}

# Estado Global de la App para que la interfaz Web lo lea
global_state = {
    "lpn": "NO DETECTADO",
    "ia_result": "Esperando...",
    "distancia": "0.00m",
    "alerts": []
}

import threading
import time

class VideoCamera(object):
    def __init__(self):
        self.video = None
        self.grabbed = False
        self.frame = None
        self.switching = False
        self.set_source("droidcam")
        threading.Thread(target=self.update, args=(), daemon=True).start()

    def set_source(self, src):
        self.switching = True
        time.sleep(0.1) # Esperar a que el hilo pause
        if self.video is not None:
            self.video.release()
        
        if src == "droidcam":
            self.video = cv2.VideoCapture("http://192.168.100.115:4747/video")
            # Fallback automático si DroidCam falla
            if not self.video.isOpened():
                self.video = cv2.VideoCapture(0)
        else:
            self.video = cv2.VideoCapture(int(src))
            
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.switching = False

    def update(self):
        while True:
            if self.switching or self.video is None or not self.video.isOpened():
                time.sleep(0.05)
                continue
                
            grabbed, frame = self.video.read()
            if grabbed:
                self.grabbed = True
                self.frame = cv2.resize(frame, (800, 600))
            else:
                time.sleep(0.01)

    def get_frame(self):
        return self.frame

camera_instance = None

def generate_frames():
    global global_state, camera_instance
    if camera_instance is None:
        camera_instance = VideoCamera()
    
    frame_count = 0
    last_frame_time = 0
    
    while True:
        frame = camera_instance.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue
            
        # Control estricto a 30 FPS máximos para no colapsar el WiFi con frames duplicados
        current_time = time.time()
        if current_time - last_frame_time < 0.033:
            time.sleep(0.005)
            continue
        last_frame_time = current_time

        frame_copy = frame.copy()
        h, w = frame_copy.shape[:2]
        
        # 1. AprilTags (SLAM)
        corners, ids, rejected = detector.detectMarkers(frame_copy)
        if ids is not None:
            camera_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float32)
            dist_coeffs = np.zeros((4,1))
            cv2.aruco.drawDetectedMarkers(frame_copy, corners, ids)
            for i in range(len(ids)):
                tag_id = int(np.ravel(ids[i])[0])
                image_points = corners[i].reshape((4, 2))
                obj_points = np.array([
                    [-MARKER_SIZE/2,  MARKER_SIZE/2, 0], [ MARKER_SIZE/2,  MARKER_SIZE/2, 0],
                    [ MARKER_SIZE/2, -MARKER_SIZE/2, 0], [-MARKER_SIZE/2, -MARKER_SIZE/2, 0]
                ], dtype=np.float32)
                suc, rvec, tvec = cv2.solvePnP(obj_points, image_points, camera_matrix, dist_coeffs)
                if suc:
                    distancia = tvec[2][0]
                    global_state["distancia"] = f"{distancia:.2f}m"
                    try: cv2.drawFrameAxes(frame_copy, camera_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
                    except: cv2.aruco.drawAxis(frame_copy, camera_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
        else:
            global_state["distancia"] = "Buscando..."
        
        # 2. PyZbar (Códigos de Barras)
        decoded = decode(frame_copy)
        current_lpn = "NO DETECTADO"
        for obj in decoded:
            current_lpn = obj.data.decode('utf-8')
            (x, y, bw, bh) = obj.rect
            cv2.rectangle(frame_copy, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
            cv2.putText(frame_copy, f"LPN: {current_lpn}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        global_state["lpn"] = current_lpn
        
        # 3. Keras AI (Cada 10 frames)
        if model and frame_count % 10 == 0:
            img_rgb = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            pil_img = ImageOps.fit(pil_img, (224, 224), Image.Resampling.LANCZOS)
            img_array = np.asarray(pil_img)
            normalized_img = (img_array.astype(np.float32) / 127.5) - 1
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            data[0] = normalized_img
            prediction = model.predict(data, verbose=0)
            index = np.argmax(prediction)
            global_state["ia_result"] = class_names[index]
            
        current_rack = "Ninguno"
        if "ids" in locals() and ids is not None and len(ids) > 0:
            tid = int(np.ravel(ids[0])[0])
            current_rack = MAPA_RACKS.get(tid, f"Tag {tid}")
        global_state["current_rack"] = current_rack

        frame_count += 1
        ret, buffer = cv2.imencode('.jpg', frame_copy, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def api_status():
    return jsonify(global_state)

@app.route('/api/set_camera', methods=['POST'])
def set_camera():
    global camera_instance
    src = request.json.get('src', 'droidcam')
    if camera_instance is not None:
        camera_instance.set_source(src)
    return jsonify({"status": "ok", "src": src})

if __name__ == '__main__':
    print("[SISTEMA] Servidor Flask corriendo. Abre http://localhost:5000 en tu navegador.")
    # Threaded=True permite que el video fluya sin bloquearse
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
