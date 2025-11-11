# 🤖 Módulo de IA - SmartSales365

## Inicio Rápido

### 1. Realizar Migraciones

```bash
cd ss_backend
python manage.py makemigrations ai
python manage.py migrate ai
```

### 2. Entrenar el Modelo (Primera Vez)

```bash
python manage.py train_model
```

**Output esperado**:

```
🚀 INICIANDO ENTRENAMIENTO DEL MODELO DE PREDICCIÓN DE VENTAS
📊 Paso 1: Obteniendo datos históricos...
✅ 600 registros obtenidos
🔧 Paso 2: Preparando features...
✅ 11 features creadas
...
🎉 ENTRENAMIENTO COMPLETADO EXITOSAMENTE
```

### 3. Probar API

**Opción A: Con Swagger UI**

```
http://localhost:8000/api/docs/#/ai/
```

**Opción B: Con cURL**

**Dashboard completo**:

```bash
curl http://localhost:8000/api/ai/dashboard/
```

**Predicción para próximos 3 meses**:

```bash
curl -X POST http://localhost:8000/api/ai/predictions/sales-forecast/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"n_months": 3}'
```

**Predicción por categoría**:

```bash
curl -X POST http://localhost:8000/api/ai/predictions/sales-forecast/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"categoria": "Vestidos", "n_months": 1}'
```

---

## 📚 Documentación

- **Explicación Simple**: [AI_EXPLICACION_SIMPLE.md](../docs/AI_EXPLICACION_SIMPLE.md)
- **Documentación Técnica**: [AI_TECNICA_DETALLADA.md](../docs/AI_TECNICA_DETALLADA.md)
- **Guía de Defensa**: [AI_DEFENSA_INGENIERO.md](../docs/AI_DEFENSA_INGENIERO.md)

---

## 🔄 Re-entrenar Modelo

Se recomienda re-entrenar mensualmente con datos actualizados:

```bash
python manage.py train_model --estimators 100 --depth 10
```

**Opciones**:

- `--estimators N`: Número de árboles (default: 100)
- `--depth N`: Profundidad máxima (default: 10)
- `--test-size 0.2`: Proporción de test (default: 0.2)

---

## 📊 Endpoints Disponibles

| Endpoint                              | Método | Descripción                                   |
| ------------------------------------- | ------ | --------------------------------------------- |
| `/api/ai/dashboard/`                  | GET    | Dashboard completo (histórico + predicciones) |
| `/api/ai/predictions/sales-forecast/` | POST   | Generar predicciones                          |
| `/api/ai/train-model/`                | POST   | Entrenar/re-entrenar modelo                   |
| `/api/ai/active-model/`               | GET    | Info del modelo activo                        |
| `/api/ai/models/`                     | GET    | Lista de todos los modelos                    |
| `/api/ai/predictions/history/`        | GET    | Historial de predicciones                     |

---

## 🏗️ Estructura

```
apps/ai/
├── __init__.py
├── apps.py
├── admin.py
├── models.py              # MLModel, PrediccionVentas
├── serializers.py         # Serializers de DRF
├── urls.py               # Routing
├── views.py              # ViewSets
├── services/
│   ├── __init__.py
│   ├── data_preparation.py    # Extracción y features
│   ├── model_training.py      # Entrenamiento
│   └── prediction.py          # Predicciones
├── management/
│   └── commands/
│       └── train_model.py     # Comando CLI
└── tests/
    └── test_ai.py            # Tests unitarios
```

---

## 🛠️ Troubleshooting

### Error: "No module named 'sklearn'"

```bash
pip install scikit-learn pandas numpy joblib
```

### Error: "No hay modelo activo"

```bash
python manage.py train_model
```

### Predicciones incorrectas (R² < 0.5)

1. Verificar que hay suficientes datos reales
2. Re-entrenar con más árboles: `--estimators 200`
3. Revisar logs de Feature Importance

---

## 📈 Métricas de Calidad

El modelo se evalúa con:

- **R² Score**: Debe ser > 0.7 (actualmente ~0.82)
- **MAE**: Error promedio en unidades (~8.5)
- **RMSE**: Error cuadrático medio (~10.2)

---

## 🚀 Próximos Pasos

- [ ] Integrar frontend con gráficas (Recharts)
- [ ] Implementar caching con Redis
- [ ] Agregar validación cruzada (K-Fold)
- [ ] Notificaciones automáticas al re-entrenar
- [ ] Dashboard admin para comparar modelos

---

**Desarrollado para SmartSales365**  
**Última actualización**: 10 de Noviembre 2025
