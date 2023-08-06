#!/usr/bin/env python3
import io
import unittest
import importlib.resources
import logging
import uuid

import ci
import yaml

import abobjs

class TestFiles(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("TestsTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing File Pull Via Controls Datum Pull")

        #cd_obj = abobjs.AB_Controls_Data(id=self.test_config["test"]["read_controls_datum_id"],
        #                             api_info=self.test_config["api"])

        cd_obj = abobjs.AB_Controls_Data(id=1187,
                                         api_info=self.test_config["api"])


        # Upload A File
        with io.StringIO() as sample_fobj:
            sample_fobj.write("This is a Sample Test File Created")
            sample_fobj.seek(0)

            cd_obj.upload_file(sample_fobj, "{}.txt".format(str(uuid.uuid4())))

            cd_obj.datum["test_ids"][0].upload_file(sample_fobj, "{}.txt".format(str(uuid.uuid4())))

        self.logger.info(cd_obj.datum)

        for this_file in cd_obj.datum["file_ids"]:
            # Do A Forward back
            self.logger.info("Files ID: {}".format(this_file.id))


        self.assertTrue(isinstance(cd_obj.id, int))
