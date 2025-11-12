# 📊 Dashboard de Predicciones - Documentación Frontend

**Última actualización:** 11 de Noviembre 2025  
**Tecnologías:** React 18 + TypeScript + Recharts + TailwindCSS

---

## 1. ARQUITECTURA DEL FRONTEND

### Estructura de Archivos

```
ss_frontend/src/modules/admin/
├── pages/
│   └── AdminPredictions.tsx         ← Componente principal
├── services/
│   └── ai.service.ts                ← Servicio para API calls
└── types/
    └── (tipos compartidos)
```

### Stack Tecnológico

| Librería         | Versión | Propósito             |
| ---------------- | ------- | --------------------- |
| **React**        | 18.2+   | Framework UI          |
| **TypeScript**   | 5.0+    | Tipado estático       |
| **Recharts**     | 2.8+    | Gráficos interactivos |
| **TailwindCSS**  | 3.4+    | Estilos utility-first |
| **Lucide React** | Latest  | Iconos modernos       |
| **Axios**        | 1.6+    | HTTP client           |

---

## 2. COMPONENTE PRINCIPAL: AdminPredictions.tsx

### 2.1. Estados del Componente

```typescript
const [loading, setLoading] = useState(true); // Carga inicial
const [generating, setGenerating] = useState(false); // Generando predicciones
const [error, setError] = useState<string | null>(null); // Errores
const [dashboard, setDashboard] = useState<DashboardResponse | null>(null); // Datos
const [monthsBack, setMonthsBack] = useState(12); // Filtro histórico
const [monthsForward, setMonthsForward] = useState(3); // Filtro predicción
const [currentMonthIndex, setCurrentMonthIndex] = useState(0); // Carrusel
```

### 2.2. Funciones Principales

#### `loadDashboard(historic?, prediction?)`

**Propósito:** Cargar datos del dashboard desde el backend

