import logging
import urllib.parse
import datetime
import json

import requests
import pyjq

import abobjs

class AB_EffectivenessOption(abobjs.AB_Base):

    """
    A.K.A. Cycles. Not Sure why the mismatch exists
    """

    _endpoint = "/api/v1/effectiveness_options"
    _single = ".effectiveness_options[0]"
    _name = "effectiveness_option"
    #_datefront = "%Y-%m-%dT%H:%M:%S"
    #_mslength = 3
    #_date_keys = ["created_at", "updated_at", "deleted_at",	"effective_date",
	#              "baseline_date", "last_modification_date", "last_review_date"]


    def __init__(self, id=None, api_info=None, **kwargs):

        #self.api_info = api_info
        #self.id = control_id
        #self.datum = kwargs.get("control_datum", dict())

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name,
                                **kwargs)