# Literatura y fuentes

Verificación del 29-oct-2026. **Verificado** = abrí el documento original (PDF oficial, ficha de la revista o PubMed) y confirmé el título, los autores y el dato que se usa.

## Datos

| Fuente | Qué aporta | Estado |
|---|---|---|
| INEI (2026). *Perú: Encuesta Demográfica y de Salud Familiar 2025 – Nacional y Departamental*. [PDF](https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib2089/libro.pdf) | Anemia en 6–35 meses: **43,4 %** con RM 363-2022-MINSA y **34,9 %** con OMS 2024 / RM 251-2024-MINSA. Fórmula del ajuste anterior (CDC/PNSS y Dirren): ajuste = −0,032·alt + 0,022·alt², con alt = (m/1000)·3,3. Mapas departamentales con los dos criterios (cap. 9). | verificado |
| INEI. Portal de microdatos (ENDES: RECH0, RECH1, RECH6). [Portal](https://proyectos.inei.gob.pe/microdatos/) | Microdatos de la ENDES 2025 (código 1038) y 2024 (código 968), módulos 1629 y 1638. | verificado (descargados) |
| INEI. *Ficha técnica ENDES 2024* y *Ficha técnica ENDES 2025* (vienen dentro de los módulos de microdatos). | Diseño muestral. Sección IV: se rota un tercio de los conglomerados por año; los que tienen el mismo `HV001` en dos años consecutivos son paneles, con viviendas distintas. | verificado en los PDF |
| INEI. *ENDES 2024 y 2025, informes departamentales*, capítulo 9. `https://proyectos.inei.gob.pe/endes/AAAA/departamentales/EndesNN/pdf/Cap09.pdf` | Anemia por departamento con los dos criterios, para validar. | verificado (descargados) |
| INEI (2007). Límite provincial, vía Geoservidor MINAM / GEOIDEP; GeoJSON en [juaneladio/peru-geojson](https://github.com/juaneladio/peru-geojson) (MPL-2.0). | Límites para el mapa. Se agrupan por ubigeo en 26 ámbitos (provincia 1501 = Lima Metropolitana). Solo sirven para dibujar: ninguna cifra depende de ellos. | verificado (fuente y licencia en el repositorio) |
| IHSN. Diccionario de datos ENDES **2011**, archivo RECH6. [Link](https://datacatalog.ihsn.org/catalog/3423/data-dictionary/F7) | hc53 = hemoglobina observada (g/dL), hc56 = ajustada por altitud, hc57 = nivel de anemia. | verificado; confirmado con las etiquetas de los microdatos 2024 (HC56/HC57 = RM 363-2022; HC56A/HC57A = OMS 2024 / RM 251-2024) |

## Normas

| Fuente | Qué aporta | Estado |
|---|---|---|
| MINSA. RM N.º 251-2024-MINSA (8-abr-2024), aprueba la NTS N.º 213-MINSA/DGIESP-2024, modificada por RM N.º 429-2024-MINSA. [gob.pe](https://www.gob.pe/institucion/minsa/normas-legales/5440166-251-2024-minsa) · [El Peruano](https://busquedas.elperuano.pe/dispositivo/NL/2277624-1) | Adopta la guía OMS 2024: nuevo ajuste por altitud y punto de corte de 10,5 g/dL para 6–23 meses. | verificado |
| MINSA. RM N.º 363-2022-MINSA. [gob.pe](https://www.gob.pe/institucion/minsa/normas-legales/2998207-363-2022-minsa) · [El Peruano](https://busquedas.elperuano.pe/dispositivo/NL/2068796-1) | Guía técnica para medir la hemoglobina con hemoglobinómetro portátil. Es el "criterio anterior" que usa la ENDES. | verificado |

## Metodología

| Fuente | Qué aporta | Estado |
|---|---|---|
| WHO (2024). *Guideline on haemoglobin cutoffs to define anaemia in individuals and populations*. Geneva, 5-mar-2024. ISBN 978-92-4-008854-2. [Página](https://www.who.int/publications-detail-redirect/9789240088542) · [PDF](https://iris.who.int/server/api/core/bitstreams/f9f74397-1440-478d-a63c-26f29a01552f/content) | Puntos de corte: <105 g/L (6–23 m) y <110 g/L (24–59 m) (Tabla 2). Ajuste por altitud (g/L) = 0,0056384·elev + 0,0000003·elev², tabla que empieza en 500 m. | verificado en el PDF |
| Gonzales GF, Suarez Moreno VJ (2024). Hemoglobin levels for determining anemia: new WHO guidelines and adaptation of the national standard. *Rev Peru Med Exp Salud Publica* 41(2). DOI [10.17843/rpmesp.2024.412.13894](https://doi.org/10.17843/rpmesp.2024.412.13894) | Explica cómo se adaptó la norma peruana. | verificado (PubMed) |
| Sharma AJ, Addo OY, Mei Z, Suchdev PS (2019). Reexamination of hemoglobin adjustments to define anemia: altitude and smoking. *Ann N Y Acad Sci* 1450:190–203. DOI [10.1111/nyas.14167](https://doi.org/10.1111/nyas.14167) | Base empírica (BRINDA) del nuevo ajuste. | verificado (PubMed) |
| CDC (1989). CDC criteria for anemia in children and childbearing-aged women. *MMWR* 38(22):400–404. PMID 2542755 | Origen de la fórmula cuadrática anterior. | verificado (PubMed) |
| Rao JNK, Wu CFJ (1988). Resampling inference with complex survey data. *JASA* 83(401):231–241. DOI [10.1080/01621459.1988.10478591](https://doi.org/10.1080/01621459.1988.10478591) | Bootstrap de diseño para la incertidumbre del orden de los departamentos. | verificado (Crossref) |

## Estudios sobre el Perú

| Fuente | Qué aporta | Estado |
|---|---|---|
| Hernández-Vásquez A, Vargas-Fernández R, Guerra Valencia J (2025). Redefinición de la anemia infantil en el Perú: variaciones distritales tras la adopción de la guía OMS 2024. *Acta Médica Peruana* (30-jun-2025). [Artículo](https://amp.cmp.org.pe/index.php/AMP/article/view/3624) | Antecedente directo. Usa el **SIEN** (registros de establecimientos de salud), no la ENDES, y compara CDC 1989 con OMS 2024 por distrito. En zonas de ≥3500 m la anemia baja de 31,3 % a 15,8 %; entre 500 y 2500 m sube. Los distritos altoandinos bajan de categoría y algunos amazónicos suben. | verificado (ficha de la revista) |
| Hernández-Vásquez A, Guerra Valencia J, Vargas-Fernández R (2024). How much has the prevalence of anemia in Peruvian women changed with the WHO 2024 criteria? Analysis of ENDES 2023. *Rev Peru Med Exp Salud Publica* 41(3). DOI [10.17843/rpmesp.2024.413.13993](https://doi.org/10.17843/rpmesp.2024.413.13993) | El mismo ejercicio con la ENDES, en mujeres. | verificado (PubMed) |
| Gonzales GF, Vásquez-Velásquez C, Yucra S, Tapia V, Gasco M, Suchdev PS, Rees CA, Aguilar J (2025). The New WHO Cut-off Point for Defining High-altitude Anemia may be Inadequate. *Inquiry* 62. DOI [10.1177/00469580251372827](https://doi.org/10.1177/00469580251372827) | Contrapunto: el ajuste por altitud podría sobreestimar la anemia en altura. Va en limitaciones. | verificado (ficha institucional) |
