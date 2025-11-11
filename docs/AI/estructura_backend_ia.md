# Arquitectura del Módulo de IA (Backend)

**Sistema:** SmartSales365 - Módulo de Predicción de Ventas  
**Framework:** Django 4.2.7 + scikit-learn  
**Fecha:** Noviembre 2025

---

## 📐 Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React/Next.js)                      │
│  - Dashboard de Predicciones                                     │
│  - Gráficos interactivos (Recharts)                             │
│  - Filtros dinámicos                                             │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP REST API
                     │ /api/ai/dashboard/
                     │ /api/ai/train/
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO BACKEND (Python)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              apps/ai/views.py                             │  │
│  │  - AIModelViewSet (endpoints REST)                        │  │
│  └───────────────────┬──────────────────────────────────────┘  │
│                      │                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           apps/ai/services/                               │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  DataPreparationService                             │  │  │
│  │  │  - get_historical_sales_data()                      │  │  │
│  │  │  - prepare_training_data()                          │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  ModelTrainingService                               │  │  │
│  │  │  - train_model()                                    │  │  │
│  │  │  - evaluate_model()                                 │  │  │
│  │  │  - save_model()                                     │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  PredictionService                                  │  │  │
│  │  │  - load_model()                                     │  │  │
│  │  │  - predict_next_n_months()                          │  │  │
│  │  │  - get_dashboard_data()                             │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │ SQL Queries
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                           │
│  - orders_pedido                                                 │
│  - orders_detallepedido                                         │
│  - products_prenda                                              │
│  - products_categoria                                           │
└─────────────────────────────────────────────────────────────────┘
                     
┌─────────────────────────────────────────────────────────────────┐
│                    FILE SYSTEM                                   │
│  models/                                                         │
│  ├── ventas_model_v1.0_20251111.pkl  (Modelo entrenado)        │
│  └── ventas_model_v1.0_20251111_metadata.json (Metadata)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Capa de Servicios (Service Layer)

### 1.1. DataPreparationService

**Ubicación:** `apps/ai/services/data_preparation.py`

**Responsabilidad:** Preparar y transformar datos crudos para el modelo de ML

#### Métodos Principales:

##### `get_historical_sales_data(months_back=36)`

**Propósito:** Extraer datos históricos de ventas desde PostgreSQL

**Input:**
```python
months_back: int = 36  # Número de meses hacia atrás
```

**Proceso:**
```python
1. Calcular fecha de inicio (hoy - months_back)
2. Query a base de datos:
   SELECT año, mes, categoria, SUM(cantidad), COUNT(DISTINCT pedido)
   FROM orders_detallepedido
   WHERE created_at >= fecha_inicio
   GROUP BY año, mes, categoria
3. Retornar DataFrame de pandas
```

**Output:**
```python
DataFrame con columnas:
- año: int (2023, 2024, 2025)
- mes: int (1-12)
- categoria: str ('Blusas', 'Vestidos', 'Jeans', 'Jackets')
- cantidad_vendida: int
- num_transacciones: int
- precio_promedio: float
```

**Casos especiales manejados:**
```python
# 1. Meses sin ventas (se completan con 0)
if not existe_venta(2025, 2, 'Jackets'):
    agregar_fila(año=2025, mes=2, categoria='Jackets', cantidad=0)

# 2. Categorías nuevas (se ignoran si tienen <3 meses de datos)
if categoria.meses_con_datos < 3:
    excluir_categoria()

# 3. Datos futuros (se filtran)
if fecha > datetime.now():
    excluir_registro()
```

---

##### `prepare_training_data(df, target_column='cantidad_vendida')`

**Propósito:** Aplicar feature engineering y preparar X, y para entrenamiento

**Input:**
```python
df: DataFrame (resultado de get_historical_sales_data)
target_column: str = 'cantidad_vendida'
```

**Proceso:**

**Paso 1: Eliminar features no predictivas**
```python
# ❌ Eliminar: num_transacciones, precio_promedio
# Razón: No conocemos estos valores en el futuro
df = df.drop(['num_transacciones', 'precio_promedio'], axis=1)
```

**Paso 2: One-Hot Encoding de categorías**
```python
# Convertir 'Blusas', 'Vestidos', etc. en columnas binarias
df_encoded = pd.get_dummies(df, columns=['categoria'], prefix='cat')

Antes:
| año | mes | categoria |
|-----|-----|-----------|
| 2025| 1   | Blusas    |

Después:
| año | mes | cat_Blusas | cat_Vestidos | cat_Jeans | cat_Jackets |
|-----|-----|------------|--------------|-----------|-------------|
| 2025| 1   | 1          | 0            | 0         | 0           |
```

