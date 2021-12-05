from django.urls import path
from rest_framework import routers
from .views import RegistrationView

router = routers.DefaultRouter()

urlpatterns = [
    path('register/', RegistrationView.as_view()),
]
