from django.http import HttpResponse
from django.template import RequestContext, loader

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response, redirect, render

from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.timezone import localtime
from pytz import timezone
import datetime

from django.views.decorators.csrf import csrf_exempt

# REST Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

# Provider OAUTH2
from provider.oauth2.models import Client

from django.contrib.auth.models import User
from ownerportal.serializers import RegistrationSerializer
from devices.models import Device, Remote
from vehicles.models import Vehicle


class RegistrationView(APIView):
    """ Allow registration of new users. """
    permission_classes = ()

    @csrf_exempt
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        # Chech format and unique constraint
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.data

        u = User.objects.create(username=data['username'])
        u.set_password(data['password'])
        u.save()

        # Create Oauth2 client
        name = u.username
        client = Client(user=u, name=name, url='' + name,
                        client_id=name, client_secret='', client_type=1)
        client.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def login_user(request):
    state = ""
    username = password = ''

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)


        if user is not None:
            if user.is_active or request.user.is_authenticated():

                owner = Vehicle.objects.filter(account_id=user.id)
                if owner.count():
                    login(request, user)
                    return redirect('owner_history')
                else:
                    state = "You must be a vehicle owner to log in."
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render(request, 'rvi/login.html', {
        'state': state,
        'username': username,
        'user': request.user
    })


def logout_user(request):
    state = "Successfully logged out!"
    username = password = ''

    logout(request)

    return render(request, 'rvi/login.html', {
        'state': state,
        'username': username,
        'user': request.user
    })


@login_required
def keys(request):
    owner = request.user
    owner_devices = Device.objects.get(dev_owner=owner)

    now = datetime.datetime.utcnow()
    non_owner_certificates = Remote.objects.filter(~Q(rem_device=owner_devices))

    '''
    for record in non_owner_certificates:
        time = localtime(record.rem_validto, timezone('US/Pacific'))
        time = record.rem_validto.strftime("%m/%d/%Y\n%-I:%M %p %Z")
        #record.rem_validto = time
    '''
    # TODO filter keys tied to the selected vehicle and only show "friend" accounts of the owner
    # Presently, showing all keys
    #
    active_certificates = non_owner_certificates.filter(
        Q(rem_validto__gte=now)|
        Q(rem_validto=None)
    ).order_by('-rem_validto')

    expired_certificates = non_owner_certificates.filter(
        Q(rem_validto__lt=now)
    ).order_by('-rem_validto')

    return render(request, 'rvi/keys.html', {
        'title': 'Keys',
        'user': request.user,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates
    })
