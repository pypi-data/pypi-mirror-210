#!/usr/bin/env python3

import logging
import urllib.parse
import datetime
import json

import requests
import pyjq

import abobjs

class AB_Auditable_Entity_Regions(abobjs.AB_Base):

    _endpoint = "/api/v1/auditable_entity_regions"
    _single = ".auditable_entity_regions[0]"
    _name = "auditable_entity_region"

    def __init__(self, id=None, api_info=None, **kwargs):

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name,
                                **kwargs)
