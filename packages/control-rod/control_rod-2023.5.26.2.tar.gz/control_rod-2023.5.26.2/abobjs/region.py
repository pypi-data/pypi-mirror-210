import logging
import urllib.parse
import datetime
import json

import requests
import pyjq

import abobjs

class AB_Region(abobjs.AB_Base):

    """
    A.K.A. Cycles. Not Sure why the mismatch exists
    """

    _endpoint = "/api/v1/regions"
    _single = ".regions[0]"
    _name = "region"
    #_datefront = "%Y-%m-%dT%H:%M:%S"
    #_mslength = 3
    #_date_keys = ["created_at", "updated_at", "deleted_at",	"effective_date",
	#              "baseline_date", "last_modification_date", "last_review_date"]
    _uid_field = "region_code"

    _strips = ["form_templates", "sort_order", "enabled_attributes", "excluded_attributes",
               *abobjs.AB_Base._strips]

    def __init__(self, id=None, api_info=None, **kwargs):

        #self.api_info = api_info
        #self.id = control_id
        #self.datum = kwargs.get("control_datum", dict())

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)
        self.uid_field = kwargs.get("uid_field", self._uid_field)

        strips = kwargs.get("strips", self._strips)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name, strips=strips,
                                **kwargs)