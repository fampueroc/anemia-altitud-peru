# Validación contra cifras oficiales del INEI

Todos los resultados del proyecto salen de los microdatos de la ENDES 2025; la ENDES 2024 se usa para replicarlos (sección 5). Antes de usarlos, comprobamos que reproducen lo que publica el INEI.

## 1. Cálculo por niña y niño

`scripts/procesar.py` recalcula la hemoglobina ajustada por altitud a partir de la hemoglobina observada (`HC53`) y la altitud del conglomerado (`HV040`). El script se detiene si algún valor no coincide.

| Paso | Fórmula | Fuente | Coincidencia con el INEI |
|---|---|---|---|
| Ajuste RM 363-2022 | −0,032·a + 0,022·a², a = (m/1000)·3,3, desde 1000 m | INEI, ENDES 2025, cap. 9; CDC 1989 | 100 % con `HC56` |
| Ajuste OMS 2024 | 0,0056384·m + 0,0000003·m² (g/L), desde 500 m | WHO 2024, Tabla 4 | 100 % con `HC56A` |
| Anemia RM 363-2022 | Hb ajustada < 11,0 g/dL | INEI | 100 % con `HC57` |
| Anemia OMS 2024 | < 10,5 g/dL (6–23 m), < 11,0 g/dL (24–59 m) | WHO 2024, Tabla 2 | 100 % con `HC57A` |

Para coincidir exactamente, la hemoglobina ajustada se **trunca** a un decimal; no se redondea.

Población: niñas y niños de 6 a 35 meses, residentes habituales que durmieron en el hogar la noche anterior (`HV103 = 1`), con hemoglobina medida. Ponderador `HV005`, estrato `HV022`, conglomerado `HV001`.

## 2. Cifras nacionales

| Indicador | Nuestro cálculo | INEI (ENDES 2025) |
|---|---|---|
| Anemia 6–35 m, RM 363-2022 | 43,4 % [42,1 – 44,7] | 43,4 % [42,1 – 44,7] |
| Anemia 6–35 m, OMS 2024 | 34,9 % [33,7 – 36,1] | 34,9 % [33,7 – 36,1] |
| Anemia 6–59 m, RM 363-2022 | 33,4 % | 33,4 % |

Los intervalos de confianza también coinciden con los oficiales. Eso valida el cálculo del error de muestreo (linealización de Taylor).

## 3. Cifras por departamento

`scripts/validar_inei.py` descarga el capítulo 9 de cada informe departamental de la ENDES 2025 y compara. Resultado en `datos/procesados/validacion_inei_cap09_2025.csv`.

- **23 ámbitos × 2 criterios = 46 de 46 cifras coinciden.**
- **Moquegua:** su capítulo publica solo el dato de 6 a 59 meses. Lo calculamos para ese grupo y coincide: 25,8 % (RM 363-2022) y 27,1 % (OMS 2024).
- **Lima Metropolitana:** no se pudo validar. El archivo del INEI (`Endes15/pdf/Cap09.pdf`) lleva el encabezado de Lima Metropolitana, pero su texto es el de Callao (las mismas cifras y la misma redacción que `Endes15_2`). La estimación usa la misma metodología que reproduce exactamente a Lima Provincias y a Callao. Lima Metropolitana es la provincia de Lima (ubigeo 1501), como la define el INEI.

## 4. Incertidumbre del orden de los departamentos

`scripts/incertidumbre_puestos.py` usa un bootstrap de diseño con reescalamiento de Rao y Wu (2000 réplicas, semilla fija). Sus errores estándar coinciden con los de la linealización de Taylor (por ejemplo, Puno: 3,40 frente a 3,35). Un cambio de puesto se considera robusto si su intervalo de 95 % no incluye el cero.