```typescript
const loadDashboard = async (historic?: number, prediction?: number) => {
  try {
    setLoading(true);
    setError(null);
    const histMonths = historic !== undefined ? historic : monthsBack;
    const predMonths = prediction !== undefined ? prediction : monthsForward;
    const data = await aiService.getDashboard(histMonths, predMonths);
    setDashboard(data);
  } catch (err: any) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

**Llamada API:**

```
GET /api/ai/dashboard/?months_back=12&months_forward=3
```

#### `handleGeneratePredictions()`

**Propósito:** Generar nuevas predicciones en el backend

```typescript
const handleGeneratePredictions = async () => {
  try {
    setGenerating(true);
    await aiService.generatePredictions(monthsForward);
    await loadDashboard(); // Recargar datos
    alert("✅ Predicciones generadas exitosamente");
  } catch (err: any) {
    setError(err.message);
  } finally {
    setGenerating(false);
  }
};
```

**Llamada API:**

```
POST /api/ai/predictions/sales-forecast/
Body: { "months_forward": 3 }
```

#### `getCombinedChartData()`

**Propósito:** Preparar datos para gráfico histórico + predicciones

```typescript
const getCombinedChartData = () => {
  const historicalData = dashboard.historical.map((item) => ({
    periodo: aiService.formatPeriodo(item.periodo), // "Nov 2025"
    Histórico: item.cantidad_vendida,
    Predicción: null,
  }));

  const predictionData = dashboard.predictions.map((item) => ({
    periodo: aiService.formatPeriodo(item.periodo),
    Histórico: null,
    Predicción: Math.round(item.ventas_predichas),
  }));

  return [...historicalData, ...predictionData];
};
```

**Resultado:**

```typescript
[
  { periodo: "Oct 2025", Histórico: 1024, Predicción: null },
  { periodo: "Nov 2025", Histórico: 1938, Predicción: null },
  { periodo: "Dic 2025", Histórico: null, Predicción: 1487 },
  { periodo: "Ene 2026", Histórico: null, Predicción: 425 },
];
```

#### `getCategoryChartData()`

**Propósito:** Agrupar predicciones por mes para el carrusel

```typescript
const getCategoryChartData = () => {
  const groupedByPeriod: Record<string, any> = {};

  dashboard.predictions_by_category.forEach((pred) => {
    const periodo = aiService.formatPeriodo(pred.periodo);
    if (!groupedByPeriod[periodo]) {
      groupedByPeriod[periodo] = { periodo };
    }
    groupedByPeriod[periodo][pred.categoria] = Math.round(
      pred.ventas_predichas
    );
  });

  return Object.values(groupedByPeriod);
};
```

**Resultado:**

```typescript
[
  {
    periodo: "Dic 2025",
    Blusas: 817,
    Vestidos: 218,
    Jeans: 226,
    Jackets: 226,
  },
  {
    periodo: "Ene 2026",
    Blusas: 175,
    Vestidos: 64,
    Jeans: 136,
    Jackets: 50,
  },
];
```

#### `getKeyMetrics()`

**Propósito:** Calcular métricas para las tarjetas superiores

```typescript
const getKeyMetrics = () => {
  // ✅ CORREGIDO: Suma TODAS las categorías en TODOS los meses
  const totalPredicted = dashboard.predictions_by_category.reduce(
    (sum, pred) => sum + pred.ventas_predichas,
    0
  );

  const numMonths = monthsForward;
  const avgPredicted = totalPredicted / numMonths;

  const lastHistorical =
    dashboard.historical[dashboard.historical.length - 1]?.cantidad_vendida ||
    0;
  const growth = aiService.calculateGrowth(avgPredicted, lastHistorical);

  const r2 = dashboard.model_info.r2_score;
  let confidence: "Alta" | "Media" | "Baja" = "Media";
  if (r2 >= 0.8) confidence = "Alta";
  else if (r2 < 0.6) confidence = "Baja";

  return { totalPredicted, avgPredicted, growth, confidence };
};
```

---

## 3. COMPONENTES VISUALES

### 3.1. Tarjetas de Métricas

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Total Predicho */}
  <div className="bg-white rounded-lg shadow-sm border p-6">
    <p className="text-sm text-gray-600">Total Predicho</p>
    <p className="text-2xl font-bold text-gray-900 mt-1">
      {aiService.formatNumber(metrics.totalPredicted)}
    </p>
    <p className="text-xs text-gray-500 mt-1">unidades</p>
  </div>

  {/* Promedio Mensual */}
  {/* Tendencia */}
  {/* Confianza (R²) */}
</div>
```

**Cálculos:**

| Métrica              | Fórmula                                                | Ejemplo                                        |
| -------------------- | ------------------------------------------------------ | ---------------------------------------------- |
| **Total Predicho**   | Σ(todas las predicciones)                              | 817+218+226+226+175+64+136+50 = 1,912 unidades |
| **Promedio Mensual** | Total / N meses                                        | 1,912 / 3 = 637 unidades/mes                   |
| **Tendencia**        | (Promedio - Último Histórico) / Último Histórico × 100 | (637 - 1938) / 1938 × 100 = -67%               |
| **Confianza**        | Basado en R²                                           | R² = 0.81 → "Alta"                             |

### 3.2. Gráfico Histórico + Predicciones

**Tipo:** AreaChart (Recharts)

**Características:**

- Área azul: Datos históricos reales
- Área verde (línea punteada): Predicciones del modelo
- Tooltips interactivos al hover
- Eje Y dinámico según rango de valores
- Etiquetas del eje X rotadas 45° para legibilidad

