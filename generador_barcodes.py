import barcode
from barcode.writer import ImageWriter
import os
from PIL import Image, ImageDraw, ImageFont

# Crear carpeta si no existe
carpeta_salida = 'barcodes_trazabilidad'
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Leer las etiquetas de Teachable Machine
try:
    with open('labels.txt', 'r', encoding='utf-8') as f:
        labels = f.readlines()
except FileNotFoundError:
    print("Error: No se encontró el archivo labels.txt")
    exit()

print("Generando Códigos de Barras (EAN-128 / Code128) con IDs dinámicos de Trazabilidad...")

index = 1
for line in labels:
    if not line.strip(): 
        continue
    
    # Limpiar nombre (Teachable machine pone "0 Nombre", queremos solo "Nombre")
    parts = line.strip().split(" ", 1)
    name = parts[1] if len(parts) > 1 else parts[0]
    
    # El espacio vacío no lleva Código de Barras
    if "VACIO" in name.upper(): 
        continue 
    
    # Usamos Code128 para soportar letras y números (simulando EAN-128 o SSCC/LPN)
    lpn_id = f"NSL1000{index:03d}"
    titulo = f"{lpn_id} - {name}"
    
    # 1. Crear el código de barras
    code128 = barcode.get('code128', lpn_id, writer=ImageWriter())
    # Guardar en memoria para manipular con PIL
    safe_name = name.replace(" ", "_").replace("/", "-")
    nombre_archivo_base = f"LPN_{lpn_id}_{safe_name}"
    ruta_base = os.path.join(carpeta_salida, nombre_archivo_base)
    
    # Genera ruta_base.png
    filename = code128.save(ruta_base, options={"write_text": False})
    
    # 2. Lienzo para escribir el título
    img_barcode = Image.open(filename).convert('RGB')
    ancho_bc, alto_bc = img_barcode.size
    alto_texto = 40
    imagen_final = Image.new('RGB', (ancho_bc, alto_bc + alto_texto), 'white')
    imagen_final.paste(img_barcode, (0, 0))
    
    # 3. Escribir el título corto solicitado
    draw = ImageDraw.Draw(imagen_final)
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    draw.text((10, alto_bc + 5), titulo, fill="black", font=font)
    
    # 4. Sobrescribir la imagen final
    imagen_final.save(filename)
    
    print(f"Creado: {filename}")
    index += 1

# Generar el Código de Barras especial para la desalineación
lpn_id_error = "NSL999999"
titulo_error = f"{lpn_id_error} - ERROR HUMANO"

code128_error = barcode.get('code128', lpn_id_error, writer=ImageWriter())
ruta_base_error = os.path.join(carpeta_salida, f"LPN_{lpn_id_error}_ERROR")
filename_error = code128_error.save(ruta_base_error, options={"write_text": False})

img_barcode_error = Image.open(filename_error).convert('RGB')
ancho_bc, alto_bc = img_barcode_error.size
imagen_final_error = Image.new('RGB', (ancho_bc, alto_bc + 40), 'white')
imagen_final_error.paste(img_barcode_error, (0, 0))
draw_error = ImageDraw.Draw(imagen_final_error)
draw_error.text((10, alto_bc + 5), titulo_error, fill="black", font=font)
imagen_final_error.save(filename_error)

print(f"Creado: {filename_error}")

print(f"\n¡Proceso completado! Todos los Códigos de Barras están en la carpeta '{carpeta_salida}'.")
