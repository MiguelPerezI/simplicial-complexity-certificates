# MikeSimplex: mapa de repositorios y guía de análisis

Revisión de contenido: 23 de septiembre de 2026. Este índice describe los archivos presentes en esta copia del directorio, no el estado de repositorios remotos. Esta copia está versionada en `simplicial-complexity-certificates/`. Los enlaces a proyectos hermanos requieren tenerlos junto a este repositorio en `MikeSimplex/`.

## Qué es este conjunto

Estos proyectos estudian cómo construir y verificar sistemas de planificación de movimiento sobre complejos simpliciales. Para un espacio triangulado `K`, se cubre `K × K` (pares inicio-destino) con dominios en los que las proyecciones `π₁` y `π₂` están conectadas por cadenas de mapas contiguos. Un sistema de `k` dominios certifica `SC_strict(K) ≤ k - 1`, usando la convención reducida.

El conjunto reúne una implementación GPU del método greedy de referencia, un método posterior de búsqueda de cadenas completas, certificados de resultados y el manuscrito que presenta la investigación. La relación es de desarrollo científico y formato compartido; no implica que los repos se importen como paquetes entre sí.

## Mapa rápido

| Directorio o archivo | Qué contiene | Punto de entrada | Para qué consultarlo |
|---|---|---|---|
| [Abstract_Motion_GPU/](../Abstract_Motion_GPU/) | Repo Git: implementación Python + Numba/CUDA de los algoritmos greedy de referencia | [README](../Abstract_Motion_GPU/README.md) | Entender la primera etapa, su validación y sus límites |
| [chain-first-annealer/](../chain-first-annealer/) | Repo Git: motor de investigación, experimentos y herramientas; el trabajo está en `opti/` | [opti/README.md](../chain-first-annealer/opti/README.md) | Estudiar y reproducir la búsqueda nueva y las construcciones explícitas |
| [simplicial-complexity-certificates/](./) | Repo Git: selección de siete certificados, auditor fijado y manual para interpretarlos | [README](README.md) | Consultar y verificar la evidencia concreta y aprender a leer los planificadores |
| [Abstract_Motion_Planners/](../Abstract_Motion_Planners/) | Carpeta sin `.git`: manuscrito LaTeX y estilos de algoritmos | [main.tex](../Abstract_Motion_Planners/main.tex) | Revisar la exposición, los teoremas y las afirmaciones del artículo |
| [Abstract_Motion_Planners.zip](../Abstract_Motion_Planners.zip) | Archivo con `main.tex`, cinco estilos `.sty` y `algorithms.zip` | Carpeta descomprimida anterior | Identificar el paquete de fuentes del manuscrito |

## 1. Abstract_Motion_GPU: implementación de referencia en GPU

Porta a Python y CUDA el pipeline de búsqueda local, reducción de cadenas, crecimiento de dominios y optimización de cubiertas. Su README distingue la política `paper` de la política `batched-retry`: no deben tratarse como algoritmos idénticos al comparar resultados.

| Ruta | Función |
|---|---|
| [main.py](../Abstract_Motion_GPU/main.py) | Entrada de línea de comandos para experimentos |
| [absmotion/tables.py](../Abstract_Motion_GPU/absmotion/tables.py) | Complejo `K`, producto triangulado, proyecciones y tablas auxiliares |
| [absmotion/kernels.py](../Abstract_Motion_GPU/absmotion/kernels.py) | Caminatas de búsqueda en CUDA |
| [absmotion/cpu_twin.py](../Abstract_Motion_GPU/absmotion/cpu_twin.py) | Referencia CPU, reconstrucción y reducción de cadenas |
| [absmotion/driver.py](../Abstract_Motion_GPU/absmotion/driver.py) y [pipeline.py](../Abstract_Motion_GPU/absmotion/pipeline.py) | Coordinación del crecimiento y de los experimentos |
| [validate_host.py](../Abstract_Motion_GPU/validate_host.py), [validate.py](../Abstract_Motion_GPU/validate.py) | Comprobaciones CPU y comparación CPU/GPU |
| [independent_check.py](../Abstract_Motion_GPU/independent_check.py) | Auditor propio de esta etapa |
| [docs/EXECUTION.md](../Abstract_Motion_GPU/docs/EXECUTION.md) | Registro de ejecuciones y resultados |
| [docs/AUDIT_GPU_20260917.md](../Abstract_Motion_GPU/docs/AUDIT_GPU_20260917.md) | Revisión de fidelidad algorítmica |
| [paper_abs/](../Abstract_Motion_GPU/paper_abs/) | Material del artículo de referencia y fuentes auxiliares; distinguirlo del manuscrito nuevo |

