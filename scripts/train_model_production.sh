#!/bin/bash

# 📊 Script para entrenar el modelo en producción de forma optimizada
# Uso: ./scripts/train_model_production.sh [12|18|24|30|34]

set -e  # Salir si hay error

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ============= MAIN =============

print_header "📊 ENTRENAMIENTO DE MODELO EN PRODUCCIÓN"

# Verificar RAM disponible
RAM_GB=$(free -h | grep Mem | awk '{print $7}' | sed 's/G//')
print_success "RAM disponible: ${RAM_GB} GB"

# Determinar parámetros según RAM
if (( $(echo "$RAM_GB < 1" | bc -l) )); then
    print_warn "Servidor con <1GB de RAM. Usando configuración mínima..."
    MONTHS=12
    ESTIMATORS=50
    DEPTH=8
elif (( $(echo "$RAM_GB < 2" | bc -l) )); then
    print_success "Servidor con 1-2GB de RAM. Usando configuración estándar..."
    MONTHS=18
    ESTIMATORS=75
    DEPTH=9
elif (( $(echo "$RAM_GB < 4" | bc -l) )); then
    print_success "Servidor con 2-4GB de RAM. Usando configuración óptima..."
    MONTHS=24
    ESTIMATORS=100
    DEPTH=10
else
    print_success "Servidor con 4GB+ de RAM. Usando configuración completa..."
    MONTHS=34
    ESTIMATORS=150
    DEPTH=12
fi

echo ""
print_header "CONFIGURACIÓN A USAR"
echo "📊 Meses de datos: $MONTHS"
echo "🌲 Árboles: $ESTIMATORS"
echo "📈 Profundidad: $DEPTH"
echo ""

read -p "¿Continuar? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    print_error "Abortado por el usuario"
    exit 1
fi

print_header "INICIANDO ENTRENAMIENTO"

# Ejecutar comando
cd /home/ubuntu/smart_sales/ss_backend

python manage.py train_model \
    --months $MONTHS \
    --estimators $ESTIMATORS \
    --depth $DEPTH

if [ $? -eq 0 ]; then
    print_success "¡Modelo entrenado exitosamente!"
    print_success "Recarga el frontend para ver los cambios"
else
    print_error "Error durante el entrenamiento"
    exit 1
fi
