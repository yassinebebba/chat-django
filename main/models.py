from __future__ import annotations

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import _user_has_perm
from django.contrib.auth.models import _user_has_module_perms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from random import randint


class UserManager(BaseUserManager):
    def create_user(self, phone_number: str, password: str):
        if not phone_number:
            return ValueError('User must have a phone number')
        if not password:
            return ValueError('User must have a password')

        user = self.model(phone_number=phone_number)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number: str, password: str):
        user = self.create_user(phone_number, password)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Meta:
        db_table = 'user'

    phone_number = models.CharField(max_length=15, unique=True, null=False)
    creation_date = models.DateTimeField(default=timezone.now, null=False)
    is_active = models.BooleanField(default=False, null=False)
    is_staff = models.BooleanField(default=False, null=False)
    is_admin = models.BooleanField(default=False, null=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'

    @staticmethod
    def exists(phone_number: str) -> User | None:
        try:
            return User.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            return None

    @staticmethod
    def update_or_create_user(phone_number, password) -> tuple[User, bool]:
        user, created = User.objects.update_or_create(phone_number=phone_number, defaults={'phone_number': phone_number})
        user.set_password(password)
        user.save()
        return user, created

    def activate(self) -> None:
        self.is_active = True
        self.save()
        return None

    def has_perm(self, perm: str, obj=None) -> bool:
        if self.is_active and self.is_admin:
            return True
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perms: list[str], obj=None) -> bool:
        if self.is_active and self.is_admin:
            return True
        return all(self.has_perm(perm, obj) for perm in perms)

    def has_module_perms(self, app_label: str) -> bool:
        if self.is_active and self.is_admin:
            return True
        return _user_has_module_perms(self, app_label)

    def __repr__(self):
        return f'User(phone_number=\'{self.phone_number}\')'

    def __str__(self):
        return f'{self.phone_number}'


class OTP(models.Model):
    class Meta:
        db_table = 'otp'

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    otp_code = models.IntegerField(null=False)  # 6 digits to save space with int type in the DB
    attempts = models.IntegerField(default=0, null=False)
    creation_date = models.DateTimeField(default=timezone.now, null=False)

    @staticmethod
    def is_valid(user: User, otp_code: int) -> bool:
        try:
            OTP.objects.get(user=user, otp_code=otp_code)
            return True
        except ObjectDoesNotExist:
            return False

    @staticmethod
    def update_or_create_otp(user: User) -> tuple[OTP, bool]:
        return OTP.objects.update_or_create(user=user, defaults={'user': user, 'otp_code':randint(100000, 999999)})


class Message(models.Model):
    class Meta:
        db_table = 'message'

    sender = models.ForeignKey(User, related_name='sender_set', on_delete=models.DO_NOTHING, null=False)
    recipient = models.ForeignKey(User, related_name='recipient_set', on_delete=models.DO_NOTHING, null=False)
    content = models.CharField(max_length=250, null=False)
    creation_date = models.DateTimeField(default=timezone.now, null=False)
    delivered = models.BooleanField(default=False, null=False)
    read = models.BooleanField(default=False, null=False)
    deleted = models.BooleanField(default=False, null=False)

    def __repr__(self):
        return f'Message(sender={self.sender!r}, recipient={self.recipient!r}, content=\'{self.content}\')'

    def __str__(self):
        return f'{self.sender.phone_number} -> {self.recipient.phone_number}'