Resultados presentes: `s2_smoke`, `s2_big`, `s2_big_attempt1`, `s3_smoke`, `s3_escalated`, `wedge2_example` y `audit_20260917`. El README documenta S² con tres dominios en `s2_smoke` y S³ con veinte dominios en `s3_smoke`. Son experimentos distintos de los certificados posteriores del annealer.

La búsqueda requiere NVIDIA/CUDA y las dependencias de [requirements.txt](../Abstract_Motion_GPU/requirements.txt). Consultar la documentación para los límites de tamaño y los cambios en semillas: el propio README advierte que ciertas ejecuciones antiguas no se reproducen bit a bit con el código actual.

## 2. chain-first-annealer: búsqueda nueva y laboratorio

El código principal está en `opti/src/`, dentro de [opti/](../chain-first-annealer/opti/); el cuaderno técnico está en `opti/experiments/`. El enfoque `chain-first` evoluciona sistemas completos de cadenas y mide qué facetas quedan cubiertas. Incluye también construcciones por productos de estrellas, herramientas de optimización y experimentos que no alcanzaron cobertura completa.

| Ruta dentro de `opti/` | Función |
|---|---|
| [optimized_algorithms.md](../chain-first-annealer/opti/experiments/optimized_algorithms.md) | Cuaderno técnico: diagnóstico, formulación, pruebas y evolución de resultados |
| [gpu_sc.py](../chain-first-annealer/opti/src/gpu_sc.py) | Annealer CUDA, estructuras del producto, verificación y exportación |
| [opti_sc.py](../chain-first-annealer/opti/src/opti_sc.py) | Implementación CPU del greedy optimizado |
| [star_cover.py](../chain-first-annealer/opti/src/star_cover.py) | Construcciones explícitas mediante dominios producto |
| [rect_cover.py](../chain-first-annealer/opti/src/rect_cover.py) | Número de cobertura por rectángulos `ρ(K)` |
| [stream_starcover.py](../chain-first-annealer/opti/src/stream_starcover.py) | Comprobaciones sin materializar todo el producto para casos grandes |
| [hybrid_cover.py](../chain-first-annealer/opti/src/hybrid_cover.py) | Experimentos que combinan dominios producto y búsqueda |
| [h1_obstruction.py](../chain-first-annealer/opti/src/h1_obstruction.py), [band_test.py](../chain-first-annealer/opti/src/band_test.py) | Análisis de obstrucciones para dominios candidatos |
| [independent_check.py](../chain-first-annealer/opti/src/independent_check.py) | Fuente del auditor independiente fijado en este archivo para los siete certificados seleccionados |
| [make_certificate_md.py](../chain-first-annealer/opti/src/make_certificate_md.py), [make_definition_md.py](../chain-first-annealer/opti/src/make_definition_md.py) | Generación de documentos a partir de resultados y definiciones |
| [reproduce_all.sh](../chain-first-annealer/opti/reproduce_all.sh) | Recetas de reproducción CPU y GPU |
| [results/](../chain-first-annealer/opti/results/) y [logs/](../chain-first-annealer/opti/logs/) | Resultados completos, parciales y registros |

Familias útiles para navegar `results/`:

