"""
Tests para la app de IA y predicción de ventas
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.ai.services.data_preparation import DataPreparationService
from apps.ai.services.model_training import ModelTrainingService
from apps.ai.services.prediction import PredictionService
from apps.ai.models import MLModel, PrediccionVentas

User = get_user_model()


class DataPreparationServiceTest(TestCase):
    """Tests para el servicio de preparación de datos"""
    
    def setUp(self):
        self.service = DataPreparationService()
    
    def test_generate_synthetic_data(self):
        """Verifica que se generen datos sintéticos correctamente"""
        df = self.service._generate_synthetic_data(num_months=3, records_per_month=20)
        
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        self.assertEqual(len(df), 60)  # 3 meses * 20 registros
        
        # Verificar columnas
        required_columns = ['fecha', 'categoria', 'precio_unitario', 'cantidad', 'subtotal']
        for col in required_columns:
            self.assertIn(col, df.columns)
    
    def test_prepare_features(self):
        """Verifica que se preparen features correctamente"""
        df = self.service._generate_synthetic_data(num_months=2, records_per_month=30)
        X, y, feature_columns = self.service.prepare_features(df)
        
        self.assertIsNotNone(X)
        self.assertIsNotNone(y)
        self.assertGreater(len(feature_columns), 0)
        self.assertEqual(len(X), len(y))


class ModelTrainingServiceTest(TestCase):
    """Tests para el servicio de entrenamiento"""
    
    def setUp(self):
        self.service = ModelTrainingService()
    
    def test_train_model_basic(self):
        """Verifica que el modelo se entrene correctamente"""
        result = self.service.train_model(
            n_estimators=10,  # Reducido para testing
            max_depth=5,
            test_size=0.3
        )
        
        self.assertIsNotNone(result)
        self.assertIn('model_id', result)
        self.assertIn('metrics', result)
        
        # Verificar que el modelo se guardó en BD
        model = MLModel.objects.get(id=result['model_id'])
        self.assertTrue(model.activo)
        self.assertIsNotNone(model.r2_score)
    
    def test_load_active_model(self):
        """Verifica que se pueda cargar el modelo activo"""
        # Primero entrenar un modelo
        self.service.train_model(n_estimators=10, max_depth=5)
        
        # Luego cargar
        ml_model, model, feature_columns = self.service.load_active_model()
        
        self.assertIsNotNone(ml_model)
        self.assertIsNotNone(model)
        self.assertIsNotNone(feature_columns)
        self.assertTrue(ml_model.activo)


class PredictionServiceTest(TestCase):
    """Tests para el servicio de predicción"""
    
    def setUp(self):
        self.service = PredictionService()
        # Entrenar un modelo primero
        training_service = ModelTrainingService()
        training_service.train_model(n_estimators=10, max_depth=5)
    
    def test_predict_next_month(self):
        """Verifica que se generen predicciones para el próximo mes"""
        prediction = self.service.predict_next_month()
        
        self.assertIsNotNone(prediction)
        self.assertIn('ventas_predichas', prediction)
        self.assertIn('periodo', prediction)
        self.assertGreater(prediction['ventas_predichas'], 0)
    
    def test_predict_multiple_months(self):
        """Verifica que se generen predicciones para múltiples meses"""
        predictions = self.service.predict_next_n_months(n_months=3)
        
        self.assertIsNotNone(predictions)
        self.assertEqual(len(predictions), 3)
        
        for pred in predictions:
            self.assertIn('ventas_predichas', pred)
            self.assertIn('periodo', pred)
    
    def test_predict_by_category(self):
        """Verifica que se generen predicciones por categoría"""
        predictions = self.service.predict_by_category()
        
        self.assertIsNotNone(predictions)
        self.assertGreater(len(predictions), 0)


class MLModelTest(TestCase):
    """Tests para el modelo MLModel"""
    
    def test_create_model(self):
        """Verifica que se pueda crear un modelo"""
        model = MLModel.objects.create(
            nombre='Test Model',
            version='v1.0.0',
            archivo_modelo='/path/to/model.pkl',
            mae=10.5,
            mse=150.0,
            rmse=12.25,
            r2_score=0.85,
            registros_entrenamiento=100,
            features_utilizadas=['mes', 'año', 'categoria'],
            hiperparametros={'n_estimators': 100, 'max_depth': 10}
        )
        
        self.assertIsNotNone(model.id)
        self.assertEqual(model.nombre, 'Test Model')
        self.assertFalse(model.activo)
    
    def test_activar_modelo(self):
        """Verifica que solo un modelo puede estar activo"""
        model1 = MLModel.objects.create(
            nombre='Model 1',
            version='v1.0',
            archivo_modelo='/path/to/model1.pkl',
            registros_entrenamiento=100,
            activo=True
        )
        
        model2 = MLModel.objects.create(
            nombre='Model 2',
            version='v2.0',
            archivo_modelo='/path/to/model2.pkl',
            registros_entrenamiento=100
        )
        
        # Activar el segundo modelo
        model2.activar()
        
        # Verificar que model1 se desactivó
        model1.refresh_from_db()
        self.assertFalse(model1.activo)
        self.assertTrue(model2.activo)


class PrediccionVentasTest(TestCase):
    """Tests para el modelo PrediccionVentas"""
    
    def setUp(self):
        self.ml_model = MLModel.objects.create(
            nombre='Test Model',
            version='v1.0',
            archivo_modelo='/path/to/model.pkl',
            registros_entrenamiento=100,
            activo=True
        )
    
    def test_create_prediccion(self):
        """Verifica que se pueda crear una predicción"""
        prediccion = PrediccionVentas.objects.create(
            modelo=self.ml_model,
            periodo_predicho='2025-12',
            ventas_predichas=150.5,
            categoria='Vestidos',
            features_input={'mes': 12, 'año': 2025}
        )
        
        self.assertIsNotNone(prediccion.id)
        self.assertEqual(prediccion.periodo_predicho, '2025-12')
        self.assertEqual(prediccion.ventas_predichas, 150.5)
    
    def test_calcular_error(self):
        """Verifica que se calcule el error correctamente"""
        prediccion = PrediccionVentas.objects.create(
            modelo=self.ml_model,
            periodo_predicho='2025-12',
            ventas_predichas=150.0,
            ventas_reales=160.0,
            categoria='Vestidos'
        )
        
        prediccion.calcular_error()
        
        self.assertEqual(prediccion.error, 10.0)