**Paso 3: Feature engineering temporal**
```python
import numpy as np

# Componentes trigonométricas (capturan ciclicidad)
df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)

# Trimestre
df['trimestre'] = (df['mes'] - 1) // 3 + 1  # 1, 2, 3, 4
```

**Output:**
```python
X: DataFrame con features
   [año, mes, mes_sin, mes_cos, trimestre, cat_Blusas, cat_Vestidos, cat_Jeans, cat_Jackets]

y: Series con target
   [cantidad_vendida]
```

---

### 1.2. ModelTrainingService

**Ubicación:** `apps/ai/services/model_training.py`

**Responsabilidad:** Entrenar, evaluar y persistir el modelo de ML

#### Métodos Principales:

##### `train_model(months_back=36, test_size=0.2)`

**Propósito:** Entrenar modelo Random Forest con datos históricos

**Input:**
```python
months_back: int = 36  # Meses de histórico
test_size: float = 0.2  # Porcentaje para testing (20%)
```

**Proceso:**

**Paso 1: Obtener y preparar datos**
```python
# Usar DataPreparationService
data_service = DataPreparationService()
df = data_service.get_historical_sales_data(months_back)
X, y = data_service.prepare_training_data(df)
```

**Paso 2: División Train/Test**
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=test_size,  # 20%
    random_state=42
)

# Ejemplo:
# Total: 140 registros
# Train: 112 registros (80%)
# Test: 28 registros (20%)
```

**Paso 3: Entrenar Random Forest**
```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(
    n_estimators=100,      # 100 árboles
    max_depth=10,          # Profundidad máxima
    min_samples_split=5,   # Mínimo para dividir
    min_samples_leaf=2,    # Mínimo en hojas
    random_state=42
)

model.fit(X_train, y_train)
```

**Paso 4: Evaluar modelo**
```python
y_pred = model.predict(X_test)

metrics = {
    'r2_score': r2_score(y_test, y_pred),
    'mae': mean_absolute_error(y_test, y_pred),
    'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
}
```

**Paso 5: Analizar importancia de features**
```python
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)
```

**Output:**
```python
{
    'model': RandomForestRegressor (entrenado),
    'metrics': {
        'r2_score': 0.9727,
        'mae': 10.34,
        'rmse': 15.82
    },
    'feature_importance': DataFrame,
    'feature_names': ['año', 'mes', ...]
}
```

---

##### `save_model(model, metadata, filename=None)`

**Propósito:** Persistir modelo y metadata en disco

**Input:**
```python
model: RandomForestRegressor (entrenado)
metadata: dict {
    'version': 'v1.0',
    'trained_at': '2025-11-11 15:04:56',
    'r2_score': 0.9727,
    'mae': 10.34,
    'feature_names': ['año', 'mes', ...],
    'categories': ['Blusas', 'Vestidos', 'Jeans', 'Jackets']
}
filename: str (opcional)
```

**Proceso:**
```python
import joblib
import json
from datetime import datetime

# 1. Generar nombre de archivo
if not filename:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    version = metadata.get('version', 'v1.0')
    filename = f'ventas_model_{version}_{timestamp}'

# 2. Guardar modelo (.pkl)
model_path = f'models/{filename}.pkl'
joblib.dump(model, model_path)

# 3. Guardar metadata (.json)
metadata_path = f'models/{filename}_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
```

**Estructura del archivo metadata.json:**
```json
{
  "version": "v1.0",
  "trained_at": "2025-11-11T15:04:56",
  "model_type": "RandomForestRegressor",
  "hyperparameters": {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5,
    "min_samples_leaf": 2
  },
  "metrics": {
    "r2_score": 0.9727,
    "mae": 10.34,
    "rmse": 15.82
  },
  "feature_names": [
    "año", "mes", "mes_sin", "mes_cos", "trimestre",
    "cat_Blusas", "cat_Vestidos", "cat_Jeans", "cat_Jackets"
  ],
  "categories": ["Blusas", "Vestidos", "Jeans", "Jackets"],
  "training_data": {
    "months_back": 36,
    "total_records": 140,
    "date_range": "2023-01-01 to 2025-11-11"
  }
}
```

---

### 1.3. PredictionService

**Ubicación:** `apps/ai/services/prediction.py`

**Responsabilidad:** Cargar modelo y generar predicciones para el frontend

#### Métodos Principales:

##### `load_model(model_path=None)`

**Propósito:** Cargar modelo entrenado desde disco

**Input:**
```python
model_path: str (opcional)
# Si no se proporciona, carga el modelo más reciente
```

**Proceso:**
```python
import joblib
import json
from pathlib import Path

