"""Reel final con las tomas elegidas por la autora, sin volver a generar la voz.

    python armar_reel.py

Guarda en salidas/: reel.mp4, reel.wav, reel.srt y portada.png.
"""
import json

import numpy as np
import soundfile as sf

import reel

SALIDAS = reel.AQUI / "salidas"
ESCENAS = SALIDAS / "narracion_mi_voz_2_escenas"
TOMAS = [SALIDAS / "toma_escena1_sin_coma_1.wav", SALIDAS / "toma_escena2_mi_voz_2_3.wav",
         ESCENAS / "escena_3.wav", ESCENAS / "escena_4.wav", ESCENAS / "escena_5.wav",
         SALIDAS / "toma_escena6_nueva_2.wav", SALIDAS / "toma_escena7_nueva_2.wav"]
MUSICA = reel.AQUI / "recursos" / "musica_opciones" / "Wholesome.mp3"
AUTOR, FUENTE = "Fiorella Ampuero", "INEI, ENDES 2024 y 2025"
CORRECCIONES = {("criterio.", "Que"): ("criterio", "que"), ("metros.", "Con"): ("metros,", "con")}

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
reel.a_srt(narracion, SALIDAS / "reel.srt")
reel.portada(guion, narracion, SALIDAS / "portada.png", FUENTE, AUTOR)
reel.video(guion, narracion, SALIDAS / "reel.mp4", FUENTE, AUTOR, musica=MUSICA)
print("Listo:", SALIDAS / "reel.mp4", flush=True)
