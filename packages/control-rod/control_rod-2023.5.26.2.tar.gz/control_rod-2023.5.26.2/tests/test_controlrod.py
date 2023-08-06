#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

class ControlRodTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("ControlRodTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)

        with importlib.resources.path(ci, "sample_rod.yaml") as test_cr_path_gen:
            test_cr = test_cr_path_gen

        with open(test_cr, "r") as cr_fobj:
            self.cr_config = yaml.safe_load(cr_fobj)


    def test_rod_create_pull(self):

        self.logger.info("Testing Control Create")

        control_rod = abobjs.AB_ControlRod(cr_data=self.cr_config,
                                           api_info=self.test_config["api"])

        self.assertTrue(isinstance(control_rod.roc_objs["region"], list))

        controls_data = abobjs.AB_Controls_Data(api_info=self.test_config["api"],
                                                uid="EA.CRP.S1.CR1")

        print(controls_data.datum)


