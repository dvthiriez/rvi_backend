from django.test import TestCase
from django.contrib.auth import authenticate, login, logout

from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from django.contrib.auth.models import User
from security.models import JSONWebKey
from vehicles.models import Vehicle

from ownerportal.views import (
    INVALID_CREDENTIAL_ERROR, NONOWNER_ACCOUNT_ERROR,
    INACTIVE_ACCOUNT_ERROR
)


class LoginPageTest(TestCase):

    def test_uses_login_template(self):
        response = self.client.get('/login/')
        self.assertTemplateUsed(response, 'rvi/login.html')

    def test_nonowner_cannot_login(self):
        nonowner = User.objects.create_user(username='dthiriez',
                                            password='rvi')
        response = self.client.post(
            '/login/', 
            data={'username': 'dthiriez', 'password': 'rvi'}
        )
        
        self.assertContains(response, NONOWNER_ACCOUNT_ERROR)

    def test_admin_cannot_log_in(self):
        admin = User.objects.create_user(username='admin',
                                            password='rvi')
        response = self.client.post(
            '/login/', 
            data={'username': 'admin', 'password': 'rvi'}
        )
        
        self.assertContains(response, NONOWNER_ACCOUNT_ERROR)

    def test_nonuser_cannot_log_in(self):
        response = self.client.post(
            '/login/', 
            data={'username': 'noaccount', 'password': 'rvi'}
        )
        
        self.assertContains(response, INVALID_CREDENTIAL_ERROR)

    def test_inactive_cannot_log_in(self):
        inactive = User.objects.create_user(username='dthiriez',
                                            password='rvi'
        )
        inactive.is_active = False
        inactive.save()

        response = self.client.post(
            '/login/', 
            data={'username': 'dthiriez', 'password': 'rvi'}
        )
        
        self.assertContains(response, INACTIVE_ACCOUNT_ERROR)


class HistoryPageTest(TestCase):

    def test_login_required_for_history(self):
        response = self.client.get('/history/', follow=True)
        self.assertRedirects(response, '/login/?next=/history/')
        response = self.client.post('/history/', follow=True)
        self.assertRedirects(response, '/login/?next=/history/')

    def test_uses_history_template(self):
        owner = User.objects.create_user(username='dthiriez',
                                            password='rvi')
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        valid_from = datetime.now()
        valid_to = valid_from.replace(valid_from.year + 1)
        
        key = JSONWebKey.objects.create(
            key_name='key_dthiriez',
            key_valid_from=valid_from,
            key_valid_to=valid_to,
            key_pem=pem
        )
        key.save()
        
        vehicle = Vehicle.objects.create(
            veh_name='vehicle_test',
            veh_key=key,
            account=owner
        )
        vehicle.save()
        
        self.client.post('/login/', data={'username': 'dthiriez', 'password': 'rvi'})

        response = self.client.get('/history/')
        self.assertTemplateUsed(response, 'rvi/history.html')
