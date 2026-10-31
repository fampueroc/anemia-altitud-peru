"""Exporta los datos del dashboard a web/data/datos.js.

Se usa un .js (no .json) para que la página también abra con doble clic, sin
servidor. Requiere haber corrido antes procesar.py, incertidumbre_puestos.py
(para 2025 y 2024), replicar_2024.py y preparar_mapa.py.

Uso:
    python scripts/exportar_web.py
"""

import json

import numpy as np
import pandas as pd

from procesar import PROCESADOS, RAIZ, Z, ajustar, cargar, diferencia, proporcion

DESTINO = RAIZ / "web" / "data" / "datos.js"

# Franjas de 500 m de la Tabla 4 de la guía OMS 2024; desde 4000 m se agrupan
FRANJAS = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 2500),
           (2500, 3000), (3000, 3500), (3500, 4000), (4000, 99999)]


def por_altitud(d):
    filas = []
    for lo, hi in FRANJAS:
        dom = d.HV040.between(lo, hi - 1).astype(float)
        fila = {"desde": lo, "hasta": hi if hi < 99999 else None, "n": int(dom.sum())}
        for y in ["anemia_363", "anemia_oms", "solo_altitud", "solo_corte"]:
            p, se = proporcion(d, y, dom)
            fila[y] = [round(100 * p, 2), round(100 * (p - Z * se), 2), round(100 * (p + Z * se), 2)]
        dif, se = diferencia(d, "anemia_363", "anemia_oms", dom)
        fila["cambio"] = [round(100 * dif, 2), round(100 * (dif - Z * se), 2), round(100 * (dif + Z * se), 2)]
        filas.append(fila)
    return filas


if __name__ == "__main__":
    d = ajustar(cargar())
    t = pd.read_csv(PROCESADOS / "anemia_departamento_2025.csv")
    t["cambio_significativo"] = (t.cambio_ls < 0) | (t.cambio_li > 0)
    t["puesto_robusto"] = (t.cambio_puesto_li > 0) | (t.cambio_puesto_ls < 0)
    # Réplica con la ENDES 2024 (replicar_2024.py)
    r = pd.read_csv(PROCESADOS / "replica_departamento_2024_2025.csv")
    r = r[["ambito", "cambio_pp_2024", "cambio_li_2024", "cambio_ls_2024", "significativo_2024",
           "puesto_363_2024", "puesto_oms_2024", "puesto_robusto_2024"]]
    t = t.merge(r, on="ambito", how="left", validate="1:1")
    t["sin_cambio_ambos"] = ~t.cambio_significativo & ~t.significativo_2024.astype(bool)
    t["puesto_robusto_ambos"] = t.puesto_robusto & t.puesto_robusto_2024.fillna(False).astype(bool)
    ra = pd.read_csv(PROCESADOS / "replica_altitud_2024_2025.csv")
    replica_altitud = [{"anio": int(f.anio), "muestra": f.muestra, "desde": int(f.desde),
                        "hasta": None if pd.isna(f.hasta) else int(f.hasta), "n": int(f.n),
                        "cambio": [f.cambio, f.cambio_li, f.cambio_ls]} for f in ra.itertuples()]
    ambitos =json.loads(t.replace({np.nan: None}).to_json(orient="records", force_ascii=False))
    geo = json.loads((RAIZ / "web" / "data" / "ambitos.geojson").read_text(encoding="utf-8"))
    datos = {
        "ambitos": ambitos,
        "altitud": por_altitud(d),
        "replica_altitud": replica_altitud,
        "geo": geo,
        "fuente": "INEI, ENDES 2025 (microdatos). Cálculo propio validado contra cifras publicadas.",
    }
    filas_alt = []
    for f in datos["altitud"]:
        fila = {"desde": f["desde"], "hasta": f["hasta"], "n": f["n"]}
        for k in ["anemia_363", "anemia_oms", "solo_altitud", "solo_corte", "cambio"]:
            fila[k], fila[f"{k}_li"], fila[f"{k}_ls"] = f[k]
        filas_alt.append(fila)
    pd.DataFrame(filas_alt).to_csv(PROCESADOS / "anemia_altitud_2025.csv", index=False, encoding="utf-8")
    DESTINO.write_text("window.DATOS = " + json.dumps(datos, ensure_ascii=False) + ";\n", encoding="utf-8")
    deps = t[t.ambito != "Perú"]
    print(f"Ámbitos: {len(deps)} | sin cambio significativo: {(~deps.cambio_significativo).sum()} "
          f"({', '.join(deps[~deps.cambio_significativo].ambito)})")
    print(f"Puesto robusto: {', '.join(deps[deps.puesto_robusto].ambito)}")
    print(f"Sin cambio significativo en 2024 ni 2025: {', '.join(deps[deps.sin_cambio_ambos].ambito)}")
    print(f"Puesto robusto en 2024 y 2025: {', '.join(deps[deps.puesto_robusto_ambos].ambito)}")
    for f in datos["altitud"]:
        print(f["desde"], f["n"], f["anemia_363"][0], f["anemia_oms"][0], f["cambio"])
    print(f"{DESTINO.stat().st_size / 1e3:.0f} KB")
