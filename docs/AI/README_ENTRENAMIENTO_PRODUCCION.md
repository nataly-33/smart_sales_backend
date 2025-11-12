# 🤖 Entrenamiento del Modelo en Producción

## ❌ Problema

El servidor se queda sin memoria (OOM - Out of Memory) al intentar entrenar con `--months 34`:

```
📊 Paso 1: Obteniendo datos históricos (34 meses = 2.8 años)...
Killed
```

## ✅ Solución

Usar parámetros optimizados según la RAM disponible del servidor.

---

## 🔍 Verificar RAM Disponible

Conecta al servidor y verifica la RAM disponible:

```bash
ssh ubuntu@tu-servidor

# Ver RAM total
free -h

# Output esperado:
# total        used        free      shared  buff/cache   available
# Mem:           2.0G        800M        600M        50M        600M        1.1G
```

---

## 📋 Comandos Recomendados Según RAM

### 🟥 **Servidor muy pequeño (< 1 GB RAM)**

```bash
python manage.py train_model --months 12 --estimators 50 --depth 8
```

- ✅ 1 año de datos
- ⚡ Rápido (30-60 segundos)
- ⚠️ Menos preciso

---

### 🟨 **Servidor pequeño (1-2 GB RAM)**

```bash
python manage.py train_model --months 18 --estimators 75 --depth 9
```

- ✅ 1.5 años de datos
- ⚡ Moderado (1-2 minutos)
- ✅ Buen balance

---

### 🟩 **Servidor mediano (2-4 GB RAM)** ← RECOMENDADO

```bash
python manage.py train_model --months 24 --estimators 100 --depth 10
```

- ✅ 2 años de datos
- ⚡ Normal (2-3 minutos)
- ✅ Muy precisión

---

### 🟦 **Servidor grande (4+ GB RAM)**

```bash
python manage.py train_model --months 34 --estimators 150 --depth 12
```

- ✅ 2.8 años de datos
- ⚡ Lento (4-5 minutos)
- ✅ Máxima precisión

---

## 🚀 Ejecutar en Producción

### Opción 1: Manual (observas progreso)

```bash
cd ss_backend
python manage.py train_model --months 24 --estimators 100 --depth 10
```

### Opción 2: En background (no pierdes sesión SSH)

```bash
nohup python manage.py train_model --months 24 --estimators 100 --depth 10 > training.log 2>&1 &

# Ver progreso
tail -f training.log
```

### Opción 3: Auto-optimizado (detecta RAM)

```bash
python manage.py train_model_optimized --auto
```

### Opción 4: Script de shell

```bash
chmod +x scripts/train_model_production.sh
./scripts/train_model_production.sh
```

---

## ⚙️ Explicación de Parámetros

### `--months N`

- **Impacto:** ALTO en RAM
- **Recomendado:** 24 (2 años)
- Más meses = más datos = más RAM

### `--estimators N`

- **Impacto:** MEDIO en RAM
- **Recomendado:** 100
- Más árboles = mejor precisión pero más lento

### `--depth N`

- **Impacto:** BAJO en RAM
- **Recomendado:** 10
- Más profundidad = más complejo, riesgo de overfitting

---

## 🆘 Si Sigue Fallando

### 1️⃣ Reducir aún más

```bash
# Configuración mínima para cualquier servidor
python manage.py train_model --months 12 --estimators 50 --depth 8
```

### 2️⃣ Liberar memoria

```bash
# Detener Nginx temporalmente
sudo systemctl stop nginx

# Entrenar
python manage.py train_model --months 24 --estimators 100 --depth 10

# Reiniciar Nginx
sudo systemctl start nginx
```

### 3️⃣ Aumentar swap (último recurso)

```bash
# Ver swap actual
free -h

# Si no tienes swap, crear 2GB
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📊 Ejemplo en AWS t2.micro (1 GB RAM)

```bash
# ❌ NO HACER (mata el servidor)
python manage.py train_model --months 34 --estimators 100 --depth 10

# ✅ HACER
python manage.py train_model --months 12 --estimators 50 --depth 8

# Después, cuando tengas t2.small:
python manage.py train_model --months 24 --estimators 100 --depth 10
```

---

## 📈 Aftereffects (después de entrenar)

1. **Recarga el frontend:**

   ```
   http://localhost:3000/admin/predictions
   ```

2. **Verifica las nuevas predicciones:**

   ```
   http://localhost:3000/admin/predictions
   ```

3. **Ver métricas en admin:**
   ```
   http://localhost:3000/admin/ai/mlmodel/
   ```

---

## 🔄 Programar entrenamiento automático (Cron)

Entrenar cada mes a las 2 AM:

```bash
# Editar crontab
crontab -e

# Agregar línea:
0 2 1 * * cd /home/ubuntu/smart_sales/ss_backend && python manage.py train_model --months 24 --estimators 100 --depth 10 >> /var/log/model_training.log 2>&1
```

---

## 📝 Checklist

- [ ] Verificaste RAM disponible con `free -h`
- [ ] Elegiste comando según RAM
- [ ] Ejecutaste comando en `ss_backend`
- [ ] Esperaste a que termine (ver "✅ PROCESO COMPLETADO")
- [ ] Recargaste frontend (Ctrl+R)
- [ ] Verificaste predicciones en `/admin/predictions`

---

## 🎯 Recomendaciones Finales

| Servidor      | RAM  | Comando                                      |
| ------------- | ---- | -------------------------------------------- |
| AWS t2.micro  | 1 GB | `--months 12 --estimators 50 --depth 8`      |
| AWS t2.small  | 2 GB | `--months 24 --estimators 100 --depth 10` ✅ |
| AWS t2.medium | 4 GB | `--months 30 --estimators 120 --depth 11`    |
| Local (dev)   | 8GB+ | `--months 34 --estimators 150 --depth 12`    |

---

¡Listo! Usa estos comandos según tu servidor. 🚀
