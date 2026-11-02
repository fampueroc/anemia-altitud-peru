# ¿Bajó la anemia infantil en todo el Perú?

**Cómo cambia la anemia en niñas y niños de 6 a 35 meses al pasar del criterio RM 363-2022-MINSA al de la OMS 2024, y qué tiene que ver la altitud.**

- **Dashboard:** https://fampueroc.github.io/anemia-altitud-peru/ *(se activa al publicar con GitHub Pages)*
- **Post en LinkedIn:** *(pendiente)*
- **Autoría:** Fiorella Ampuero · Diplomado de Data Science con Python, PUCP · Tarea 3

## Tema y pregunta

En abril de 2024, el MINSA adoptó la guía de la OMS para diagnosticar anemia (RM 251-2024-MINSA). La guía cambió dos cosas a la vez: la fórmula que ajusta la hemoglobina según la altitud y el punto de corte para niñas y niños de 6 a 23 meses. Con el criterio nuevo, la anemia en 6 a 35 meses pasa de **43,4 %** a **34,9 %** (INEI, ENDES 2025).

**Pregunta:** ¿esa baja ocurrió igual en todo el país, y cambia el orden de los departamentos?

## Descripción

El proyecto recalcula la anemia infantil con los dos criterios a partir de los microdatos de la ENDES. Para cada departamento y para cada franja de altitud estima cuánto cambia la cifra y con qué incertidumbre, y separa qué parte del cambio viene de la nueva fórmula de altitud y qué parte del nuevo punto de corte. Todo se replica con la ENDES 2024.

Es un análisis **descriptivo**: muestra cómo cambia la cifra según el criterio. No dice cuál criterio refleja mejor la condición de los niños ni atribuye causas.

## Fuentes y metodología

