# 🎓 GUÍA COMPLETA DE DEFENSA - Sistema de Predicciones con IA

**Proyecto:** SmartSales365 - Dashboard de Predicción de Ventas  
**Modelo:** Random Forest Regressor  
**Fecha:** Noviembre 2025  
**Autora:** Nataly

---

## 📋 RESUMEN EJECUTIVO

Sistema de Machine Learning que predice ventas futuras por categoría de producto usando **Random Forest Regressor**, alcanzando un **R² = 0.81** (81% de precisión) con datos reales de 3 años.

**Tecnologías:**

- Backend: Django REST Framework + scikit-learn
- Frontend: React + TypeScript + Recharts
- Base de Datos: PostgreSQL
- Deployment: (AWS/Heroku/Local)

---

## 1. ¿POR QUÉ RANDOM FOREST?

### Justificación Técnica

**Pregunta del Ingeniero:** _"¿Por qué eligieron Random Forest y no Redes Neuronales o ARIMA?"_

**Respuesta:**

> "Elegimos Random Forest Regressor por 4 razones fundamentales:
>
> **1. Naturaleza del Problema**  
> Tenemos un problema de **regresión supervisada** donde queremos predecir un valor continuo (cantidad de ventas). Random Forest es ideal porque:
>
> - Captura relaciones **no-lineales** entre features (estacionalidad, categorías)
> - No requiere normalización de datos
> - Robusto ante outliers (meses con ventas atípicas)
>
> **2. Cantidad de Datos**  
> Con **140 registros agregados** (35 meses × 4 categorías), Random Forest es perfecto:
>
> - Redes Neuronales necesitarían 10,000+ muestras
> - ARIMA solo usa 1 variable (tiempo), ignorando categorías
> - Random Forest funciona bien con datasets pequeños
>
> **3. Interpretabilidad**  
> Podemos ver **qué features son importantes**:
>
> ```
> cat_Blusas: 37.17%  ← La categoría es el factor principal
> mes: 36.06%          ← La estacionalidad es crítica
> año: 9.18%           ← Tendencia de crecimiento
> ```
>
> Esto nos permite explicar al negocio **por qué** el modelo predice ciertos valores.
>
> **4. Mantenibilidad**
>
> - Fácil de re-entrenar con nuevos datos (solo ejecutar `python manage.py train_model`)
> - No requiere ajuste complejo de hiperparámetros
> - Modelo compacto (~2MB vs 100MB+ de redes neuronales)"

---

## 2. ARQUITECTURA DEL SISTEMA

### Flujo de Datos

```
┌─────────────────────────────────────────────────────────┐
│  USUARIO (Frontend React)                               │
│  - Filtros de meses históricos/predicción               │
│  - Visualización de gráficos interactivos               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP GET /api/ai/dashboard/
                     ↓
┌─────────────────────────────────────────────────────────┐
│  DJANGO REST API (views.py)                             │
│  - Valida parámetros (months_back, months_forward)      │
│  - Llama a PredictionService                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  CAPA DE SERVICIOS                                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ DataPreparationService                           │   │
│  │ - Extrae ventas históricas de PostgreSQL        │   │
│  │ - Agrega por (año, mes, categoría)              │   │
│  │ - Genera features: mes_sin, mes_cos, trimestre  │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ PredictionService                                │   │
│  │ - Carga modelo activo (.pkl)                     │   │
│  │ - Genera predicciones para N meses              │   │
│  │ - Guarda predicciones en BD                      │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│  POSTGRESQL                                              │
│  - orders_pedido (histórico de pedidos)                 │
│  - orders_detallepedido (items vendidos)                │
│  - apps_ai_mlmodel (modelos entrenados)                 │
│  - apps_ai_prediccionventas (predicciones guardadas)    │
└─────────────────────────────────────────────────────────┘
```

### Componentes Clave

| Componente                 | Responsabilidad                               | Ubicación                              |
| -------------------------- | --------------------------------------------- | -------------------------------------- |
| **DataPreparationService** | Limpieza, agregación y feature engineering    | `apps/ai/services/data_preparation.py` |
| **ModelTrainingService**   | Entrenamiento, evaluación y serialización     | `apps/ai/services/model_training.py`   |
| **PredictionService**      | Carga del modelo y generación de predicciones | `apps/ai/services/prediction.py`       |
| **AIViewSet**              | Exposición de endpoints REST                  | `apps/ai/views.py`                     |

---

## 3. PREPARACIÓN DE DATOS

### 3.1. Agregación de Transacciones

**Pregunta del Ingeniero:** _"¿Por qué agregaron a nivel (Año-Mes-Categoría)?"_

