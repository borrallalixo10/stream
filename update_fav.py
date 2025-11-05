import requests
import re

SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"
OUTPUT_FILE = "favoritos.m3u"

# Orden deseado (usa nombres tal como aparecen en la lista oficial)
PREFERRED_ORDER = [
    "La 1",
    "La 2",
    "TVG",
    "Antena 3",
    "Telecinco",
    "La Sexta",
    "Cuatro",
    "24H",
    "nova",
    "Neox",
    "Divinity",
    "Veo",
    "Trece",
    "Real Madrid TV",
    "A3Series"
]

def parse_m3u_with_metadata(content):
    """Parsea el M3U y extrae (nombre, extinf_line, url) manteniendo metadatos completos."""
    lines = content.strip().splitlines()
    channels = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                extinf = line
                # Extraer nombre: todo después de la última coma
                name = extinf.split(',', 1)[1] if ',' in extinf else ''
                channels.append((name, extinf, url))
                i += 2
            else:
                i += 1
        else:
            i += 1
    return channels

def normalize_name(name):
    """Normaliza el nombre para comparación flexible (opcional: ajusta según necesidad)"""
    return name.strip().lower()

def main():
    print("Descargando lista oficial de España...")
    resp = requests.get(SOURCE_URL)
    resp.raise_for_status()
    resp.encoding = 'utf-8'
    full_content = resp.text

    # Parsear todos los canales
    all_channels = parse_m3u_with_metadata(full_content)
    print(f"Total de canales encontrados: {len(all_channels)}")

    # Crear un mapa de nombres normalizados -> lista de coincidencias (por si hay duplicados)
    name_map = {}
    for name, extinf, url in all_channels:
        norm = normalize_name(name)
        if norm not in name_map:
            name_map[norm] = []
        name_map[norm].append((name, extinf, url))

    # Paso 1: Buscar los canales prioritarios
    prioritized = []
    used_urls = set()

    for target in PREFERRED_ORDER:
        norm_target = normalize_name(target)
        found = False
        # Buscar coincidencia exacta o parcial
        for norm_name in name_map:
            if norm_target in norm_name or norm_name in norm_target:
                for entry in name_map[norm_name]:
                    _, extinf, url = entry
                    if url not in used_urls:
                        prioritized.append((extinf, url))
                        used_urls.add(url)
                        found = True
                        break
                if found:
                    break
        if not found:
            print(f"Advertencia: no se encontró '{target}' en la lista.")

    # Paso 2: Añadir el resto de los canales (en orden original, sin repetidos)
    rest = []
    for name, extinf, url in all_channels:
        if url not in used_urls:
            rest.append((extinf, url))
            used_urls.add(url)

    # Combinar: priorizados + resto
    final_channels = prioritized + rest

    # Guardar archivo
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for extinf, url in final_channels:
            f.write(extinf + "\n")
            f.write(url + "\n")

    print(f"Guardado {OUTPUT_FILE} con {len(final_channels)} canales.")

if __name__ == "__main__":
    main()
