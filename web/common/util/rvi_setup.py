"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
Author: David Thiriez (david.thiriez@p3-group.com)
"""

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


DEFAULT_PASSWORD = 'rvi'
RVI_BASENAME = 'jlr.com'


class RVIModelSetup():

    def __init__(self):
        self.password = DEFAULT_PASSWORD
        self.valid_from = datetime.now()
        self.valid_to = self.valid_from.replace(self.valid_from.year + 1)
        self.rvi_basename = RVI_BASENAME

    def setup_user(self, username, password=None):
        password = password or self.password
        user = User.objects.create_user(
            username=username,
            password=password
        )
        user.save()
        return user

    def setup_key(self, user, valid_from=None, valid_to=None):
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

        valid_from = valid_from or self.valid_from
        valid_to = valid_to or self.valid_to

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
            veh_rvibasename=self.rvi_basename,
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
            dev_rvibasename=self.rvi_basename,
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