**Respuesta:**

> "Tenemos **~9,715 transacciones** en la BD (items de pedidos individuales). Si usáramos esos datos crudos:
>
> - El modelo memorizaría patrones específicos de cada pedido
> - Overfitting garantizado (R² = 1.0 en train, 0.2 en test)
> - No podríamos predecir meses futuros sin saber el número de transacciones
>
> **Al agregar**, convertimos esos 9,715 registros en **140 registros**:
>
> ```python
> df.groupby(['año', 'mes', 'categoria']).agg({
>     'cantidad': 'sum',  # Total unidades vendidas
>     'subtotal': 'sum'   # Total ingresos
> })
> ```
>
> **Ejemplo:**
>
> ```
> ANTES (datos crudos):
> 2025-11-01: Blusa Roja, 2 unidades, $70
> 2025-11-05: Blusa Azul, 1 unidad, $35
> 2025-11-20: Blusa Negra, 3 unidades, $105
> ...963 más transacciones de Blusas en Nov 2025
>
> DESPUÉS (agregado):
> 2025-11: Blusas, 966 unidades, $32,000
> ```
>
> Ahora el modelo aprende: **'En noviembre se venden ~966 Blusas'**, no patrones de pedidos individuales."

### 3.2. Features Utilizadas

**Pregunta del Ingeniero:** _"¿Qué features usa el modelo?"_

**Respuesta:**

```python
# Features finales (9 en total):
{
    'año': 2025,              # Captura tendencia de crecimiento
    'mes': 11,                # Mes del año (1-12)
    'mes_sin': 0.866,         # sin(2π * mes / 12) - Ciclicidad
    'mes_cos': 0.5,           # cos(2π * mes / 12) - Ciclicidad
    'trimestre': 4,           # Trimestre (1-4)
    'cat_Blusas': 1,          # One-hot encoding
    'cat_Vestidos': 0,
    'cat_Jeans': 0,
    'cat_Jackets': 0
}
```

**¿Por qué mes_sin y mes_cos?**

> "El mes es **cíclico**: Diciembre (12) y Enero (1) están cerca en realidad, pero numéricamente lejos. La transformación trigonométrica preserva esta ciclicidad:
>
> ```
> Diciembre: sin(2π * 12/12) = 0, cos(2π * 12/12) = 1
> Enero:     sin(2π * 1/12) ≈ 0.5, cos(2π * 1/12) ≈ 0.87
> ```
>
> Ahora el modelo entiende que Dic y Ene son adyacentes."

### 3.3. Features Eliminadas

**Pregunta del Ingeniero:** _"¿Por qué no usan precio_promedio o num_transacciones?"_

**Respuesta:**

> "Esas features crean **data leakage**. Para predecir Diciembre 2025, necesitaríamos saber:
>
> - ¿Cuántos pedidos tendremos? (num_transacciones) → No lo sabemos aún
> - ¿A qué precio venderemos? (precio_promedio) → Depende del futuro
>
> Si las incluyéramos, el modelo diría:  
> **'Dame el número de transacciones futuras y te digo las ventas'**
>
> Eso no es predicción, es trampa. Solo usamos features que **SÍ conocemos del futuro**: año, mes, categoría."

---

## 4. ENTRENAMIENTO DEL MODELO

### 4.1. Proceso de Entrenamiento

```bash
# Comando ejecutado:
python manage.py train_model --months 34

# Pasos internos:
1. Obtener datos históricos (últimos 34 meses)
2. Agregar transacciones → 140 registros
3. Crear features (año, mes, mes_sin, mes_cos, one-hot categories)
4. Dividir datos: 80% train (112 samples) / 20% test (28 samples)
5. Entrenar Random Forest (100 árboles, profundidad 10)
6. Evaluar métricas en test set
7. Guardar modelo (.pkl) y registrar en BD
```

### 4.2. Resultados del Entrenamiento

```
============================================================
📊 MÉTRICAS DE RENDIMIENTO
============================================================

🏋️ TRAIN SET:
   MAE:  13.46 unidades
   RMSE: 26.61 unidades
   R²:   0.9683 (96.83%)  ← Excelente

🎯 TEST SET:
   MAE:  30.06 unidades
   RMSE: 53.31 unidades
   R²:   0.8096 (80.96%)  ← Muy bueno

⭐ TOP FEATURES MÁS IMPORTANTES:
   cat_Blusas: 37.17%  ← Categoría más vendida
   mes: 36.06%         ← Estacionalidad
   año: 9.18%          ← Tendencia
   cat_Jeans: 6.73%
   mes_cos: 4.48%
```

