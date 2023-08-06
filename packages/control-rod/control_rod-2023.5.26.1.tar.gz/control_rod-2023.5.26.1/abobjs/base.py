#!/usr/bin/env python3

import logging
import urllib.parse
import datetime
import json
import time

import requests
import pyjq
import xmltodict

import abobjs


class AB_Base:
    '''
    Base Object for API Calls
    '''

    # People need to set these three
    _endpoint = None
    _single = None
    _name = "base"
    _file_modal = None
    _fileable_type = None

    # Base Stuff Override as needed
    _datefront = "%Y-%m-%dT%H:%M:%S"
    _mslength = 3
    _date_keys = ["created_at", "updated_at", "deleted_at", "effective_date",
                  "baseline_date", "last_modification_date", "last_review_date"]

    _create_null_keys = ["created_at", "deleted_at", "updated_at"]
    _read_args = dict()
    _allow_full_update = True

    _uid_field = "uid"
    _id_field = "id"
    _name_field = "name"
    _max_depth = 2

    _strips = ["_permissions"]

    _upload_endpoint = "/api/v1/files/s3_upload_signature"
    _file_notify_endpoint = "/api/v1/files"
    _user_endpoint = "/api/v1/user_stats"

    #
    _post_upload_post_headers = {}
    _upload_file_headers = {}
    _get_params = {}
    _create_params = {}
    _search_params = {}

    _stich_def = []

    def __init__(self, id=None, api_info=None, **kwargs):

        self.api_info = api_info
        self.id = id
        self.datum = kwargs.get("datum", dict())

        self.kwargs = kwargs

        # Dunder Handling
        self.endpoint = self.kwargs.get("endpoint", self._endpoint)
        self.single = self.kwargs.get("single", self._single)
        self.all_jq = self.kwargs.get("all_jq", self.single.replace("0", ""))
        self.name = self.kwargs.get("name", self._name)
        self.datefront = self.kwargs.get("datefront", self._datefront)
        self.mslength = self.kwargs.get("mslength", self._mslength)
        self.date_keys = self.kwargs.get("date_keys", self._date_keys)
        self.strips = self.kwargs.get("strips", self._strips)
        self.uid_field = self.kwargs.get("uid_field", self._uid_field)
        self.id_field = self.kwargs.get("id_field", self._id_field)
        self.name_field = self.kwargs.get("name_field", self._name_field)
        self.create_null_keys = self.kwargs.get("create_null_keys", self._create_null_keys)
        self.read_args = self.kwargs.get("read_args", self._read_args)
        self.max_depth = self.kwargs.get("max_depth", self._max_depth)
        self.allow_full_update = self.kwargs.get("allow_full_update", self._allow_full_update)
        self.file_modal = self.kwargs.get("file_modal", self._file_modal)
        self.fileable_type = self.kwargs.get("fileable_type", self._fileable_type)
        self.user_endpoint = self.kwargs.get("user_endpoint", self._user_endpoint)
        self.file_notify_endpoint = self.kwargs.get("file_notify_endpoint", self._file_notify_endpoint)
        self.stich_def = self.kwargs.get("stich_def", self._stich_def)

        self.headers = {"Authorization": self.api_info["ab_token"],
                        "User-Agent": self.kwargs.get("user_agent", abobjs.USER_AGENT),
                        **self.api_info.get("headers", {})}

        # Custom Headers
        self.custom_params = {"get_params": self.kwargs.get("get_params", self._get_params),
                              "create_params": self.kwargs.get("create_params", self._create_params),
                              "search_params": self.kwargs.get("search_params", self._search_params)
                              }

        self.logger = logging.getLogger("AB:{}".format(self.name))

        self.my_user_id = self.user_id()

        ignore_read = False
        self.init_action_taken = "none"

        if self.kwargs.get("init_action", "read") in ("read", "readorcreate") and self.id is None:
            # I didn't get an ID
            if self.kwargs.get("uid", None) is not None or \
                    self.kwargs.get("search_name", None) is not None or \
                    self.kwargs.get("search_complex", None) is not None or \
                    self.kwargs.get("multi", False) is True:

                # I searched for and found (or not) a result
                try:
                    self.id = self.search()
                except Exception as error_in_search:
                    self.logger.debug(error_in_search)
                    raise error_in_search

                self.init_action_taken = "read"

                self.logger.info("Found ID : {} on search.".format(self.id))

                if self.kwargs.get("init_action", "read") == "readorcreate" and self.id is None:
                    # If I didn't find a result and it's requested, let's create based on the data.
                    self.id, self.datum = self.create()

                    self.init_action_taken = "create"
                    # Don't try to read twice, that's ridiculous
                    ignore_read = True
            else:
                self.logger.warning("Read requested, but insufficient data for search given.")

        if self.kwargs.get("init_action", "read") == "read" and self.id is not None and ignore_read is False:
            self.id, self.datum = self.get()
            self.init_action_taken = "read"
        elif self.kwargs.get("init_action", "read") == "create":
            self.id, self.datum = self.create()
            self.init_action_taken = "create"

    def user_id(self):

        self_user_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                                  self.user_endpoint)

        if self.kwargs.get("my_user_id", None) is not None:
            this_userid = self.kwargs["my_user_id"]
        else:
            try:
                whoami_request = requests.get(self_user_endpoint, headers=self.headers)
            except Exception as error:
                self.logger.error("Error when Information about Myself: {}".format(error))
                self.logger.debug("I'm having an existential crisis...")
                raise error
            else:
                self.logger.debug(whoami_request.status_code)
                if whoami_request.status_code != requests.codes.ok:
                    raise ValueError()

                self.logger.debug(whoami_request.json())
                user_data = whoami_request.json()["user_stats"]

                if len(user_data) == 0:
                    # Set Default UID of 1
                    this_userid = 1
                else:
                    this_userid = user_data[0].get("user_id", 1)

        return this_userid

    def __str__(self):

        return "{} : {}".format(self.name, self.id)

    def delete(self):

        """
        Delete this Control
        :return:
        """

        control_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                                "{}/{}".format(self.endpoint, self.id))

        try:
            data_request = requests.delete(control_endpoint, headers=self.headers)
        except Exception as error:
            self.logger.error("Error when requesting delete about Control: {}".format(self.id))
        else:
            self.logger.debug(data_request.status_code)
            if data_request.status_code != requests.codes.ok:
                raise ValueError()

        return data_request.status_code

    def search(self):

        '''
        Search All items for a particular item.
        :return:
        '''

        search_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                               self.endpoint)

        try:
            data_request = requests.get(search_endpoint, headers=self.headers,
                                        params={**self.custom_params["search_params"], **self.read_args})
        except Exception as error:
            self.logger.error("Error when requesting update about Control: {}".format(self.id))
            self.logger.debug("Error Message: {}".format(error))
        else:
            if data_request.status_code != requests.codes.ok:
                self.logger.error("Unable to Search {} for Data".format(self.name))
                self.logger.debug(data_request.text)
                raise ValueError()
            else:
                self.kwargs["all_data"] = data_request.json()

        found_item = None
        self.logger.debug("All JQ: {}".format(self.all_jq))
        self.logger.debug(self.kwargs["all_data"])
        for potential in pyjq.all(self.all_jq, self.kwargs["all_data"]):
            if self.kwargs.get("uid", None) is not None:
                if potential.get(self.uid_field, None) == self.kwargs["uid"]:
                    found_item = potential
                    break
            elif self.kwargs.get("search_name", None) is not None:
                if potential.get(self.name_field, None) == self.kwargs["search_name"]:
                    found_item = potential
                    break
            elif self.kwargs.get("search_complex", None) is not None:
                self.logger.debug("Doing Complex Search: {}".format(potential))
                all_passed = True
                for k, v in self.kwargs["search_complex"].items():
                    compare_value = potential.get(k, None)

                    if isinstance(compare_value, list):
                        self.logger.error("List Values can't be compared at this time.")
                        # TODO add in/only/not logic for lists
                        all_passed = False
                        break

                    if isinstance(v, abobjs.AB_Base):
                        if compare_value == v.id:
                            # This one passed Continue to check the other items in search_complex
                            pass
                        else:
                            self.logger.debug("{} {} != {}".format(k, compare_value, v.id))
                            all_passed = False
                            break
                    else:
                        if compare_value == v:
                            # This one Passed Continue to Check the other items in search_complex
                            pass
                        else:
                            self.logger.debug("{} {} != {}".format(k, compare_value, v))
                            all_passed = False
                            break

                if all_passed is True:
                    self.logger.debug("Found object via complex match {}".format(self.kwargs["search_complex"]))
                    found_item = potential
                    break

            elif self.kwargs.get("multi", False) is True:
                # This is a multi request, we're going to use the results from kwargs["all_data"] So we just want
                # to leave as soon as possible.
                found_item = potential
                break

            else:
                # Continue to the Next Item to search for it.
                pass

        found_id = None

        if found_item is None:
            self.logger.debug("Unable to Search for and Find a {} with given characteristics.".format(self.name))
        else:
            found_id = found_item[self.id_field]

        return found_id

    def update(self, only_fields=None):

        """
        Update Control Data with New Data
        :return:
        """

        control_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                                "{}/{}".format(self.endpoint, self.id))

        all_put = self.serialize(full_json=False)
        if only_fields is None:
            put_data = {self.name: all_put}
        elif only_fields is None and self.allow_full_update is False:
            raise ValueError("Updates require specific field(s) for this type.")
        else:
            put_data = {self.name: {k: v for k, v in all_put.items() if k in only_fields}}

        self.logger.debug(put_data)

        try:
            data_request = requests.put(control_endpoint, headers=self.headers, json=put_data)
        except Exception as error:
            self.logger.error("Error when requesting update about Control: {}".format(self.id))
            self.logger.debug("Error Message: {}".format(error))
        else:
            self.logger.debug("Create Response: {}".format(data_request.status_code))
            if data_request.status_code != requests.codes.ok:
                self.logger.debug(data_request.text)
                raise ValueError()
            else:
                self.logger.debug("Created Control Verbose : {}".format(data_request.json()))
                control_data = pyjq.first(self.single, data_request.json())

                self.logger.debug(control_data)

                obj_cont_data = self.objectify_datum(control_data)

        return obj_cont_data[self.id_field], obj_cont_data

    def create(self):

        """
        Delete this Control
        :return:
        """

        control_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                                self.endpoint)

        self.logger.debug("Create URL : {}".format(control_endpoint))

        post_data = {self.name: self.serialize(full_json=False)}

        self.logger.debug("Create Post Data: {}".format(json.dumps(post_data, default=str)))

        try:
            data_request = requests.post(control_endpoint, headers=self.headers, json=post_data)
        except Exception as error:
            self.logger.error("Error when requesting delete about Control: {}".format(self.id))
            self.logger.debug("Error Message: {}".format(error))
        else:
            self.logger.debug("Create Response: {}".format(data_request.status_code))
            if data_request.status_code != requests.codes.ok:
                self.logger.debug(data_request.text)
                raise ValueError("{} create erorr {}".format(self.name, data_request.text))
            else:
                self.logger.debug("Created Control Verbose : {}".format(data_request.json()))
                print(data_request.json())
                control_data = pyjq.first(self.single, data_request.json())

                self.logger.debug(control_data)

                obj_cont_data = self.objectify_datum(control_data)

        return obj_cont_data[self.id_field], obj_cont_data

    def objectify_datum(self, straight_data):

        objectified = straight_data

        current_depth = self.kwargs.get("depth", 0)

        if self.kwargs.get("depth", 0) < self.max_depth:
            for key, desired_obj in abobjs.SUBOBJ_LK.items():
                do_replace = False
                subobj = None
                compare_data = None
                if key in straight_data.keys():
                    compare_data = straight_data[key]
                    do_replace = True
                elif key in straight_data.get("field_data", {}).keys():
                    compare_data = straight_data["field_data"][key]
                    do_replace = True
                    subobj = "field_data"

                if do_replace:
                    if isinstance(compare_data, list):
                        # Replace List of Items
                        replace_with = list()
                        for x in compare_data:
                            if "map" in desired_obj.keys() and x in desired_obj["map"].keys():
                                replace_with.append(desired_obj["map"][x])
                            elif "obj" in desired_obj.keys():
                                replace_with.append(desired_obj["obj"](id=x, init_action="read",
                                                                       api_info=self.api_info,
                                                                       depth=current_depth + 1,
                                                                       my_user_id=self.my_user_id))
                            else:
                                replace_with.append(x)
                    elif isinstance(compare_data, int):
                        # Replace Single Item
                        if "map" in desired_obj.keys() and compare_data in desired_obj["map"].keys():
                            replace_with = (desired_obj["map"][compare_data])
                        elif "obj" in desired_obj.keys():
                            replace_with = desired_obj["obj"](id=straight_data[key], init_action="read",
                                                          api_info=self.api_info,
                                                          depth=current_depth + 1,
                                                          my_user_id=self.my_user_id)
                        else:
                            replace_with = compare_data
                    else:
                        replace_with = compare_data

                    if subobj is None:
                        objectified[key] = replace_with
                    else:
                        objectified[subobj][key] = replace_with

        else:
            self.logger.debug("Because of Depth {}, not Enumerating type : {}".format(current_depth, self.name))

        for key in self.date_keys:
            if key in objectified.keys():
                if objectified[key] is not None:
                    objectified[key] = self.dateread(straight_data[key])

        # Strip out Unwanted Bits.
        for strip in self.strips:
            if strip in objectified.keys():
                del objectified[strip]

        return objectified

    def get(self):

        control_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                                "{}/{}".format(self.endpoint, self.id))

        self.logger.debug(control_endpoint)

        try:
            data_request = requests.get(control_endpoint,
                                        headers=self.headers,
                                        params={**self.custom_params["get_params"], **self.read_args})
        except Exception as error:
            self.logger.error("Error when requesting data about Control: {}".format(self.id))
            raise error
        else:
            self.logger.debug(data_request.status_code)
            if data_request.status_code != requests.codes.ok:
                self.logger.error("Unable to Get Data for {} {}".format(self.name, self.id))
                self.logger.info("Error: {}".format(data_request.text))
                raise ValueError()
            else:
                f_req_data = data_request.json()
                self.logger.debug("Verbose Data {}".format(data_request.json()))
                self.kwargs["full_single"] = data_request.json()
                control_data = pyjq.first(self.single, data_request.json())

                for stich_cfg in self.stich_def:
                    source = stich_cfg["source"]
                    idfield = stich_cfg["idfield"]
                    val = stich_cfg["val"]
                    isjqval = stich_cfg.get("isjqval", False)

                    map = dict()

                    if isinstance(f_req_data, dict):
                        if source in f_req_data.keys() and isinstance(f_req_data[source], (list,tuple)):
                            for x in f_req_data[source]:
                                self.logger.debug(x)
                                if isjqval is True:
                                    map[x[idfield]] = pyjq.one(val, x)
                                elif isinstance(x, dict):
                                    map[x[idfield]] = x.get(val, None)
                                else:
                                    map[x[idfield]] = None

                    control_data["{}_map".format(source)] = map

                obj_cont_data = self.objectify_datum(control_data)

                # Add Stiches Here
                self.logger.debug(data_request.json())

        return self.id, obj_cont_data

    def dateread(self, datestring):

        """
        Reads AB Datestring with miliseconds and converts it to datetime object

        :param datestring:
        :return:
        """

        this_date = None

        try:
            front, back = datestring.split(".")
        except ValueError as abnormal_date:
            self.logger.warning("Abnormal Date String: {}".format(datestring))

            try:
                this_date = datetime.datetime.strptime("%Y-%m-%d", datestring)
            except Exception as not_secondary_date:
                self.logger.warning("Abnormal Date String not day, returning as string: {}".format(datestring))
                this_date = datestring
        else:
            this_ms = int("{}000".format(back.strip("Z")))
            this_date = datetime.datetime.strptime(front, self.datefront)

            this_date.replace(microsecond=this_ms)

        return this_date

    def datewrite(self, dateobj):

        """
        Reads a Datetime and returns it in the format that Datestring Needs

        :param dateobj:
        :return:
        """

        datestring = None

        if dateobj is not None:

            try:
                frontdatestring = dateobj.strftime(self.datefront)
            except Exception as date_error:
                self.logger.error("Unable to Date Object : {}".format(dateobj))
                self.logger.error("Type of Bad Date : {}".format(type(dateobj)))
                raise ValueError(str(date_error))

            backdatestring = ".{}Z".format(str(dateobj.microsecond)[:self.mslength])

            datestring = "{}{}".format(frontdatestring, backdatestring)

        return datestring

    def serialize(self, full_json=True, cust_data=False):

        if cust_data is False:
            to_serialize = self.datum
        else:
            to_serialize = cust_data

        # Format Dates Properly
        for date_key in self.date_keys:
            if date_key in to_serialize:
                to_serialize[date_key] = self.datewrite(to_serialize[date_key])

        # Serialize Objects
        for key, val in to_serialize.items():

            if isinstance(val, abobjs.AB_Base) is True:
                to_serialize[key] = val.id

            if isinstance(val, list) is True:
                new_val = list()

                for x in val:
                    if isinstance(x, abobjs.AB_Base):
                        new_val.append(x.id)
                    else:
                        new_val.append(x)

                to_serialize[key] = new_val

        # Make Requested Null Keys
        for nk in self.create_null_keys:
            if nk not in to_serialize:
                to_serialize[nk] = None

        # Renamed Name/UID if needed
        if self.uid_field != "uid" and self.uid_field not in to_serialize.keys() and "uid" in to_serialize.keys():
            to_serialize[self.uid_field] = to_serialize.pop("uid")
        if self.name_field != "name" and self.name_field not in to_serialize.keys() and "name" in to_serialize.keys():
            to_serialize[self.name_field] = to_serialize.pop("name")

        if full_json is True:
            json_string = json.dumps(to_serialize, default=str)
        else:
            # Return Dictionary
            json_string = to_serialize

        return json_string

    def upload_file(self, fileobj, file_name):

        """
        Uploads Given FileObj to a parent object

        :param fileobj:
        :param parent_object: ABBase object to attach new file too.
        :param parent_id:
        :return:
        """

        uploaded = False

        if self.file_modal is None or self.fileable_type is None:
            self.logger.error(
                "Unable to Upload File to {} as it does not have a defined modal name.".format(self.name))

        else:

            # I have a Modal
            get_upload_sig_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                                           self._upload_endpoint)

            self.logger.debug(get_upload_sig_endpoint)

            upload_sig_params = {"file_name": file_name,
                                 "model_name": self.file_modal,
                                 "model_id": int(self.id)}

            try:
                upload_sig_request = requests.post(get_upload_sig_endpoint,
                                                   headers=self.headers,
                                                   data=upload_sig_params)

            except Exception as error:
                self.logger.error("Error when Upload Signature: {}".format(error))
                raise error
            else:
                self.logger.debug(upload_sig_request.status_code)
                if upload_sig_request.status_code != requests.codes.ok:
                    raise ValueError()
                else:
                    upload_request_data = upload_sig_request.json()

                    self.logger.info(upload_request_data)

                    try:
                        upload_request = requests.post(upload_request_data["url"],
                                                       data=upload_request_data["formData"],
                                                       files={"file": (file_name, fileobj)})

                        self.logger.debug(upload_request.url)


                    except Exception as upload_error:
                        self.logger.error("Unable to Upload File with error: {}".format(upload_error))
                        raise upload_error
                    else:
                        self.logger.debug("AWS Upload Response: {}".format(upload_request.status_code))
                        self.logger.debug("AWS Upload Response: {}".format(upload_request.text))
                        if upload_request.status_code != int(upload_request_data["formData"]["success_action_status"]):
                            raise ValueError()
                        else:
                            uploaded_response = dict(xmltodict.parse(upload_request.text)["PostResponse"])

                            self.logger.debug("Uploaded File : {}".format(uploaded_response))

                            self.post_upload_post(file_name, upload_request_data["formData"], uploaded_response)

                            uploaded = True

                            # Refresh My Object
                            self.id, self.datum = self.get()

        return uploaded

    def post_upload_post(self, file_name, form_data, response_data):

        file_post_data = {"file": {
            "_permissions": {},
            "updated_at": None,
            "deleted_at": None,
            "local_folder_path": "",
            "comments": None,
            "embed_url": None,
            "thumb_url": None,
            "image_url": None,
            "meta": {},
            "creator_user_id": None,
            "created_at": self.datewrite(datetime.datetime.now()),
            "fileable_id": self.id,
            "fileable_type": self.fileable_type,
            "name": file_name,
            "size": "1",
            "type": "",
            "key": form_data["key"],
            "url": response_data["Location"],
            "storage_type": "s3",
            "user_agent": self.kwargs.get("user_agent", abobjs.USER_AGENT),
            "upload_user_id": "1"
        }}

        fn_endpoint = urllib.parse.urljoin(self.api_info.get("base_domain", None),
                                           self.file_notify_endpoint)

        self.logger.debug(file_post_data)

        try:
            fn_request = requests.post(fn_endpoint,
                                       headers=self.headers,
                                       json=file_post_data)
        except Exception as error:
            self.logger.error("File Notify Post Error: {}".format(error))
            raise error
        else:
            self.logger.debug(fn_request.status_code)
            if fn_request.status_code != requests.codes.ok:
                self.logger.error(fn_request.json())
                raise ValueError("Unable to Post about Uploaded File")

            self.logger.debug("Created File Information: {}".format(fn_request.json()))

        return