- `s*_k3_v2`: resultados de búsqueda con tres cadenas para esferas.
- `*_starcover` y `torus_starcover_opt`: construcciones por dominios producto.
- `s3_k2_*`, `s4_k2_v2`, `wedge_k2`: búsquedas con dos cadenas; el nombre no certifica éxito.
- `cube_k3`, `cube_k3_v2`, `cube_k3_guided`: etapas de búsqueda y continuación del cubo.
- `torus_*`: experimentos del toro, incluidos híbridos y coberturas parciales.
- `bary_*`, `circle_*`, `*_equiv_*`: casos adicionales y variantes.

El README menciona resultados que no están en este checkout, incluidos `wedge_k3_v2`, `s7_starcover` y `s8_starcover`. El certificado del wedge sí está en el repo de certificados. Para decidir qué evidencia existe localmente, comprobar los archivos, no solo las tablas del README.

## 3. simplicial-complexity-certificates: evidencia seleccionada

Contiene datos y documentación, sin el motor de búsqueda. Incluye una copia fijada del auditor independiente, su procedencia y un manifiesto de hashes. Los siete casos viven en [results/chain-first-annealer/](results/chain-first-annealer/).

| Caso | Facetas de `K × K` | Tamaños de los tres dominios | Cota certificada |
|---|---:|---|---|
| [S²](results/chain-first-annealer/s2_k3_v2/) | 96 | 54 + 29 + 13 | `SC_strict ≤ 2` |
| [S³](results/chain-first-annealer/s3_k3_v2/) | 500 | 309 + 130 + 61 | `SC_strict ≤ 2` |
| [S⁴](results/chain-first-annealer/s4_k3_v2/) | 2,520 | 1,634 + 653 + 233 | `SC_strict ≤ 2` |
| [S⁵](results/chain-first-annealer/s5_k3_v2/) | 12,348 | 7,061 + 4,239 + 1,048 | `SC_strict ≤ 2` |
| [S⁶](results/chain-first-annealer/s6_k3_chain_first_continuation_01/) | 59,136 | 44,909 + 11,451 + 2,776 | `SC_strict ≤ 2` |
| [Cubo](results/chain-first-annealer/cube_k3_guided/) | 864 | 482 + 236 + 146 | `SC_strict ≤ 2` |
| [Dos círculos](results/chain-first-annealer/wedge_k3_v2/) | 50 | 18 + 16 + 16 | `SC_strict ≤ 2` |

Cada caso incluye `definition.md` (complejo y numeración), `cover.txt` (partición de facetas), `planners.txt` (mapas reducidos) y `summary.json` (metadatos y estado de búsqueda). Cubo y wedge añaden `certificate.md`. `chain_lengths` cuenta enlaces: una cadena con `T` enlaces tiene `T + 1` mapas. En las tablas, `@` marca un vértice ajeno al dominio.

La cubierta, los planificadores y el resumen archivados de S⁶ coinciden byte por byte con el resultado auditado `chain-first-annealer/opti/results/s6_k3_chain_first_continuation_01/rung02`. El `summary.json` conserva la revisión generadora y los hashes de sus fuentes.

Los siete casos pasan la copia fijada del auditor independiente, con salida 0: reconstrucción de facetas, cobertura, extremos de las cadenas, simplicialidad y contigüidad. Esto verifica los certificados; no reproduce los tiempos de búsqueda ni prueba por sí solo optimalidad.

## 4. Abstract_Motion_Planners: manuscrito del artículo

[main.tex](../Abstract_Motion_Planners/main.tex) lleva el título *Simplicial complexity of spheres: a chain-first annealer for explicit covers of boundary-of-simplex spheres*, firmado por Miguel Esteban Perez Ibarra y Jaziel Flores. Los comentarios del archivo lo identifican como borrador para arXiv; esto no acredita publicación.

