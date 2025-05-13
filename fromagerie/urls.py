from django.urls import path
from . import views
from .views import generer_etiquettes_pdf

urlpatterns = [
    path('/generer_etiquettes/', generer_etiquettes_pdf, name='generer_etiquettes'),
]