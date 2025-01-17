# :copyright (c) URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.
# See also https://github.com/urbanopt/geojson-modelica-translator/blob/develop/LICENSE.md

import unittest
from pathlib import Path

from geojson_modelica_translator.modelica.csv_modelica import CSVModelica


class CsvModelicaTest(unittest.TestCase):
    def setUp(self):
        self.data_dir = Path(__file__).parent / 'data'
        self.output_dir = Path(__file__).parent / 'output'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def test_csv_does_not_exist(self):
        with self.assertRaises(Exception) as context:
            input_file = Path(self.data_dir) / 'DNE.csv'
            CSVModelica(input_file)
        self.assertIn("Unable to convert CSV file because this path does not exist:", str(context.exception))

    def test_misshapen_csv_fails_gracefully(self):
        with self.assertRaises(Exception) as context:
            input_file = Path(self.data_dir) / 'misshapen_building_loads.csv'
            # This input file has a typo in a column name and a missing column. Each will cause the Exception.
            CSVModelica(input_file)
            self.assertIn(
                "Columns are missing or misspelled in your file:", str(
                    context.exception))

    def test_csv_modelica_at_15_min_timestep(self):
        input_file = Path(self.data_dir) / 'building_loads_15min_snippet.csv'
        output_modelica_file_name = Path(self.output_dir) / 'modelica_timestep.csv'

        csv_converter = CSVModelica(input_file)
        # save the updated time series to the output directory of the test folder
        csv_converter.timeseries_to_modelica_data(output_modelica_file_name)
        self.assertTrue(output_modelica_file_name.exists())

        # check if a string is in there
        with open(output_modelica_file_name, 'r') as f:
            data = f.read()
            self.assertTrue('14400,41.8,82.2,1.659,14.7,6.7,1.375' in data)
            self.assertTrue('28800,37.7,82.2,0.721,14.9,6.7,2.018' in data)

    def test_csv_modelica_at_60_min_timestep(self):
        input_file = Path(self.data_dir) / 'building_loads_snippet.csv'
        output_modelica_file_name = Path(self.output_dir) / 'modelica.csv'

        csv_converter = CSVModelica(input_file)
        # save the updated time series to the output directory of the test folder
        csv_converter.timeseries_to_modelica_data(output_modelica_file_name)
        self.assertTrue(output_modelica_file_name.exists())

        # check if a string is in there
        with open(output_modelica_file_name, 'r') as f:
            data = f.read()
            self.assertTrue('18000,41.9,82.2,1.392,14.6,6.7,1.648' in data)
            self.assertTrue('111600,57.2,82.2,5.784,16.2,6.7,3.062' in data)
            self.assertFalse('9900,40.1,82.2,0.879,14.9,6.7,1.512' in data)

    def test_csv_modelica_at_60_min_timestep_with_Eplus_file(self):
        input_file = Path(self.data_dir) / 'mfrt.csv'
        output_modelica_file_name = Path(self.output_dir) / 'mfrt_output.csv'

        csv_converter = CSVModelica(input_file)
        # save the updated time series to the output directory of the test folder
        csv_converter.timeseries_to_modelica_data(output_modelica_file_name)
        self.assertTrue(output_modelica_file_name.exists())

        # check if a string is in there
        with open(output_modelica_file_name, 'r') as f:
            data = f.read()
            self.assertTrue('18000,42.3,55.0,15.8,6.7,8.275,0.2' in data)
            self.assertTrue('111600,41.9,55.0,15.1,6.7,12.32,0.021' in data)

    def test_csv_modelica_no_overwrite(self):
        with self.assertRaises(Exception) as context:
            input_file = Path(self.data_dir) / 'building_loads_snippet.csv'
            csv_converter = CSVModelica(input_file)
            csv_converter.timeseries_to_modelica_data(output_modelica_file_name, overwrite=False)
            self.assertIn(
                "Output file already exists and overwrite is False:", str(
                    context.exception))