Su estructura conecta las piezas anteriores: introducción y antecedentes, diagnóstico del greedy, annealer, teorema de dominios producto, resultados, auditoría y reproducción, y conjeturas. La carpeta contiene también cinco estilos LaTeX para algoritmos y un pequeño `algorithms.zip`. No incluye un PDF compilado, código Python ni certificados.

Puntos concretos para revisar al alinear manuscrito, código y datos:

1. **Disponibilidad de artefactos.** El manuscrito dice que el repo de certificados incluye annealer, auditor y reproducción. En los checkouts actuales esos archivos están en `chain-first-annealer/opti/`; además, las rutas de resultados del texto omiten el nivel `chain-first-annealer/` del repo de certificados.
2. **Convención de conteo.** La conjetura C1 escribe `SC_strict(∂Δ⁴) = 2` y enseguida dice que dos cadenas bastan. Con la convención definida en el mismo texto, dos cadenas certificarían `SC_strict ≤ 1`. Hay que aclarar la afirmación pretendida.
3. **Definición de la energía.** Contrastar la fórmula del manuscrito con el kernel: el código usa una penalización del mínimo de defectos por faceta, pesos y un término `gamma` sobre los defectos de todas las cadenas. La fórmula expositiva no identifica esos elementos del mismo modo.
4. **Alcance de los mapas candidatos.** El manuscrito describe mapas simpliciales sobre todo `K × K`; el método admite candidatos con defectos y certifica su restricción al dominio cubierto. Conviene precisar esa distinción.
5. **Tiempos y configuración.** Separar el tiempo de la etapa guiada del cubo (aproximadamente 304 s) del total con sus etapas previas (aproximadamente 24 min). Los parámetros varían por corrida; cotejar el pie de tabla con cada `summary.json`.

Estos son hallazgos de lectura y cotejo local, no una revisión completa de las demostraciones, de la bibliografía ni de las afirmaciones de novedad científica. No se compiló el manuscrito durante esta revisión.

## Orden sugerido para analizar el conjunto

1. Leer el [manual de certificados](README.md) y seguir su ejemplo S² para fijar el significado de dominio, mapa y cadena.
2. Leer la introducción y los antecedentes de [main.tex](../Abstract_Motion_Planners/main.tex) para entender la pregunta de investigación.
3. Revisar [Abstract_Motion_GPU/README.md](../Abstract_Motion_GPU/README.md) y su auditoría para establecer el método base y las variantes.
4. Leer las secciones 10–12 y la evolución posterior de [optimized_algorithms.md](../chain-first-annealer/opti/experiments/optimized_algorithms.md), contrastando con `gpu_sc.py`.
5. Auditar los siete resultados seleccionados y comparar los certificados buscados con las construcciones de `star_cover.py`.
6. Volver al manuscrito para alinear cada afirmación con su demostración, experimento o certificado, atendiendo a los pendientes anteriores.

## Comandos de consulta y verificación

Ejecutar desde el directorio padre `MikeSimplex/`. El auditor usa Python estándar y no requiere GPU:

```bash
# Verificar un certificado.
python3 chain-first-annealer/opti/src/independent_check.py \
  simplicial-complexity-certificates/results/chain-first-annealer/s2_k3_v2

# Verificar los siete certificados y el manifiesto de hashes.
python3 simplicial-complexity-certificates/audit/verify_all.py --check
```

Para volver a generar resultados, revisar primero `reproduce_all.sh`: escribe en `opti/results/`, su intérprete por defecto apunta a una ubicación histórica y debe configurarse mediante `PY`. Necesita NumPy, Numba y SciPy; el modo GPU añade CUDA. La reproducción de búsquedas no se ejecutó en esta revisión.

## Criterio para interpretar resultados

Una ejecución parcial o estancada no demuestra imposibilidad. Un certificado completo prueba una cota superior; una igualdad requiere además una cota inferior. La optimalidad entre coberturas por rectángulos no implica optimalidad entre todos los dominios posibles. Mantener separadas esas tres clases de evidencia al comparar el artículo, los logs y los resultados.
