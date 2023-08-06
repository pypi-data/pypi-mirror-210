#!/usr/bin/env python3

import logging
import urllib.parse
import datetime
import json

import requests
import pyjq

import abobjs

class AB_Controls_Data(abobjs.AB_Base):

    _endpoint = "/api/v1/controls_data"
    _single = ".controls_data[0]"
    _name = "controls_data"
    _file_modal = "controlsDatum"
    _fileable_type = "ControlsDatum"

    _date_keys = [*abobjs.AB_Base._date_keys]

    _create_null_keys = [*abobjs.AB_Base._create_null_keys, "xnull"]

    _read_args = {"include[]": ["tests", "files"]}


    def __init__(self, id=None, api_info=None, **kwargs):

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)

        date_keys = kwargs.get("date_keys", self._date_keys)
        create_null_keys = kwargs.get("create_null_keys", self._create_null_keys)

        file_modal = kwargs.get("file_modal", self._file_modal)
        fileable_type = kwargs.get("fileable_type", self._fileable_type)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name,
                                date_keys=date_keys,
                                create_null_keys=create_null_keys,
                                file_modal=file_modal,
                                fileable_type=fileable_type,
                                **kwargs)
