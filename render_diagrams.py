import base64
import urllib.request
import os
import json

def generate_mermaid_image(txt_path, output_png_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        mermaid_code = f.read()
    
    # Codificar solo el texto en base64 para la API moderna de mermaid.ink
    b64_str = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
    
    url = f"https://mermaid.ink/img/{b64_str}?type=png"
    
    print(f"Downloading {output_png_path}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(output_png_path, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Guardado: {output_png_path}")
    except Exception as e:
        print(f"Error descargando {txt_path}: {e}")

diagrams_dir = r"C:\GitHub\aerostock-mvp\docs\diagramas"
images_dir = r"C:\GitHub\aerostock-mvp\docs\images"

# List of diagrams to process
diagrams = [
    "diagrama_1_arquitectura.txt",
    "diagrama_2_doble_verificacion.txt",
    "diagrama_3_fefo_termico.txt"
]

for diag in diagrams:
    txt_path = os.path.join(diagrams_dir, diag)
    png_path = os.path.join(images_dir, diag.replace(".txt", ".png"))
    if os.path.exists(txt_path):
        generate_mermaid_image(txt_path, png_path)
    else:
        print(f"No se encontró {txt_path}")
