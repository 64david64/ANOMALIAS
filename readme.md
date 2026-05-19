# SismoTectoLab

**SismoTectoLab** es un visor web académico y pedagógico para visualizar e interpretar información gravimétrica y GNSS en un contexto sismotectónico regional de Colombia.

El proyecto integra anomalías gravimétricas, gradiente horizontal de Bouguer y velocidades GNSS retenidas, con el objetivo de apoyar una lectura contextual de posibles zonas de interés estructural.

---

## Objetivo

Construir una plataforma web que permita explorar de forma visual, didáctica y organizada:

- anomalía de aire libre;
- anomalía de Bouguer;
- gradiente horizontal de Bouguer;
- estaciones GNSS retenidas;
- velocidades medias derivadas de desplazamientos acumulados;
- perfiles W–E;
- visualización 2D y 3D;
- interpretación sismotectónica contextual.

---

## Caso de estudio base

El visor toma como referencia conceptual el caso de estudio asociado al **campo de velocidades geodésicas en Colombia**, presentado en el marco del documento:

**“Marco de Referencia Geodésico de Colombia y Desarrollo Sostenible”**

Referencia atribuida a:

**Héctor Mora Páez, MSc, PhD**  
Dirección de Gestión de Información Geográfica  
IGAC, Colombia

Perfil académico de referencia:

<https://www.researchgate.net/profile/Hector-Mora-Paez>

---

## Fuentes de datos

Los datos GNSS fueron consultados a partir de productos públicos del **Nevada Geodetic Laboratory**:

<https://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html>

Las salidas gravimétricas y geodésicas usadas por el visor son generadas previamente mediante procesamiento en MATLAB.

---

## Alcance metodológico

Este visor tiene un propósito académico y pedagógico. No busca reemplazar un producto geodésico, geológico o sismotectónico oficial.

La relación entre puntos gravimétricos y estaciones GNSS se interpreta únicamente de forma **contextual por proximidad espacial**. Los puntos gravimétricos no se consideran pertenecientes directamente a una estación GNSS.

Las zonas de alto gradiente horizontal de Bouguer se presentan como:

- posibles lineamientos gravimétricos;
- bordes corticales potenciales;
- áreas de interés estructural.

No se declaran fallas activas sin contraste geológico y sismológico adicional.

---

## Estructura del proyecto

```text
SismoTectoLab/
├── run.py
├── config.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   │
│   ├── services/
│   │   ├── data_loader.py
│   │   ├── geojson_builder.py
│   │   ├── interpretation_service.py
│   │   ├── metadata_service.py
│   │   └── station_service.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── inicio.html
│   │   ├── marco_conceptual.html
│   │   ├── metodologia.html
│   │   ├── resultados.html
│   │   ├── visor_2d.html
│   │   ├── visor_3d.html
│   │   ├── perfiles.html
│   │   ├── gnss.html
│   │   ├── interpretacion.html
│   │   └── acerca.html
│   │
│   └── static/
│       ├── css/
│       │   └── styles.css
│       ├── js/
│       │   ├── main.js
│       │   ├── visor-2d.js
│       │   ├── visor-3d.js
│       │   ├── perfiles.js
│       │   ├── gnss.js
│       │   └── interpretation-ui.js
│       └── img/
│           ├── portada.webp
│           ├── concepto_bouguer.png
│           └── concepto_gnss.png
│
├── data/
│   └── processed/
│       └── salidas_sismotectonicas/
│           ├── grilla_bouguer_gradiente.csv
│           ├── gnss_resumen_estaciones.csv
│           ├── puntos_gravimetricos_clasificados.csv
│           ├── metadata_variables.json
│           └── figuras/
│
└── docs/
```

---

## Salidas esperadas de MATLAB

El visor espera los siguientes archivos:

```text
data/processed/salidas_sismotectonicas/
├── grilla_bouguer_gradiente.csv
├── gnss_resumen_estaciones.csv
├── puntos_gravimetricos_clasificados.csv
├── metadata_variables.json
└── figuras/
    ├── 01_anomalia_aire_libre_vectores_gnss.png
    ├── 02_anomalia_bouguer_lineamientos_gnss.png
    ├── 03_gradiente_horizontal_bouguer_gnss.png
    ├── 04_perfiles_we_bouguer_topografia.png
    ├── 05_velocidades_gnss_estaciones_retenidas.png
    ├── 06_mapa_integrado_sismotectonico.png
    └── 07_correlacion_bouguer_topografia.png
```

---

## Instalación

Crear entorno virtual:

```powershell
python -m venv .venv
```

Activar entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

---

## Dependencias

El proyecto funciona sin pandas.

```text
Flask==3.0.3
```

Las visualizaciones del lado del cliente usan:

