#!/usr/bin/env python3

import logging

import abobjs

class AB_ControlRod:

    _order = {"workspace": {"obj": abobjs.AB_Workspace},
              "region": {"obj": abobjs.AB_Region},
              "process": {"obj": abobjs.AB_Process},
              "subprocess": {"obj": abobjs.AB_SubProcess},
              "risk": {"obj": abobjs.AB_Risk},
              "assertion": {"obj": abobjs.AB_Assertion},
              "effectiveness_option": {"obj": abobjs.AB_EffectivenessOption},
              "status_option": {"obj": abobjs.AB_StatusOption},
              "test_section": {"obj": abobjs.AB_TestSection},
              "test_type": {"obj": abobjs.AB_TestType},
              "control": {"obj": abobjs.AB_Control},
              "entity": {"obj": abobjs.AB_Entity}
              }

    def __init__(self, cr_data=None, api_info=None, **kwargs):

        self.api_info = api_info
        self.cr_name = cr_data["cr_name"]
        self.cr_data = cr_data

        self.kwargs = kwargs

        self.order = self.kwargs.get("order", self._order)

        self.logger = logging.getLogger("CR:{}:".format(self.cr_name))

        self.roc_objs = dict()

        if self.kwargs.get("make", True) is True:
            self.confirm_rod()

    def confirm_rod(self):

        # Wiping Rods and Starting over
        self.roc_objs = dict()

        for obj_type in self.order.keys():
            self.logger.info("Processing Requests of Type: {}".format(obj_type))

            self.roc_objs[obj_type] = self.roc_obj(obj_type)

    def roc_obj(self, obj_type):

        these_configs = list()

        obj_configs = self.cr_data.get(obj_type, list())

        if isinstance(obj_configs, dict):
            # Turn into a list
            obj_configs = [obj_configs]

        for obj_order in obj_configs:

            order_kwargs = dict(init_action="read",
                                uid=obj_order.get("uid", None),
                                search_name=obj_order.get("name", None))

            order_kwargs_kwargs = dict()

            order_datum = dict(uid=obj_order.get("uid", None),
                               name=obj_order.get("name", None))

            if obj_order.get("cim", False) is True:
                order_kwargs["init_action"] = "readorcreate"

            # Process Includes
            for include_order in obj_order.get("include", list()):

                ias = include_order["as"]
                indx = include_order.get("indx", [0])
                ito = include_order.get("to", "datum")

                if isinstance(indx, int):
                    indx = [indx]

                iobj = include_order.get("obj", None)
                iconst = include_order.get("const", None)

                is_list = include_order.get("is_list", False)

                place_obj = None
                if is_list is True:
                    place_obj = list()


                if iobj is None and iconst is None:
                    # Error
                    ValueError("Rod must have a const or an object specified.")

                # Handle Constants
                if iconst is not None and isinstance(place_obj, list):
                    place_obj.append(iconst)
                elif iconst is not None:
                    place_obj = iconst
                else:
                    # Object Flow
                    if iobj not in self.roc_objs.keys():
                        self.logger.error("Obj {} requested, but hasn't been made yet.".format(iobj))
                    else:
                        for tindx in indx:

                            try:
                                this_obj = self.roc_objs[iobj][tindx]
                            except Exception as e:
                                self.logger.debug(self.roc_objs)
                                raise e

                            if isinstance(place_obj, list):
                                place_obj.append(this_obj)
                            else:
                                place_obj = this_obj
                                # Non list requested only first item needed
                                break

                # I've got my objects let's place this item in datum
                if place_obj is not None:
                    # This will place an empty list.
                    if ito == "datum":
                        order_datum[ias] = place_obj
                    elif ito == "kwargs":
                        order_kwargs_kwargs[ias] = place_obj


            # Now Place Order Datum as Datum
            order_kwargs["datum"] = order_datum

            this_ab_obj = self.order[obj_type]["obj"](api_info=self.api_info, **order_kwargs, **order_kwargs_kwargs)

            these_configs.append(this_ab_obj)

        return these_configs