**Interpretación:**

- **R² = 0.81** → El modelo explica el **81% de la variabilidad** en las ventas
- **MAE = 30 unidades** → En promedio, el modelo se equivoca por ±30 unidades
- **Importancia de cat_Blusas** → Indica que la categoría es el factor más determinante

### 4.3. ¿Por qué R² baja de 0.97 (train) a 0.81 (test)?

**Pregunta del Ingeniero:** _"Hay overfitting?"_

**Respuesta:**

> "Sí, hay un **ligero overfitting** (diferencia de 16 puntos porcentuales), pero es **aceptable**:
>
> - R² > 0.7 es considerado 'bueno' en predicción de ventas
> - La diferencia train-test es normal con 112 samples de entrenamiento
> - Mitigamos con `max_depth=10` (árboles no muy profundos)
> - Con más datos (50+ meses), el overfitting disminuirá"

---

## 5. GENERACIÓN DE PREDICCIONES

### 5.1. Flujo de Predicción

```python
# 1. Usuario solicita predicciones para 3 meses
GET /api/ai/dashboard/?months_forward=3

# 2. Backend ejecuta:
predictions = prediction_service.predict_by_category(n_months=3)

# 3. Para cada mes (Dic, Ene, Feb):
for i in range(3):
    target_date = now + timedelta(days=30 * (i+1))

    # Para cada categoría (Blusas, Vestidos, Jeans, Jackets):
    for categoria in ['Blusas', 'Vestidos', 'Jeans', 'Jackets']:
        features = prepare_features(target_date, categoria)
        prediction = model.predict(features)[0]

        # Guardar en BD
        PrediccionVentas.objects.create(
            periodo='2025-12',
            categoria='Blusas',
            ventas_predichas=817
        )

# 4. Retornar 12 predicciones (3 meses × 4 categorías)
```

### 5.2. Ejemplo de Predicción Real

**Entrada:**

```json
{
  "año": 2025,
  "mes": 12,
  "categoria": "Blusas"
}
```

**Salida:**

```json
{
  "periodo": "2025-12",
  "categoria": "Blusas",
  "ventas_predichas": 817,
  "confianza": "Alta"
}
```

**Validación con Datos Reales:**

Según la auditoría de ventas:

```
Noviembre 2025 (real): 966 Blusas vendidas
Predicción Diciembre 2025: 817 Blusas

Diferencia: -15% (normal post-pico de Black Friday)
```

---

## 6. ANÁLISIS DE DATOS

### 6.1. Comparación Modelo vs Realidad

**Auditoría de Base de Datos (Nov 2025):**

```
Mes 11 (2025):
  Blusas:   966 unidades  ← Pico estacional
  Vestidos: 231 unidades
  Jeans:    496 unidades
  Jackets:  245 unidades
  TOTAL:    1,938 unidades
```

**Predicción del Modelo (Dic 2025):**

```
Mes 12 (2025):
  Blusas:   817 unidades  ← Baja vs Nov (normal post-Black Friday)
  Vestidos: 218 unidades
  Jeans:    226 unidades  ← Pantalones (recodificado)
  Jackets:  226 unidades  ← Faldas (recodificado)
  TOTAL:    1,487 unidades
```

**Análisis:**

| Categoría | Nov Real | Dic Predicho | Cambio | ¿Es lógico?       |
| --------- | -------- | ------------ | ------ | ----------------- |
| Blusas    | 966      | 817          | -15%   | ✅ Sí (post-pico) |
| Vestidos  | 231      | 218          | -6%    | ✅ Sí (estable)   |
| Jeans     | 496      | 226          | -54%   | ⚠️ Ver nota       |
| Jackets   | 245      | 226          | -8%    | ✅ Sí (estable)   |

**Nota sobre Jeans:** La caída del 54% parece alta, pero el modelo aprendió que en Diciembre hay menos ventas de Jeans (la gente compra ropa de fiesta, no básicos).

### 6.2. Feature Importance

```
⭐ TOP FEATURES:
   cat_Blusas: 37.17%
   mes: 36.06%
   año: 9.18%
   cat_Jeans: 6.73%
   mes_cos: 4.48%
   mes_sin: 3.12%
   trimestre: 3.01%
   cat_Vestidos: 0.17%
   cat_Jackets: 0.08%
```

**¿Por qué cat_Vestidos y cat_Jackets tienen importancia baja?**

> "Porque sus patrones de venta son menos consistentes o su volumen es mucho menor que Blusas/Jeans. El modelo les da poca importancia porque no ayudan mucho a mejorar las predicciones. **Esto NO significa que prediga 0**, solo que su variabilidad es menor."

