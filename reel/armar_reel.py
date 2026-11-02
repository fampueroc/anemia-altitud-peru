"""Reel final con las tomas elegidas por la autora, sin volver a generar la voz.

    python armar_reel.py

Guarda en salidas/: reel.mp4, reel.wav, reel.srt y portada.png.
"""
import json
import sys

import numpy as np
import soundfile as sf

import reel
import visuales

SALIDAS = reel.AQUI / "salidas"
ESCENAS = SALIDAS / "narracion_mi_voz_2_escenas"
TOMAS = [SALIDAS / "toma_escena1_sin_coma_1.wav", SALIDAS / "toma_escena2_mi_voz_2_3.wav",
         ESCENAS / "escena_3.wav", ESCENAS / "escena_4.wav", ESCENAS / "escena_5.wav",
         SALIDAS / "toma_escena6_nueva_5.wav", SALIDAS / "toma_escena7_nueva_2.wav"]
MUSICA = reel.AQUI / "recursos" / "musica_opciones" / "Wholesome.mp3"
AUTOR, FUENTE = "Fiorella Ampuero", "INEI, ENDES 2024 y 2025"
CORRECCIONES = {("criterio.", "Que"): ("criterio", "que"), ("metros.", "Con"): ("metros,", "con")}
# La voz dice las cifras en palabras; los subtítulos las muestran en números
CIFRAS = {"dos mil veinticuatro": "2024", "dos mil veinticinco": "2025", "dos mil quinientos": "2500",
          "tres mil": "3000", "quinientos": "500", "cuarenta y tres coma cuatro": "43,4",
          "treinta y cuatro coma nueve por ciento": "34,9 %", "treinta y cuatro": "34", "catorce": "14",
          "once": "11", "siete": "7", "cinco": "5"}


def cifras_en_numeros(palabras):
    """Une las palabras de cada cifra en un solo elemento con su tiempo; conserva la puntuación final."""
    limpia = [p[2].strip(".,:;").lower() for p in palabras]
    salida, i = [], 0
    while i < len(palabras):
        for texto, numero in sorted(CIFRAS.items(), key=lambda c: -len(c[0].split())):
            n = len(texto.split())
            if limpia[i:i + n] == texto.split():
                fin = palabras[i + n - 1]
                salida.append((palabras[i][0], fin[1], numero + fin[2][len(fin[2].rstrip(".,:;")):]))
                i += n
                break
        else:
            salida.append(palabras[i])
            i += 1
    return salida


guion = json.loads((reel.AQUI / "guion.json").read_text(encoding="utf-8"))
wavs = [sf.read(t, dtype="float32") for t in TOMAS]
sr = wavs[0][1]
assert all(s == sr for _, s in wavs)

partes, escenas, t = [np.zeros(int(reel.INICIO * sr), np.float32)], [], reel.INICIO
for w, _ in wavs:
    escenas.append((t, t + len(w) / sr))
    partes += [w, np.zeros(int(reel.PAUSA * sr), np.float32)]
    t += len(w) / sr + reel.PAUSA
partes.append(np.zeros(int(reel.FINAL * sr), np.float32))
narracion = reel.Narracion(np.concatenate(partes), sr, escenas)
print(f"Narración: {narracion.duracion:.1f} s; con créditos: {narracion.duracion + reel.CREDITOS:.1f} s", flush=True)

reel.subtitulos(narracion, guion)
# Whisper corta estas frases con un punto que el guion no tiene
for i in range(len(narracion.palabras) - 1):
    (ini, fin, p), (ini2, fin2, p2) = narracion.palabras[i:i + 2]
    if (p, p2) in CORRECCIONES:
        q, q2 = CORRECCIONES[(p, p2)]
        narracion.palabras[i:i + 2] = [(ini, fin, q), (ini2, fin2, q2)]
narracion.palabras = cifras_en_numeros(narracion.palabras)
if "--subtitulos" in sys.argv:   # solo muestra el texto de los subtítulos, para revisarlo
    for b in reel._bloques(narracion.palabras):
        print(" ".join(p[2] for p in b), flush=True)
    sys.exit()
reel.a_srt(narracion, SALIDAS / "reel.srt")
capas = visuales.capas(guion, narracion)
if "--cuadros" in sys.argv:   # solo cuadros de prueba, sin armar el video
    base = reel._base(guion["titulo"], FUENTE, AUTOR)
    bloques, fuente_sub = reel._bloques(narracion.palabras), reel._fuente("PublicSans", reel.SUB_TAMANO, 700)
    momentos = [narracion.escenas[1][0] + 2, narracion.escenas[3][0] + 2, narracion.escenas[4][0] + 2]
    momentos += [p[0] + 0.3 for p in narracion.palabras if narracion.escenas[5][0] <= p[0] <= narracion.escenas[5][1]
                 and p[2].strip(".,").lower() in ("amazonas", "arequipa", "cajamarca", "pasco")]
    for k, t in enumerate(momentos):
        reel._cuadro(base, capas, narracion, t, bloques, fuente_sub).save(SALIDAS / f"_cuadro_{k}.png")
    sys.exit()
reel.portada(guion, narracion, SALIDAS / "portada.png", FUENTE, AUTOR, capas=capas)
reel.video(guion, narracion, SALIDAS / "reel.mp4", FUENTE, AUTOR, musica=MUSICA, capas=capas)
print("Listo:", SALIDAS / "reel.mp4", flush=True)
