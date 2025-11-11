# 🚀 GUÍA RÁPIDA: PROBAR MEJORAS DE REPORTES

## ⚡ Ejecutar en 3 Pasos

### 1️⃣ Actualizar Datos Existentes (Backend)

```powershell
cd ss_backend
python scripts\master_update.py
```

Esto ejecutará 6 scripts automáticamente:

- ✅ Actualizar fechas de clientes (2024-2025)
- ✅ Actualizar fechas de prendas (2024-2025)
- ✅ Limpiar nombres de prendas (quitar colores)
- ✅ Actualizar fechas de pedidos (2024-2025)
- ✅ Mejorar notas de pedidos
- ✅ Llenar carritos de clientes 1-20

**Tiempo estimado:** 2-5 minutos

---

### 2️⃣ Verificar Frontend (Opcional)

```powershell
cd ss_frontend
npm run dev
```

Navegar a: **http://localhost:3000/admin**

- ✅ Debe redirigir automáticamente a `/admin/analytics`
- ✅ Analytics debe ser el primer ítem del menú
- ✅ Reportes debe ser el segundo ítem del menú

---

### 3️⃣ Probar Reportes Mejorados

#### Opción A: Desde el Frontend

1. Ir a **http://localhost:3000/admin/reports**
2. Escribir: `"Ventas del año 2024 en PDF"`
3. Click en **"Generar Reporte"**
4. Descargar y abrir PDF

#### Opción B: Con cURL

```powershell
# Obtener token primero
curl -X POST http://localhost:8000/api/auth/token/ `
  -H "Content-Type: application/json" `
  -d '{\"email\": \"admin@smartsales365.com\", \"password\": \"Admin2024!\"}'

# Generar reporte PDF
curl -X POST 'http://localhost:8000/api/reports/generate/' `
  -H 'Authorization: Bearer TU_TOKEN_AQUI' `
  -H 'Content-Type: application/json' `
  -d '{\"prompt\": \"Ventas del año 2024 en PDF\"}' `
  --output ventas_2024.pdf

# Generar reporte Excel
curl -X POST 'http://localhost:8000/api/reports/generate/' `
  -H 'Authorization: Bearer TU_TOKEN_AQUI' `
  -H 'Content-Type: application/json' `
  -d '{\"prompt\": \"Clientes del año 2025 en Excel\"}' `
  --output clientes_2025.xlsx

# Generar reporte CSV
curl -X POST 'http://localhost:8000/api/reports/generate/' `
  -H 'Authorization: Bearer TU_TOKEN_AQUI' `
  -H 'Content-Type: application/json' `
  -d '{\"prompt\": \"Pedidos del último mes en CSV\"}' `
  --output pedidos.csv
```

---

## ✅ Qué Verificar en los Reportes

### PDF (Abrir con Acrobat/Chrome)

- ✅ Logo **ss_logo_letra.png** en esquina superior izquierda
- ✅ Metadata completa: **Organización, Generado por, Fecha, Rol, Email**
- ✅ Título compacto (no ocupa mucho espacio)
- ✅ Columna **#** en la tabla
- ✅ Colores **rose** (#CFA195) en headers
- ✅ Colores **cream** (#E2B8AD) alternados en filas
- ✅ Fuente **Arial 9pt** en datos
- ✅ Numeración de página: **"Página 1"** en pie de página

### Excel (Abrir con Microsoft Excel/LibreOffice)

- ✅ Archivo **SE ABRE CORRECTAMENTE** (sin errores)
- ✅ Columna **#** con números 1, 2, 3...
- ✅ Headers con color **rose** (#CFA195)
- ✅ Filas alternas con color **cream** (#E2B8AD)
- ✅ Fuente **Arial 9pt** legible
- ✅ Anchos de columna auto-ajustados

### CSV (Abrir con Excel/Editor de texto)

- ✅ Archivo **NO ES PDF** (es texto plano)
- ✅ Primera columna es **#**
- ✅ Headers correctos separados por comas
- ✅ Datos legibles con formato CSV estándar
- ✅ Compatible con Excel (UTF-8 con BOM)

---

---

## 🐛 Solución de Problemas

### Error: "PDF shows binary data"

✅ **Solucionado** - El generador ahora crea PDFs correctos

### Error: "Excel file is corrupted"

✅ **Solucionado** - El generador Excel ahora funciona perfectamente

### Error: "CSV opens as PDF in Excel"

✅ **Solucionado** - CSV ahora genera archivos CSV reales con UTF-8 BOM

### Error: "No data in reports"

❓ Ejecuta primero: `python scripts/master_update.py` para actualizar fechas

### Error: "Logo not showing in PDF"

❓ Verifica que existe: `ss_frontend/public/logo/ss_logo_letra.png`

---

## 📁 Archivos Modificados

### Backend

- ✅ `apps/reports/generators/pdf_generator.py`
- ✅ `apps/reports/generators/excel_generator.py`
- ✅ `apps/reports/generators/csv_generator.py`
- ✅ `scripts/super_seeder.py`
- ✅ `scripts/update_pedidos_fechas.py` (nuevo)
- ✅ `scripts/update_prendas_fechas.py` (nuevo)
- ✅ `scripts/fix_prendas_nombres.py` (nuevo)
- ✅ `scripts/fix_pedidos_notas.py` (nuevo)
- ✅ `scripts/populate_carritos.py` (nuevo)
- ✅ `scripts/update_clientes_fechas.py` (nuevo)
- ✅ `scripts/master_update.py` (nuevo)

### Frontend

- ✅ `src/core/routes/index.tsx`
- ✅ `src/shared/components/layout/AdminLayout.tsx`

---

## 🎯 Próximos Pasos

1. ✅ **Ejecutar master_update.py**
2. ✅ **Probar 3 reportes** (PDF, Excel, CSV)
3. ✅ **Verificar Analytics** en /admin
4. ⏳ Agregar más tipos de reportes
5. ⏳ Actualizar documentación

---

## 📞 Ayuda Rápida

### Ver estadísticas actuales

```python
# En Django shell
python manage.py shell

from apps.orders.models import Pedido
from apps.products.models import Prenda
from apps.accounts.models import User

print(f"Pedidos 2024: {Pedido.objects.filter(created_at__year=2024).count()}")
print(f"Pedidos 2025: {Pedido.objects.filter(created_at__year=2025).count()}")
print(f"Prendas: {Prenda.objects.count()}")
print(f"Clientes: {User.objects.filter(rol__nombre='Cliente').count()}")
```

### Restaurar datos originales

```bash
# Si algo sale mal
python manage.py flush --no-input
python scripts/super_seeder.py
```

---

**¡Listo para probar!** 🚀

Ejecuta `master_update.py` y genera tu primer reporte mejorado.
