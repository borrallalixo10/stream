import requests
import re
import os

# Archivos
TEMPLATE = "corto.m3u"
OUTPUT = "favoritos.m3u"
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

def extract_channel_names(filepath):
    names = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#EXTINF'):
                # Extraer el nombre después de la última coma
                if ',' in line:
                    name = line.split(',', 1)[1].strip()
                    names.add(name)
    return names

def parse_m3u(content):
    lines = content.strip().splitlines()
    channels = []
    i = 0
    while i < len(lines):
        if lines[i].startswith('#EXTINF'):
            if i + 1 < len(lines):
                extinf = lines[i]
                url = lines[i + 1]
                name = extinf.split(',', 1)[1] if ',' in extinf else ''
                channels.append((name.strip(), extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def main():
    # Cargar nombres deseados
    desired_names = extract_channel_names(TEMPLATE)
    print(f"Canales deseados: {len(desired_names)}")

    # Descargar lista completa
    print("Descargando es.m3u...")
    resp = requests.get(SOURCE_URL)
    resp.raise_for_status()
    full_list = resp.text

    # Parsear
    all_channels = parse_m3u(full_list)

    # Filtrar
    matched = []
    for name, extinf, url in all_channels:
        if name in desired_names:
            matched.append(extinf)
            matched.append(url)

    # Guardar
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        f.write("\n".join(matched))
        f.write("\n")

    print(f"Guardado {OUTPUT} con {len(matched)//2} canales.")

if __name__ == "__main__":
    main()
