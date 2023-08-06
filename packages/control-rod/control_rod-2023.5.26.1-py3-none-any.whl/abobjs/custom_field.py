#!/usr/bin/env python3

import logging
import urllib.parse
import datetime
import json

import requests
import pyjq
import urllib.parse

import abobjs

class AB_Custom_Fields(abobjs.AB_Base):

    _endpoint = "/api/v1/custom_fields"
    _single = ".custom_fields[0]"
    _name = "custom_field"
    _get_params = {"include[]": "customFieldOptions"}
    _search_params = {"filter[deleted_at]": ""}

    _stich_def = [
        {"source": "custom_field_options",
         "idfield": "id",
         "val": "name",
         "isjqval": False}
    ]

    def __init__(self, id=None, api_info=None, **kwargs):

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name,
                                **kwargs)

