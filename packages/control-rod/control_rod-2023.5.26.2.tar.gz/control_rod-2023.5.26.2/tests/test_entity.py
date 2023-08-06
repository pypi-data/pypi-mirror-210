#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

class EntityTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("EntityTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing Entity Pull")

        test_obj = abobjs.AB_Entity(id=self.test_config["test"]["read_entity_id"],
                                    api_info=self.test_config["api"])

        print(test_obj.datum)
        self.assertTrue(isinstance(test_obj.id, int))

    def test_create_delete(self):

        sample_entity = {"name": "test Control Set 2",
                         "entity_code": "TCS4",
                         "region_id": self.test_config["test"]["read_region_id"]}

        create_obj = abobjs.AB_Entity(api_info=self.test_config["api"],
                                      datum=sample_entity,
                                      init_action="create")

        self.assertTrue(isinstance(create_obj.id, int))
        self.assertTrue(isinstance(create_obj.datum, dict))

        create_obj.datum["name"] = "Changed Name"
        create_obj.update()
        create_obj.get()

        self.assertEqual(create_obj.datum["name"], "Changed Name")

        create_obj.delete()
