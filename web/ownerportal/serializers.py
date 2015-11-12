from django.db import transaction

from rest_framework import serializers
from common.util.rvi_setup import RVIModelSetup

from devices.tasks import send_account_details

from django.contrib.auth.models import User
from devices.models import Device, Remote
from vehicles.models import Vehicle


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('dev_mdn', 'dev_uuid')
        depth = 1


class RegistrationSerializer(serializers.ModelSerializer):

    device = DeviceSerializer()

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'device')
        depth = 2

    def create(self, validated_data):
        device_data = validated_data.pop('device')[0]
        mdn = device_data['dev_mdn']
        uuid = device_data['dev_uuid']

        # TODO raise integrity errors back to serializer response
        rvi_model = RVIModelSetup()
        with transaction.atomic():
            user = rvi_model.setup_user(**validated_data)
            user_key = rvi_model.setup_key(user)
            device = rvi_model.setup_device(user, user_key, mdn, uuid)
            remote = rvi_model.setup_remote(user, device, Vehicle.objects.first())

        registration_response = send_account_details(remote)

        # TODO potentially seperate send_remote task from task
        for vehicle in Vehicle.objects.all():
            for owner_device in Device.objects.filter(account=vehicle.account):
                for owner_remote in Remote.objects.filter(rem_device=owner_device):
                    send_account_details(owner_remote)
        return registration_response

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.username = attrs.get('username', instance.username)
            instance.password = attrs.get('password', instance.password)
            instance.email = attrs.get('email', instance.email)
            instance.first_name = attrs.get('first_name', instance.first_name)
            instance.last_name = attrs.get('last_name', instance.last_name)
            return instance

        device = attrs.get('device')
        del attrs['device']

        user = User(**attrs)
        user.device = device

        return user
