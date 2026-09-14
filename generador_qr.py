import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

# Crear carpeta si no existe
carpeta_salida = 'qrs_trazabilidad'
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Estos son los datos de prueba que concuerdan exactamente con la DB SQLite en app.py
# Formato: (ID_QR, Titulo_Para_Imprimir, Instruccion)
datos_prueba = [
    ("NSL-001", "CAJA GALAK", "Pegar en caja Galak"),
    ("NSL-002", "CAJA MAGGI", "Pegar en caja Maggi"),
    ("NSL-003", "LECHE VAQUITA", "VENCIDO - Pegar en leche"),
    ("NSL-004", "CAJA RICA", "Pegar en caja Rica"),
    ("NSL-999", "ERROR HUMANO", "Pegar en empaque incorrecto") # Para probar la desalineación
]

print("Generando QRs con IDs de Trazabilidad...")

for qr_id, titulo, instruccion in datos_prueba:
    # 1. Crear el código QR (solo contiene el ID para simular un sistema real)
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_id)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white').convert('RGB')
    
    # 2. Preparar un lienzo más grande para escribir texto debajo del QR
    ancho_qr, alto_qr = qr_img.size
    alto_texto = 80
    imagen_final = Image.new('RGB', (ancho_qr, alto_qr + alto_texto), 'white')
    imagen_final.paste(qr_img, (0, 0))
    
    # 3. Dibujar el texto
    draw = ImageDraw.Draw(imagen_final)
    # Intentar cargar una fuente por defecto
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    # Escribir el ID y el título
    texto_principal = f"ID: {qr_id} | {titulo}"
    texto_instruccion = f"Uso: {instruccion}"
    
    # Posiciones simples
    draw.text((10, alto_qr + 10), texto_principal, fill="black", font=font)
    draw.text((10, alto_qr + 30), texto_instruccion, fill="blue", font=font)
    
    # 4. Guardar la imagen
    nombre_archivo = f"QR_{qr_id}.png"
    ruta = os.path.join(carpeta_salida, nombre_archivo)
    imagen_final.save(ruta)
    
    print(f"Creado: {nombre_archivo} -> {texto_principal}")

print(f"\n¡Proceso completado! Los nuevos QRs están en la carpeta '{carpeta_salida}'.")
