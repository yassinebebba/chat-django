from django.urls import path
from .views import RegistrationView
from .views import OTPValidationView
from .views import LoginView

urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('validate-otp/', OTPValidationView.as_view()),
    path('login/', LoginView.as_view()),
]
