#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

class TestSectionTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("TestSectionTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing Test Section")

        test_obj = abobjs.AB_TestSection(id=self.test_config["test"]["read_test_section_id"],
                                         api_info=self.test_config["api"])

        self.assertTrue(isinstance(test_obj.id, int))

    def test_create_delete(self):

        self.logger.info("Testing Test Create/Delete")

        sample_control = {"name": "CR Testsuite",
                          "uid": "TEST0",
                          "short_name": "CR Tst", "workspace_ids": []
                          #"workspace_ids": [self.test_config["test"]["read_workspace_id"]],
                          }

        create_obj = abobjs.AB_TestSection(api_info=self.test_config["api"],
                                           datum=sample_control,
                                           init_action="create")

        self.assertTrue(isinstance(create_obj.id, int))
        self.assertTrue(isinstance(create_obj.datum, dict))

        search_obj = abobjs.AB_TestSection(api_info=self.test_config["api"],
                                           init_action="read",
                                           uid=sample_control["uid"])

        self.assertEqual(create_obj.id, search_obj.id)

        create_obj.datum["name"] = "Changed Name"
        create_obj.update()
        create_obj.get()

        self.assertEqual(create_obj.datum["name"], "Changed Name")

        create_obj.delete()
