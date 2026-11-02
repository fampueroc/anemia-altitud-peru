# Reel

Reel vertical (1080×1920) de 45 a 75 segundos, narrado con la voz clonada de la autora. Todo corre en local y con modelos abiertos; no se usa ninguna API de pago. El código viene de la sesión 15 del curso (`sessions/15-texto-a-reel`), con dos agregados: una escena final de créditos y música de fondo.

| Archivo | Qué es |
|---|---|
| `guion.json` | Guion revisado: frase narrada, cifra y etiqueta de cada escena, con la fuente de cada cifra, más los créditos |
| `reel.py` | Voz clonada (Qwen3-TTS), subtítulos (Whisper), video (Pillow + ffmpeg), créditos y música |
| `hacer_reel.py` | Corre todo desde la terminal |
| `armar_reel.py` | Arma el reel final con las tomas elegidas, sin volver a generar la voz |
| `visuales.py` | Mapas y gráfico por altitud del reel, a partir de `datos/procesados` |
| `probar_voz.py` | Prueba corta de la voz clonada |

## Entorno

```bash
cd reel
uv venv .venv --python 3.12
uv pip install --python .venv/Scripts/python.exe torch --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv/Scripts/python.exe qwen-tts faster-whisper pillow imageio-ffmpeg soundfile jiwer num2words
```

La primera corrida baja unos 4 GB de modelos.

## Uso

```bash
.venv/Scripts/python.exe hacer_reel.py --voz recursos/mi_voz_2.ogg --autor "Fiorella Ampuero" \
    --fuente "INEI, ENDES 2024 y 2025" --velocidad 1.08 --musica recursos/musica_opciones/Wholesome.mp3
```

Guarda el video, los subtítulos (`reel.srt`) y la portada en `salidas/`. Cada corrida de la voz sale un poco distinta. Para el reel final se eligieron tomas por escena, y `armar_reel.py` las une sin volver a generar la voz.

La grabación de voz (`recursos/mi_voz*`), la música y `salidas/` no se suben al repositorio.

## Música

Kevin MacLeod (incompetech.com), con licencia [Creative Commons Attribución 4.0](https://creativecommons.org/licenses/by/4.0/). Según las preguntas frecuentes de incompetech, se puede usar en videos para redes sociales si se da el crédito. Para reproducir el reel, la pista se baja de `https://incompetech.com/music/royalty-free/mp3-royaltyfree/<Título>.mp3` y se guarda en `recursos/musica_opciones/`.

Pista elegida: "Wholesome", Kevin MacLeod (incompetech.com), CC BY 4.0, al 25 % de volumen.
