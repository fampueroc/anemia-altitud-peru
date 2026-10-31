"""Prueba corta de la voz clonada, antes de generar el reel.

    python probar_voz.py                          # Qwen3-TTS 1.7B
    python probar_voz.py Qwen/Qwen3-TTS-12Hz-0.6B-Base

Guarda salidas/prueba_voz_<modelo>.wav e imprime cuánto tardó y qué entendió Whisper.
"""
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

import reel

FRASE = ("Con el criterio nuevo, la anemia en niñas y niños de seis a treinta y cinco meses baja de "
         "cuarenta y tres coma cuatro a treinta y cuatro coma nueve por ciento. Pero no bajó igual en todo el país.")

modelo = sys.argv[1] if len(sys.argv) > 1 else reel.TTS
t0 = time.time()
voz = reel.Voz(reel.AQUI / "recursos" / "mi_voz_2.ogg", modelo=modelo)
reel._reloj(f"voz cargada; referencia: «{voz.texto_ref}»", t0)
t1 = time.time()
w = np.asarray(voz.decir([FRASE])[0], np.float32)
dur = len(w) / voz.sr
reel._reloj(f"{dur:.1f} s de audio en {time.time() - t1:.0f} s de cálculo", t0)
salidas = reel.AQUI / "salidas"
salidas.mkdir(exist_ok=True)
ruta = salidas / f"prueba_voz_{Path(modelo).name}.wav"
sf.write(ruta, w, voz.sr)
print("WER:", round(reel._wer(FRASE, reel._a16k(w, voz.sr)), 3))
print("Whisper oyó:", reel._transcribir(reel._a16k(w, voz.sr)))
print("Archivo:", ruta)
