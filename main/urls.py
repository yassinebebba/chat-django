from django.urls import path
from .views import LoginView
from .views import OTPVerificationView
from .views import UserDetailsView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('verify-otp/', OTPVerificationView.as_view()),
    path('user-details/', UserDetailsView.as_view()),
]
