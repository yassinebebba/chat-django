from django.urls import path
from .views import RegistrationView
from .views import OTPValidationView
from .views import index
from .views import room

urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('validate-otp/', OTPValidationView.as_view()),
    path('', index, name='index'),
    path('<str:room_name>/', room, name='room'),
]