```tsx
<ResponsiveContainer width="100%" height={400}>
  <AreaChart data={getCombinedChartData()}>
    <defs>
      <linearGradient id="colorHistorico" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.6} />
        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1} />
      </linearGradient>
      <linearGradient id="colorPrediccion" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor="#10B981" stopOpacity={0.6} />
        <stop offset="95%" stopColor="#10B981" stopOpacity={0.1} />
      </linearGradient>
    </defs>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="periodo" angle={-45} textAnchor="end" height={80} />
    <YAxis label={{ value: "Unidades Vendidas", angle: -90 }} />
    <Tooltip content={<CustomTooltip />} />
    <Legend />
    <Area
      dataKey="Histórico"
      stroke="#3B82F6"
      strokeWidth={2}
      fill="url(#colorHistorico)"
      connectNulls={false}
    />
    <Area
      dataKey="Predicción"
      stroke="#10B981"
      strokeWidth={2}
      strokeDasharray="5 5"
      fill="url(#colorPrediccion)"
      connectNulls={false}
    />
  </AreaChart>
</ResponsiveContainer>
```

**Propiedades clave:**

- `connectNulls={false}` → Evita unir histórico con predicciones
- `strokeDasharray="5 5"` → Línea punteada para predicciones
- `angle={-45}` → Etiquetas rotadas para evitar overlap

### 3.3. Gráfico por Categoría (Carrusel)

**Tipo:** BarChart con navegación

**Características:**

- **Carrusel:** Un gráfico por mes
- **Botones:** ◀ y ▶ para navegar
- **Colores consistentes:** Blusas (naranja), Vestidos (rosa), Jeans (azul), Jackets (púrpura)
- **Labels:** Valores sobre cada barra

```tsx
<div className="flex items-center justify-between mb-4">
  <h3>Predicciones por Categoría</h3>
  <div className="flex items-center gap-2">
    <button
      onClick={() => setCurrentMonthIndex(Math.max(0, currentMonthIndex - 1))}
      disabled={currentMonthIndex === 0}
    >
      <ChevronLeft />
    </button>
    <span>{getCategoryChartData()[currentMonthIndex]?.periodo}</span>
    <button
      onClick={() => setCurrentMonthIndex(Math.min(..., currentMonthIndex + 1))}
      disabled={currentMonthIndex === getCategoryChartData().length - 1}
    >
      <ChevronRight />
    </button>
  </div>
</div>

<BarChart data={[getCategoryChartData()[currentMonthIndex]]}>
  <Bar dataKey="Blusas" fill="#F59E0B" label={{ position: 'top' }} />
  <Bar dataKey="Vestidos" fill="#EC4899" label={{ position: 'top' }} />
  <Bar dataKey="Jeans" fill="#3B82F6" label={{ position: 'top' }} />
  <Bar dataKey="Jackets" fill="#8B5CF6" label={{ position: 'top' }} />
</BarChart>
```

**Funcionamiento:**

```
Estado inicial: currentMonthIndex = 0
Muestra: getCategoryChartData()[0] = { periodo: "Dic 2025", Blusas: 817, ... }

Usuario hace clic en ▶:
currentMonthIndex = 1
Muestra: getCategoryChartData()[1] = { periodo: "Ene 2026", Blusas: 175, ... }
```

### 3.4. Tabla de Predicciones Detalladas

```tsx
<table className="w-full">
  <thead>
    <tr>
      <th>Período</th>
      <th>Categoría</th>
      <th>Predicción</th>
      <th>Confianza</th>
    </tr>
  </thead>
  <tbody>
    {dashboard.predictions_by_category.map((pred) => (
      <tr key={pred.prediccion_id}>
        <td>{aiService.formatPeriodo(pred.periodo)}</td>
        <td>{pred.categoria}</td>
        <td>{aiService.formatNumber(pred.ventas_predichas)}</td>
        <td>
          <span className={aiService.getConfidenceColor(pred.confianza)}>
            {pred.confianza}
          </span>
        </td>
      </tr>
    ))}
  </tbody>
</table>
```

---

## 4. SERVICIO AI (ai.service.ts)

### 4.1. Métodos Principales

#### `getDashboard(months_back, months_forward)`

```typescript
async getDashboard(
  months_back: number = 6,
  months_forward: number = 3
): Promise<DashboardResponse> {
  const response = await api.get<DashboardResponse>('/ai/dashboard/', {
    params: { months_back, months_forward },
  });
  return response.data;
}
```

**Respuesta del Backend:**

