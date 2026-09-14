import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

# Crear carpeta si no existe
carpeta_salida = 'qrs_trazabilidad'
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Leer las etiquetas de Teachable Machine
try:
    with open('labels.txt', 'r', encoding='utf-8') as f:
        labels = f.readlines()
except FileNotFoundError:
    print("Error: No se encontró el archivo labels.txt")
    exit()

print("Generando QRs con IDs dinámicos de Trazabilidad...")

index = 1
for line in labels:
    if not line.strip(): 
        continue
    
    # Limpiar nombre (Teachable machine pone "0 Nombre", queremos solo "Nombre")
    parts = line.strip().split(" ", 1)
    name = parts[1] if len(parts) > 1 else parts[0]
    
    # El espacio vacío no lleva QR
    if "VACIO" in name.upper(): 
        continue 
    
    qr_id = f"NSL-{index:03d}"
    titulo = f"{qr_id} - {name}"
    
    # 1. Crear el código QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white').convert('RGB')
    
    # 2. Lienzo para escribir el título
    ancho_qr, alto_qr = qr_img.size
    alto_texto = 40
    imagen_final = Image.new('RGB', (ancho_qr, alto_qr + alto_texto), 'white')
    imagen_final.paste(qr_img, (0, 0))
    
    # 3. Escribir el título corto solicitado
    draw = ImageDraw.Draw(imagen_final)
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    draw.text((10, alto_qr + 5), titulo, fill="black", font=font)
    
    # 4. Guardar la imagen
    safe_name = name.replace(" ", "_").replace("/", "-")
    nombre_archivo = f"QR_{qr_id}_{safe_name}.png"
    ruta = os.path.join(carpeta_salida, nombre_archivo)
    imagen_final.save(ruta)
    
    print(f"Creado: {nombre_archivo}")
    index += 1

# Generar el QR especial para la desalineación
qr_id_error = "NSL-999"
titulo_error = f"{qr_id_error} - ERROR HUMANO"

qr_error = qrcode.QRCode(version=1, box_size=10, border=4)
qr_error.add_data(qr_id_error)
qr_error.make(fit=True)
qr_img_error = qr_error.make_image(fill='black', back_color='white').convert('RGB')

ancho_qr, alto_qr = qr_img_error.size
imagen_final_error = Image.new('RGB', (ancho_qr, alto_qr + 40), 'white')
imagen_final_error.paste(qr_img_error, (0, 0))
draw_error = ImageDraw.Draw(imagen_final_error)
draw_error.text((10, alto_qr + 5), titulo_error, fill="black", font=font)

ruta_error = os.path.join(carpeta_salida, f"QR_{qr_id_error}_ERROR.png")
imagen_final_error.save(ruta_error)
print(f"Creado: QR_{qr_id_error}_ERROR.png")

print(f"\n¡Proceso completado! Todos los QRs están en la carpeta '{carpeta_salida}'.")
