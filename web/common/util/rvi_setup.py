"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
Author: David Thiriez (david.thiriez@p3-group.com)
"""

import uuid, string, random, pytz
from random import randint
from django.utils import timezone
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from django.db import IntegrityError

from django.contrib.auth.models import User
from security.models import JSONWebKey, CANFWKey
from vehicles.models import Vehicle
from devices.models import Device, Remote


RVI_BASENAME = 'jlr.com'
DEFAULT_PASSWORD = 'rvi'


class RVIModelSetup():

    def __init__(self, rvi_basename=None):
        self.rvi_basename = rvi_basename or RVI_BASENAME
        self.password = DEFAULT_PASSWORD
        utc_datetime = timezone.now()
        self.valid_from = utc_datetime
        self.valid_to = self.valid_from.replace(utc_datetime.year + 1)

    def setup_user(self, username, password=None, first_name=None, last_name=None, email=None):
        password = password or self.password
        first_name = first_name or self.__string_gen()
        last_name = last_name or self.__string_gen()
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        try:
            user.save()
        except IntegrityError:
            raise
        return user

    def setup_key(self, user, valid_from=None, valid_to=None):
        valid_from = valid_from or self.valid_from
        valid_to = valid_to or self.valid_to

        # TODO implemented rsa key generation is insecure
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        key = JSONWebKey.objects.create(
            key_name='key_' + user.username + "_" + self.__uuid_gen(),
            key_valid_from=valid_from,
            key_valid_to=valid_to,
            key_pem=pem
        )
        try:
            key.save()
        except IntegrityError:
            raise
        return key    
    
    def setup_canfw_key(self):
        can_fw_key = CANFWKey.objects.create(
            key_name = 'canfwkey_' + self.__string_gen()
        )
        try:
            can_fw_key.save()
        except IntegrityError:
            raise
        return can_fw_key

    def setup_vehicle(self, owner, owner_key, vin=None, make=None, model=None):
        vin = vin or self.__number_gen(size=17)
        make = make or self.__string_gen()
        model = model or self.__string_gen()
        can_fw_key = self.setup_canfw_key()
        vehicle = Vehicle.objects.create(
            veh_name='vehicle_test' + vin,
            veh_vin = vin,
            veh_key=owner_key,
            canfw_key=can_fw_key,
            veh_rvibasename=self.rvi_basename,
            account=owner
        )
        try:
            vehicle.save()
        except IntegrityError:
            raise
        return vehicle
        
    def setup_device(self, user, user_key, mdn=None, uuid=None):
        mdn = mdn or self.__number_gen()
        uuid = uuid or self.__uuid_gen()
        device = Device.objects.create(
            dev_name='device_' + user.username + '_' + uuid,
            dev_owner=user.username,
            dev_mdn=mdn,
            dev_uuid=uuid,
            dev_key=user_key,
            dev_rvibasename=self.rvi_basename,
            account=user
        )
        try:
            device.save()
        except IntegrityError:
            raise
        return device

    def setup_remote(self, user, user_device, vehicle, valid_from=None, valid_to=None):
        valid_from = valid_from or self.valid_from
        valid_to = valid_to or self.valid_to
        uuid = self.__uuid_gen()

        remote = Remote(
            rem_name='remote_' + user.username,
            rem_vehicle=vehicle,
            rem_device=user_device,
            rem_validfrom=valid_from,
            rem_validto=valid_to,
            rem_uuid=uuid
        )
        try:
            remote.save()
        except IntegrityError:
            raise
        return remote

    def __string_gen(self, size=None, chars=None):
        size = size or 10
        chars = chars or (string.ascii_uppercase+string.ascii_lowercase)
        return ''.join(random.choice(chars) for _ in range(size))

    def __number_gen(self, size=None):
        size = size or 10
        return str(randint(10**(size-1), (10**size)-1))

    def __uuid_gen(self):
        return str(uuid.uuid4())
