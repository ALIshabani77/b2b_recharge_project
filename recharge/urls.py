from django.urls import path
from .views import TopUpAPIView

urlpatterns = [
    path('top-up/', TopUpAPIView.as_view(), name='top-up'),
]