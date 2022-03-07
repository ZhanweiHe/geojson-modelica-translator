"""
****************************************************************************************************
:copyright (c) 2019-2022, Alliance for Sustainable Energy, LLC, and other contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions
and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions
and the following disclaimer in the documentation and/or other materials provided with the
distribution.

Neither the name of the copyright holder nor the names of its contributors may be used to endorse
or promote products derived from this software without specific prior written permission.

Redistribution of this software, without modification, must refer to the software by the same
designation. Redistribution of a modified version of this software (i) may not refer to the
modified version by the same designation, or by any confusingly similar designation, and
(ii) must refer to the underlying software originally provided by Alliance as “URBANopt”. Except
to comply with the foregoing, the term “URBANopt”, or any confusingly similar designation may
not be used to refer to any modified version of this software or any modified version of the
underlying software originally provided by Alliance without the prior written consent of Alliance.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
****************************************************************************************************
"""

import unittest

from geojson_modelica_translator.geojson.schemas import Schemas


class SchemasTest(unittest.TestCase):
    def test_load_schemas(self):
        s = Schemas()
        data = s.retrieve("building")
        self.assertEqual(data["title"], "URBANopt Building")

    def test_invalid_retrieve(self):
        s = Schemas()
        with self.assertRaises(Exception) as context:
            s.retrieve("judicate")
        self.assertEqual("Schema for judicate does not exist", str(context.exception))

    def test_validate_schema(self):
        s = Schemas()
        s.retrieve("building")

        # verify that the schema can validate an instance with simple parameters
        instance = {
            "id": "5a6b99ec37f4de7f94020090",
            "type": "Building",
            "name": "Medium Office",
            "footprint_area": 17059,
            "footprint_perimeter": 533,
            "building_type": "Office",
            "number_of_stories": 3,
            "system_type": "PTAC with district hot water",
            "number_of_stories_above_ground": 3,
            "building_status": "Proposed",
            "floor_area": 51177,
            "year_built": 2010,
        }
        res = s.validate("building", instance)
        self.assertEqual(len(res), 0)

        # bad system_type
        instance["type"] = "MagicBuilding"
        res = s.validate("building", instance)
        self.assertIn("'MagicBuilding' is not one of ['Building']", res[0])
        self.assertEqual(len(res), 1)
