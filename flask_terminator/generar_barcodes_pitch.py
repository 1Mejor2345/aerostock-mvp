import os
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

# Crear carpeta de salida
carpeta_salida = r'c:\GitHub\aerostock-mvp\barcodes_trazabilidad\pitch'
if not os.path.exists(carpeta_salida):
    os.makedirs(carpeta_salida)

# Opciones para barras muy gruesas y legibles (EAN-128)
opciones = {
    "write_text": False,
    "module_width": 0.8,
    "module_height": 25.0,
    "quiet_zone": 10.0
}

# Configuración de los 3 pallets
pallets = [
    {"lpn": "N101", "titulo": "PALLET Hot Cocoa Mix", "archivo": "Caja_Rosada_Cocoa"},
    {"lpn": "N102", "titulo": "PALLET Cereales Nestle", "archivo": "Caja_Verde_Cereales"},
    {"lpn": "N05", "titulo": "PALLET Galleta Taco Sal", "archivo": "Caja_Roja_GalletasTaco"} # N05 coincide con tu BD en app.py
]

print("Generando Códigos de Barras para el Pitch...")

for p in pallets:
    # 1. Generar Código de Barras
    code = barcode.get('code128', p['lpn'], writer=ImageWriter())
    ruta_base = os.path.join(carpeta_salida, p['archivo'])
    filename = code.save(ruta_base, options=opciones)
    
    # 2. Lienzo para escribir el texto
    img_barcode = Image.open(filename).convert('RGB')
    ancho_bc, alto_bc = img_barcode.size
    alto_texto = 60
    imagen_final = Image.new('RGB', (ancho_bc, alto_bc + alto_texto), 'white')
    imagen_final.paste(img_barcode, (0, 0))
    
    # 3. Escribir el título
    draw = ImageDraw.Draw(imagen_final)
    try:
        # Intentar cargar una fuente más grande (Arial en Windows)
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()
        
    # Centrar texto aproximadamente
    text_width = draw.textlength(p['titulo'], font=font) if hasattr(draw, 'textlength') else 150
    x_pos = (ancho_bc - text_width) / 2
    
    draw.text((x_pos, alto_bc + 10), p['titulo'], fill="black", font=font)
    
    # 4. Guardar imagen final
    imagen_final.save(filename)
    print(f"Creado: {filename}")

print("¡Listo!")
