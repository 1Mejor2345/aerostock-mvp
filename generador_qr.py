import qrcode
import os

# Crear carpeta si no existe
carpeta_salida = 'qrs'
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Leer etiquetas del modelo de Teachable Machine
try:
    with open('labels.txt', 'r', encoding='utf-8') as f:
        labels = f.readlines()
except FileNotFoundError:
    print("Error: No se encontró el archivo labels.txt")
    exit()

print("Generando QRs...")

# Generar un QR para cada etiqueta
for line in labels:
    if not line.strip(): 
        continue
    
    # Limpiar nombre (Teachable machine pone "0 Nombre", queremos solo "Nombre")
    parts = line.strip().split(" ", 1)
    name = parts[1] if len(parts) > 1 else parts[0]
    
    # No necesitamos un QR para el espacio vacío
    if "VACIO" in name.upper(): 
        continue 
    
    # Crear la imagen del QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(name)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # Guardar imagen con nombre limpio
    safe_name = name.replace(" ", "_").replace("/", "-")
    img.save(os.path.join(carpeta_salida, f"QR_{safe_name}.png"))
    print(f"Creado: QR_{safe_name}.png")

# Crear un QR especial con error para demostrar el problema de Filippo (Misalignment)
qr_error = qrcode.QRCode(version=1, box_size=10, border=4)
qr_error.add_data("ERROR-HUMANO-DESALINEACION")
qr_error.make(fit=True)
img_error = qr_error.make_image(fill='black', back_color='white')
img_error.save(os.path.join(carpeta_salida, "QR_ERROR_DEMO.png"))
print("Creado: QR_ERROR_DEMO.png (Usalo para engañar a la camara en la demo)")

print(f"\n¡Proceso completado! Todos los QRs están en la carpeta '{carpeta_salida}'.")