Rao JNK, Wu CFJ (1988). Resampling inference with complex survey data. *Journal of the American Statistical Association* 83(401):231–241. DOI [10.1080/01621459.1988.10478591](https://doi.org/10.1080/01621459.1988.10478591)

## 5. Réplica con la ENDES 2024

Se repite todo el cálculo con los microdatos de la ENDES 2024 (código de encuesta 968; n = 9959 niñas y niños de 6 a 35 meses): `python procesar.py 2024`, `python incertidumbre_puestos.py 2024`, `python validar_inei.py 2024` y `python replicar_2024.py`.

**Validación 2024.** Los microdatos 2024 traen las dos clasificaciones del INEI (`HC56A` y `HC57A`, etiquetadas "NUEVA DIRECTRIZ OMS 2024/RM 251-2024-MINSA"). Nuestras fórmulas las reproducen al 100 %. Contra los capítulos departamentales 2024 (`datos/procesados/validacion_inei_cap09_2024.csv`):

- **49 de 49 cifras verificables coinciden**, incluida **Lima Metropolitana** (32,9 % y 24,0 %), que en 2025 no se pudo contrastar. Así queda validada nuestra definición de Lima Metropolitana (ubigeo 1501).
- **Moquegua** publica solo 6–59 meses: 28,5 % y 30,4 %. Nuestro cálculo da 28,49 % y 30,448 %.
- **Lambayeque, OMS 2024:** no se puede contrastar. En el PDF del INEI la sección OMS repite el texto de la sección RM 363-2022 (36,5 %, con los mismos porcentajes de anemia leve y moderada). Nuestro cálculo da 25,9 %; la clasificación niño por niño coincide al 100 % con `HC57A`.

**Las dos muestras no son independientes.** La ENDES rota un tercio de los conglomerados cada año (ficha técnica ENDES 2025, sección IV). En los microdatos, 2165 de los 3253 conglomerados de 2025 (66,6 %) tienen el mismo código `HV001` en 2024, que la ficha define como paneles. Las viviendas encuestadas son distintas, pero los lugares se repiten. Por eso la coincidencia entre años indica **estabilidad**, no una confirmación independiente. Como prueba más limpia, el patrón por altitud se estima también solo con los 1089 conglomerados de 2024 que no están en 2025.

**Resultados** (`datos/procesados/replica_departamento_2024_2025.csv` y `replica_altitud_2024_2025.csv`):

| Hallazgo | 2025 | 2024 | 2024, solo conglomerados que no están en 2025 |
|---|---|---|---|
| Cambio nacional (p.p.) | −8,5 [−9,4; −7,6] | −8,4 [−9,2; −7,6] | — |
| Sin cambio significativo | Amazonas, Arequipa, Cajamarca, Huánuco, Moquegua, San Martín | Amazonas, Arequipa, Cajamarca, Huánuco, Moquegua, Tacna | — |
| Cambio bajo 500 m | −11,2 | −11,0 | −10,8 |
| Cambio entre 500 y 2499 m (4 franjas) | +6,9 a +11,2, todas significativas | +6,6 a +8,5, todas significativas | +7,0 a +8,0, todas significativas |
| Cambio entre 2500 y 2999 m | −0,8 [−3,6; 2,1] | −2,4 [−4,7; −0,1] | −3,1 [−6,6; 0,4] |
| Cambio desde 3000 m (3 franjas) | −13,6 a −34,1 | −12,5 a −38,9 | −11,6 a −42,7 |
| Cambio de puesto robusto | Suben Amazonas, Arequipa, Cajamarca, San Martín; bajan Pasco, Ucayali | Suben Amazonas, Arequipa, Cajamarca, Moquegua; bajan Pasco, Huancavelica | — |

- **Ámbitos sin cambio significativo:** cinco se repiten los dos años. San Martín (2025: −2,3 [−5,3; 0,7]; 2024: −3,8 [−7,5; −0,1]) y Tacna (2024: −2,8 [−6,5; 0,8]; 2025: −5,0 [−8,9; −1,0]) están en el límite y cambian de grupo por pocas décimas.
- **Altitud:** el patrón se repite en todas las franjas, también en la submuestra sin paneles: baja bajo 500 m, sube entre 500 y 2499 m, no cambia de forma clara entre 2500 y 2999 m y baja desde 3000 m.
- **Puestos:** cuatro cambios son robustos los dos años: Amazonas, Arequipa y Cajamarca suben; Pasco baja. San Martín, Ucayali, Moquegua y Huancavelica son robustos solo en uno de los dos años.
