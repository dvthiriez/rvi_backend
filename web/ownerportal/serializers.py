from rest_framework import serializers
from django.contrib.auth.models import User
from devices.models import Device


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ('dev_uuid', 'dev_mdn')
        depth = 1


class RegistrationSerializer(serializers.ModelSerializer):
    device = DeviceSerializer()
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'device')
        depth = 2

    def create(self, validated_data):
        device_data = validated_data.pop('device')[0]
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        device_data['account'] = user
        device_data['dev_name'] = 'device_'+user.username
        device_data['dev_owner'] = user.username
        device = Device.objects.create(**device_data)
        device.save()
        user.save()
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
