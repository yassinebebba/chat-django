from __future__ import annotations

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import _user_has_perm
from django.contrib.auth.models import _user_has_module_perms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

class UserManager(BaseUserManager):
    def create_user(self, phone_number: str, password: str):
        if not phone_number:
            return ValueError('User must have a phone number')
        if not password:
            return ValueError('User must have a password')

        user = self.model(phone_number=phone_number)
        user.set_passowrd(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number: str, password: str):
        user = self.create_user(phone_number, password)
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

    USERNAME_FIELD = phone_number

    @staticmethod
    def exists(phone_number: str) -> User | None:
        try:
            return User.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
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
