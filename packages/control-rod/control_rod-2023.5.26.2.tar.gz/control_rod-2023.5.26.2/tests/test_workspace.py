#!/usr/bin/env python3

import unittest
import importlib.resources
import logging

import ci
import yaml

import abobjs

'''

Needs Workspace Fixes

class WorkspaceTests(unittest.TestCase):

    @classmethod
    def setUp(self):

        self.logger = logging.getLogger("WorkspaceTests")

        with importlib.resources.path(ci, "config.yaml") as test_config_path_gen:
            test_config_path = test_config_path_gen

        with open(test_config_path, "r") as test_config_fobj:
            self.test_config = yaml.safe_load(test_config_fobj)


    def test_pull(self):

        self.logger.info("Testing Workspace Pull")

        test_obj = abobjs.AB_Workspace(control_id=self.test_config["test"]["read_workspace_id"],
                                       api_info=self.test_config["api"])

        self.assertTrue(isinstance(test_obj.id, int))


'''