# 1. Determinar path del modelo
if not model_path:
    models_dir = Path('models/')
    model_files = sorted(models_dir.glob('ventas_model_*.pkl'))
    model_path = model_files[-1]  # Más reciente

# 2. Cargar modelo
model = joblib.load(model_path)

# 3. Cargar metadata
metadata_path = model_path.with_suffix('').with_suffix('.json')  # .pkl → .json
with open(metadata_path, 'r') as f:
    metadata = json.load(f)

# 4. Validar integridad
assert model is not None, "Modelo no pudo cargarse"
assert metadata['model_type'] == 'RandomForestRegressor'
```

**Output:**
```python
{
    'model': RandomForestRegressor (cargado),
    'metadata': dict (metadata del modelo)
}
```

---

##### `predict_next_n_months(n_months=3, categories=None)`

**Propósito:** Generar predicciones para los próximos N meses

**Input:**
```python
n_months: int = 3  # Número de meses a predecir
categories: list = None  # Si None, predice todas las categorías
```

**Proceso:**

**Paso 1: Determinar período de predicción**
```python
from datetime import datetime
from dateutil.relativedelta import relativedelta

hoy = datetime.now()
primer_mes_futuro = hoy + relativedelta(months=1)

periodos = [
    primer_mes_futuro + relativedelta(months=i)
    for i in range(n_months)
]

# Ejemplo (hoy = 11-Nov-2025):
# periodos = [Dic 2025, Ene 2026, Feb 2026]
```

**Paso 2: Preparar features de entrada**
```python
import pandas as pd
import numpy as np

categorias = categories or ['Blusas', 'Vestidos', 'Jeans', 'Jackets']

features_input = []
for periodo in periodos:
    año = periodo.year
    mes = periodo.month
    
    for categoria in categorias:
        # Crear feature vector
        row = {
            'año': año,
            'mes': mes,
            'mes_sin': np.sin(2 * np.pi * mes / 12),
            'mes_cos': np.cos(2 * np.pi * mes / 12),
            'trimestre': (mes - 1) // 3 + 1,
            'cat_Blusas': 1 if categoria == 'Blusas' else 0,
            'cat_Vestidos': 1 if categoria == 'Vestidos' else 0,
            'cat_Jeans': 1 if categoria == 'Jeans' else 0,
            'cat_Jackets': 1 if categoria == 'Jackets' else 0
        }
        features_input.append(row)

X_future = pd.DataFrame(features_input)
```

**Paso 3: Predecir**
```python
model = self.load_model()['model']
predictions = model.predict(X_future)

# predictions = [638.2, 149.1, 298.4, 143.2, 175.3, ...]
```

**Paso 4: Formatear resultados**
```python
results = []
idx = 0
for periodo in periodos:
    for categoria in categorias:
        results.append({
            'año': periodo.year,
            'mes': periodo.month,
            'periodo': periodo.strftime('%b %Y'),  # 'Dic 2025'
            'categoria': categoria,
            'cantidad_predicha': round(predictions[idx]),
            'confianza': 'Alta' if metadata['r2_score'] > 0.90 else 'Media'
        })
        idx += 1
```

**Output:**
```python
[
    {
        'año': 2025,
        'mes': 12,
        'periodo': 'Dic 2025',
        'categoria': 'Blusas',
        'cantidad_predicha': 638,
        'confianza': 'Alta'
    },
    {
        'año': 2025,
        'mes': 12,
        'periodo': 'Dic 2025',
        'categoria': 'Vestidos',
        'cantidad_predicha': 149,
        'confianza': 'Alta'
    },
    # ... (12 registros para 3 meses × 4 categorías)
]
```

---

##### `get_dashboard_data(historic_months=12, prediction_months=3)`

**Propósito:** Generar todo el data payload para el dashboard frontend

**Input:**
```python
historic_months: int = 12  # Meses históricos a incluir
prediction_months: int = 3  # Meses a predecir
```

**Proceso:**

**Paso 1: Datos históricos**
```python
data_service = DataPreparationService()
df_historical = data_service.get_historical_sales_data(historic_months)

# Agregar a nivel mensual (sumar todas las categorías)
historical_totals = df_historical.groupby(['año', 'mes']).agg({
    'cantidad_vendida': 'sum'
}).reset_index()
```

**Paso 2: Predicciones**
```python
predictions = self.predict_next_n_months(prediction_months)
```

**Paso 3: Calcular métricas clave**
```python
total_predicho = sum(p['cantidad_predicha'] for p in predictions)
promedio_mensual = total_predicho / prediction_months

