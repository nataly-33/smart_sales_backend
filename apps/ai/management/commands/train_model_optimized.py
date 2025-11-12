#!/usr/bin/env python3
"""
Comando de Django para entrenar el modelo CON OPTIMIZACIÓN DE MEMORIA

Detecta automáticamente la RAM disponible y ajusta parámetros
"""

from django.core.management.base import BaseCommand
import psutil
import os
from apps.ai.services.model_training import ModelTrainingService


class Command(BaseCommand):
    help = 'Entrena el modelo de predicción de ventas (auto-optimizado por RAM disponible)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--months',
            type=int,
            default=None,
            help='Meses de datos históricos (auto-detectado si no se proporciona)'
        )
        
        parser.add_argument(
            '--estimators',
            type=int,
            default=None,
            help='Número de árboles (auto-detectado si no se proporciona)'
        )
        
        parser.add_argument(
            '--depth',
            type=int,
            default=None,
            help='Profundidad máxima (auto-detectado si no se proporciona)'
        )
        
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.2,
            help='Proporción de datos para testing (default: 0.2)'
        )
        
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Auto-detectar y optimizar parámetros según RAM disponible'
        )
    
    def detectar_ram_disponible(self):
        """Detecta la RAM disponible en el servidor"""
        try:
            # Get available RAM in bytes
            available_bytes = psutil.virtual_memory().available
            available_gb = available_bytes / (1024**3)
            return available_gb
        except:
            return None
    
    def optimizar_parametros(self, ram_gb):
        """Retorna parámetros óptimos según RAM disponible"""
        
        if ram_gb < 0.5:
            return {'months': 12, 'estimators': 50, 'depth': 8}
        elif ram_gb < 1:
            return {'months': 12, 'estimators': 75, 'depth': 8}
        elif ram_gb < 2:
            return {'months': 18, 'estimators': 75, 'depth': 9}
        elif ram_gb < 4:
            return {'months': 24, 'estimators': 100, 'depth': 10}
        elif ram_gb < 8:
            return {'months': 30, 'estimators': 120, 'depth': 11}
        else:
            return {'months': 34, 'estimators': 150, 'depth': 12}
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n' + '='*70))
        self.stdout.write(self.style.WARNING('🤖 ENTRENAMIENTO DEL MODELO (CON OPTIMIZACIÓN)'))
        self.stdout.write(self.style.WARNING('='*70 + '\n'))
        
        # Auto-detectar si se solicita
        if options['auto']:
            self.stdout.write(self.style.NOTICE('🔍 Detectando recursos disponibles...\n'))
            
            ram_disponible = self.detectar_ram_disponible()
            if ram_disponible:
                self.stdout.write(f"💾 RAM disponible: {ram_disponible:.2f} GB\n")
                parametros = self.optimizar_parametros(ram_disponible)
                
                self.stdout.write(self.style.SUCCESS('✅ Parámetros automáticos:'))
                self.stdout.write(f"   - Meses: {parametros['months']}")
                self.stdout.write(f"   - Árboles: {parametros['estimators']}")
                self.stdout.write(f"   - Profundidad: {parametros['depth']}\n")
                
                months_back = parametros['months']
                n_estimators = parametros['estimators']
                max_depth = parametros['depth']
            else:
                self.stdout.write(self.style.WARNING('⚠️  No se pudo detectar RAM, usando defaults\n'))
                months_back = options['months'] or 24
                n_estimators = options['estimators'] or 100
                max_depth = options['depth'] or 10
        else:
            # Usar valores proporcionados o defaults
            months_back = options['months'] or 24
            n_estimators = options['estimators'] or 100
            max_depth = options['depth'] or 10
        
        test_size = options['test_size']
        
        self.stdout.write(f"⚙️  Configuración final:")
        self.stdout.write(f"   - Meses de datos: {months_back} ({months_back/12:.1f} años)")
        self.stdout.write(f"   - N° de árboles: {n_estimators}")
        self.stdout.write(f"   - Profundidad máxima: {max_depth}")
        self.stdout.write(f"   - Test size: {test_size}")
        self.stdout.write("")
        
        try:
            # Crear servicio y entrenar
            training_service = ModelTrainingService()
            
            result = training_service.train_model(
                months_back=months_back,
                n_estimators=n_estimators,
                max_depth=max_depth,
                test_size=test_size
            )
            
            # Mostrar resultados
            self.stdout.write(self.style.SUCCESS('\n✅ MODELO ENTRENADO EXITOSAMENTE\n'))
            self.stdout.write(self.style.SUCCESS(f"📦 Modelo ID: {result['model_id']}"))
            self.stdout.write(self.style.SUCCESS(f"🏷️  Versión: {result['version']}"))
            self.stdout.write(self.style.SUCCESS(f"📁 Guardado en: {result['model_path']}"))
            self.stdout.write(self.style.SUCCESS(f"📊 Muestras de entrenamiento: {result['num_samples']}"))
            self.stdout.write(self.style.SUCCESS(f"🗓️  Meses de datos: {result['months_back']}"))
            
            test_metrics = result['metrics']['test']
            self.stdout.write(self.style.SUCCESS(f"\n📈 Métricas (Test Set):"))
            self.stdout.write(self.style.SUCCESS(f"   MAE:  {test_metrics['mae']:.2f}"))
            self.stdout.write(self.style.SUCCESS(f"   RMSE: {test_metrics['rmse']:.2f}"))
            self.stdout.write(self.style.SUCCESS(f"   R²:   {test_metrics['r2']:.4f}"))
            
            self.stdout.write(self.style.WARNING('\n' + '='*70))
            self.stdout.write(self.style.WARNING('🎉 PROCESO COMPLETADO'))
            self.stdout.write(self.style.WARNING('='*70 + '\n'))
        
        except MemoryError:
            self.stdout.write(self.style.ERROR('\n❌ ERROR: No hay memoria suficiente'))
            self.stdout.write(self.style.ERROR('Intenta reducir --months o --estimators\n'))
            raise
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ERROR: {str(e)}\n'))
            raise
