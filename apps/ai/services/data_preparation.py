"""
Servicio de preparación de datos para el modelo de Machine Learning

Este módulo se encarga de:
1. Extraer datos históricos de ventas desde la base de datos
2. Transformar los datos en features útiles para el modelo
3. Generar datasets sintéticos si no hay suficientes datos reales
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, F
from django.utils import timezone

from apps.orders.models import Pedido, DetallePedido
from apps.products.models import Prenda, Categoria


class DataPreparationService:
    """
    Servicio para preparar datos de entrenamiento del modelo de predicción de ventas
    """
    
    def __init__(self):
        self.min_records_for_training = 50  # Mínimo de registros para entrenar
    
    def get_historical_sales_data(self, months_back=36):
        """
        Extrae datos históricos de ventas de los últimos N meses
        
        Args:
            months_back (int): Número de meses hacia atrás a considerar (default: 36 = 3 años)
            
        Returns:
            pd.DataFrame: DataFrame con datos de ventas históricas
        """
        fecha_inicio = timezone.now() - timedelta(days=months_back * 30)
        
        # Obtener detalles de pedidos completados
        detalles = DetallePedido.objects.filter(
            pedido__created_at__gte=fecha_inicio,
            pedido__estado__in=['completado', 'enviado', 'entregado']
        ).select_related(
            'prenda',
            'prenda__marca',
            'pedido'
        ).prefetch_related(
            'prenda__categorias'
        )
        
        # Convertir a lista de diccionarios
        data = []
        for detalle in detalles:
            categoria_principal = detalle.prenda.categorias.first()
            
            data.append({
                'fecha': detalle.pedido.created_at,
                'producto_id': detalle.prenda.id,
                'producto_nombre': detalle.prenda.nombre,
                'categoria': categoria_principal.nombre if categoria_principal else 'Sin categoría',
                'marca': detalle.prenda.marca.nombre if detalle.prenda.marca else 'Sin marca',
                'precio_unitario': float(detalle.precio_unitario),
                'cantidad': detalle.cantidad,
                'subtotal': float(detalle.subtotal),
                'mes': detalle.pedido.created_at.month,
                'año': detalle.pedido.created_at.year,
                'dia_semana': detalle.pedido.created_at.weekday(),  # 0=Lunes, 6=Domingo
                'trimestre': (detalle.pedido.created_at.month - 1) // 3 + 1,
            })
        
        df = pd.DataFrame(data)
        
        # Si no hay suficientes datos, generar sintéticos
        if len(df) < self.min_records_for_training:
            print(f"⚠️ Solo {len(df)} registros reales. Generando datos sintéticos...")
            df = self._generate_synthetic_data(real_data=df)
        
        return df
    
    def prepare_features(self, df, months_back=36):
        """
        Prepara features para el modelo de Machine Learning
        IMPORTANTE: Incluye TODOS los meses (incluso con 0 ventas) para tener dataset completo
        
        Args:
            df (pd.DataFrame): DataFrame con datos crudos
            months_back (int): Meses hacia atrás para generar el rango completo
            
        Returns:
            tuple: (X, y, feature_columns) Features, target y nombres de columnas
        """
        # Agregar por mes, año y categoría
        df_agg = df.groupby(['año', 'mes', 'categoria']).agg({
            'cantidad': 'sum',
            'subtotal': 'sum',
            'precio_unitario': 'mean',
            'producto_id': 'count'  # Número de transacciones
        }).reset_index()
        
        df_agg.columns = ['año', 'mes', 'categoria', 'cantidad_vendida', 'total_ventas', 'precio_promedio', 'num_transacciones']
        
        # ✅ CORRECCIÓN CRÍTICA: Crear un rango completo de todos los meses
        # Esto asegura que tengamos 36 meses × 4 categorías = 144 registros
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=months_back * 30)
        
        # Generar todos los meses en el rango
        all_months = []
        current_date = fecha_inicio.replace(day=1)
        while current_date <= fecha_fin:
            all_months.append({
                'año': current_date.year,
                'mes': current_date.month
            })
            # Avanzar al siguiente mes
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Crear DataFrame con todas las combinaciones de mes × categoría
        categorias = ['Blusas', 'Vestidos', 'Jeans', 'Jackets']
        all_combinations = []
        for month_data in all_months:
            for categoria in categorias:
                all_combinations.append({
                    'año': month_data['año'],
                    'mes': month_data['mes'],
                    'categoria': categoria
                })
        
        df_complete = pd.DataFrame(all_combinations)
        
        # Hacer merge con los datos reales (left join para mantener todos los meses)
        df_merged = df_complete.merge(
            df_agg, 
            on=['año', 'mes', 'categoria'], 
            how='left'
        )
        
        # Rellenar valores NaN con 0 (meses sin ventas)
        df_merged['cantidad_vendida'] = df_merged['cantidad_vendida'].fillna(0)
        df_merged['total_ventas'] = df_merged['total_ventas'].fillna(0)
        df_merged['precio_promedio'] = df_merged['precio_promedio'].fillna(0)
        df_merged['num_transacciones'] = df_merged['num_transacciones'].fillna(0)
        
        # Features adicionales
        df_merged['mes_sin'] = np.sin(2 * np.pi * df_merged['mes'] / 12)
        df_merged['mes_cos'] = np.cos(2 * np.pi * df_merged['mes'] / 12)
        df_merged['trimestre'] = (df_merged['mes'] - 1) // 3 + 1
        
        # One-hot encoding para categoría
        df_encoded = pd.get_dummies(df_merged, columns=['categoria'], prefix='cat')
        
        # Separar features (X) y target (y)
        feature_columns = [
            'año', 'mes', 'mes_sin', 'mes_cos', 'trimestre',
            'cat_Blusas', 'cat_Vestidos', 'cat_Jeans', 'cat_Jackets'
        ]

        for col in feature_columns:
            if col not in df_encoded:
                df_encoded[col] = 0

        X = df_encoded[feature_columns]
        y = df_encoded['cantidad_vendida']  # Predecimos cantidad vendida
        
        print(f"📊 Dataset completo: {len(X)} registros ({len(all_months)} meses × {len(categorias)} categorías)")
        
        return X, y, feature_columns
    
    def _generate_synthetic_data(self, real_data=None, num_months=12, records_per_month=50):
        """
        Genera datos sintéticos realistas para entrenamiento inicial
        
        Args:
            real_data (pd.DataFrame): Datos reales existentes (para mezclar)
            num_months (int): Número de meses a generar
            records_per_month (int): Registros por mes
            
        Returns:
            pd.DataFrame: Dataset sintético
        """
        np.random.seed(42)
        
        categorias = ['Blusas', 'Vestidos', 'Jeans', 'Jackets']
        marcas = ['Zara', 'H&M', 'Mango', 'Pull&Bear', 'Bershka']
        
        synthetic_data = []
        
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=num_months * 30)
        
        for i in range(num_months * records_per_month):
            # Fecha aleatoria
            random_days = np.random.randint(0, num_months * 30)
            fecha = fecha_inicio + timedelta(days=random_days)
            
            # Categoría y estacionalidad
            categoria = np.random.choice(categorias)
            mes = fecha.month
            
            # Estacionalidad: más ventas en ciertos meses
            estacionalidad = 1.0
            if mes in [11, 12]:  # Noviembre-Diciembre: temporada alta
                estacionalidad = 1.5
            elif mes in [6, 7, 8]:  # Junio-Agosto: temporada media
                estacionalidad = 1.2
            elif mes in [1, 2]:  # Enero-Febrero: temporada baja
                estacionalidad = 0.7
            
            # Precio base según categoría
            precios_base = {
                'Blusas': 45.99,
                'Vestidos': 89.99,
                'Jeans': 65.99,
                'Jackets': 120.00
            }
            
            precio_base = precios_base.get(categoria, 60.0)
            precio = precio_base * np.random.uniform(0.8, 1.3)
            
            # Cantidad vendida (con estacionalidad)
            cantidad_base = np.random.randint(1, 5)
            cantidad = int(cantidad_base * estacionalidad)
            
            synthetic_data.append({
                'fecha': fecha,
                'producto_id': np.random.randint(1000, 9999),
                'producto_nombre': f'{categoria} {np.random.choice(marcas)}',
                'categoria': categoria,
                'marca': np.random.choice(marcas),
                'precio_unitario': round(precio, 2),
                'cantidad': cantidad,
                'subtotal': round(precio * cantidad, 2),
                'mes': fecha.month,
                'año': fecha.year,
                'dia_semana': fecha.weekday(),
                'trimestre': (fecha.month - 1) // 3 + 1,
            })
        
        df_synthetic = pd.DataFrame(synthetic_data)
        
        # Si hay datos reales, mezclarlos
        if real_data is not None and not real_data.empty:
            df_combined = pd.concat([real_data, df_synthetic], ignore_index=True)
            return df_combined
        
        return df_synthetic
    
    def get_aggregated_sales_by_period(self, period='month'):
        """
        Obtiene ventas agregadas por período
        
        Args:
            period (str): 'day', 'week', 'month', 'quarter', 'year'
            
        Returns:
            dict: Ventas agregadas
        """
        if period == 'month':
            # Agrupar por mes
            ventas = Pedido.objects.filter(
                estado__in=['completado', 'enviado', 'entregado']
            ).annotate(
                mes=F('created_at__month'),
                año=F('created_at__year')
            ).values('año', 'mes').annotate(
                total_ventas=Sum('total'),
                num_pedidos=Count('id')
            ).order_by('año', 'mes')
            
            return list(ventas)
        
        # Otros períodos se pueden implementar aquí
        return []
    
    def get_top_selling_products(self, limit=10):
        """
        Obtiene los productos más vendidos
        
        Returns:
            list: Top productos con sus ventas
        """
        top_products = DetallePedido.objects.filter(
            pedido__estado__in=['completado', 'enviado', 'entregado']
        ).values(
            'prenda__id',
            'prenda__nombre',
        ).annotate(
            total_vendido=Sum('cantidad'),
            ingresos_totales=Sum('subtotal')
        ).order_by('-total_vendido')[:limit]
        
        return list(top_products)
    
    def get_sales_by_category(self):
        """
        Obtiene ventas agregadas por categoría
        
        Returns:
            list: Ventas por categoría
        """
        # Esta query es compleja porque categoría está en ManyToMany
        # Vamos a simplificar obteniendo la primera categoría de cada prenda
        
        ventas_por_categoria = {}
        
        detalles = DetallePedido.objects.filter(
            pedido__estado__in=['completado', 'enviado', 'entregado']
        ).select_related('prenda').prefetch_related('prenda__categorias')
        
        for detalle in detalles:
            categoria = detalle.prenda.categorias.first()
            categoria_nombre = categoria.nombre if categoria else 'Sin categoría'
            
            if categoria_nombre not in ventas_por_categoria:
                ventas_por_categoria[categoria_nombre] = {
                    'categoria': categoria_nombre,
                    'total_ventas': 0,
                    'cantidad_vendida': 0,
                    'num_productos': 0
                }
            
            ventas_por_categoria[categoria_nombre]['total_ventas'] += float(detalle.subtotal)
            ventas_por_categoria[categoria_nombre]['cantidad_vendida'] += detalle.cantidad
            ventas_por_categoria[categoria_nombre]['num_productos'] += 1
        
        return list(ventas_por_categoria.values())
