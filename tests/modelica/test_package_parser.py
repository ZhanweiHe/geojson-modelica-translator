# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import os
import unittest

from geojson_modelica_translator.modelica.input_parser import PackageParser


class PackageParserTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def test_new_from_template(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'new_model_name', ["model_a", "model_b"], within="SomeWithin"
        )
        package.save()

        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'package.mo')))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'package.order')))

        # check for strings in files
        with open(os.path.join(self.output_dir, 'package.mo')) as f:
            file_data = f.read()
            self.assertTrue('within SomeWithin;' in file_data, 'Incorrect within clause')
            self.assertTrue('package new_model_name' in file_data, 'Incorrect package definition')
            self.assertTrue('end new_model_name;' in file_data, 'Incorrect package ending')

        with open(os.path.join(self.output_dir, 'package.order')) as f:
            self.assertTrue('model_a\nmodel_b' in f.read(), 'Incorrect package order')

    def test_round_trip(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'another_model', ["model_x", "model_y"], within="DifferentWithin"
        )
        package.save()

        # Read in the package
        package = PackageParser(self.output_dir)
        self.assertListEqual(package.order, ["model_x", "model_y"])

    def test_rename_model(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'rename_model', ["model_1", "model_2"], within="RenameWithin"
        )
        package.save()

        package.rename_model('model_1', 'my_super_new_model')
        self.assertEqual(len(package.order), 2)
        self.assertIn('my_super_new_model', package.order)

    def test_add_model(self):
        package = PackageParser.new_from_template(
            self.output_dir, 'so_many_models', ["model_beta", "model_gamma"], within="SoMany"
        )
        package.save()

        package.add_model('model_delta')
        package.add_model('model_alpha', 0)
        self.assertEqual(len(package.order), 4)
        self.assertListEqual(['model_alpha', 'model_beta', 'model_gamma', 'model_delta'], package.order)
