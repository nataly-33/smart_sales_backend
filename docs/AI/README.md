# 📚 Documentación del Sistema de IA - SmartSales365

**Última actualización:** 11 de Noviembre 2025  
**Estado:** ✅ Completamente funcional  
**Modelo actual:** Random Forest v1.0 (R² = 0.81)

---

## 📖 DOCUMENTACIÓN PRINCIPAL

### **1. [GUIA_DEFENSA_COMPLETA.md](./GUIA_DEFENSA_COMPLETA.md)** ⭐ **LECTURA OBLIGATORIA**

**Propósito:** Guía completa para defender el proyecto ante el ingeniero

**Contenido:**

- ✅ Por qué Random Forest (vs LSTM, ARIMA, XGBoost)
- ✅ Arquitectura completa del sistema (Backend + Frontend + BD)
- ✅ Preparación de datos y agregación (Año-Mes-Categoría)
- ✅ Features utilizadas (mes_sin, mes_cos, one-hot encoding)
- ✅ Features eliminadas y por qué (num_transacciones, precio_promedio)
- ✅ Métricas de evaluación (R² = 0.81, MAE = 30)
- ✅ Feature Importance (cat_Blusas = 37%, mes = 36%)
- ✅ Comparación modelo vs datos reales
- ✅ Flujo de generación de predicciones
- ✅ Preguntas frecuentes del ingeniero
- ✅ Checklist de defensa

**Audiencia:** Nataly (para estudiar y defender)

---

### **2. [DASHBOARD_FRONTEND.md](./DASHBOARD_FRONTEND.md)** ⭐ **LECTURA RECOMENDADA**

**Propósito:** Documentación técnica del dashboard React

**Contenido:**

- ✅ Arquitectura del frontend (React + TypeScript + Recharts)
- ✅ Componente AdminPredictions.tsx (línea por línea)
- ✅ Servicio ai.service.ts (métodos y tipos)
- ✅ Gráficos interactivos (Histórico + Predicciones)
- ✅ Carrusel de predicciones por categoría
- ✅ Filtros dinámicos y su funcionamiento
- ✅ Cálculo de métricas (Total Predicho, Promedio, Tendencia)
- ✅ Flujo de interacción usuario → backend → UI
- ✅ Troubleshooting (errores comunes y soluciones)
- ✅ Comandos de desarrollo

**Audiencia:** Nataly + Desarrolladores frontend

---

### **3. [AI_ENDPOINTS.md](./AI_ENDPOINTS.md)** 📡 **REFERENCIA RÁPIDA**

**Propósito:** Guía de endpoints de la API de IA

**Contenido:**

- ✅ `GET /api/ai/dashboard/` - Dashboard completo
- ✅ `POST /api/ai/predictions/sales-forecast/` - Generar predicciones
- ✅ `POST /api/ai/train-model/` - Entrenar modelo
- ✅ `GET /api/ai/active-model/` - Info del modelo activo
- ✅ Parámetros, respuestas y ejemplos de uso
- ✅ Comandos de terminal

**Audiencia:** Desarrolladores backend/frontend

---

## 🗂️ DOCUMENTACIÓN LEGACY (Archivos antiguos conservados)

Los siguientes archivos contienen información redundante o desactualizada, pero se mantienen por referencia histórica:

| Archivo                           | Estado                                              | ¿Leer?          |
| --------------------------------- | --------------------------------------------------- | --------------- |
| `AI_DEFENSA_INGENIERO.md`         | Redundante con GUIA_DEFENSA_COMPLETA.md             | ❌ No necesario |
| `AI_EXPLICACION_SIMPLE.md`        | Versión simplificada (para no técnicos)             | ⚠️ Opcional     |
| `AI_IMPLEMENTACION_COMPLETA.md`   | Histórico de implementación                         | ❌ No necesario |
| `AI_TECNICA_DETALLADA.md`         | Demasiado técnico (no necesario para defensa)       | ❌ No necesario |
| `DATOS_RANDOM_FOREST_ANALISIS.md` | Análisis de suficiencia de datos                    | ⚠️ Opcional     |
| `estructura_backend_ia.md`        | Arquitectura (cubierto en GUIA_DEFENSA_COMPLETA.md) | ❌ No necesario |
| `IMPLEMENTACION_IA_COMPLETADA.md` | Histórico de desarrollo                             | ❌ No necesario |
| `interpretacion_dashboard.md`     | Interpretación (cubierto en DASHBOARD_FRONTEND.md)  | ❌ No necesario |
| `modelo_ia_ventas.md`             | Modelo (cubierto en GUIA_DEFENSA_COMPLETA.md)       | ❌ No necesario |

---

## 🚀 INICIO RÁPIDO

### Para Nataly (Preparación de Defensa)

