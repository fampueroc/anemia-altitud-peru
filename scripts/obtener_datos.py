"""Descarga los microdatos de la ENDES 2025 (y 2024) desde el portal del INEI.

Fuente: https://proyectos.inei.gob.pe/microdatos/ (Consulta por encuesta ->
ENDES -> año -> Único). Códigos de encuesta: 1038 (2025) y 968 (2024).

Módulos:
    1629  Características del hogar  (RECH0: altitud, departamento, área; RECH1)
    1638  Peso y talla - Anemia      (RECH6: hemoglobina de niñas y niños)

Uso:
    python scripts/obtener_datos.py         # ENDES 2025
    python scripts/obtener_datos.py 2024    # ENDES 2024, para la réplica
"""

import sys
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://proyectos.inei.gob.pe/iinei/srienaho/descarga/SPSS"
ENCUESTAS = {2025: 1038, 2024: 968}
MODULOS = {1629: "caracteristicas_hogar", 1638: "peso_talla_anemia"}
ANIO = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
ENCUESTA = ENCUESTAS[ANIO]
ORIGINALES = Path(__file__).resolve().parent.parent / "datos" / "originales"
DESTINO = ORIGINALES if ANIO == 2025 else ORIGINALES / f"endes_{ANIO}"


def descargar(modulo: int) -> Path:
    url = f"{BASE}/{ENCUESTA}-Modulo{modulo}.zip"
    zip_path = DESTINO / f"{ENCUESTA}-Modulo{modulo}.zip"
    if not zip_path.exists():
        print(f"Bajando {url}")
        urllib.request.urlretrieve(url, zip_path)
    carpeta = DESTINO / f"modulo_{modulo}_{MODULOS[modulo]}" if ANIO == 2025 else DESTINO
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(carpeta)
    return carpeta


if __name__ == "__main__":
    DESTINO.mkdir(parents=True, exist_ok=True)
    for m in MODULOS:
        carpeta = descargar(m)
        for f in sorted(carpeta.rglob("*")):
            if f.is_file():
                print(f"  {f.relative_to(DESTINO)}  ({f.stat().st_size / 1e6:.1f} MB)")
