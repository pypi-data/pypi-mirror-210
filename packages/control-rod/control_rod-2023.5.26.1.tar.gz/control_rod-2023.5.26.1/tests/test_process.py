#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

class ProcessTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("ProcessTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing Process Pull")

        test_obj = abobjs.AB_Process(id=self.test_config["test"]["read_process_id"],
                                     api_info=self.test_config["api"])

        self.logger.debug(test_obj.datum)
        self.assertTrue(isinstance(test_obj.id, int))

    def test_create_delete(self):

        sample_process = {
            "uid": "CRTP",
            "name": "Control Rod Test Process",
            "process_type_ids": []
        }

        create_obj = abobjs.AB_Process(api_info=self.test_config["api"],
                                       datum=sample_process,
                                       init_action="create")

        self.assertTrue(isinstance(create_obj.id, int))
        self.assertTrue(isinstance(create_obj.datum, dict))

        create_obj.datum["name"] = "Changed Name"
        create_obj.update()
        create_obj.get()

        self.assertEqual(create_obj.datum["name"], "Changed Name")

        create_obj.delete()
