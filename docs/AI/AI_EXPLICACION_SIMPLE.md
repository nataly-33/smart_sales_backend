# 🤖 Sistema de IA Predictiva - Explicación Simple

## ¿Qué es esto?

Este es un sistema de **Inteligencia Artificial** que aprende de las ventas pasadas de tu tienda para **predecir cuánto venderás en el futuro**. Es como tener una bola de cristal, pero basada en matemáticas y datos reales.

---

## 🎯 ¿Para qué sirve?

Imagina que tienes una tienda de ropa. Este sistema te ayuda a:

1. **Predecir ventas futuras**: "El próximo mes probablemente vendas 150 vestidos"
2. **Planificar inventario**: Si sabes que venderás mucho en diciembre, puedes comprar más stock antes
3. **Tomar decisiones**: ¿Qué categoría vende más? ¿Cuándo hacer promociones?
4. **Ver tendencias**: ¿Las ventas están subiendo o bajando?

---

## 🧠 ¿Cómo funciona? (Versión para no técnicos)

### 1. **Aprendizaje del Pasado**

El sistema mira todas tus ventas anteriores (últimos 12 meses) y busca **patrones**:

- ¿En qué meses se vende más?
- ¿Qué categorías son populares?
- ¿Hay temporadas altas (Navidad, verano)?
- ¿Cuál es el precio promedio de venta?

**Ejemplo real**:

```
El sistema ve que:
- Diciembre: 200 ventas de vestidos
- Julio: 150 ventas de blusas
- Precio promedio: $65

Entonces aprende: "En diciembre la gente compra más vestidos"
```

### 2. **Creación del "Cerebro" (Modelo de IA)**

El sistema usa un algoritmo llamado **Random Forest** (Bosque Aleatorio). Imagina que:

- Es como tener **100 expertos** (árboles de decisión)
- Cada experto da su opinión sobre cuánto se venderá
- Al final, se promedian todas las opiniones

**¿Por qué es bueno?**

- No se confunde fácilmente con datos raros
- Es preciso incluso con pocos datos
- Funciona bien para ventas que tienen estacionalidad

### 3. **Haciendo Predicciones**

Una vez entrenado, le das información del futuro:

- "Quiero saber cuánto venderé en enero de 2026"

El sistema analiza:

- ¿Qué mes es? (enero = temporada baja generalmente)
- ¿Qué categoría? (vestidos, pantalones, etc.)
- ¿Cómo fueron los eneros anteriores?

Y te da una respuesta: **"Predigo que venderás 85 unidades en enero"**

---

## 📊 ¿Qué datos usa?

El sistema necesita saber:

| Dato                 | Ejemplo        | ¿Para qué?                     |
| -------------------- | -------------- | ------------------------------ |
| **Fecha de venta**   | 15/11/2025     | Identificar temporalidad       |
| **Categoría**        | Vestidos       | Cada categoría tiene su patrón |
| **Precio**           | $89.99         | Afecta cantidad vendida        |
| **Cantidad vendida** | 3 unidades     | Lo que queremos predecir       |
| **Mes/Año**          | Noviembre 2025 | Patrones estacionales          |

---

## 🎬 ¿Cómo se usa?

### Opción 1: Desde el Backend (API)

**Entrenar el modelo**:

```bash
python manage.py train_model
```

**Ver predicciones en el Dashboard**:

```
GET /api/ai/dashboard/
```

**Predecir próximo mes**:

```
POST /api/ai/predictions/sales-forecast/
Body: { "n_months": 3 }
```

### Opción 2: Desde el Frontend (React)

El frontend consumirá estos endpoints y mostrará:

- 📈 Gráficas de ventas históricas
- 🔮 Predicciones futuras en colores diferentes
- 📊 Comparativas por categoría
- 🏆 Top productos más vendidos

---

## 🔄 Ciclo de Vida del Sistema

```
1. RECOPILACIÓN DE DATOS
   ↓
   Se guardan todas las ventas en la base de datos
   (Pedidos, productos, fechas, cantidades)

2. PREPARACIÓN DE DATOS
   ↓
   El sistema extrae y limpia los datos
   Los transforma en "features" (características)

3. ENTRENAMIENTO DEL MODELO
   ↓
   Se divide en 80% entrenamiento, 20% prueba
   Random Forest aprende los patrones
   Se evalúa: "¿Qué tan bueno es?"

4. PREDICCIÓN
   ↓
   Le das datos del futuro (mes, categoría)
   El modelo genera una predicción
   Se guarda para comparar después

5. VALIDACIÓN (OPCIONAL)
   ↓
   Cuando llegue ese mes, comparamos:
   ¿Cuánto predije? ¿Cuánto se vendió realmente?
   Así medimos la precisión
```

---

## 📏 ¿Cómo saber si funciona bien?

El sistema te da **métricas de calidad**:

### R² Score (Coeficiente de determinación)

- **0.0 - 0.5**: Malo (no confíes mucho)
- **0.5 - 0.7**: Regular (útil pero con precaución)
- **0.7 - 0.9**: Bueno (confía en las predicciones)
- **0.9 - 1.0**: Excelente (muy preciso)

