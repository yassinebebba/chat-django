from __future__ import annotations

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
import re
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .models import User
from .models import OTP
from .serializers import UserSerializer


from django.shortcuts import render

def index(request):
    return render(request, 'main/index.html', {})

def room(request, room_name):
    return render(request, 'main/room.html', {
        'room_name': room_name
    })

class RegistrationView(APIView):
    """
       API to register users
    """

    def post(self, request, *args, **kwargs):
        response: dict = {'details': 'success'}
        status_code: int = status.HTTP_200_OK
        if len(request.data) != 2:
            response['error'] = 'not allowed'
            response['details'] = 'only fields `phone_number` ' \
                                  'and `password` are required'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        elif not re.search(r'^\+[0-9]{7,15}$', request.data['phone_number']):
            # concatenate country code and the phone number before submission
            response['error'] = 'wrong information'
            response['details'] = 'field `phone_number` must not be empty'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        elif not re.search('^.{8,30}$', request.data['password']):
            response['error'] = 'wrong information'
            response['details'] = 'password must be ' \
                                  'between 8 and 30 characters'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        else:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                otp, created = OTP.update_or_create_otp(user)
                is_sent: bool = self.send_otp(
                    request.data['phone_number'],
                    otp.otp_code
                )
                if created and not is_sent:
                    response['error'] = 'invalid phone number'
                    response['details'] = 'invalid phone number'
                    status_code = status.HTTP_406_NOT_ACCEPTABLE
            else:
                user, _ = User.update_or_create_user(
                    request.data['phone_number'],
                    request.data['password']
                )
                otp, created = OTP.update_or_create_otp(user)
                is_sent: bool = self.send_otp(
                    request.data['phone_number'],
                    otp.otp_code
                )
                if not created and not is_sent:
                    response['error'] = 'invalid phone number'
                    response['details'] = 'invalid phone number'
                    status_code = status.HTTP_406_NOT_ACCEPTABLE

                # response['error'] = 'error'
                # response['details'] = 'Phone number might be in use'
                # status_code = status.HTTP_406_NOT_ACCEPTABLE

        return Response(data=response, status=status_code)

    def send_otp(self, phone_number: str, otp_code: int) -> bool:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']
        client = Client(account_sid, auth_token)
        try:
            client.messages.create(
                body='Welcome to SGB\'s Utopia'
                     f'! this is your code: {otp_code}',
                from_=twilio_phone_number,
                to=phone_number
            )
            return True
        except TwilioRestException:
            return False


class OTPValidationView(APIView):
    """
    Validates the user's OTP
    """

    def post(self, request, *args, **kwargs):
        response: dict = {'details': 'success'}
        status_code: int = status.HTTP_200_OK
        if len(request.data) != 3:
            response['error'] = 'not allowed'
            response['details'] = 'fields `phone_number`, ' \
                                  '`password` and `otp` are required'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        elif not re.search(r'^\+[0-9]{7,15}$', request.data['phone_number']):
            response['error'] = 'wrong information'
            response['details'] = 'field `phone_number` must not be empty'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        elif not isinstance(request.data['otp'], int):
            response['error'] = 'wrong information'
            response['details'] = 'Invalid OTP'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        else:
            user: User = User.exists(request.data['phone_number'])
            if user:
                if user.is_active:
                    pass
                elif OTP.is_valid(user, request.data['otp']):
                    user.activate()
                else:
                    response['error'] = 'error'
                    response['details'] = 'Invalid OTP'
                    status_code = status.HTTP_406_NOT_ACCEPTABLE
            else:
                response['error'] = 'error'
                response['details'] = 'Phone number does not exist'
                status_code = status.HTTP_404_NOT_FOUND

        return Response(data=response, status=status_code)
