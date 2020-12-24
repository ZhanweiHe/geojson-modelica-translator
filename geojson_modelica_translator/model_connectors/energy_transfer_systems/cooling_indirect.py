"""
****************************************************************************************************
:copyright (c) 2019-2020 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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

import os

from geojson_modelica_translator.model_connectors.energy_transfer_systems.energy_transfer_base import (
    EnergyTransferBase
)
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import simple_uuid


class CoolingIndirect(EnergyTransferBase):
    model_name = 'CoolingIndirect'

    def __init__(self, system_parameters):
        super().__init__(system_parameters)
        self.id = 'cooInd_' + simple_uuid()

    def to_modelica(self, scaffold):
        """
        Create indirect cooling models based on the data in the buildings and geojsons

        :param scaffold: Scaffold object, Scaffold of the entire directory of the project.
        """
        cooling_indirect_template = self.template_env.get_template("CoolingIndirectNew.mot")

        ets_data = self.system_parameters.get_param(
            "$.buildings.default.ets_model_parameters.indirect"
        )

        self.run_template(
            template=cooling_indirect_template,
            save_file_name=os.path.join(scaffold.project_path, "Substations", "CoolingIndirect.mo"),
            project_name=scaffold.project_name,
            ets_data=ets_data,
        )

        # now create the Package level package. This really needs to happen at the GeoJSON to modelica stage, but
        # do it here for now to aid in testing.
        package = PackageParser(scaffold.project_path)
        if 'Substations' not in package.order:
            package.add_model('Substations')
            package.save()

        package_models = ['CoolingIndirect']
        ets_package = PackageParser(scaffold.substations_path.files_dir)
        if ets_package.order_data is None:
            ets_package = PackageParser.new_from_template(
                path=scaffold.substations_path.files_dir,
                name="Substations",
                order=package_models,
                within=scaffold.project_name)
        else:
            for model_name in package_models:
                if model_name not in ets_package.order:
                    ets_package.add_model(model_name)
        ets_package.save()

    def get_modelica_type(self, scaffold):
        return f'{scaffold.project_name}.Substations.CoolingIndirect'
