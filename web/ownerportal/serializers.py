from django.db import transaction

from rest_framework import serializers
from common.util.rvi_setup import RVIModelSetup

from devices.tasks import send_remote

from django.contrib.auth.models import User
from security.models import JSONWebKey
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
            # remote = rvi_model.setup_remote(user, device, Vehicle.objects.first())
        # registration_response = send_account_details(remote)
        registration_response = {
            u'username': user.username,
            u'userType': u'guest',
            u'vehicleName': u'unavailable',
            u'validTo': u'2004-09-16T00:00:00Z',
            u'authorizedServices': {
                u'lock': unicode(False),
                u'engine': unicode(False),
                u'trunk': unicode(False),
                u'windows': unicode(False),
                u'lights': unicode(False),
                u'hazard': unicode(False),
                u'horn': unicode(False)
            },
            u'guests':u'',
        }
        # TODO potentially seperate send_remote task from task
        for vehicle in Vehicle.objects.all():
            for owner_device in Device.objects.filter(account=vehicle.account):
                for owner_remote in Remote.objects.filter(rem_device=owner_device):
                    send_remote(owner_remote)
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

class AddDeviceSerializer(serializers.Serializer):

    device = DeviceSerializer()
    username = serializers.CharField(max_length=200)


    class Meta:
        #model = User
        fields = ('device', 'username')
        #read_only_fields = ('username',)
        depth = 2

    def check_for_existing_device(self, validated_data):
        device_data = validated_data['device'][0]
        uuid = device_data['dev_uuid']
        user = User.objects.get(username=validated_data['username'])
        matching_devices = Device.objects.filter(account=user, dev_uuid=uuid)
        if matching_devices.exists():
            return True
        else:
            return False

    def create(self, validated_data):
        device_exists = self.check_for_existing_device(validated_data)
        if not device_exists:
            device_data = validated_data['device'][0]
            mdn = device_data['dev_mdn']
            uuid = device_data['dev_uuid']

            user = User.objects.get(username=validated_data['username'])
            rvi_model = RVIModelSetup()
            user_key = rvi_model.setup_key(user)
            device = rvi_model.setup_device(user, user_key, mdn, uuid)

        add_device_response = {u'deviceAdded': unicode(not device_exists),}
        return add_device_response

    def restore_object(self, attrs, instance=None):
        if instance is not None:
            instance.username = attrs.get('username', instance.username)
            return instance

        device = attrs.get('device')
        del attrs['device']

        user = User(**attrs)
        user.device = device

        return user
