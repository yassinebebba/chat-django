from django.urls import path
from .views import RegistrationView
from .views import OTPValidationView

urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('validate-otp/', OTPValidationView.as_view()),
]
