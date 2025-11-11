# 📡 Guía Completa de Endpoints de IA

Esta guía explica **TODOS** los endpoints de IA, qué hace cada uno, cuándo usarlos y ejemplos prácticos.

---

## 📋 Índice

1. [Resumen Rápido](#-resumen-rápido)
2. [Entrenamiento del Modelo](#-entrenamiento-del-modelo)
3. [Obtener Dashboard Completo](#-obtener-dashboard-completo)
4. [Generar Predicciones](#-generar-predicciones)
5. [Flujo de Trabajo Recomendado](#-flujo-de-trabajo-recomendado)
6. [Preguntas Frecuentes (FAQ)](#-preguntas-frecuentes-faq)

---

## 🎯 Resumen Rápido

| Endpoint | Método | ¿Qué hace? | ¿Cuándo usarlo? |
|----------|--------|------------|-----------------|
| `/api/ai/dashboard/` | `GET` | Muestra predicciones ya guardadas + datos históricos | Siempre que quieras ver el dashboard de IA |
| `/api/ai/predictions/sales-forecast/` | `POST` | **Genera** nuevas predicciones y las guarda | Cuando quieras actualizar las predicciones |
| `python manage.py train_model` | Comando | Entrena el modelo con datos reales | Cuando tengas nuevos datos de ventas |

---

## 🤖 Entrenamiento del Modelo

### **Comando: `python manage.py train_model`**

**¿Qué hace?**
- Lee datos históricos de ventas desde la base de datos
- Entrena un modelo Random Forest con esos datos
- Guarda el modelo entrenado en `models/`
- Marca el modelo como **"activo"** (desactiva modelos anteriores)

**¿Cuándo usarlo?**
- Al inicio del proyecto (para crear el primer modelo)
- Cuando tengas **nuevos datos de ventas** importantes (cada mes, cada 3 meses, etc.)
- Si quieres **cambiar la cantidad de datos** para entrenamiento

**Opciones disponibles:**

```bash
# Usar 36 meses (3 años) de datos - RECOMENDADO
python manage.py train_model --months 36

# Usar 24 meses (2 años)
python manage.py train_model --months 24

# Usar más árboles para mejor precisión (más lento)
python manage.py train_model --months 36 --estimators 200 --depth 15

# Ver todas las opciones
python manage.py train_model --help
```

**Respuesta esperada:**

```
============================================================
🤖 ENTRENAMIENTO DEL MODELO DE PREDICCIÓN DE VENTAS
============================================================

⚙️  Parámetros:
   - Meses de datos: 36 (3.0 años)
   - N° de árboles: 100
   - Profundidad máxima: 10
   - Test size: 0.2

📊 Dataset completo: 148 registros (37 meses × 4 categorías)
✅ Train: 118 samples | Test: 30 samples

📈 Métricas (Test Set):
   MAE:  10.34
   RMSE: 24.47
   R²:   0.9727  <-- Esto debe ser > 0.70

✅ MODELO ENTRENADO EXITOSAMENTE
📦 Modelo ID: 53ade523-6983-4bb7-99a2-6edb35025eb7
```

**¿Qué significa cada métrica?**
- **R² (R-cuadrado)**: Qué tan bien el modelo explica los datos (0 = malo, 1 = perfecto). **Objetivo: > 0.70**
- **MAE (Error Absoluto Medio)**: Cuánto se equivoca en promedio (en unidades vendidas). **Menor es mejor**
- **RMSE (Raíz del Error Cuadrático Medio)**: Penaliza errores grandes. **Menor es mejor**

---

## 📊 Obtener Dashboard Completo

### **GET `/api/ai/dashboard/`**

**¿Qué hace?**
- Obtiene datos históricos de ventas (últimos N meses)
- Obtiene las **predicciones ya guardadas** en la base de datos
- Obtiene productos más vendidos
- Obtiene ventas por categoría
- **NO genera nuevas predicciones** (solo muestra las existentes)

**¿Cuándo usarlo?**
- Para mostrar el dashboard de IA en el frontend
- Cuando quieras ver el estado actual sin generar nuevas predicciones
- **Es el endpoint principal del dashboard**

**Parámetros:**

| Parámetro | Tipo | Descripción | Valor por defecto |
|-----------|------|-------------|-------------------|
| `months_back` | int | Meses de histórico a mostrar | 6 |
| `months_forward` | int | Meses de predicciones a mostrar | 3 |

**Ejemplos:**

```bash
# Ver últimos 6 meses + próximos 3 meses (por defecto)
GET /api/ai/dashboard/

# Ver últimos 12 meses + próximos 6 meses
GET /api/ai/dashboard/?months_back=12&months_forward=6

# Ver TODO el histórico de 3 años
GET /api/ai/dashboard/?months_back=36&months_forward=3
```

**Respuesta:**

```json
{
  "historical": [
    {
      "periodo": "2025-05",
      "cantidad_vendida": 181,
      "total_ventas": 12450
    },
    ...
  ],
  "predictions": [
    {
      "periodo": "2025-12",
      "ventas_predichas": 58.5,
      "categoria": "Total",
      "mes": 12,
      "año": 2025
    },
    ...
  ],
  "predictions_by_category": [
    {
      "periodo": "2025-12",
      "ventas_predichas": 58.5,
      "categoria": "Blusas",
      "prediccion_id": "18952148-df4c-487f-be86-39b544373c3f",
      "confianza": "Alta"
    },
    ...
  ],
  "top_products": [...],
  "category_sales": [...],
  "model_info": {
    "version": "v1.0_20251111_150456",
    "trained_at": "2025-11-11T18:26:48+00:00",
    "r2_score": 0.9727,
    "mae": 10.34
  }
}
```

---

## 🔮 Generar Predicciones

### **POST `/api/ai/predictions/sales-forecast/`**

**¿Qué hace?**
- Usa el modelo activo para **generar nuevas predicciones**
- **Guarda las predicciones** en la base de datos
- Calcula predicciones para los próximos N meses
- **Sobrescribe predicciones anteriores** para los mismos períodos

**¿Cuándo usarlo?**
- Cuando quieras **actualizar las predicciones** con datos nuevos
- Después de entrenar un nuevo modelo
- Cuando cambies parámetros y quieras ver nuevas predicciones

**Parámetros:**

| Parámetro | Tipo | Descripción | Valor por defecto |
|-----------|------|-------------|-------------------|
| `months_forward` | int | Meses a predecir hacia el futuro | 3 |

**Ejemplo:**

```bash
# Generar predicciones para los próximos 3 meses
POST /api/ai/predictions/sales-forecast/
{
  "months_forward": 3
}

# Generar predicciones para los próximos 6 meses
POST /api/ai/predictions/sales-forecast/
{
  "months_forward": 6
}
```

**Respuesta:**

```json
{
  "message": "Predicciones generadas exitosamente",
  "model_version": "v1.0_20251111_150456",
  "predictions_count": 12,
  "predictions": [
    {
      "periodo": "2025-12",
      "ventas_predichas": 58.5,
      "categoria": "Blusas",
      "mes": 12,
      "año": 2025,
      "confianza": "Alta"
    },
    ...
  ]
}
```

---

## 🔄 Flujo de Trabajo Recomendado

### **Escenario 1: Primera vez configurando IA**

```bash
# 1. Entrenar el modelo con 3 años de datos
python manage.py train_model --months 36

# 2. Generar predicciones para los próximos 3 meses
POST /api/ai/predictions/sales-forecast/
{
  "months_forward": 3
}

# 3. Ver el dashboard completo
GET /api/ai/dashboard/?months_back=36&months_forward=3
```

### **Escenario 2: Actualización mensual**

```bash
# Cada mes, después de cerrar ventas:

# 1. Re-entrenar modelo con datos actualizados
python manage.py train_model --months 36

# 2. Generar nuevas predicciones
POST /api/ai/predictions/sales-forecast/
{
  "months_forward": 3
}

# 3. El frontend automáticamente mostrará las nuevas predicciones
GET /api/ai/dashboard/
```

### **Escenario 3: Solo ver el dashboard (uso diario)**

```bash
# NO necesitas generar predicciones cada vez
# Solo obtén el dashboard con las predicciones ya guardadas

GET /api/ai/dashboard/?months_back=12&months_forward=3
```

---

## ❓ Preguntas Frecuentes (FAQ)

### **1. ¿Por qué el modelo solo usó 148 registros y no 3 años completos?**

**Respuesta:** El modelo **agrupa los datos por mes y categoría**. Con 3 años (36 meses) × 4 categorías = 144 registros teóricos. Si aparecen 148, es porque el rango incluye algunos meses extra por cómo se calcula el período.

Cada registro representa: **"Cantidad vendida de X categoría en Y mes"**.

Ejemplo:
- Registro 1: Blusas vendidas en Enero 2023
- Registro 2: Vestidos vendidos en Enero 2023
- Registro 3: Jeans vendidos en Enero 2023
- Registro 4: Jackets vendidos en Enero 2023
- Registro 5: Blusas vendidas en Febrero 2023
- ...

### **2. ¿Qué es "modelo activo"?**

**Respuesta:** Es el modelo Random Forest **más reciente** que está siendo usado para generar predicciones.

- Solo puede haber **1 modelo activo** a la vez
- Cuando entrenas un nuevo modelo, automáticamente se marca como activo
- Los modelos antiguos se quedan guardados pero inactivos

Puedes ver el modelo activo en:
- **Admin Django:** `/admin/ai/mlmodel/`
- **Dashboard API:** `GET /api/ai/dashboard/` → `model_info`

### **3. ¿Cuál es la diferencia entre `train_model` y `sales-forecast`?**

| | `train_model` | `POST sales-forecast` |
|---|---|---|
| **¿Qué hace?** | Entrena el modelo con datos históricos | Usa el modelo para predecir futuro |
| **¿Cuándo?** | Cuando tengas nuevos datos de ventas | Cuando quieras actualizar predicciones |
| **¿Con qué frecuencia?** | Mensual / Trimestral | Cuando lo necesites |
| **Salida** | Modelo `.pkl` guardado | Predicciones en BD |

### **4. ¿Por qué algunas categorías tienen importancia 0.0001?**

**Respuesta:** Significa que **esa categoría no aporta mucho** a la predicción comparada con otros factores. Mira este ejemplo:

```
num_transacciones: 0.9738  ← Factor MÁS importante
precio_promedio: 0.0078     ← Poco importante
cat_Vestidos: 0.0000        ← Casi no importa
```

Esto es **normal**. Significa que el **número de transacciones** es mucho más predictivo que la categoría específica.

### **5. ¿Cómo decido cuántos meses usar para entrenar?**

**Recomendaciones:**

| Situación | Meses recomendados | Comando |
|-----------|-------------------|---------|
| **Datos estables, pocas fluctuaciones** | 24 meses (2 años) | `--months 24` |
| **Negocio con estacionalidad clara** | **36 meses (3 años)** ✅ | `--months 36` |
| **Negocio muy nuevo** | 12-18 meses | `--months 12` |
| **Experimentar** | Prueba con diferentes valores | `--months 18` / `--months 30` |

### **6. ¿Qué significa R² = 0.9727?**

**Respuesta:** Significa que tu modelo explica el **97.27%** de la variabilidad en las ventas. ¡Es **excelente**!

**Escala de calidad:**
- **< 0.50:** Malo 😞
- **0.50 - 0.70:** Aceptable 😐
- **0.70 - 0.85:** Bueno ✅
- **0.85 - 0.95:** Muy bueno 🌟
- **> 0.95:** Excelente 🎉 ← Tú estás aquí

### **7. ¿Cuándo debo re-entrenar el modelo?**

**Respuesta:** Re-entrena cuando:
- ✅ Cada mes (después de cerrar ventas)
- ✅ Cuando agregas **muchos nuevos productos**
- ✅ Cuando cambian **tendencias de mercado**
- ✅ Cuando la **precisión baja** (R² < 0.70)
- ❌ NO necesitas re-entrenar cada vez que consultas el dashboard

### **8. ¿Las predicciones son en unidades o en dinero?**

**Respuesta:** Las predicciones son en **unidades vendidas** (cantidad de productos).

Si el modelo predice `ventas_predichas: 58.5`, significa **~59 unidades** de esa categoría en ese mes.

### **9. ¿Qué es "confianza: Alta"?**

**Respuesta:** Es una estimación de qué tan confiable es la predicción:

- **Alta:** R² del modelo > 0.80
- **Media:** R² entre 0.60 - 0.80
- **Baja:** R² < 0.60

### **10. ¿Puedo tener múltiples modelos activos?**

**Respuesta:** No. Solo 1 modelo puede estar activo. Pero todos los modelos anteriores se quedan guardados en:
- Base de datos: Tabla `ai_mlmodel`
- Archivos: Carpeta `models/`

Puedes **activar manualmente** un modelo antiguo desde el admin de Django si es necesario.

---

## 🎯 Resumen Ejecutivo

**Para uso diario:**
```bash
GET /api/ai/dashboard/
```

**Para actualizar predicciones:**
```bash
POST /api/ai/predictions/sales-forecast/
{
  "months_forward": 3
}
```

**Para mejorar el modelo (mensual):**
```bash
python manage.py train_model --months 36
```

---

## 📚 Recursos Adicionales

- **Documentación técnica:** `AI_TECNICA_DETALLADA.md`
- **Guía para no técnicos:** `AI_EXPLICACION_SIMPLE.md`
- **Implementación completa:** `AI_IMPLEMENTACION_COMPLETA.md`
- **Defensa para ingenieros:** `AI_DEFENSA_INGENIERO.md`

---

**Última actualización:** 11 de noviembre de 2025
