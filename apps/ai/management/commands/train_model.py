"""
Comando de Django para entrenar el modelo de predicción de ventas

Uso:
    python manage.py train_model
    python manage.py train_model --estimators 200 --depth 15
"""

from django.core.management.base import BaseCommand
from apps.ai.services.model_training import ModelTrainingService


class Command(BaseCommand):
    help = 'Entrena el modelo de predicción de ventas con Random Forest'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--estimators',
            type=int,
            default=100,
            help='Número de árboles en el Random Forest (default: 100)'
        )
        
        parser.add_argument(
            '--depth',
            type=int,
            default=10,
            help='Profundidad máxima de los árboles (default: 10)'
        )
        
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.2,
            help='Proporción de datos para testing (default: 0.2)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\n' + '='*60))
        self.stdout.write(self.style.WARNING('🤖 ENTRENAMIENTO DEL MODELO DE PREDICCIÓN DE VENTAS'))
        self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        # Obtener parámetros
        n_estimators = options['estimators']
        max_depth = options['depth']
        test_size = options['test_size']
        
        self.stdout.write(f"⚙️  Parámetros:")
        self.stdout.write(f"   - N° de árboles: {n_estimators}")
        self.stdout.write(f"   - Profundidad máxima: {max_depth}")
        self.stdout.write(f"   - Test size: {test_size}")
        self.stdout.write("")
        
        try:
            # Crear servicio y entrenar
            training_service = ModelTrainingService()
            
            result = training_service.train_model(
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
            
            test_metrics = result['metrics']['test']
            self.stdout.write(self.style.SUCCESS(f"\n📈 Métricas (Test Set):"))
            self.stdout.write(self.style.SUCCESS(f"   MAE:  {test_metrics['mae']:.2f}"))
            self.stdout.write(self.style.SUCCESS(f"   RMSE: {test_metrics['rmse']:.2f}"))
            self.stdout.write(self.style.SUCCESS(f"   R²:   {test_metrics['r2']:.4f}"))
            
            self.stdout.write(self.style.WARNING('\n' + '='*60))
            self.stdout.write(self.style.WARNING('🎉 PROCESO COMPLETADO'))
            self.stdout.write(self.style.WARNING('='*60 + '\n'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ ERROR: {str(e)}\n'))
            raise
