from django.urls import path
from rest_framework import routers
from .views import RegistrationView
from .views import OTPValidationView

router = routers.DefaultRouter()

urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('validate-otp/', OTPValidationView.as_view()),
]
