#!/usr/bin/python

#
# Copyright (C) 2014, Jaguar Land Rover
#
# This program is licensed under the terms and conditions of the
# Mozilla Public License, version 2.0.  The full text of the 
# Mozilla Public License is at https://www.mozilla.org/MPL/2.0/
#
# 
# Simple RVI service caller
#  

import sys
from rvilib import RVI
import threading
import time
import getopt
from datetime import datetime
import json

from django.contrib.auth.models import User
from vehicles.models import Vehicle


RVI_BASENAME = 'jlr.com'


class RVICalls():

    def __init__(self):
        self.valid_from = datetime.now()
        self.valid_to = self.valid_from.replace(self.valid_from.year + 1)
        self.rvi_basename = RVI_BASENAME

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

    def cert_create(self, user, vehicle, services=None, valid_from=None, valid_to=None):
        services = services or self.services
        valid_from = valid_from or self.valid_from
        valid_from = unicode(valid_from.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
        valid_to = valid_to or self.valid_to
        valid_to = unicode(valid_to.strftime('%Y-%m-%dT%H:%M:%S.000Z'))
        
        # Construct a dictionary from the provided paths.
        service = self.rvi_basename + "/backend/dm/cert_create"
        rvi_node = "http://localhost:8801"
        rvi_args = [{
            'username': user.username,
            'vehicleVIN': vehicle.veh_vin,
            'authorizedServices': services,
            'validFrom': valid_from,
            'validTo': valid_to
        },]

        # Setup an outbound JSON-RPC connection to the backend RVI node
        # Service Edge.
        #
        rvi = RVI(rvi_node)

        #
        # Send the messge.
        #
        rvi.message(service, rvi_args)
