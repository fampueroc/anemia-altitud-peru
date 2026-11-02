"""Mapas y gráficos del reel, dibujados con Pillow a partir de los resultados de datos/procesados.

    capas(guion, narracion)  capa de cada escena; las escenas 2, 4, 5 y 6 llevan mapa o gráfico

En la escena 6 cada departamento se resalta cuando la voz lo nombra (tiempos de Whisper).
"""
import csv
import json
import math

from PIL import Image, ImageDraw

import reel
from reel import ALTO, ANCHO, MARGEN, SUAVE, TEXTO, _envolver, _escena, _fuente

RAIZ = reel.AQUI.parent
SUBE, BAJA, APAGADO, BORDE = reel.ACENTO, "#6EA8E6", "#3B3833", "#1C1A17"
ESCALA = 3   # se dibuja a 3x y se reduce, para que los bordes salgan suaves


def _leer(nombre):
    with open(RAIZ / "datos" / "procesados" / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _si(valor):
    return valor.strip().lower() == "true"


GEO = json.loads((RAIZ / "web" / "data" / "ambitos.geojson").read_text(encoding="utf-8"))["features"]
REPLICA = [r for r in _leer("replica_departamento_2024_2025.csv") if r["ambito"] != "Perú"]
ALTITUD = _leer("anemia_altitud_2025.csv")

SIN_CAMBIO = sorted(r["ambito"] for r in REPLICA if not _si(r["significativo_2024"]) and not _si(r["significativo_2025"]))
ROBUSTOS = {r["ambito"]: r for r in REPLICA if _si(r["puesto_robusto_2024"]) and _si(r["puesto_robusto_2025"])}
assert SIN_CAMBIO == ["Amazonas", "Arequipa", "Cajamarca", "Huánuco", "Moquegua"], SIN_CAMBIO
assert sorted(ROBUSTOS) == ["Amazonas", "Arequipa", "Cajamarca", "Pasco"], sorted(ROBUSTOS)


def _poligonos(f):
    g = f["geometry"]
    return [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]


def _proyeccion(x, y, ancho, alto):
    """Mercator ajustado a la caja (x, y, ancho, alto)."""
    def merc(p):
        return p[0], math.degrees(math.log(math.tan(math.pi / 4 + math.radians(p[1]) / 2)))
    pts = [merc(p) for f in GEO for pol in _poligonos(f) for anillo in pol for p in anillo]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = min(ancho / (x1 - x0), alto / (y1 - y0))
    def proyectar(p):
        mx, my = merc(p)
        return (x + (mx - x0) * k) * ESCALA, (y + (y1 - my) * k) * ESCALA
    return proyectar


def _mapa(capa, caja, colores):
    """Dibuja el mapa en la capa; `colores` da el color de los ámbitos resaltados, que van encima."""
    proyectar = _proyeccion(*caja)
    w, h = ANCHO * ESCALA, ALTO * ESCALA
    grande = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    orden = sorted(GEO, key=lambda f: f["properties"]["ambito"] in colores)
    for f in orden:
        nombre = f["properties"]["ambito"]
        marcado = nombre in colores
        mascara = Image.new("L", (w, h), 0)
        dm = ImageDraw.Draw(mascara)
        for pol in _poligonos(f):
            dm.polygon([proyectar(p) for p in pol[0]], fill=255)
            for hueco in pol[1:]:
                dm.polygon([proyectar(p) for p in hueco], fill=0)
        grande.paste(Image.new("RGBA", (w, h), colores.get(nombre, APAGADO)), (0, 0), mascara)
        d = ImageDraw.Draw(grande)
        for pol in _poligonos(f):
            for anillo in pol:
                pts = [proyectar(p) for p in anillo]
                d.line(pts + pts[:1], fill=TEXTO if marcado else BORDE, width=(3 if marcado else 1) * ESCALA, joint="curve")
    pequena = grande.resize((ANCHO, ALTO), Image.LANCZOS)
    capa.alpha_composite(pequena)


def _flecha(d, x, y, izq, der, f, color):
    """Escribe "izq → der"; la flecha se dibuja porque las fuentes no traen ese carácter."""
    d.text((x, y), izq, font=f, fill=color, anchor="ls")
    x0 = x + d.textlength(izq + " ", font=f)
    ym = y - f.size * 0.33
    d.line((x0, ym, x0 + 36, ym), fill=color, width=4)
    d.polygon([(x0 + 46, ym), (x0 + 30, ym - 11), (x0 + 30, ym + 11)], fill=color)
    d.text((x0 + 58, y), der, font=f, fill=color, anchor="ls")


def _capa_vacia():
    return Image.new("RGBA", (ANCHO, ALTO), (0, 0, 0, 0))


def _sin_cambio(e):
    """Escena 2: el 5, y en el mapa los cinco ámbitos sin cambio significativo los dos años."""
    capa = _capa_vacia()
    d = ImageDraw.Draw(capa)
    fc = _fuente("Oswald", 190, 700)
    d.text((MARGEN, 610), e["cifra"], font=fc, fill=TEXTO, anchor="ls")
    fe = _fuente("PublicSans", 46, 600)
    for i, linea in enumerate(_envolver(d, e["etiqueta"], fe, 720)):
        d.text((MARGEN + 150, 500 + i * 58), linea, font=fe, fill=SUAVE, anchor="ls")
    _mapa(capa, (MARGEN, 650, 500, 590), {n: SUBE for n in SIN_CAMBIO})
    fn = _fuente("Oswald", 56, 600)
    for i, n in enumerate(SIN_CAMBIO):
        d.text((MARGEN + 540, 800 + i * 84), n, font=fn, fill=SUBE, anchor="ls")
    return capa


def _altitud(e, resaltar, color):
    """Escenas 4 y 5: cambio de la anemia por franja de altitud, con las franjas que menciona la voz."""
    capa = _capa_vacia()
    d = ImageDraw.Draw(capa)
    d.text((MARGEN, 580), e["cifra"], font=_fuente("Oswald", 170, 700), fill=TEXTO, anchor="ls")
    d.text((MARGEN, 645), e["etiqueta"], font=_fuente("PublicSans", 44, 600), fill=SUAVE, anchor="ls")
    fl, fv = _fuente("PublicSans", 32, 500), _fuente("PublicSans", 36, 800)
    izq, der = MARGEN + 225, ANCHO - MARGEN
    minimo, maximo = -44, 20
    def x(v):
        return izq + (v - minimo) / (maximo - minimo) * (der - izq)
    y0, fila = 690, 60
    for i, r in enumerate(ALTITUD):
        desde, hasta, cambio = float(r["desde"]), r["hasta"], float(r["cambio"])
        nombre = f"{desde:.0f}+ m" if not hasta else f"{desde:.0f}–{float(hasta) - 1:.0f} m"
        activo = resaltar(desde)
        tono = color if activo else APAGADO
        y = y0 + i * fila
        d.text((MARGEN, y + 23), nombre, font=fl, fill=TEXTO if activo else SUAVE, anchor="lm")
        d.rounded_rectangle((min(x(0), x(cambio)), y, max(x(0), x(cambio)), y + 44), radius=6, fill=tono)
        texto = f"{cambio:+.0f}".replace("-", "−")
        d.text((x(cambio) + (10 if cambio > 0 else -10), y + 23), texto, font=fv, fill=TEXTO if activo else SUAVE,
               anchor="lm" if cambio > 0 else "rm")
    d.line((x(0), y0 - 8, x(0), y0 + fila * len(ALTITUD) - 8), fill=SUAVE, width=2)
    return capa


def _orden(palabras, inicio, fin):
    """Escena 6: una capa por momento; Amazonas, Arequipa y Cajamarca se suman y Pasco va solo, después."""
    def momento(nombre):
        return next(p[0] for p in palabras if inicio <= p[0] <= fin and p[2].strip(".,:;").lower() == nombre.lower())

    def puesto(n):
        return ROBUSTOS[n]["puesto_363_2025"].split(".")[0], ROBUSTOS[n]["puesto_oms_2025"].split(".")[0]

    fn, fp = _fuente("Oswald", 58, 600), _fuente("PublicSans", 40, 700)
    ft = _fuente("PublicSans", 40, 600)

    def dibujar(nombres, color, rotulo):
        capa = _capa_vacia()
        d = ImageDraw.Draw(capa)
        d.text((MARGEN, 455), "Puesto en anemia, 2025 (1 = más anemia)", font=ft, fill=SUAVE, anchor="ls")
        d.text((MARGEN, 505), "RM 363-2022 → OMS 2024".replace("→", "a"), font=_fuente("PublicSans", 32, 500), fill=SUAVE, anchor="ls")
        _mapa(capa, (MARGEN, 530, 560, 710), {n: color for n in nombres})
        x = MARGEN + 590
        if rotulo:
            d.text((x, 700), rotulo, font=fp, fill=color, anchor="ls")
        for i, n in enumerate(nombres):
            y = 780 + i * 145
            d.text((x, y), n, font=fn, fill=color, anchor="ls")
            izq, der = puesto(n)
            _flecha(d, x, y + 58, izq, der, fp, TEXTO)
        return capa

    return [(inicio - 1, dibujar([], SUBE, "")),
            (momento("Amazonas"), dibujar(["Amazonas"], SUBE, "SUBEN")),
            (momento("Arequipa"), dibujar(["Amazonas", "Arequipa"], SUBE, "SUBEN")),
            (momento("Cajamarca"), dibujar(["Amazonas", "Arequipa", "Cajamarca"], SUBE, "SUBEN")),
            (momento("Pasco"), dibujar(["Pasco"], BAJA, "BAJA"))]


def capas(guion, narracion):
    e = guion["escenas"]
    ini6, fin6 = narracion.escenas[5]
    momentos = _orden(narracion.palabras, ini6, fin6)

    def escena6(t):
        return [c for ini, c in momentos if ini <= t][-1] if t >= momentos[0][0] else momentos[0][1]

    return [_escena(e[0]), _sin_cambio(e[1]), _escena(e[2]),
            _altitud(e[3], lambda d: 500 <= d < 2500, SUBE), _altitud(e[4], lambda d: d >= 3000, BAJA),
            escena6, _escena(e[6])]
