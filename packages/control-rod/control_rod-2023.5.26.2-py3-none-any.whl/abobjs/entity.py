import logging
import urllib.parse
import datetime
import json

import requests
import pyjq

import abobjs

class AB_Entity(abobjs.AB_Base):

    """
    A.K.A. Cycles. Not Sure why the mismatch exists
    """

    _endpoint = "/api/v1/entities"
    _single = ".entities[0]"
    _name = "entity"
    #_datefront = "%Y-%m-%dT%H:%M:%S"
    #_mslength = 3
    #_date_keys = ["created_at", "updated_at", "deleted_at",	"effective_date",
	#              "baseline_date", "last_modification_date", "last_review_date"]

    _uid_field = "entity_code"

    def __init__(self, id=None, api_info=None, **kwargs):

        #self.api_info = api_info
        #self.id = control_id
        #self.datum = kwargs.get("control_datum", dict())

        # Dunder Handling
        endpoint = kwargs.get("endpoint", self._endpoint)
        single = kwargs.get("single", self._single)
        name = kwargs.get("name", self._name)
        uid_field = kwargs.get("uid_field", self._uid_field)

        strips = kwargs.get("strips", self._strips)

        abobjs.AB_Base.__init__(self, id=id, api_info=api_info,
                                endpoint=endpoint, single=single, name=name, strips=strips,
                                uid_field=uid_field,
                                **kwargs)

        if kwargs.get("control_ids", None)  is not None:
            self.control_link = self.set_controls(control_ids=kwargs["control_ids"])

    def set_controls(self, control_ids=list()):

        if len(control_ids) == 0 or isinstance(control_ids, list) is False:
            raise ValueError("We need to set a list of controls.")

        add_controls_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                                    "{}/{}/add_controls".format(self.endpoint, self.id))

        post_data = self.serialize(full_json=False, cust_data={"entityId": self.id, "control_ids":  control_ids})

        try:
            data_request = requests.post(add_controls_endpoint, headers=self.headers, json=post_data)
        except Exception as error:
            self.logger.error("Error when Adding Controls {} to Entity: {}".format(control_ids, self.id))
            self.logger.debug("Error Message: {}".format(error))
            objectified_data = self.objectify_datum({"entityId": self.id, "control_ids": []})
        else:
            self.logger.debug("Create Response: {}".format(data_request.status_code))
            if data_request.status_code != requests.codes.ok:
                self.logger.debug(data_request.text)
                raise ValueError("{} Add Control erorr {}".format(self.name, data_request.text))

            objectified_data = self.objectify_datum(data_request.json())

        return objectified_data