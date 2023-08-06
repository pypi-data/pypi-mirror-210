import logging
import urllib.parse
import datetime
import json

import requests
import pyjq

import abobjs

class AB_Risk(abobjs.AB_Base):

    """
    A.K.A. Cycles. Not Sure why the mismatch exists
    """

    _endpoint = "/api/v1/risks"
    _single = ".risks[0]"
    _name = "risk"
    #_datefront = "%Y-%m-%dT%H:%M:%S"
    #_mslength = 3
    _date_keys = ["custom_date1", "custom_date2", "custom_date3", "custom_date4",
                  *abobjs.AB_Base._date_keys]

    #_strips = ["form_templates", "sort_order", "enabled_attributes", "excluded_attributes"]

    def __init__(self, id=None, api_info=None, **kwargs):

        #self.api_info = api_info
        #self.id = control_id
        #self.datum = kwargs.get("control_datum", dict())

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)
        date_keys = kwargs.get("date_keys", self._date_keys)

        #print(self._strips)
        #strips = kwargs.get("strips", self._strips)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name,
                                date_keys=date_keys,
                                **kwargs)