```typescript
{
  historical: HistoricalData[];           // Ventas pasadas
  predictions: Prediction[];              // Totales por mes
  predictions_by_category: PredictionByCategory[]; // Por categoría
  top_products: TopProduct[];             // Más vendidos
  category_sales: CategorySales[];        // Ventas por categoría
  model_info: ModelInfo;                  // Info del modelo
}
```

#### `generatePredictions(months_forward)`

```typescript
async generatePredictions(
  months_forward: number = 3
): Promise<GeneratePredictionsResponse> {
  const response = await api.post<GeneratePredictionsResponse>(
    '/ai/predictions/sales-forecast/',
    { months_forward }
  );
  return response.data;
}
```

### 4.2. Utilidades de Formateo

```typescript
// Formatear período: "2025-11" → "Nov 2025"
formatPeriodo(periodo: string): string {
  const [year, month] = periodo.split('-');
  const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                  'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  return `${months[parseInt(month) - 1]} ${year}`;
}

// Formatear número: 1487 → "1,487"
formatNumber(num: number): string {
  return new Intl.NumberFormat('es-BO').format(Math.round(num));
}

// Color de confianza
getConfidenceColor(confianza: 'Alta' | 'Media' | 'Baja'): string {
  switch (confianza) {
    case 'Alta': return 'bg-green-100 text-green-800';
    case 'Media': return 'bg-yellow-100 text-yellow-800';
    case 'Baja': return 'bg-red-100 text-red-800';
  }
}
```

---

## 5. FLUJO DE INTERACCIÓN

### 5.1. Carga Inicial

```
1. Usuario accede a /admin/predictions
   ↓
2. useEffect(() => loadDashboard(), [])
   ↓
3. GET /api/ai/dashboard/?months_back=12&months_forward=3
   ↓
4. Backend retorna datos
   ↓
5. Frontend renderiza:
   - 4 tarjetas de métricas
   - Gráfico histórico + predicciones
   - Carrusel (muestra primer mes)
   - Tabla detallada
```

### 5.2. Cambio de Filtro de Predicción

```
Usuario cambia de "3 meses" a "6 meses"
   ↓
handlePredictionFilterChange(6)
   ↓
setMonthsForward(6)
setCurrentMonthIndex(0)  ← Reset carrusel
   ↓
loadDashboard(12, 6)
   ↓
GET /api/ai/dashboard/?months_back=12&months_forward=6
   ↓
Backend genera 24 predicciones (6 meses × 4 categorías)
   ↓
Frontend actualiza:
- Total Predicho suma 24 predicciones
- Carrusel muestra 6 meses
- Tabla lista 24 filas
```

### 5.3. Generación de Nuevas Predicciones

```
Usuario hace clic en "Generar Predicciones"
   ↓
handleGeneratePredictions()
   ↓
setGenerating(true)  ← Botón muestra "Generando..."
   ↓
POST /api/ai/predictions/sales-forecast/
Body: { "months_forward": 3 }
   ↓
Backend ejecuta modelo, guarda predicciones en BD
   ↓
loadDashboard()  ← Recargar datos actualizados
   ↓
setGenerating(false)
alert("✅ Predicciones generadas exitosamente")
```

---

## 6. CASOS DE ERROR

### 6.1. Modelo No Entrenado

**Escenario:** No hay modelo activo en la BD

**Manejo:**

```typescript
try {
  const data = await aiService.getDashboard();
} catch (err: any) {
  setError("No hay modelo activo. Entrena el modelo primero.");
}
```

**UI:**

```tsx
{
  error && (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6">
      <AlertCircle className="w-6 h-6 text-red-600" />
      <p>{error}</p>
      <button onClick={() => loadDashboard()}>Reintentar</button>
    </div>
  );
}
```

### 6.2. Sin Datos Históricos

**Escenario:** Base de datos vacía

**Manejo Backend:**

```python
if df.empty:
    return []  # Lista vacía en lugar de error
```

**UI Frontend:**

