# Notas metodológicas

## Enfoque general

El proyecto desarrolla un visor web académico para explorar la relación contextual entre velocidades GNSS y anomalías gravimétricas en Colombia.

El caso de estudio se basa en un producto ya existente: el campo de velocidades geodésicas. El aporte del visor consiste en descomponer el proceso y mostrarlo de manera pedagógica, integrando capas gravimétricas, gradiente horizontal, estaciones GNSS y perfiles espaciales.

## Datos GNSS

Los datos GNSS provienen de estaciones consultadas en el Nevada Geodetic Laboratory. En este proyecto se emplean desplazamientos acumulados durante la serie temporal, convertidos a velocidades medias estimadas en mm/año.

El marco de referencia considerado es IGS20 / ITRF2020.

## Datos gravimétricos

Los datos gravimétricos se procesan para generar anomalías de aire libre, anomalía de Bouguer y gradiente horizontal. Estas capas se interpretan a escala regional.

## Relación gravedad-GNSS

La comparación entre puntos gravimétricos y estaciones GNSS se realiza únicamente de forma contextual por proximidad espacial. Los puntos gravimétricos no se consideran pertenecientes directamente a una estación GNSS.

## Interpretación sismotectónica

Las zonas de alto gradiente horizontal pueden señalar áreas de interés estructural o posibles lineamientos. No se interpretan como fallas activas confirmadas.

## Alcance

El visor tiene fines pedagógicos y exploratorios. Sus resultados requieren contraste con información geológica, sismológica y tectónica adicional.
```

### `docs/descripcion_variables.md`

```md
# Descripción de variables

| Variable | Unidad | Descripción |
|---|---:|---|
| `lat` | grados | Latitud del punto o celda de grilla. |
| `lon` | grados | Longitud del punto o celda de grilla. |
| `gravity_anomaly_base_mgal` | mGal | Anomalía gravimétrica base de entrada. |
| `aire_libre_mgal` | mGal | Anomalía de aire libre calculada a partir del procesamiento gravimétrico. |
| `bouguer_mgal` | mGal | Anomalía de Bouguer derivada del dato base y correcciones aplicadas. |
| `altura_m` | m | Altura/topografía asociada al punto o celda. |
| `gradiente_mgal_km` | mGal/km | Gradiente horizontal de la anomalía de Bouguer. |
| `vel_e_mm_yr` | mm/año | Velocidad media estimada en componente Este. |
| `vel_n_mm_yr` | mm/año | Velocidad media estimada en componente Norte. |
| `vel_u_mm_yr` | mm/año | Velocidad media estimada en componente vertical. |
| `vel_e_residual_mm_yr` | mm/año | Componente Este residual respecto a la media de la red retenida. |
| `vel_n_residual_mm_yr` | mm/año | Componente Norte residual respecto a la media de la red retenida. |
| `vel_horizontal_mm_yr` | mm/año | Magnitud horizontal resultante. |
| `clase_distancia` | texto | Clasificación contextual de proximidad entre punto gravimétrico y estación GNSS retenida. |

## Nota metodológica

Las variables GNSS se interpretan como velocidades medias estimadas a partir de desplazamientos acumulados durante la serie temporal. La comparación con puntos gravimétricos es contextual por proximidad espacial.
```

### `docs/referencias.md`

```md
# Referencias y fuentes

## Datos GNSS

Nevada Geodetic Laboratory. MAGNET + Global GPS Network Map.  
https://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html

Uso en el proyecto: consulta de estaciones GNSS, series temporales y datos asociados para el análisis de velocidades geodésicas.

## Referencia conceptual principal

Mora Páez, H. Marco de Referencia Geodésico de Colombia y Desarrollo Sostenible. IGAC. Presentación disponible en SIRGAS/IPGH.  
https://sirgas.ipgh.org/wp-content/uploads/2025/03/Marco-de-Referencia-Geodesico-de-Colombia-y-Desarrollo-Sostenible-Hector-Mora-Paez.pdf

Uso en el proyecto: caso de estudio y referencia conceptual, especialmente el componente de campo de velocidades geodésicas.

## Marco de referencia

International GNSS Service. IGS20 reference frame.  
https://igs.org/news/igs20/

Uso en el proyecto: marco de referencia GNSS IGS20 / ITRF2020.

## Créditos de imágenes

Geovirtual2. Material conceptual sobre anomalía de Bouguer.  
https://www.geovirtual2.cl/EXPLORAC/TEXT/06002bgra.htm

Toposervis. Material divulgativo sobre GNSS.  
https://toposervis.com/que-es-y-para-que-sirve-un-gnss/
```

---

## 9. Ruta para servir figuras de MATLAB

Si todavía no tienes una ruta para servir figuras exportadas desde MATLAB, añade esto en `app/routes.py`.

Primero importa:

```python
from flask import send_from_directory
from pathlib import Path
```

Luego añade:

```python
BASE_DIR = Path(__file__).resolve().parents[1]
FIGURES_DIR = BASE_DIR / "data" / "processed" / "salidas_sismotectonicas" / "figuras"


@bp.route("/figuras/<path:filename>")
def figure_file(filename):
    return send_from_directory(FIGURES_DIR, filename)
```

Si esa ruta falla por ubicación, usa esta alternativa:

```python
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BASE_DIR.parent
FIGURES_DIR = PROJECT_DIR / "data" / "processed" / "salidas_sismotectonicas" / "figuras"
```

---

## 10. Wavelet: decisión para esta fase

Por ahora **no integrar Wavelet**.

Dejarlo como fase posterior:

```md
## Fase futura: análisis multiescala Wavelet

El análisis mediante transformadas wavelet se contempla como una fase posterior del visor. Su propósito será descomponer perfiles o superficies de anomalía de Bouguer en diferentes escalas espaciales para explorar estructuras locales, intermedias y regionales.

No se implementa en la primera versión para mantener una base estable y clara del visor.
```

---

## 11. Checklist antes de avanzar a interacción avanzada

- [ ] El visor abre en `http://127.0.0.1:5000`.
- [ ] La portada carga `portada.webp`.
- [ ] Las imágenes conceptuales cargan correctamente.
- [ ] Las figuras MATLAB se visualizan desde `/figuras/...`.
- [ ] Las tablas públicas solo muestran estaciones retenidas.
- [ ] El texto no menciona estaciones descartadas.
- [ ] El texto usa “relación contextual” y no “asociación directa”.
- [ ] El texto usa “lineamientos potenciales” y no “fallas detectadas”.
- [ ] El README explica fuentes, alcance y limitaciones.
- [ ] Los documentos en `docs/` están actualizados.