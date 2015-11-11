"""
Copyright (C) 2014, Jaguar Land Rover
This program is licensed under the terms and conditions of the
Mozilla Public License, version 2.0.  The full text of the
Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
Maintainer: Rudolf Streif (rstreif@jaguarlandrover.com)
Author: David Thiriez (david.thiriez@p3-group.com)
"""

import sys, jsonrpclib
from rvilib import RVI
import threading
import time
import getopt
from datetime import datetime
import json

from server.utils import get_setting

from django.contrib.auth.models import User
from vehicles.models import Vehicle
from devices.models import Device


RVI_BASENAME = 'jlr.com'
RVI_SERVICE_ENABLE = 'RVI_CERTIFICATE_SERVICES_ENABLE'
RVI_SERVICE_EDGE = "RVI_SERVICE_EDGE_URL"


class RVIBackendCalls():

    def __init__(self):
        if get_setting(RVI_SERVICE_ENABLE) == True:
            self.__setup()
        else:
            raise RVIServiceNotRunning(RVI_SERVICE_ENABLE)

    def __setup(self):
        self.rvi_node = get_setting(RVI_SERVICE_EDGE)
        self.rvi = RVI(self.rvi_node)
        self.rvi_basename = RVI_BASENAME

        self.valid_from = datetime.now()
        self.valid_to = self.valid_from.replace(self.valid_from.year + 1)

        service_json = []
        lock = start = trunk = windows = lights = hazard = horn = False
        service_json.append({'lock': lock})
        service_json.append({'start': start})
        service_json.append({'trunk': trunk})
        service_json.append({'windows': windows})
        service_json.append({'lights': lights})
        service_json.append({'hazard': hazard})
        service_json.append({'horn': horn})
        self.services = json.dumps(service_json)

        self.service_executed = 'Door Lock'
        self.latitude = '33.8315126'
        self.longitude = '-117.9119521'
        self.timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def cert_create(self, user, vehicle, services=None, valid_from=None, valid_to=None):
        services = services or self.services
        valid_from = valid_from or self.valid_from
        valid_from = unicode(valid_from.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
        valid_to = valid_to or self.valid_to
        valid_to = unicode(valid_to.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
        
        service = self.rvi_basename + "/backend/dm/cert_create"
        rvi_args = [{
            'username': user.username,
            'vehicleVIN': vehicle.veh_vin,
            'authorizedServices': services,
            'validFrom': valid_from,
            'validTo': valid_to
        },]
        self.rvi.message(service, rvi_args)

    def cert_modify(self, certid, services=None, valid_from=None, valid_to=None):
        services = services or self.services
        valid_from = valid_from or self.valid_from
        valid_from = unicode(valid_from.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
        valid_to = valid_to or self.valid_to
        valid_to = unicode(valid_to.strftime('%Y-%m-%dT%H:%M:%S.000Z'))

        service = self.rvi_basename + "/backend/dm/cert_modify"
        rvi_args = [{
            'certid': certid,
            'authorizedServices': services,
            'validFrom': valid_from,
            'validTo': valid_to
        },]
        self.rvi.message(service, rvi_args)

    def request_certs(self, vehicle, mobile):
        service = self.rvi_basename + "/backend/dm/cert_requestall"
        rvi_args = [
            {'username': vehicle.veh_vin},
            {'mobileUUID': mobile.dev_uuid},
        ]
        self.rvi.message(service, rvi_args)

    def service_invoked(self, user, vehicle, service_executed=None, latitude=None, longitude=None, timestamp=None):
        service_executed = service_executed or self.service_executed
        latitude = latitude or self.latitude
        longitude = longitude or self.longitude
        timestamp = timestamp or self.timestamp

        service = self.rvi_basename + "/backend/logging/report/serviceinvoked"
        rvi_args = [
            {'username': user.username},
            {'vehicleVIN': vehicle.veh_vin},
            {'service': service_executed},
            {'latitude': latitude},
            {'longitude': longitude},
            {'timestamp': timestamp},
        ]
        self.rvi.message(service, rvi_args)


class RVIDeviceCalls():

    def __init__(self, device):
        self.rvi_basename = RVI_BASENAME
        self.rvi_node = get_setting(RVI_SERVICE_EDGE)
        self.rvi = RVI(rvi_node)
        self.device = device
        self.dst_url = device.get_rvi_id()
        self.rvi_service_id = get_settting(RVI_DM_SERVICE_ID)

    def cert_provision(self):
        service_name = self.dst_url + '/cert_provision'
        full_service_name = rvi.register_service(service_name, service_invoked)
        pass

    def cert_response(self):
        service_name = self.dst_url + '/cert_reponse'
        full_service_name = rvi.register_service(service_name, service_invoked)
        pass

    def cert_accountdetails(self):
        service_name = self.dst_url + '/cert_accountdetails'
        full_service_name = rvi.register_service(service_name, service_invoked)
        pass

    def service_invokedbyguest(self):
        service_name = '/report/serviceinvokedbyguest'
        full_service_name = rvi.register_service(service_name, service_invoked)
        pass


class RVIServiceNotRunning(Exception):
    pass
