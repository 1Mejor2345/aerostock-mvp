import cv2
import numpy as np

# 1. Diccionario que mapea cada Tag ID con la ubicación física en bodega
MAPA_RACKS = {
    0: "Pasillo 01 - Nivel 02 (Rack A1)",
    1: "Pasillo 01 - Nivel 03 (Rack A2)",
    2: "Pasillo 02 - Nivel 01 (Zona Picking B1)",
}

# 2. Configurar el diccionario AprilTag tag36h11 nativo en OpenCV
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
detector_params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)

# 3. Conectar cámara (0 para webcam integrada, o la URL IP de DroidCam)
# Reemplaza con la IP exacta que muestra tu celular
url_droidcam = "http://192.168.100.115:4747/video"
cap = cv2.VideoCapture(url_droidcam)

print(
    "Iniciando auditoria AeroStock con AprilTags. Presiona 'q' para finalizar."
)

while True:
  ret, frame = cap.read()
  if not ret:
    print("No se pudo leer el flujo de video.")
    break

  # Detección de marcadores
  corners, ids, rejected = detector.detectMarkers(frame)

  if ids is not None:
    # Generar matriz de cámara aproximada para el celular
    h, w = frame.shape[:2]
    camera_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float32)
    dist_coeffs = np.zeros((4,1))
    
    # Tamaño físico de tu cuadrito impreso (Ajusta este valor si lo imprimes más grande o pequeño)
    # 0.078 significa 7.8 centímetros (Tamaño real impreso por el usuario)
    MARKER_SIZE = 0.078 
    obj_points = np.array([
        [-MARKER_SIZE/2,  MARKER_SIZE/2, 0],
        [ MARKER_SIZE/2,  MARKER_SIZE/2, 0],
        [ MARKER_SIZE/2, -MARKER_SIZE/2, 0],
        [-MARKER_SIZE/2, -MARKER_SIZE/2, 0]
    ], dtype=np.float32)

    cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    for i in range(len(ids)):
        tag_id = int(np.ravel(ids[i])[0])
        ubicacion = MAPA_RACKS.get(tag_id, f"Tag {tag_id} desconocido")

        # MAGIA MATEMÁTICA: Resolver PnP (Perspectiva de N Puntos)
        image_points = corners[i].reshape((4, 2))
        success, rvec, tvec = cv2.solvePnP(obj_points, image_points, camera_matrix, dist_coeffs)

        if success:
            distancia_z = tvec[2][0] # La distancia en metros desde la cámara al papel
            texto = f"Rack: {ubicacion} | Dist: {distancia_z:.2f}m"
            
            # Dibuja los Ejes 3D saliendo del papel (X=Rojo, Y=Verde, Z=Azul)
            try:
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
            except AttributeError:
                cv2.aruco.drawAxis(frame, camera_matrix, dist_coeffs, rvec, tvec, MARKER_SIZE)
        else:
            texto = f"Rack: {ubicacion}"

        # Dibujar el texto en pantalla
        c = corners[i].reshape((-1, 2))
        x, y = int(c[0][0]), int(c[0][1])
        cv2.putText(frame, texto, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

  cv2.imshow("AeroStock - Navegacion por Racks (AprilTags)", frame)

  if cv2.waitKey(1) & 0xFF == ord("q"):
    break

cap.release()
cv2.destroyAllWindows()