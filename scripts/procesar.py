"""Anemia en niñas y niños de 6 a 35 meses, ENDES 2025, con dos criterios.

Pasos:
1. Une RECH6 (hemoglobina) con RECH1 (residencia de facto) y RECH0
   (ponderador, estrato, conglomerado, departamento, altitud).
2. Recalcula la hemoglobina ajustada con las dos fórmulas y verifica que
   coincide con HC56 y HC56A del INEI.
3. Estima la prevalencia nacional y por departamento con su error estándar
   (linealización de Taylor, diseño estratificado por conglomerados).

Criterios:
- RM 363-2022-MINSA: ajuste CDC (1989) desde 1000 m; anemia si Hb < 11,0 g/dL.
- OMS 2024 / RM 251-2024-MINSA: ajuste (g/L) = 0,0056384·m + 0,0000003·m²
  desde 500 m; anemia si Hb < 10,5 g/dL (6–23 meses) o < 11,0 g/dL (24–59).

Uso:
    python scripts/procesar.py          # ENDES 2025
    python scripts/procesar.py 2024     # réplica con la ENDES 2024
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

RAIZ = Path(__file__).resolve().parent.parent
ORIGINALES = RAIZ / "datos" / "originales"
PROCESADOS = RAIZ / "datos" / "procesados"
Z = 1.96

# Ámbitos como los publica el INEI: Lima se divide en Lima Metropolitana
# (provincia de Lima, ubigeo 1501) y Lima Provincias (las otras 9 provincias)
DEPARTAMENTOS = {
    1: "Amazonas", 2: "Áncash", 3: "Apurímac", 4: "Arequipa", 5: "Ayacucho",
    6: "Cajamarca", 7: "Callao", 8: "Cusco", 9: "Huancavelica", 10: "Huánuco",
    11: "Ica", 12: "Junín", 13: "La Libertad", 14: "Lambayeque", 15: "Lima Provincias",
    16: "Loreto", 17: "Madre de Dios", 18: "Moquegua", 19: "Pasco", 20: "Piura",
    21: "Puno", 22: "San Martín", 23: "Tacna", 24: "Tumbes", 25: "Ucayali",
    26: "Lima Metropolitana",
}


def leer(nombre, columnas=None):
    ruta = next(ORIGINALES.rglob(nombre))
    df, _ = pyreadstat.read_sav(ruta, usecols=columnas)
    return df.rename(columns=str.upper)


def cargar(anio=2025):
    r6 = leer(f"RECH6_{anio}.sav")
    r1 = leer(f"RECH1_{anio}.sav", ["HHID", "HVIDX", "HV103"])
    r0 = leer(f"RECH0_{anio}.sav", ["HHID", "HV001", "HV005", "HV022", "HV024", "HV025", "HV040", "UBIGEO"])
    r6["HC0"] = pd.to_numeric(r6["HC0"])
    r1["HVIDX"] = pd.to_numeric(r1["HVIDX"])
    d = (r6.merge(r1, left_on=["HHID", "HC0"], right_on=["HHID", "HVIDX"], how="left", validate="1:1")
           .merge(r0, on="HHID", how="left", validate="m:1"))
    d["AMBITO"] = np.where(d.UBIGEO.str[:4] == "1501", 26, d.HV024).astype(int)
    # Población del indicador del INEI: de facto, 6-35 meses, con hemoglobina medida
    return d[(d.HV103 == 1) & d.HC1.between(6, 35) & d.HC53.notna()].copy()


def ajustar(d):
    """Hemoglobina ajustada en décimas de g/dL, truncada como en la ENDES."""
    m, hb = d.HV040, d.HC53
    a = m / 1000 * 3.3
    ajuste_cdc = np.where(m >= 1000, (-0.032 * a + 0.022 * a**2) * 10, 0)
    ajuste_oms = np.where(m >= 500, 0.0056384 * m + 0.0000003 * m**2, 0)
    d["HB_363"] = np.floor(hb - ajuste_cdc)
    d["HB_OMS"] = np.floor(hb - ajuste_oms)
    assert (d.HB_363 == d.HC56).all(), "El ajuste RM 363-2022 no reproduce HC56"
    assert (d.HB_OMS == d.HC56A).all(), "El ajuste OMS 2024 no reproduce HC56A"

    corte_oms = np.where(d.HC1 < 24, 105, 110)
    d["anemia_363"] = (d.HB_363 < 110).astype(float)
    d["anemia_oms"] = (d.HB_OMS < corte_oms).astype(float)
    # Escenarios para separar los dos cambios
    d["solo_altitud"] = (d.HB_OMS < 110).astype(float)
    d["solo_corte"] = (d.HB_363 < corte_oms).astype(float)
    assert (d.anemia_363 == (d.HC57 <= 3)).all()
    assert (d.anemia_oms == (d.HC57A <= 3)).all()
    return d


def proporcion(d, y, dominio):
    """Proporción ponderada en un dominio y su error estándar (Taylor)."""
    w = d.HV005 * dominio
    total = w.sum()
    p = (w * d[y]).sum() / total
    z = w * (d[y] - p) / total
    return p, _error_estandar(d, z)


def diferencia(d, y1, y2, dominio):
    """Diferencia y2 - y1 (mismos niños) y su error estándar."""
    w = d.HV005 * dominio
    total = w.sum()
    p1 = (w * d[y1]).sum() / total
    p2 = (w * d[y2]).sum() / total
    z = w * ((d[y2] - p2) - (d[y1] - p1)) / total
    return p2 - p1, _error_estandar(d, z)


def _error_estandar(d, z):
    psu = pd.DataFrame({"h": d.HV022, "c": d.HV001, "z": z}).groupby(["h", "c"]).z.sum().reset_index()
    var = 0.0
    for _, g in psu.groupby("h"):
        n = len(g)
        if n > 1:
            var += n / (n - 1) * ((g.z - g.z.mean()) ** 2).sum()
    return np.sqrt(var)


def tabla(d):
    filas = []
    dominios = [("Perú", pd.Series(1.0, index=d.index))]
    dominios += [(nombre, (d.AMBITO == cod).astype(float)) for cod, nombre in DEPARTAMENTOS.items()]
    for nombre, dom in dominios:
        fila = {"ambito": nombre, "n": int(dom.sum()),
                "altitud_mediana_m": float(np.median(d.HV040[dom == 1]))}
        for y in ["anemia_363", "anemia_oms", "solo_altitud", "solo_corte"]:
            p, se = proporcion(d, y, dom)
            fila[y] = 100 * p
            fila[f"{y}_li"] = 100 * (p - Z * se)
            fila[f"{y}_ls"] = 100 * (p + Z * se)
        dif, se = diferencia(d, "anemia_363", "anemia_oms", dom)
        fila["cambio_pp"] = 100 * dif
        fila["cambio_li"] = 100 * (dif - Z * se)
        fila["cambio_ls"] = 100 * (dif + Z * se)
        fila["efecto_altitud_pp"] = fila["solo_altitud"] - fila["anemia_363"]
        fila["efecto_corte_pp"] = fila["solo_corte"] - fila["anemia_363"]
        filas.append(fila)
    t = pd.DataFrame(filas)
    deps = t.ambito != "Perú"
    t.loc[deps, "puesto_363"] = t.loc[deps, "anemia_363"].rank(ascending=False).astype(int)
    t.loc[deps, "puesto_oms"] = t.loc[deps, "anemia_oms"].rank(ascending=False).astype(int)
    return t


if __name__ == "__main__":
    anio = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    PROCESADOS.mkdir(parents=True, exist_ok=True)
    d = ajustar(cargar(anio))
    t = tabla(d)
    t.round(4).to_csv(PROCESADOS / f"anemia_departamento_{anio}.csv", index=False, encoding="utf-8")
    cols = ["ambito", "n", "altitud_mediana_m", "anemia_363", "anemia_oms", "cambio_pp",
            "cambio_li", "cambio_ls", "efecto_altitud_pp", "efecto_corte_pp", "puesto_363", "puesto_oms"]
    print(t[cols].round(1).to_string(index=False))
