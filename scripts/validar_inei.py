"""Compara nuestras estimaciones con las cifras publicadas por el INEI.

Fuente: capítulo 9 (Nutrición) de los informes departamentales de la ENDES 2025
(y 2024), https://proyectos.inei.gob.pe/endes/AAAA/departamentales/EndesNN/pdf/Cap09.pdf
Cada capítulo dice "...afectó a NN,N% de niños de 6 a 35 meses..." una vez con
RM 363-2022-MINSA y otra con la nueva directriz OMS 2024 / RM 251-2024-MINSA.

Uso:
    python scripts/validar_inei.py         # ENDES 2025
    python scripts/validar_inei.py 2024    # ENDES 2024
"""

import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

import numpy as np
import pandas as pd

from procesar import DEPARTAMENTOS, ORIGINALES, PROCESADOS

URL = "https://proyectos.inei.gob.pe/endes/{}/departamentales/Endes{}/pdf/Cap09.pdf"
ANIO = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
CARPETA = ORIGINALES / "inei_capitulos_departamentales" / str(ANIO)
# Errores de texto en los capítulos publicados (revisados a mano)
NOTAS = {
    (2025, "15"): "El archivo de Lima Metropolitana contiene el texto de Callao",
    (2024, "14"): "La sección OMS 2024 repite el texto de la sección RM 363-2022",
    (2024, "18"): "Solo publica 6-59 meses",
    (2025, "18"): "Solo publica 6-59 meses",
}
PATRON = re.compile(r"afect[óo]\s+(?:a|al)\s+(\d+,\d)\s*%?\s+de\s+(?:los\s+)?niños\s+de\s+6\s+a\s+35", re.S)


def texto(codigo):
    pdf = CARPETA / f"Endes{codigo}_Cap09.pdf"
    if not pdf.exists():
        parcial = pdf.with_suffix(".part")
        for intento in range(3):
            try:
                urllib.request.urlretrieve(URL.format(ANIO, codigo), parcial)
                parcial.rename(pdf)
                break
            except urllib.error.HTTPError:
                raise
            except OSError:
                if intento == 2:
                    raise
                time.sleep(5)
    return subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                          capture_output=True, text=True, encoding="utf-8").stdout


def cifras(t):
    # La primera mención es RM 363-2022 y la segunda OMS 2024 (orden de las secciones)
    encabezado = t.splitlines()[0].strip()
    hallados = [float(x.replace(",", ".")) for x in PATRON.findall(t)]
    if len(hallados) != 2:
        return encabezado + f" [revisar: {len(hallados)} menciones]", None, None
    return encabezado, hallados[0], hallados[1]


if __name__ == "__main__":
    CARPETA.mkdir(parents=True, exist_ok=True)
    # Callao (07) no tiene capítulo propio con ese código; el INEI publica 15 (Lima
    # Metropolitana), 15_1 (Departamento de Lima) y 15_2 (Callao)
    codigos = [f"{i:02d}" for i in range(1, 26) if i not in (7, 15)] + ["15", "15_1", "15_2"]
    filas = []
    for c in codigos:
        try:
            enc, a, b = cifras(texto(c))
        except Exception as e:  # noqa: BLE001
            enc, a, b = f"ERROR {e}", None, None
        filas.append({"codigo_inei": c, "encabezado": enc, "inei_363": a, "inei_oms": b})
    v = pd.DataFrame(filas)
    # El encabezado del PDF dice "Departamento de X"; el código 15 es Lima Metropolitana,
    # 15_1 corresponde a Lima Provincias y 15_2 a Callao
    nombres = dict(DEPARTAMENTOS)
    v["ambito"] = v.codigo_inei.map(lambda c: {"15": "Lima Metropolitana", "15_1": "Lima Provincias", "15_2": "Callao"}.get(c, nombres.get(int(c))))
    v["nota"] = v.codigo_inei.map(lambda c: NOTAS.get((ANIO, c), ""))
    propio = pd.read_csv(PROCESADOS / f"anemia_departamento_{ANIO}.csv")[["ambito", "anemia_363", "anemia_oms"]]
    v = v.merge(propio, on="ambito", how="left")
    # Redondeo a 1 decimal con la regla de la mitad hacia arriba, como en los informes
    redondear = lambda x: np.floor(x * 10 + 0.5) / 10
    v["coincide_363"] = np.where(v.inei_363.notna(), redondear(v.anemia_363) == v.inei_363, np.nan)
    v["coincide_oms"] = np.where(v.inei_oms.notna(), redondear(v.anemia_oms) == v.inei_oms, np.nan)
    v.to_csv(PROCESADOS / f"validacion_inei_cap09_{ANIO}.csv", index=False, encoding="utf-8")
    print(v[["codigo_inei", "ambito", "inei_363", "anemia_363", "inei_oms", "anemia_oms",
             "coincide_363", "coincide_oms", "nota"]].round(1).to_string(index=False))