### MAE (Error Absoluto Medio)

Es el promedio de qué tan lejos está la predicción de la realidad.

**Ejemplo**:

- Predije: 100 ventas
- Realidad: 110 ventas
- Error: 10 unidades
- MAE: Si el promedio de errores es 10, está bien

### RMSE (Raíz del Error Cuadrático Medio)

Similar al MAE pero penaliza más los errores grandes.

---

## 🚀 Ejemplo Práctico Completo

Imagina que hoy es **10 de noviembre de 2025** y quieres saber cuánto venderás en diciembre:

### 1. Entrenas el modelo:

```bash
python manage.py train_model
```

**Output**:

```
✅ Modelo entrenado con 500 registros históricos
📈 R² Score: 0.82 (Bueno!)
📊 MAE: 8.5 unidades
```

### 2. Pides predicción para diciembre:

```bash
POST /api/ai/predictions/sales-forecast/
Body: { "categoria": "Vestidos", "n_months": 1 }
```

**Respuesta**:

```json
{
  "periodo": "2025-12",
  "ventas_predichas": 185.5,
  "categoria": "Vestidos",
  "confianza": "Alta"
}
```

### 3. Interpretación:

**"Se espera vender aproximadamente 186 vestidos en diciembre"**

Ahora puedes:

- ✅ Asegurar tener 200+ vestidos en stock
- ✅ Contratar más personal para diciembre
- ✅ Planificar promociones

---

## ❓ Preguntas Frecuentes

### ¿Qué pasa si no tengo muchos datos?

El sistema genera **datos sintéticos** (falsos pero realistas) para entrenar. A medida que tengas más ventas reales, las predicciones mejorarán.

### ¿Se actualiza automáticamente?

No, debes re-entrenar el modelo periódicamente (mensual o trimestral) con:

```bash
python manage.py train_model
```

### ¿Puede predecir productos específicos?

Sí, actualmente predice por **categoría** (Vestidos, Blusas, etc.). Podría extenderse a productos específicos.

### ¿Es 100% preciso?

No, ningún modelo es perfecto. Pero con R² > 0.7, puedes confiar en las tendencias generales.

### ¿Necesito conocimientos de IA?

**No**, el sistema está listo para usar. Solo llamas a los endpoints y obtienes predicciones.

---

## 🎨 Visualización en el Frontend

El frontend debería mostrar:

### 1. Gráfica de Línea Histórica + Predicciones

```
Ventas de Vestidos (últimos 6 meses + próximos 3)

200 │         ┌──── Predicción ────┐
    │         │   (línea punteada) │
150 │    ●────●────●────○────○────○
    │   /
100 │  ●           ● = Real
    │             ○ = Predicción
 50 │
    └──────────────────────────────────
     Jul Ago Sep Oct Nov Dic Ene Feb Mar
```

### 2. Tarjetas de Predicción

```
┌─────────────────────┐
│  PRÓXIMO MES        │
│  📈 Ventas: 150     │
│  📊 +12% vs Nov     │
│  ⭐ Confianza: Alta │
└─────────────────────┘
```

### 3. Tabla de Top Productos

```
| Producto        | Vendido | Predicción Dic |
|-----------------|---------|----------------|
| Vestido Floral  | 50      | 65             |
| Blusa Casual    | 45      | 48             |
```

---

## 🎓 Resumen para Defensa con el Ingeniero

**Si te pregunta**: "¿Cómo funciona tu IA?"

**Respuesta**:

> "Implementé un modelo de Machine Learning usando **Random Forest Regressor** de scikit-learn. El sistema extrae datos históricos de ventas de los últimos 12 meses desde nuestra base de datos PostgreSQL, los prepara en features como mes, año, categoría, precio promedio, y estacionalidad (usando transformaciones trigonométricas para capturar patrones cíclicos).
>
> El modelo se entrena con un 80/20 split y evaluamos su rendimiento con métricas como R² score, MAE y RMSE. Actualmente logramos un R² de ~0.82, lo que indica buena capacidad predictiva.
>
> El modelo serializado se guarda con joblib y se puede re-entrenar periódicamente. Las predicciones se exponen mediante REST API y se guardan en base de datos para validación posterior cuando tengamos ventas reales.
>
> Si no hay suficientes datos, el sistema genera un dataset sintético con patrones estacionales realistas para bootstrap inicial."

---

## ✅ Checklist de Implementación

- [x] ✅ Modelo Random Forest entrenado
- [x] ✅ Servicio de preparación de datos
- [x] ✅ Servicio de entrenamiento
- [x] ✅ Servicio de predicción
- [x] ✅ Endpoints REST API
- [x] ✅ Serialización del modelo (joblib)
- [x] ✅ Tracking de modelos en BD
- [x] ✅ Generación de datos sintéticos
- [x] ✅ Métricas de evaluación
- [x] ✅ Comando de management
- [ ] 🔄 Frontend con gráficas (pendiente)

---

**Próximo paso**: Integrar el frontend para visualizar estas predicciones con gráficas interactivas usando Recharts o Chart.js.
