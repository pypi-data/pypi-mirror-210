#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

class RegionTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("RegionTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing Region Pull")

        test_obj = abobjs.AB_Region(id=self.test_config["test"]["read_region_id"],
                                    api_info=self.test_config["api"])

        #self.logger.debug(test_obj.datum)
        self.assertTrue(isinstance(test_obj.id, int))

    def test_create_delete(self):

        sample_control = {'region_code': 'CRTC',
                          'name': 'Control Rod Test Cycle',
                          'workspace_id': 1}

        create_obj = abobjs.AB_Region(api_info=self.test_config["api"],
                                      datum=sample_control,
                                      init_action="create")

        self.assertTrue(isinstance(create_obj.id, int))
        self.assertTrue(isinstance(create_obj.datum, dict))

        create_obj.datum["name"] = "Changed Name"
        create_obj.update()
        create_obj.get()

        self.assertEqual(create_obj.datum["name"], "Changed Name")

        create_obj.delete()
