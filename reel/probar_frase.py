"""Genera varias tomas de una escena y mide la pausa después de la primera palabra.

    python probar_frase.py 2 3                  # escena 2 del guion, 3 tomas, con mi_voz_2.ogg
    python probar_frase.py 2 3 otra_voz.ogg     # lo mismo con otra grabación de recursos/

Guarda salidas/toma_escena<N>_<k>.wav (con la voz 8 % más rápida, como en el reel) e imprime
la pausa entre la primera y la segunda palabra según Whisper.
"""
import json
import sys

import numpy as np
import soundfile as sf

import reel

escena, tomas = int(sys.argv[1]), int(sys.argv[2])
referencia = sys.argv[3] if len(sys.argv) > 3 else "mi_voz_2.ogg"
sufijo = "" if len(sys.argv) <= 3 else "_" + reel.Path(referencia).stem
VELOCIDAD = 1.08
frase = json.loads((reel.AQUI / "guion.json").read_text(encoding="utf-8"))["escenas"][escena - 1]["frase"]
print("Frase:", frase)
voz = reel.Voz(reel.AQUI / "recursos" / referencia)
salidas = reel.AQUI / "salidas"
for k in range(1, tomas + 1):
    w = reel._acelerar(np.asarray(voz.decir([frase])[0], np.float32), voz.sr, VELOCIDAD)
    sf.write(salidas / f"toma_escena{escena}{sufijo}_{k}.wav", w, voz.sr)
    segs, _ = reel._whisper().transcribe(reel._a16k(w, voz.sr), language="es", word_timestamps=True)
    ws = [x for s in segs for x in s.words]
    pausa = ws[1].start - ws[0].end if len(ws) > 1 else float("nan")
    print(f"Toma {k}: {len(w) / voz.sr:.1f} s · pausa después de «{ws[0].word.strip()}»: {pausa:.2f} s · "
          f"WER {reel._wer(frase, reel._a16k(w, voz.sr)):.2f}", flush=True)
