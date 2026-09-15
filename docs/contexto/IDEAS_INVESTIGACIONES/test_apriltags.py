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
    # Dibujar los bordes automáticos sobre el frame
    cv2.aruco.drawDetectedMarkers(frame, corners, ids)

    for i in range(len(ids)):
        # Extraer el ID de forma segura sin importar la dimensión del array
        tag_id = int(np.ravel(ids[i])[0])
        ubicacion = MAPA_RACKS.get(tag_id, f"Tag ID {tag_id} no registrado")

        # Obtener la esquina superior izquierda
        c = corners[i].reshape((-1, 2))
        x, y = int(c[0][0]), int(c[0][1])

        texto = f"Rack: {ubicacion}"
        cv2.putText(
            frame,
            texto,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
        )

  cv2.imshow("AeroStock - Navegacion por Racks (AprilTags)", frame)

  if cv2.waitKey(1) & 0xFF == ord("q"):
    break

cap.release()
cv2.destroyAllWindows()