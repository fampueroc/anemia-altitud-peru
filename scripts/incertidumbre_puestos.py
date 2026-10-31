"""Incertidumbre del puesto de cada departamento con bootstrap de diseño.

Bootstrap con reescalamiento de Rao y Wu (1988): en cada estrato con n_h
conglomerados se sortean n_h - 1 con reemplazo y los pesos se multiplican por
(veces elegido) · n_h / (n_h - 1). Así se respeta el diseño estratificado por
conglomerados de la ENDES.

Referencia: Rao JNK, Wu CFJ (1988). Resampling inference with complex survey
data. Journal of the American Statistical Association 83(401):231-241.

Uso:
    python scripts/incertidumbre_puestos.py         # ENDES 2025
    python scripts/incertidumbre_puestos.py 2024    # réplica con la ENDES 2024
"""

import sys

import numpy as np
import pandas as pd

from procesar import DEPARTAMENTOS, PROCESADOS, ajustar, cargar

REPLICAS = 2000
SEMILLA = 20251101


def bootstrap(d, columnas):
    psu = d.groupby(["HV022", "HV001"]).ngroup().to_numpy()
    estrato_psu = d.groupby(["HV022", "HV001"]).HV022.first().to_numpy()
    dep = d.AMBITO.to_numpy() - 1
    k = len(DEPARTAMENTOS)
    w = d.HV005.to_numpy()
    y = {c: d[c].to_numpy() for c in columnas}
    n_psu = psu.max() + 1
    estratos = [np.flatnonzero(estrato_psu == h) for h in np.unique(estrato_psu)]

    rng = np.random.default_rng(SEMILLA)
    salida = {c: np.empty((REPLICAS, k)) for c in columnas}
    for r in range(REPLICAS):
        mult = np.zeros(n_psu)
        for idx in estratos:
            n = len(idx)
            if n < 2:
                mult[idx] = 1.0
                continue
            elegidos = rng.choice(idx, size=n - 1, replace=True)
            np.add.at(mult, elegidos, n / (n - 1))
        wr = w * mult[psu]
        total = np.bincount(dep, weights=wr, minlength=k)
        for c in columnas:
            salida[c][r] = 100 * np.bincount(dep, weights=wr * y[c], minlength=k) / total
    return salida


def puestos(prev):
    # Puesto 1 = mayor anemia
    return (-prev).argsort(axis=1).argsort(axis=1) + 1


if __name__ == "__main__":
    anio = int(sys.argv[1]) if len(sys.argv) > 1 else 2025
    d = ajustar(cargar(anio))
    b = bootstrap(d, ["anemia_363", "anemia_oms"])
    p363, poms = puestos(b["anemia_363"]), puestos(b["anemia_oms"])
    cambio = p363 - poms  # positivo = sube en el orden (más anemia relativa) con OMS 2024

    t = pd.read_csv(PROCESADOS / f"anemia_departamento_{anio}.csv")
    filas = []
    for i, nombre in enumerate(DEPARTAMENTOS.values()):
        filas.append({
            "ambito": nombre,
            "se_boot_363": b["anemia_363"][:, i].std(ddof=1),
            "se_boot_oms": b["anemia_oms"][:, i].std(ddof=1),
            "puesto_363_li": np.percentile(p363[:, i], 2.5),
            "puesto_363_ls": np.percentile(p363[:, i], 97.5),
            "puesto_oms_li": np.percentile(poms[:, i], 2.5),
            "puesto_oms_ls": np.percentile(poms[:, i], 97.5),
            "cambio_puesto_li": np.percentile(cambio[:, i], 2.5),
            "cambio_puesto_ls": np.percentile(cambio[:, i], 97.5),
            "prob_sube": (cambio[:, i] > 0).mean(),
            "prob_baja": (cambio[:, i] < 0).mean(),
        })
    u = t.merge(pd.DataFrame(filas), on="ambito", how="left")
    u["se_taylor_363"] = (u.anemia_363_ls - u.anemia_363_li) / (2 * 1.96)
    u.round(4).to_csv(PROCESADOS / f"anemia_departamento_{anio}.csv", index=False, encoding="utf-8")

    v = u[u.ambito != "Perú"].copy()
    v["cambio_puesto"] = v.puesto_363 - v.puesto_oms
    cols = ["ambito", "puesto_363", "puesto_363_li", "puesto_363_ls", "puesto_oms", "puesto_oms_li",
            "puesto_oms_ls", "cambio_puesto", "cambio_puesto_li", "cambio_puesto_ls", "prob_sube",
            "prob_baja", "se_taylor_363", "se_boot_363"]
    print(v[cols].sort_values("cambio_puesto", ascending=False).round(2).to_string(index=False))
