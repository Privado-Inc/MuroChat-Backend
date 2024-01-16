from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from utils.uuid import get24CharUuid
from django.core.validators import EmailValidator
from rest_framework.authtoken.models import Token
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField
from utils.Permissions import Roles

ROLE_CHOICES = [(Roles.IT_ADMIN, Roles.IT_ADMIN),
                (Roles.SECURITY_PRIVACY_ADMIN, Roles.SECURITY_PRIVACY_ADMIN),
                (Roles.USER, Roles.USER)]

class CustomUserManager(BaseUserManager):
    def createUser(self, email, password, **extraFields):
        user = User.objects.filter(email=email).first()
    
        if not user:
            user = User.objects.create(email=email, **extraFields)
            user.set_password(password)
            user.save()

            Token.objects.create(user=user)
            user.refresh_from_db()
            return user, False

        return user, True


class Account(models.Model):
    id = models.CharField(primary_key=True, verbose_name='ID', max_length=25, default=get24CharUuid)
    name = models.CharField(verbose_name='Name', max_length=128, default='')
    is_setup_done = models.BooleanField(default=False)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(primary_key=True, verbose_name='ID', max_length=25, default=get24CharUuid)
    email = models.EmailField(verbose_name='email address', max_length=256, unique=True, validators=[EmailValidator])
    firstName = models.CharField(verbose_name='First Name', max_length=128, null=False)
    lastName = models.CharField(verbose_name='Last Name', max_length=128, default='')
    isOkta = models.BooleanField(default=True)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    oktaId = models.CharField(verbose_name='Invitor Id', max_length=128, null=True)
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField()

    evKey = models.CharField(verbose_name='Last Name', max_length=128, default='')
    invitor_id = models.CharField(verbose_name='Invitor Id', max_length=128, null=True)
    invitedRole = models.CharField(max_length=128, choices=ROLE_CHOICES, default=Roles.USER)
    accounts = models.ManyToManyField(Account, verbose_name='All accounts that the user is a part of', related_name='users')
    USERNAME_FIELD = 'email'
    objects = CustomUserManager()

class UserDetails(models.Model):
    id = models.CharField(primary_key=True, verbose_name='ID', max_length=25, default=get24CharUuid)
    user = models.ForeignKey(User, verbose_name='User Id', on_delete=models.CASCADE, null=False)
    departmentName = models.CharField(verbose_name='Department Name', max_length=128, default='')
    organizationName = models.CharField(verbose_name='Organization Name', max_length=128, default='')
    isManager = models.BooleanField(default=False)
    reportsTo = models.CharField(verbose_name='user Id', max_length=25)


class UserRoleMapping(models.Model):
    id = models.CharField(primary_key=True, verbose_name='ID', max_length=25, default=get24CharUuid)
    user = models.ForeignKey(User, verbose_name='User Id', on_delete=models.CASCADE, null=False)
    role = models.CharField(max_length=128, choices=ROLE_CHOICES, default=Roles.USER)

class UserApplicationMapping(models.Model):
    id = models.CharField(primary_key=True, verbose_name='ID', max_length=25, default=get24CharUuid)
    user = models.ForeignKey(User, verbose_name='User Id', on_delete=models.CASCADE, null=False)
    isGPTEnabled = models.BooleanField(default=False)