ultimo_historico = historical_totals.iloc[-1]['cantidad_vendida']
primer_predicho = sum(
    p['cantidad_predicha'] 
    for p in predictions 
    if p['mes'] == predictions[0]['mes']
)
tendencia = ((primer_predicho - ultimo_historico) / ultimo_historico) * 100
```

**Output (JSON para frontend):**
```python
{
    "model_info": {
        "version": "v1.0_20251111_150456",
        "trained_at": "2025-11-11T15:04:56",
        "r2_score": 0.9727,
        "mae": 10.34
    },
    "key_metrics": {
        "total_predicted": 2199,
        "average_monthly": 733,
        "trend_percentage": -10.3,
        "confidence": "Alta"
    },
    "historical_data": [
        {"period": "Nov 2024", "total": 1267},
        {"period": "Dic 2024", "total": 1254},
        {"period": "Ene 2025", "total": 425},
        # ... 12 meses
    ],
    "predictions": [
        {
            "año": 2025,
            "mes": 12,
            "periodo": "Dic 2025",
            "categoria": "Blusas",
            "cantidad_predicha": 638,
            "confianza": "Alta"
        },
        # ... todas las predicciones
    ],
    "predictions_by_category": {
        "Blusas": [
            {"periodo": "Dic 2025", "cantidad": 638},
            {"periodo": "Ene 2026", "cantidad": 175},
            {"periodo": "Feb 2026", "cantidad": 263}
        ],
        "Vestidos": [...],
        "Jeans": [...],
        "Jackets": [...]
    }
}
```

---

## 2. Capa de Vistas (Views / Controllers)

**Ubicación:** `apps/ai/views.py`

### AIModelViewSet

**Responsabilidad:** Exponer endpoints REST para el frontend

#### Endpoints:

##### `GET /api/ai/dashboard/`

**Query Parameters:**
```
?historic_months=12
&prediction_months=3
```

**Respuesta:**
```json
{
    "model_info": {...},
    "key_metrics": {...},
    "historical_data": [...],
    "predictions": [...]
}
```

##### `POST /api/ai/train/`

**Body:**
```json
{
    "months_back": 36,
    "test_size": 0.2
}
```

**Respuesta:**
```json
{
    "success": true,
    "model_version": "v1.0_20251111_150456",
    "metrics": {
        "r2_score": 0.9727,
        "mae": 10.34,
        "rmse": 15.82
    },
    "message": "Modelo entrenado exitosamente"
}
```

---

## 3. Flujo de Trabajo Completo

### Flujo 1: Entrenamiento Inicial

```
1. Usuario ejecuta: python manage.py train_model --months 36
   ↓
2. ModelTrainingService.train_model(months_back=36)
   ↓
3. DataPreparationService.get_historical_sales_data(36)
   - Query a PostgreSQL
   - Agregar a nivel Año-Mes-Categoría
   ↓
4. DataPreparationService.prepare_training_data(df)
   - Feature engineering
   - One-Hot Encoding
   - Componentes trigonométricas
   ↓
5. RandomForestRegressor.fit(X_train, y_train)
   - Entrenar 100 árboles
   - Evaluar en test set
   ↓
6. ModelTrainingService.save_model()
   - Guardar ventas_model_v1.0_20251111.pkl
   - Guardar metadata.json
   ↓
7. ✅ Modelo listo para predicciones
```

### Flujo 2: Predicción en Tiempo Real (Dashboard)

```
1. Frontend hace: GET /api/ai/dashboard/?prediction_months=3
   ↓
2. AIModelViewSet.dashboard_view()
   ↓
3. PredictionService.get_dashboard_data(prediction_months=3)
   ↓
4. PredictionService.load_model()
   - Cargar ventas_model_v1.0_20251111.pkl
   ↓
5. PredictionService.predict_next_n_months(3)
   - Preparar features para Dic, Ene, Feb
   - model.predict(X_future)
   ↓
6. Formatear JSON response
   ↓
7. ← Retornar al frontend
   ↓
8. Frontend renderiza dashboard con Recharts
```

---

## 4. Gestión de Modelos (Model Versioning)

### Estructura de Archivos:

```
models/
├── ventas_model_v1.0_20251111_150456.pkl
├── ventas_model_v1.0_20251111_150456_metadata.json
├── ventas_model_v1.1_20260115_103022.pkl
├── ventas_model_v1.1_20260115_103022_metadata.json
└── ...
```

### Estrategia de Versionado:

**Versión Semántica:**
```
v[MAJOR].[MINOR]_[TIMESTAMP]