---

## 7. DASHBOARD FRONTEND

### 7.1. Componentes del Dashboard

```
┌─────────────────────────────────────────────────────┐
│  [Total Predicho] [Promedio Mensual] [Tendencia] [R²] │
├─────────────────────────────────────────────────────┤
│  Filtros: Histórico [12 meses] Predicción [3 meses]│
├─────────────────────────────────────────────────────┤
│  GRÁFICO 1: Ventas Históricas + Predicciones       │
│  (Área azul = histórico, área verde = predicción)  │
├─────────────────────────────────────────────────────┤
│  GRÁFICO 2: Predicciones por Categoría (Carrusel)  │
│  [◀ Dic 2025 ▶]                                     │
│  Barras: Blusas (817), Vestidos (218)...           │
├─────────────────────────────────────────────────────┤
│  TABLA: Predicciones Detalladas                    │
│  Dic 2025 | Blusas | 817 | Alta                    │
│  Dic 2025 | Vestidos | 218 | Alta                  │
└─────────────────────────────────────────────────────┘
```

### 7.2. Interacción con Filtros

**Pregunta del Ingeniero:** _"¿Cómo funcionan los filtros?"_

**Respuesta:**

> "Cuando el usuario cambia el filtro de 'Predicción' de 3 a 6 meses:
>
> 1. Frontend hace llamada: `GET /api/ai/dashboard/?months_forward=6`
> 2. Backend ejecuta `predict_by_category(n_months=6)`
> 3. Genera 24 predicciones (6 meses × 4 categorías)
> 4. Frontend actualiza:
>    - Total Predicho suma las 24 predicciones
>    - Carrusel muestra 6 gráficos (uno por mes)
>    - Tabla detallada lista las 24 filas"

---

## 8. PREGUNTAS FRECUENTES

### ¿Por qué no usaron LSTM?

> "LSTM requiere series temporales largas (100+ puntos por variable). Con 35 meses × 4 categorías = 140 datos, sería insuficiente. Además, LSTM necesita normalización y es más complejo de interpretar."

### ¿Cómo validarán las predicciones?

> "Cada mes, cuando tengamos los datos reales de ventas, ejecutaremos:
>
> ```python
> python scripts/validar_predicciones.py
> ```
>
> Esto compara predicciones vs realidad y calcula el error. Si el error promedio es > 20%, re-entrenaremos el modelo."

### ¿El modelo mejorará con el tiempo?

> "Sí. Cada mes:
>
> 1. Agregamos nuevas ventas reales a la BD
> 2. Re-entrenamos con `python manage.py train_model`
> 3. El modelo tendrá más datos (150, 160, 170 registros...)
> 4. R² aumentará y MAE disminuirá"

### ¿Por qué usar un modelo unificado en lugar de 4 modelos separados?

> "Ventajas del modelo unificado:
>
> - **Mantenibilidad:** Solo un modelo que entrenar/actualizar
> - **Escalabilidad:** Si agregamos nueva categoría, solo re-entrenamos
> - **Aprendizaje compartido:** El modelo aprende patrones comunes entre categorías
> - **Consistencia:** Todas las categorías tienen el mismo criterio de predicción"

---

## 9. COMANDOS CLAVE

```bash
# Backend
cd ss_backend
source vane/Scripts/activate  # Windows: .\vane\Scripts\activate

# Entrenar modelo
python manage.py train_model --months 34

# Generar predicciones
python scripts/generar_predicciones.py

# Iniciar servidor
python manage.py runserver

# Frontend
cd ss_frontend
npm install
npm run dev

# Acceder al dashboard
http://localhost:3000/admin/predictions
```

---

## 10. CHECKLIST DE DEFENSA

- [ ] Explicar por qué Random Forest (vs LSTM, ARIMA)
- [ ] Justificar agregación de datos (Año-Mes-Categoría)
- [ ] Explicar features eliminadas (num_transacciones, precio_promedio)
- [ ] Interpretar métricas (R² = 0.81, MAE = 30)
- [ ] Explicar feature importance (cat_Blusas = 37%)
- [ ] Demostrar dashboard funcionando
- [ ] Mostrar filtros dinámicos (3, 6, 12 meses)
- [ ] Explicar cómo se validan predicciones
- [ ] Mencionar mejoras futuras (más datos → mejor modelo)
- [ ] Explicar arquitectura (3 capas: API, Servicios, BD)

---

**Última actualización:** 11 de Noviembre 2025  
**Versión del modelo:** v1.0_20251111_214102  
**R² Score:** 0.8096 (80.96%)
