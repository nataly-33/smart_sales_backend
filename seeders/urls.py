from django.urls import path
from .views import SeederRunView

urlpatterns = [
    path('run/', SeederRunView.as_view(), name='run_seeders'),
]
