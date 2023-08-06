#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

class TestTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("TestsTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing Test Pull Via Controls Datum Pull")

        cd_obj = abobjs.AB_Controls_Data(id=self.test_config["test"]["read_controls_datum_id"],
                                     api_info=self.test_config["api"])

        for this_test in cd_obj.datum["test_ids"]:
            # Do A Forward back
            string_var = "put in test suite\n"
            this_test.datum["results"] = string_var

            this_test.update()

            this_test.get()

            self.assertEqual(this_test.datum["results"], string_var)

            this_test.datum["results"] = "\n"

            this_test.update()
            this_test.get()

            self.logger.warning(this_test.datum)

            self.assertEqual(this_test.datum["results"], "\n")
            break

        self.assertTrue(isinstance(cd_obj.id, int))
