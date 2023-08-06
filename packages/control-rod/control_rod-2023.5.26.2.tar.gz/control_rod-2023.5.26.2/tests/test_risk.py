#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

class RiskTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("RiskTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing Risk Pull")

        test_obj = abobjs.AB_Risk(id=self.test_config["test"]["read_risk_id"],
                                     api_info=self.test_config["api"])

        print(test_obj.datum)

        self.assertTrue(isinstance(test_obj.id, int))

    def test_create_delete(self):

        self.logger.info("Testing Risk Create/Delete")

        sample_control = {"name": "Risk Control Test Suite",
                          "uid": "R3",
                          "process_id": self.test_config["test"]["read_process_id"],
                          "subprocess_id": self.test_config["test"]["read_subprocess_id"]
                          }

        create_obj = abobjs.AB_Risk(api_info=self.test_config["api"],
                                    datum=sample_control,
                                    init_action="create")

        self.assertTrue(isinstance(create_obj.id, int))
        self.assertTrue(isinstance(create_obj.datum, dict))

        search_obj = abobjs.AB_Risk(api_info=self.test_config["api"],
                                    init_action="read",
                                    uid=sample_control["uid"])

        self.assertEqual(create_obj.id, search_obj.id)

        create_obj.datum["name"] = "Changed Name"
        create_obj.update()
        create_obj.get()

        self.assertEqual(create_obj.datum["name"], "Changed Name")

        create_obj.delete()
