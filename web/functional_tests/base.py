import sys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

import uuid
from random import randint
from datetime import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from django.contrib.auth.models import User
from security.models import JSONWebKey
from vehicles.models import Vehicle
from devices.models import Device, Remote

class FunctionalTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg:
                cls.server_url = 'http://' + arg.split('=')[1]
                return
            super(FunctionalTest, cls).setUpClass()
            cls.server_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        if cls.server_url == cls.live_server_url:
            super(FunctionalTest, cls).tearDownClass()

    def setup_user(self, username, password):
        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()
        return user

    def setup_key(self, user):
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
            key_name='key_' + user.username,
            key_valid_from=valid_from,
            key_valid_to=valid_to,
            key_pem=pem
        )
        key.save()
        return key    
    
    def setup_vehicle(self, owner, owner_key):
        vehicle_vin = str(
            randint(10**(17-1), (10**17)-1)
        )
        vehicle = Vehicle.objects.create(
            veh_name='vehicle_test' + vehicle_vin,
            veh_vin = vehicle_vin,
            veh_key=owner_key,
            veh_rvibasename='jlr.com',
            account=owner
        )
        vehicle.save()
        return vehicle
        
    def setup_device(self, user, user_key):
        device_uuid = str(uuid.uuid4())
        device = Device.objects.create(
            dev_name='device_' + user.username + '_' + device_uuid[:8],
            dev_owner=user.username,
            dev_uuid=str(uuid.uuid4()),
            dev_key=user_key,
            dev_rvibasename='jlr.com',
            account=user
        )
        device.save()
        return device

    def setup_remote(self, user, user_device, vehicle):
        valid_from = datetime.now()
        valid_to = valid_from.replace(valid_from.year + 1)
        guest_remote = Remote(
            rem_name='remote_' + user.username,
            rem_vehicle=vehicle,
            rem_device=user_device,
            rem_validfrom=valid_from,
            rem_validto=valid_to
        )

