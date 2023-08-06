#!/usr/bin/env python3

import logging
import pyjq


class AB_Multi:
    '''
    Hit an endpoint for a given type and give me a container with all of the objects in that list

    Useful for "give me all the controls".
    '''

    def __init__(self, type=None, api_info=None, filter=None, **kwargs):

        self.logger = logging.getLogger("multi")

        self.api_info = api_info
        self.type = type
        self.filter = filter
        self.metadata = dict(results=0, errors=list())
        self.multidatum = kwargs.get("multidatum", list())

        self.kwargs = kwargs

        self.base_search_obj = self.type(api_info=self.api_info,
                                         multi=True,
                                         max_depth=self.kwargs.get("max_depth", -1),
                                         read_args=self.kwargs.get("read_args", {}))

        for obj in pyjq.all(self.base_search_obj.all_jq, self.base_search_obj.kwargs["all_data"]):

            this_okay = True

            # Future Checks for Okayness based on Filters

            if this_okay is True:
                this_id = obj[self.base_search_obj.id_field]

                this_obj = self.type(id=this_id, api_info=self.api_info)

                self.metadata["results"] += 1
                self.multidatum.append(this_obj)

    def check_filter(self, object):

        okay = True

        # ADD PFE Logic here in the Future

        return okay
