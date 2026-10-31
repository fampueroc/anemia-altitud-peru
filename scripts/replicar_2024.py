"""Réplica de los tres hallazgos con la ENDES 2024.

La ENDES rota un tercio de los conglomerados por año (ficha técnica 2025, sección
IV): 2 de cada 3 conglomerados de 2025 ya estaban en 2024, con viviendas
distintas. Por eso 2024 no es una muestra independiente de 2025. Como prueba más
limpia, el patrón por altitud también se estima solo con los conglomerados de
2024 que no están en 2025 (un grupo de rotación completo).

Compara, para 2024 y 2025:
1. En qué ámbitos el cambio de criterio no es significativo.
2. El cambio por franja de altitud.
3. Qué cambios de puesto son robustos (el intervalo bootstrap excluye el 0).

Requiere haber corrido procesar.py e incertidumbre_puestos.py para los dos años.

Uso:
    python scripts/replicar_2024.py
"""

import pandas as pd

from exportar_web import por_altitud
from procesar import PROCESADOS, ajustar, cargar, leer

ANIOS = (2024, 2025)


def departamentos(anio):
    t = pd.read_csv(PROCESADOS / f"anemia_departamento_{anio}.csv")
    t["significativo"] = (t.cambio_ls < 0) | (t.cambio_li > 0)
    t["cambio_puesto"] = t.puesto_363 - t.puesto_oms
    t["puesto_robusto"] = (t.cambio_puesto_li > 0) | (t.cambio_puesto_ls < 0)
    cols = ["ambito", "anemia_363", "anemia_oms", "cambio_pp", "cambio_li", "cambio_ls", "significativo",
            "puesto_363", "puesto_oms", "cambio_puesto", "cambio_puesto_li", "cambio_puesto_ls", "puesto_robusto"]
    return t[cols].add_suffix(f"_{anio}").rename(columns={f"ambito_{anio}": "ambito"})


def conglomerados(anio):
    return set(pd.to_numeric(leer(f"RECH0_{anio}.sav", ["HV001"]).HV001).astype(int))


def altitud(anio, muestra="completa"):
    d = ajustar(cargar(anio))
    if muestra == "sin_panel":
        d = d[~pd.to_numeric(d.HV001).astype(int).isin(conglomerados(2025))]
    filas = []
    for f in por_altitud(d):
        fila = {"anio": anio, "muestra": muestra, "desde": f["desde"], "hasta": f["hasta"], "n": f["n"]}
        for k in ["anemia_363", "anemia_oms", "cambio"]:
            fila[k], fila[f"{k}_li"], fila[f"{k}_ls"] = f[k]
        filas.append(fila)
    return pd.DataFrame(filas)


if __name__ == "__main__":
    t = departamentos(2024).merge(departamentos(2025), on="ambito", validate="1:1")
    t.round(4).to_csv(PROCESADOS / "replica_departamento_2024_2025.csv", index=False, encoding="utf-8")
    panel = conglomerados(2024) & conglomerados(2025)
    print(f"Conglomerados en ambos años: {len(panel)} de {len(conglomerados(2025))}")
    a = pd.concat([altitud(x) for x in ANIOS] + [altitud(2024, "sin_panel")])
    a.round(4).to_csv(PROCESADOS / "replica_altitud_2024_2025.csv", index=False, encoding="utf-8")

    deps = t[t.ambito != "Perú"]
    print(deps[["ambito", "cambio_pp_2024", "significativo_2024", "cambio_pp_2025", "significativo_2025"]]
          .round(1).to_string(index=False))
    for x in ANIOS:
        print(f"Sin cambio significativo {x}: {', '.join(deps[~deps[f'significativo_{x}']].ambito)}")
    print()
    a["serie"] = a.anio.astype(str) + a.muestra.map({"completa": "", "sin_panel": " sin panel"})
    print(a.pivot(index="desde", columns="serie", values=["n", "cambio", "cambio_li", "cambio_ls"]).round(1).to_string())
    print()
    for x in ANIOS:
        r = deps[deps[f"puesto_robusto_{x}"]]
        print(f"Puesto robusto {x}: " + ", ".join(
            f"{n} ({p1:.0f}->{p2:.0f})" for n, p1, p2 in zip(r.ambito, r[f"puesto_363_{x}"], r[f"puesto_oms_{x}"])))
    ambos = deps[deps.puesto_robusto_2024 & deps.puesto_robusto_2025]
    print("Robusto en los dos años:", ", ".join(ambos.ambito))