**Datos.**
- INEI, ENDES 2025 y 2024, microdatos (módulos 1629 y 1638: RECH0, RECH1, RECH6).
- Población: niñas y niños de 6 a 35 meses, residentes que durmieron en el hogar la noche anterior, con hemoglobina medida. n = 9306 en 2025 y 9959 en 2024.
- Límites para el mapa: INEI (2007), vía [juaneladio/peru-geojson](https://github.com/juaneladio/peru-geojson) (MPL-2.0).

**Criterios.**

| | Ajuste por altitud | Punto de corte |
|---|---|---|
| RM 363-2022-MINSA | CDC (1989): −0,032·a + 0,022·a², a = (m/1000)·3,3, desde 1000 m | < 11,0 g/dL |
| OMS 2024 / RM 251-2024-MINSA | 0,0056384·m + 0,0000003·m² (g/L), desde 500 m | < 10,5 g/dL (6–23 meses); < 11,0 g/dL (24–59 meses) |

**Estimación.**
- Prevalencias ponderadas con el diseño de la ENDES (estratos y conglomerados). Error estándar por linealización de Taylor.
- La incertidumbre del puesto de cada departamento se estima con un bootstrap de diseño de Rao y Wu (1988), con 2000 réplicas.
- Un cambio de puesto se considera robusto si su intervalo de 95 % no incluye cero.

**Validación.**
- El cálculo reproduce al 100 % la hemoglobina ajustada y la clasificación de anemia del INEI para cada niña y niño, en 2025 y en 2024.
- Reproduce las cifras nacionales con sus intervalos de confianza.
- Coincide con todas las cifras departamentales verificables de los informes del INEI: 46 de 46 en 2025 y 49 de 49 en 2024.
- El detalle, incluidos dos errores de texto en los PDF del INEI, está en [`docs/validacion.md`](docs/validacion.md).

**Literatura.** Todas las fuentes, con enlace y estado de verificación, están en [`docs/literatura.md`](docs/literatura.md). Las principales son WHO (2024), Sharma et al. (2019), CDC (1989), Rao y Wu (1988), Hernández-Vásquez et al. (2025) y Gonzales et al. (2025).

## Hallazgos

1. **La baja no fue pareja.** En 2025 la anemia baja de forma significativa en 20 de 26 ámbitos. En 5 (Amazonas, Arequipa, Cajamarca, Huánuco y Moquegua) el cambio no se distingue de cero, ni en 2025 ni en 2024.
2. **El patrón depende de la altitud.** Con la nueva fórmula, la cifra de anemia sube entre 6,9 y 11,2 puntos entre 500 y 2499 m, y baja entre 13,6 y 34,1 puntos desde 3000 m (ENDES 2025). El patrón se repite con la ENDES 2024, también usando solo los conglomerados que no están en 2025. Coincide con lo que reporta Hernández-Vásquez et al. (2025) con datos de establecimientos de salud.
3. **Cambia el orden.** Con los datos de 2025 y de 2024, Amazonas, Arequipa y Cajamarca suben en el orden de anemia y Pasco baja. Puno sigue primero con ambos criterios.

## Limitaciones

- Es descriptivo. No dice cuál criterio refleja mejor la condición biológica de los niños; ese debate sigue abierto (Sharma et al. 2019; Gonzales et al. 2025).
- La ENDES es representativa a nivel nacional y departamental, no distrital. La altitud es la del conglomerado, no la de cada vivienda.
- Se hacen 26 comparaciones a la vez, y al 95 % podría aparecer un falso positivo por azar. Por eso solo se destacan los resultados que se repiten en 2024.
- La réplica con 2024 no es independiente: la ENDES rota un tercio de los conglomerados por año, y el 66,6 % de los de 2025 ya estaba en 2024, con viviendas distintas. La coincidencia indica estabilidad, no una confirmación independiente.
- Lima Metropolitana 2025 no se pudo contrastar con el INEI porque su archivo contiene el texto de Callao. Con 2024, el mismo cálculo sí coincide con la cifra publicada.

## Cómo reproducirlo

Requiere Python 3.11 o superior.

```bash
pip install -r requirements.txt
cd scripts

python obtener_datos.py              # microdatos ENDES 2025 (INEI)
python obtener_datos.py 2024         # microdatos ENDES 2024
python procesar.py                   # prevalencias 2025 con los dos criterios
python incertidumbre_puestos.py      # bootstrap de los puestos 2025
python procesar.py 2024
python incertidumbre_puestos.py 2024
python replicar_2024.py              # comparación 2024 frente a 2025
python validar_inei.py               # contraste con los informes departamentales del INEI
python validar_inei.py 2024
python preparar_mapa.py              # límites para el mapa
python exportar_web.py               # datos del dashboard (web/data/datos.js)
```

- **Dashboard estático:** abrir `web/index.html` en el navegador.
- **Versión Streamlit:** `streamlit run app.py` desde la raíz.

Los microdatos no se suben al repositorio; `obtener_datos.py` los vuelve a bajar del portal del INEI.

## Estructura

```
datos/procesados/   resultados (CSV) y validación contra el INEI
docs/               literatura y validación
scripts/            descarga, cálculo, réplica, validación y exportación
web/                dashboard estático (D3)
app.py              versión Streamlit del dashboard
reel/               guion y recursos del reel
```

## Uso de inteligencia artificial

- **Claude Code (Anthropic)** ayudó a escribir el código de análisis y del dashboard, a buscar y verificar la literatura y a redactar parcialmente los textos. Las cifras que el INEI publica se contrastaron con sus informes (detalle en `docs/validacion.md`), y el estado de verificación de cada fuente está en `docs/literatura.md`. Las decisiones del análisis y la revisión (tema, pregunta, qué hallazgos destacar y cómo formularlos) fueron mías.
- **Reel:** la narración usa mi voz clonada con Qwen3-TTS (Alibaba, Apache 2.0) a partir de una grabación mía, y los subtítulos se generaron con Whisper (MIT). Los dos modelos corren en local. El video lo indica con el aviso "Voz generada con IA".
