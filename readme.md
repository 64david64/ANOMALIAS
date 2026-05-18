# SismoTectoLab

SismoTectoLab es un visor web local para la visualización pedagógica e interpretación contextual de información gravimétrica y GNSS aplicada al análisis sismotectónico regional en Colombia.

El proyecto integra:

- anomalía gravimétrica base;
- anomalía de aire libre;
- anomalía de Bouguer simple;
- gradiente horizontal de Bouguer;
- velocidades GNSS estimadas desde desplazamientos acumulados;
- vectores GNSS residuales respecto a la media de la red retenida;
- perfiles espaciales W-E;
- figuras oficiales exportadas desde MATLAB.

## Alcance

El visor no declara fallas activas de forma definitiva. Los resultados se interpretan como patrones regionales, zonas de contraste gravimétrico, posibles lineamientos estructurales y áreas de interés sismotectónico que requieren contraste con información geológica y sismológica adicional.

La relación entre puntos gravimétricos y estaciones GNSS es contextual por proximidad espacial. No se interpreta que un punto gravimétrico pertenezca directamente a una estación GNSS.

## Flujo general

```text
Datos originales
    ↓
Procesamiento MATLAB
    ↓
Salidas oficiales CSV/JSON/PNG
    ↓
Flask + JavaScript
    ↓
Visor 2D, visor 3D, perfiles, GNSS e interpretación
```

## Instalación

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
python run.py
```

Luego abrir:

```text
http://127.0.0.1:5000
```

## Archivos requeridos

Las salidas oficiales deben estar en:

```text
data/processed/salidas_sismotectonicas/
```

con:

```text
grilla_bouguer_gradiente.csv
gnss_resumen_estaciones.csv
puntos_gravimetricos_clasificados.csv
metadata_variables.json
figuras/*.png
```

## Módulo Wavelet

El análisis wavelet queda planeado como fase posterior. No se integra todavía al visor base para evitar aumentar la complejidad antes de tener una plataforma estable.
```

---

# 4. Carpetas de datos

## `data/raw/README.md`

```md
# Datos originales

Esta carpeta almacena los insumos originales del proyecto.

Archivos esperados:

- `resultado_cruzado.csv`
- `anomalias_por_estacion.xlsx`

Estos archivos no deben modificarse manualmente. El procesamiento se realiza desde MATLAB y las salidas oficiales se guardan en `data/processed/salidas_sismotectonicas/`.
```

---

## `data/matlab/README.md`

```md
# Scripts MATLAB

Esta carpeta almacena el script oficial de procesamiento gravimétrico y GNSS.

Archivo esperado:

- `ANOMALIAS_CORREGIDO_V7.m`

El script genera las salidas oficiales para el visor web.
```

---

## `data/processed/README.md`

```md
# Datos procesados

Esta carpeta almacena las salidas oficiales generadas desde MATLAB.

El visor web consume principalmente:

```text
salidas_sismotectonicas/
├── grilla_bouguer_gradiente.csv
├── gnss_resumen_estaciones.csv
├── puntos_gravimetricos_clasificados.csv
├── metadata_variables.json
└── figuras/
```
```

---

# 5. Aplicación Flask

## `app/__init__.py`

```python
from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("config.Config")

    from .routes import bp
    app.register_blueprint(bp)

    return app
```