```typescript
if (dashboard.historical.length === 0) {
  return <EmptyState message="No hay datos históricos" />;
}
```

---

## 7. MEJORAS VISUALES IMPLEMENTADAS

### Antes vs Después

| Aspecto                  | Antes                       | Después                                |
| ------------------------ | --------------------------- | -------------------------------------- |
| **Total Predicho**       | 61 (incorrecto)             | 1,912 (correcto)                       |
| **Gráfico Histórico**    | Línea simple                | Área azul con degradado                |
| **Gráfico Predicciones** | Línea simple                | Área verde con línea punteada          |
| **Categorías**           | Solo Dic, Jeans/Jackets = 0 | Todos los meses, todas las categorías  |
| **Navegación**           | No disponible               | Carrusel con ◀ ▶                       |
| **Tooltips**             | Básicos                     | Personalizados con valores formateados |
| **Etiquetas Eje X**      | Overlap                     | Rotadas 45°, legibles                  |

---

## 8. DEFENSA: EXPLICACIÓN DEL FRONTEND

**Pregunta del Ingeniero:** _"¿Cómo funciona la interacción frontend-backend?"_

**Respuesta:**

> "El frontend es una SPA (Single Page Application) en React con TypeScript. Cuando el usuario accede al dashboard:
>
> 1. **Carga Inicial:**  
>    Hace un `GET /api/ai/dashboard/?months_back=12&months_forward=3`
>    El backend retorna JSON con:
>
>    - 12 registros históricos (últimos 12 meses)
>    - 12 predicciones por categoría (3 meses × 4 categorías)
>    - Información del modelo activo
>
> 2. **Procesamiento de Datos:**  
>    El frontend agrupa las predicciones por mes para el carrusel:
>
>    ```typescript
>    [
>      { periodo: "Dic 2025", Blusas: 817, Vestidos: 218, ... },
>      { periodo: "Ene 2026", Blusas: 175, Vestidos: 64, ... }
>    ]
>    ```
>
> 3. **Visualización:**
>
>    - **Recharts** renderiza los gráficos de manera responsiva
>    - El carrusel usa `currentMonthIndex` para mostrar 1 mes a la vez
>    - Las tarjetas de métricas calculan totales/promedios en tiempo real
>
> 4. **Filtros Dinámicos:**  
>    Cuando el usuario cambia el filtro, hace una nueva llamada al backend con los nuevos parámetros. No hay datos hardcodeados, todo es dinámico."

---

## 9. COMANDOS PARA DESARROLLO

```bash
# Instalar dependencias
cd ss_frontend
npm install

# Iniciar en desarrollo
npm run dev

# Build para producción
npm run build

# Preview de build
npm run preview

# Linter
npm run lint
```

---

## 10. TROUBLESHOOTING

### Problema: "Total Predicho" muestra 61 en lugar de 1,912

**Causa:** Sumaba `dashboard.predictions` (3 registros) en lugar de `dashboard.predictions_by_category` (12 registros)

**Solución:**

```typescript
// ❌ ANTES
const totalPredicted = dashboard.predictions.reduce(...)

// ✅ DESPUÉS
const totalPredicted = dashboard.predictions_by_category.reduce(...)
```

### Problema: Jeans y Jackets aparecen como 0 en la gráfica

**Causa:** El gráfico intentaba leer `data.Pantalones` y `data.Faldas` pero el backend envía `Jeans` y `Jackets`

**Solución:** Verificar que las claves coincidan:

```typescript
<Bar dataKey="Jeans" fill="#3B82F6" />    // ✅ Coincide con backend
<Bar dataKey="Pantalones" fill="#3B82F6" /> // ❌ No existe en data
```

### Problema: Solo muestra Diciembre en el carrusel

**Causa:** Backend solo generaba predicciones para 1 mes

**Solución:** Modificar `predict_by_category(n_months=3)` para iterar N meses

---

**Autor:** Nataly  
**Última revisión:** 11 de Noviembre 2025  
**Estado:** ✅ Completamente funcional
