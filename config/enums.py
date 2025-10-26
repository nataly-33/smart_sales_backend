from enum import Enum

class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'

    @classmethod
    def choices(cls):
        """Devuelve las opciones para usar en Django models"""
        return [(gender.value, gender.get_label()) for gender in cls]

    def get_label(self):
        """Devuelve la etiqueta en español para cada género"""
        labels = {
            self.MALE: 'Masculino',
            self.FEMALE: 'Femenino',
            self.OTHER: 'Otro',
        }
        return labels.get(self, self.value)
    

class QuoteStatus(Enum):
    """
    Estados de las cuotas de pago
    """
    PENDING = 'pending'
    PAID = 'paid'
    OVERDUE = 'overdue'
    CANCELLED = 'cancelled'
    PARTIAL = 'partial'

    @classmethod
    def choices(cls):
        """Devuelve las opciones para usar en Django models"""
        return [(status.value, status.get_label()) for status in cls]
    
    @classmethod
    def values(cls):
        """Devuelve solo los valores de los estados"""
        return [status.value for status in cls]
    
    def get_label(self):
        """Devuelve la etiqueta en español para cada estado"""
        labels = {
            self.PENDING: 'Pendiente',
            self.PAID: 'Pagado',
            self.OVERDUE: 'Vencido',
            self.CANCELLED: 'Cancelado',
            self.PARTIAL: 'Pago Parcial',
        }
        return labels.get(self, self.value)


class PaymentFrequency(Enum):
    """
    Frecuencia de pago de cuotas
    """
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'

    @classmethod
    def choices(cls):
        """Devuelve las opciones para usar en Django models"""
        return [(freq.value, freq.get_label()) for freq in cls]
    
    @classmethod
    def values(cls):
        """Devuelve solo los valores de las frecuencias"""
        return [freq.value for freq in cls]
    
    def get_label(self):
        """Devuelve la etiqueta en español para cada frecuencia"""
        labels = {
            self.WEEKLY: 'Semanal',
            self.MONTHLY: 'Mensual',
            self.QUARTERLY: 'Trimestral',
            self.YEARLY: 'Anual',
        }
        return labels.get(self, self.value)
