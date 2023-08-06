#!/usr/bin/env python3

import logging
import urllib.parse
import datetime
import json

import requests
import pyjq
import urllib.parse

import abobjs

def fn_register_custom_fields(api_info=None):

    """
    Should Iterate through the Custom Fields And Register their select & multiselect maps in SUBOBJ_LNK
    """

    logger = logging.getLogger("fn_register_custom_fields")

    all_custom_fields = abobjs.AB_Multi(type=abobjs.AB_Custom_Fields, api_info=api_info)

    logger.debug(all_custom_fields.multidatum)

    for x in all_custom_fields.multidatum:
        logger.debug(x.datum)

        if x.datum["type"] in ("Multiselect", "Select"):
            # Add to Map
            abobjs.SUBOBJ_LK[x.datum["attr_key"]] = {"map": x.datum["custom_field_options_map"]}

    logger.debug(abobjs.SUBOBJ_LK)



