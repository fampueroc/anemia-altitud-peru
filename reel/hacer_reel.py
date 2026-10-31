"""Paso 2: guion.json -> voz clonada -> reel vertical.

    python hacer_reel.py --voz recursos/mi_voz_2.ogg --autor "Fiorella Ampuero" \
        --fuente "INEI, ENDES 2024 y 2025" --velocidad 1.08 --musica recursos/musica_opciones/Wholesome.mp3

Lee el guion revisado de reel/guion.json. Guarda en salidas/: reel.mp4, reel.wav, reel.srt, portada.png,
posts.md y una copia de guion.json con el WER por escena.
Copiado de la sesión 15 del curso; se agregaron --guion y --musica.
"""
import argparse
import json
import time

import reel

p = argparse.ArgumentParser()
p.add_argument("--voz", required=True, help="10 a 20 s de tu voz: wav, m4a, ogg o mp3")
p.add_argument("--autor", required=True)
p.add_argument("--fuente", required=True, help="fuente de los datos, aparece en el video")
p.add_argument("--device", default="cpu", help="cpu, mps (Mac) o cuda")
p.add_argument("--motor", default="qwen", choices=["qwen", "voxcpm"], help="voxcpm acepta estilo de locutor por escena")
p.add_argument("--tts", default=reel.TTS, help="con --motor qwen; Qwen/Qwen3-TTS-12Hz-0.6B-Base es más rápido en CPU")
p.add_argument("--sin-estilo", action="store_true", help="con --motor voxcpm: clona sin indicar estilo")
p.add_argument("--velocidad", type=float, default=1.0, help="1.08 = 8 %% más rápido, sin cambiar el tono")
p.add_argument("--salidas", default=str(reel.AQUI / "salidas"))
p.add_argument("--guion", default=str(reel.AQUI / "guion.json"), help="guion revisado")
p.add_argument("--musica", help="pista de música con licencia; va por debajo de la voz")
a = p.parse_args()

t0 = time.time()
salidas = reel.Path(a.salidas)
salidas.mkdir(exist_ok=True)
archivo_guion = salidas / "guion.json"

guion = json.loads(reel.Path(a.guion).read_text(encoding="utf-8"))
for e in guion["escenas"]:
    print(f"   {'ok ' if e.get('cifra_en_texto') else '¡¡ '} {e['cifra'] or '-':>10} | {e['frase']}")
if not all(e.get("cifra_en_texto") for e in guion["escenas"]):
    print("   ¡Ojo! Hay cifras que no aparecen tal cual en el texto: revisen guion.json antes de publicar.")
if guion.get("cifras_dudosas_en_posts"):
    print("   Cifras de los posts que no están en el texto:", ", ".join(guion["cifras_dudosas_en_posts"]))

if a.motor == "voxcpm":
    voz = reel.VozExpresiva(a.voz, device=a.device, con_estilo=not a.sin_estilo)
else:
    voz = reel.Voz(a.voz, modelo=a.tts, device=a.device)
reel._reloj(f"voz cargada; referencia: «{voz.texto_ref}»", t0)
narracion = reel.narrar(voz, guion, velocidad=a.velocidad)
archivo_guion.write_text(json.dumps(guion, ensure_ascii=False, indent=2), encoding="utf-8")
reel._reloj(f"narración: {narracion.duracion:.1f} s; WER por escena: "
            + ", ".join(f"{e['wer']:.2f}" for e in guion["escenas"]), t0)

reel.subtitulos(narracion, guion)
reel.a_srt(narracion, salidas / "reel.srt")
reel._reloj(f"subtítulos: {len(narracion.palabras)} palabras", t0)

reel.portada(guion, narracion, salidas / "portada.png", a.fuente, a.autor)
reel.video(guion, narracion, salidas / "reel.mp4", a.fuente, a.autor, musica=a.musica)
reel.posts(guion, salidas / "posts.md")
reel._reloj(f"listo: {salidas / 'reel.mp4'}", t0)