1. **Lee primero:** `GUIA_DEFENSA_COMPLETA.md` (1 hora de lectura)
2. **Practica respuestas** a las preguntas del ingeniero (sección 8)
3. **Revisa el checklist** antes de la defensa (sección 10)
4. **Familiarízate con el dashboard:** `DASHBOARD_FRONTEND.md` (30 minutos)

### Para Desarrolladores (Entender el Sistema)

1. **Arquitectura:** `GUIA_DEFENSA_COMPLETA.md` → Sección 2
2. **API:** `AI_ENDPOINTS.md`
3. **Frontend:** `DASHBOARD_FRONTEND.md`

---

## 📊 DATOS CLAVE PARA MEMORIZAR

```
✅ Modelo: Random Forest Regressor
✅ Algoritmo: Ensemble Learning (100 árboles)
✅ Datos de entrenamiento: 140 registros (35 meses × 4 categorías)
✅ División: 80% train (112) / 20% test (28)
✅ Métricas:
   - R² Score: 0.81 (81% de precisión)
   - MAE: 30 unidades (error promedio)
   - RMSE: 53 unidades

✅ Features más importantes:
   1. cat_Blusas: 37.17%
   2. mes: 36.06%
   3. año: 9.18%

✅ Predicciones actuales (Dic 2025):
   - Blusas: 817 unidades
   - Vestidos: 218 unidades
   - Jeans: 226 unidades
   - Jackets: 226 unidades
   - TOTAL: 1,487 unidades

✅ Comparación con Nov 2025 (real):
   - Nov: 1,938 unidades
   - Dic (predicho): 1,487 unidades
   - Cambio: -23% (normal post-Black Friday)
```

---

## 🎯 COMANDOS ESENCIALES

### Backend

```bash
cd ss_backend
.\vane\Scripts\activate  # Windows

# Entrenar modelo (ejecutar mensualmente)
python manage.py train_model --months 34

# Generar predicciones
python scripts/generar_predicciones.py

# Auditoría de ventas reales
python scripts/auditoria_ventas.py

# Iniciar servidor
python manage.py runserver
```

### Frontend

```bash
cd ss_frontend

# Instalar dependencias (solo primera vez)
npm install

# Iniciar en desarrollo
npm run dev

# Acceder al dashboard
# http://localhost:3000/admin/predictions
```

---

## 🔄 FLUJO DE TRABAJO MENSUAL

```
1. FIN DE MES
   ↓
2. Auditar ventas reales
   python scripts/auditoria_ventas.py
   ↓
3. Re-entrenar modelo con datos actualizados
   python manage.py train_model --months 36
   ↓
4. Generar nuevas predicciones
   python scripts/generar_predicciones.py
   ↓
5. Revisar dashboard en frontend
   http://localhost:3000/admin/predictions
   ↓
6. Comparar predicciones vs realidad (próximo mes)
```

---

## ❓ PREGUNTAS FRECUENTES

### ¿Qué archivo debo leer para la defensa?

**Respuesta:** Solo necesitas leer **`GUIA_DEFENSA_COMPLETA.md`** (cubre todo).

### ¿Cómo explico el frontend?

**Respuesta:** Lee **`DASHBOARD_FRONTEND.md`** sección 8 ("Defensa: Explicación del Frontend").

### ¿Dónde están los endpoints de la API?

**Respuesta:** **`AI_ENDPOINTS.md`** tiene todos los ejemplos.

### ¿Por qué hay tantos archivos .md?

**Respuesta:** Documentación histórica. Solo los 3 principales son necesarios:

1. `GUIA_DEFENSA_COMPLETA.md`
2. `DASHBOARD_FRONTEND.md`
3. `AI_ENDPOINTS.md`

---

## 📞 CONTACTO

**Autora:** Nataly  
**Proyecto:** SmartSales365  
**Universidad:** [Universidad]  
**Carrera:** Ingeniería en Sistemas  
**Fecha de defensa:** [Fecha]

---

## ✅ CHECKLIST PRE-DEFENSA

- [ ] Leí `GUIA_DEFENSA_COMPLETA.md`
- [ ] Entiendo por qué Random Forest (vs LSTM, ARIMA)
- [ ] Puedo explicar la agregación de datos (Año-Mes-Categoría)
- [ ] Sé qué son mes_sin y mes_cos
- [ ] Entiendo por qué eliminamos num_transacciones
- [ ] Puedo interpretar R² = 0.81 y MAE = 30
- [ ] Conozco las features más importantes (cat_Blusas = 37%)
- [ ] Puedo demostrar el dashboard funcionando
- [ ] Entiendo el flujo frontend → backend → BD
- [ ] Sé cómo se validan las predicciones

**¡Buena suerte en la defensa! 🚀**
