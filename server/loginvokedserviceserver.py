"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the 
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com) 
Author: David Thiriez (david.thiriez@p3-group.com)
Log invoked services.
"""

import os, threading, base64, json
from urlparse import urlparse
import Queue
from rvijsonrpc import RVIJSONRPCServer
from dateutil import parser
import requests, pytz

import __init__
from __init__ import __RVI_LOGGER__ as rvi_logger

from servicehistory.tasks import send_service_invoked_by_guest
from server.utils import get_setting

from django.contrib.auth.models import User
from vehicles.models import Vehicle
from servicehistory.models import ServiceInvokedHistory

# globals
package_queue = Queue.Queue()
SERVER_NAME = "Log Invoked Service Server: "
transaction_id = 0


# Log Invoked Service Callback Server
class LogInvokedServicesServer(threading.Thread):
    """
    RPC server thread responding to Remote callbacks from the RVI framework.
    i.e. record service request that occur at the vehicle/RasPi
    """

    def __init__(self, service_edge, callback_url, service_id):
        self.service_edge = service_edge
        self.service_id = service_id
        self.callback_url = callback_url
        threading.Thread.__init__(self)
        url = urlparse(self.callback_url)
        self.localServer =  RVIJSONRPCServer(addr=((url.hostname, url.port)), logRequests=False)
        self.register_services()

    def register_services(self):
        # register callback functions with RPC server
        self.localServer.register_function(log_invoked_service, self.service_id + "/report/serviceinvoked")

        # register services with RVI framework
        result = self.service_edge.register_service(service = self.service_id+'/report/serviceinvoked',
                                               network_address = self.callback_url)
        rvi_logger.info(SERVER_NAME + 'Registration: %s', result['service'])

    def run(self):
        self.localServer.serve_forever()

    def shutdown(self):
        self.localServer.shutdown()


# Callback functions
def log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp):
    rvi_logger.info(SERVER_NAME + 'Create new remote request: \n'
                    'username: %s\n'
                    'vehicleVIN: %s\n'
                    'service: %s\n'
                    'latitude: %s\n'
                    'longitude: %s\n'
                    'timestamp: %s'
                    , username, vehicleVIN, service, latitude, longitude, timestamp)

    t1 = threading.Thread(target=thread_log_invoked_service, args=(
        username,
        vehicleVIN,
        service,
        latitude,
        longitude,
        timestamp,
    ))
    t1.start()

    return {u'status': 0}


# Support (thread) functions
def thread_log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp):
    try:
        serviceinvoked = validate_log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp)
    except Exception:
        rvi_logger.exception(SERVER_NAME + 'Received data did not pass validation')

    serviceinvoked.save()
    rvi_logger.info(SERVER_NAME + 'Saved log of the following service invoked record: %s', serviceinvoked)

    vehicle = Vehicle.objects.get(veh_vin = vehicleVIN)
    owner_username = vehicle.list_account()

    if owner_username != username:
        send_service_invoked_by_guest(owner_username, username, vehicleVIN, service)


# Validation functions
def validate_log_invoked_service(username, vehicleVIN, service, latitude, longitude, timestamp):
    try:
        user = User.objects.get(username=username)
        vehicle = Vehicle.objects.get(veh_vin=vehicleVIN)
        service_timestamp = parser.parse(str(timestamp).replace('T', ' ').replace('0Z',' +0000'))

        api_key = get_setting("GOOGLE_API_KEY")
        if api_key:
            address = reverse_geocode_googleapi(latitude, longitude, api_key)
        else:
            address = str(latitude)+', '+str(longitude)

    except User.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'username does not exist: %s', username)
        raise
    except Vehicle.DoesNotExist:
        rvi_logger.error(SERVER_NAME + 'VIN does not exist: %s', vehicleVIN)
        raise
    except Exception as e:
        rvi_logger.error(SERVER_NAME + 'Generic Error: %s', e)
        raise

    return ServiceInvokedHistory(
        hist_user = user,
        hist_service = service,
        hist_latitude = latitude,
        hist_longitude = longitude,
        hist_address = address,
        hist_vehicle = vehicle,
        hist_timestamp = service_timestamp
    )


# Support functions
def reverse_geocode_googleapi(latitude, longitude, api_key):
    # Sensor set to True since GPS coords coming from the mobile app
    sensor = 'true'

    base = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = "latlng={lat},{lon}&sensor={sen}&key={key}".format(
        lat=latitude,
        lon=longitude,
        sen=sensor,
        key=api_key
    )
    url = "{base}{params}".format(base=base, params=params)
    response = requests.get(url)

    # rvi_logger.info('Google Detailed Response: %s', response.content)
    rvi_logger.info('Google JSON Response: %s', response.json)
    return response.json()['results'][0]['formatted_address']
