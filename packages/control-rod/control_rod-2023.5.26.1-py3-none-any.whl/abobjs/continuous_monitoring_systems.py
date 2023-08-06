#!/usr/bin/env python3

import logging
import urllib.parse
import datetime
import json

import requests
import pyjq

import abobjs

class AB_Continous_Monitoring_Systems(abobjs.AB_Base):

    _endpoint = "/api/v1/continuous_monitoring_systems"
    _single = ".continuous_monitoring_systems[0]"
    _name = "continuous_monitoring_system"

    _uid_field = None

    def __init__(self, id=None, api_info=None, **kwargs):

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name,
                                **kwargs)
