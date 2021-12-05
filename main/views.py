from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.response import Response
import re
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .models import User
from .models import OTP
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User
    serializer_class = UserSerializer


class RegistrationView(CreateAPIView):
    """
       API to register users
    """

    def post(self, request, *args, **kwargs):
        response: dict = {'details': 'success'}
        status_code: int = status.HTTP_200_OK
        if len(request.data) != 2:
            response['error'] = 'not allowed'
            response['details'] = 'fields `phone_number` and `password` are required'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        elif not re.search('^\+[0-9]{7,15}$', request.data['phone_number']):
            # concatenate the country code and the phone number before submission
            response['error'] = 'wrong information'
            response['details'] = 'field `phone_number` must not be empty'
            status_code = status.HTTP_406_NOT_ACCEPTABLE
        else:
            # TODO: this needs to change
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                otp, created = OTP.create_otp(user)
                if created:
                    account_sid = os.environ['TWILIO_ACCOUNT_SID']
                    auth_token = os.environ['TWILIO_AUTH_TOKEN']
                    twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']
                    client = Client(account_sid, auth_token)
                    try:
                        client.messages.create(
                            body='Welcome to SGB\'s Utopia! this is your code: {otp.otp_code}',
                            from_=twilio_phone_number,
                            to=request.data['phone_number']
                        )
                    except TwilioRestException:
                        response['error'] = 'invalid phone number'
                        response['details'] = 'invalid phone number'
                        status_code = status.HTTP_406_NOT_ACCEPTABLE
            else:
                response['error'] = 'error'
                response['details'] = 'Phone number might be in use'
                status_code = status.HTTP_406_NOT_ACCEPTABLE

        return Response(data=response, status=status_code)