MAJOR: Cambio de algoritmo (ej. Random Forest → XGBoost)
MINOR: Cambio de features o hiperparámetros
TIMESTAMP: Fecha/hora del entrenamiento
```

**Ejemplo:**
```
v1.0_20251111_150456 → Primera versión, Random Forest, 11-Nov-2025 15:04
v1.1_20260115_103022 → Misma arquitectura, features mejoradas, 15-Ene-2026
v2.0_20260301_140000 → Cambio a XGBoost, 1-Mar-2026
```

### Rollback de Modelo:

Si un modelo nuevo tiene mal rendimiento:
```python
# 1. Identificar modelo anterior
model_path = 'models/ventas_model_v1.0_20251111_150456.pkl'

# 2. Cambiar variable de entorno o config
settings.ACTIVE_MODEL_PATH = model_path

# 3. PredictionService cargará el modelo especificado
```

---

## 5. Escalabilidad y Mejoras Futuras

### Optimizaciones Actuales:

1. **Caching de modelo:**
   ```python
   # El modelo se carga una vez y se mantiene en memoria
   _cached_model = None
   
   def load_model():
       global _cached_model
       if _cached_model is None:
           _cached_model = joblib.load('models/...')
       return _cached_model
   ```

2. **Predicciones batch:**
   ```python
   # Predecir 3 meses × 4 categorías = 12 predicciones en una sola llamada
   predictions = model.predict(X_future)  # X_future tiene 12 filas
   ```

### Mejoras Futuras:

1. **Predicciones en tiempo real con Celery:**
   ```python
   @shared_task
   def async_train_model(months_back):
       service = ModelTrainingService()
       service.train_model(months_back)
   ```

2. **A/B Testing de modelos:**
   ```python
   # Comparar modelo antiguo vs nuevo
   predictions_v1 = model_v1.predict(X)
   predictions_v2 = model_v2.predict(X)
   # Elegir el de menor MAE en datos recientes
   ```

3. **Monitoreo de drift:**
   ```python
   # Detectar si el modelo está perdiendo precisión
   if mae_actual > mae_entrenamiento * 1.5:
       send_alert("Modelo necesita reentrenamiento")
   ```

---

## 6. Seguridad y Validación

### Validaciones Implementadas:

1. **Validación de inputs:**
   ```python
   if months_back < 12 or months_back > 60:
       raise ValueError("months_back debe estar entre 12 y 60")
   
   if prediction_months < 1 or prediction_months > 12:
       raise ValueError("prediction_months debe estar entre 1 y 12")
   ```

2. **Validación de datos:**
   ```python
   # Detectar anomalías en datos históricos
   if cantidad_vendida < 0:
       raise ValueError("Cantidad no puede ser negativa")
   
   if cantidad_vendida > 10000:
       logger.warning(f"Cantidad inusualmente alta: {cantidad_vendida}")
   ```

3. **Control de acceso:**
   ```python
   # Solo usuarios autenticados pueden acceder a endpoints de IA
   permission_classes = [IsAuthenticated, HasAIPermission]
   ```

---

## 7. Testing

### Tests Implementados:

```python
# tests/test_data_preparation.py
def test_get_historical_sales_data():
    service = DataPreparationService()
    df = service.get_historical_sales_data(months_back=12)
    assert df.shape[0] > 0
    assert 'cantidad_vendida' in df.columns

# tests/test_model_training.py
def test_train_model():
    service = ModelTrainingService()
    result = service.train_model(months_back=36)
    assert result['metrics']['r2_score'] > 0.80

# tests/test_prediction.py
def test_predict_next_n_months():
    service = PredictionService()
    predictions = service.predict_next_n_months(n_months=3)
    assert len(predictions) == 12  # 3 meses × 4 categorías
```

---

## 8. Conclusión

La arquitectura del módulo de IA está diseñada para:

✅ **Separación de responsabilidades** (Service Layer Pattern)  
✅ **Fácil mantenimiento** (cada servicio tiene una función clara)  
✅ **Escalabilidad** (fácil agregar nuevas categorías o features)  
✅ **Testeable** (cada servicio puede ser testeado independientemente)  
✅ **Versionado robusto** (modelos con timestamp y metadata)  

**La arquitectura soporta el crecimiento del sistema y facilita futuras mejoras.**

---

**Última actualización:** 11 de Noviembre de 2025  
**Versión:** 1.0  
**Próxima revisión:** Enero 2026
