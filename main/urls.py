from django.urls import path
from .views import LoginView
from .views import OTPVerificationView
from .views import UserDetailsView
from .views import ContactsVerificationView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('verify-otp/', OTPVerificationView.as_view()),
    path('user-details/', UserDetailsView.as_view()),
    path('check-contacts/', ContactsVerificationView.as_view()),
]