- Leaflet;
- Plotly;
- MathJax.

Estas librerías se cargan desde CDN en las plantillas correspondientes.

---

## Ejecución

Desde la raíz del proyecto:

```powershell
.\.venv\Scripts\python.exe run.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000
```

---

## Rutas principales

```text
/                  Inicio
/marco-conceptual  Marco conceptual
/metodologia       Metodología
/resultados        Resultados
/visor-2d          Visor 2D
/visor-3d          Visor 3D
/perfiles          Perfiles W–E
/gnss              Estaciones GNSS
/interpretacion    Interpretación sismotectónica
/acerca            Acerca del proyecto
```

---

## APIs principales

```text
/api/status
/api/metadata
/api/layers
/api/figuras
/api/grilla
/api/grilla/geojson
/api/gnss
/api/gnss/geojson
/api/puntos-gravimetricos
/api/perfiles
/api/interpretacion
```

---

## Versiones

### V1.0

Base estructural del visor: Flask, rutas, plantillas, estilos y servicios.

### V1.1

Integración real de datos exportados desde MATLAB.

### V1.2

Galería de resultados e interpretación por figura.

### V1.3

Contexto GNSS, visor 2D, visor 3D y perfiles W–E.

### V1.4

Fortalecimiento de interpretación sismotectónica.

### V2.0

Módulos avanzados, incluyendo análisis multiescala y Wavelet.

---

## Créditos

Proyecto académico desarrollado con fines pedagógicos para la integración visual de datos gravimétricos y GNSS en Colombia.

Referencia conceptual principal:

**Héctor Mora Páez, MSc, PhD**  
Dirección de Gestión de Información Geográfica  
IGAC, Colombia

Datos GNSS:

**Nevada Geodetic Laboratory**
```

---

# 7. Crear `docs/README.md`

Crea el archivo:

```text
docs/README.md
```

con:

```markdown
# Documentación técnica y metodológica

Esta carpeta reúne notas de apoyo para el desarrollo de SismoTectoLab.

## Contenido recomendado

```text
docs/
├── README.md
├── metodologia.md
├── variables.md
├── fuentes.md
└── roadmap.md
```

## Enfoque metodológico

La interpretación del visor se basa en la integración contextual de:

- anomalías gravimétricas;
- gradiente horizontal de Bouguer;
- estaciones GNSS retenidas;
- velocidades medias estimadas a partir de desplazamientos acumulados.

La relación entre puntos gravimétricos y estaciones GNSS no se considera directa. Se usa únicamente como apoyo contextual por proximidad espacial.

## Criterios de interpretación

- No declarar fallas activas sin contraste adicional.
- Interpretar los resultados a escala regional.
- Usar el gradiente horizontal como indicador de posibles cambios estructurales.
- Usar GNSS como referencia cinemática de estaciones retenidas.
- Mantener la separación conceptual entre campo gravimétrico y deformación geodésica.

## Fase futura

El análisis Wavelet se propone como fase posterior, una vez el visor base esté consolidado.
```

---

# 8. Crear `data/README.md`

Crea el archivo:

```text
data/README.md
```

con:

```markdown
# Datos del proyecto

Esta carpeta contiene los insumos y salidas procesadas usadas por SismoTectoLab.

## Estructura esperada

```text
data/
├── raw/
│   └── datos originales o de referencia
│
└── processed/
    └── salidas_sismotectonicas/
        ├── grilla_bouguer_gradiente.csv
        ├── gnss_resumen_estaciones.csv
        ├── puntos_gravimetricos_clasificados.csv
        ├── metadata_variables.json
        └── figuras/
```

## Archivos principales

### `grilla_bouguer_gradiente.csv`

Contiene la grilla procesada con variables como:

- longitud;
- latitud;
- anomalía gravimétrica base;
- anomalía de aire libre;
- anomalía de Bouguer;
- altura;
- gradiente horizontal.

### `gnss_resumen_estaciones.csv`

Contiene las estaciones GNSS retenidas para el análisis regional.

Incluye:

- estación;
- latitud;
- longitud;
- duración de serie temporal;
- velocidades absolutas;
- velocidades residuales;
- información contextual de proximidad gravimétrica.

### `puntos_gravimetricos_clasificados.csv`

Contiene los puntos gravimétricos clasificados por proximidad contextual a estaciones GNSS retenidas.

Los puntos no se interpretan como pertenecientes directamente a una estación GNSS.

### `metadata_variables.json`

Describe variables, unidades y notas metodológicas.

### `figuras/`

Contiene las figuras oficiales exportadas desde MATLAB.

## Nota metodológica

Las salidas de esta carpeta son generadas previamente mediante MATLAB. Flask no recalcula el procesamiento geofísico principal; únicamente carga, organiza y visualiza los resultados.