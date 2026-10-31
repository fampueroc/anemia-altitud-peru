"""Convierte guion.json en un texto de corrido para revisarlo (guion_para_revisar.txt).

    python guion_legible.py
"""
import json
from pathlib import Path

AQUI = Path(__file__).parent
g = json.loads((AQUI / "guion.json").read_text(encoding="utf-8"))
palabras = sum(len(e["frase"].split()) for e in g["escenas"])

lineas = [f"GUION DEL REEL: {g['titulo'].upper()}",
          f"{len(g['escenas'])} escenas · {palabras} palabras · unos {palabras / 2.4:.0f} s de narración + 4,5 s de créditos",
          "", "=" * 60, "TEXTO COMPLETO (lo que dice la voz)", "=" * 60, ""]
lineas += [e["frase"] for e in g["escenas"]]
lineas += ["", "=" * 60, "ESCENA POR ESCENA", "=" * 60]
for i, e in enumerate(g["escenas"], 1):
    lineas += ["", f"ESCENA {i}",
               f"  Voz:       {e['frase']}",
               f"  Pantalla:  {e['cifra'] + ' | ' if e['cifra'] else ''}{e['etiqueta']}"]
    if e.get("fuente"):
        lineas.append(f"  Fuente:    {e['fuente']}")
lineas += ["", "CRÉDITOS (pantalla final, sin voz)"] + [f"  - {c}" for c in g["creditos"]]
(AQUI / "guion_para_revisar.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas))
