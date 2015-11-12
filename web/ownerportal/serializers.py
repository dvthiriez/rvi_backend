from rest_framework import serializers
from django.contrib.auth.models import User
from common.util.rvi_setup import RVIModelSetup
from devices.models import Device


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
        rvi_model = RVIModelSetup()
        device_data = validated_data.pop('device')[0]

        user = rvi_model.setup_user(**validated_data)
        user_key = rvi_model.setup_key(user)

        mdn = device_data['dev_mdn']
        uuid = device_data['dev_uuid']
        device = rvi_model.setup_device(user, user_key, mdn, uuid)

        return user

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
