from django.urls import path
from .views import RegistrationView
from .views import OTPVerifyView
from .views import LoginView
from .views import UserDetailsView

urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('verify-otp/', OTPVerifyView.as_view()),
    path('login/', LoginView.as_view()),
    path('user-details/', UserDetailsView.as_view()),
]
