"""
****************************************************************************************************
:copyright (c) 2019 URBANopt, Alliance for Sustainable Energy, LLC, and other contributors.

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
import shutil
from teaser.project import Project

from geojson_modelica_translator.model_connectors.base import Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import InputParser

class TeaserConnector(model_connector_base):
    def __init__(self):
        super().__init__(self)

    def mappings(self):
        """
        :return:
        """
        pass

    def add_building(self, urbanopt_building, mapper=None):
        """
        Add building to the translator.

        :param urbanopt_building: an urbanopt_building
        :return:
        """
        # TODO: Need to convert units, these should exist on the urbanopt_building object
        # TODO: Abstract out the GeoJSON functionality
        if mapper is None:
            self.buildings.append({
                "area": urbanopt_building.feature.properties['floor_area'] * 0.092936,  # ft2 -> m2
                "building_id": urbanopt_building.feature.properties['id'],
                "building_type": urbanopt_building.feature.properties['building_type'],
                "floor_height": urbanopt_building.feature.properties['height'] * 0.3048,  # ft -> m
                "num_stories": urbanopt_building.feature.properties['number_of_stories_above_ground'],
                "num_stories_below_grade": urbanopt_building.feature.properties['number_of_stories'] -
                urbanopt_building.feature.properties['number_of_stories_above_ground'],
                "year_built": urbanopt_building.feature.properties['year_built']
            })

    def lookup_building_type(self, building_type):
        if 'office' in building_type.lower():
            return 'office'
        else:
            # TODO: define these mappings 'office', 'institute', 'institute4', institute8'
            return 'office'

    def to_modelica(self, root_building_dir):
        """
        :param root_building_dir: str, root directory where building model will be exported
        :return:
        """
        # Teaser changes the current dir, so make sure to reset it back to where we started
        building_names = []
        curdir = os.getcwd()
        try:
            prj = Project(load_data=True)
            # prj.name = self.building_id

            for building in self.buildings:
                building_name = building['building_id']
                prj.add_non_residential(
                    method='bmvbs',
                    usage=self.lookup_building_type(building['building_type']),
                    name=building_name,
                    year_of_construction=building['year_built'],
                    number_of_floors=building['num_stories'],
                    height_of_floors=building['floor_height'],
                    net_leased_area=building['area'],
                    office_layout=1,
                    window_layout=1,
                    with_ahu=False,
                    construction_type="heavy"
                )
                building_names.append(building_name)

                prj.used_library_calc = 'IBPSA'
                prj.number_of_elements_calc = 2
                prj.merge_windows_calc = False
                # prj.weather_file_path = utilities.get_full_path(
                #     os.path.join(
                #         "data",
                #         "input",
                #         "inputdata",
                #         "weatherdata",
                #         "DEU_BW_Mannheim_107290_TRY2010_12_Jahr_BBSR.mos"))

            # calculate the properties of all the buildings and export to the Buildings library
            prj.calc_all_buildings()
            prj.export_ibpsa(
                library="Buildings",
                path=os.path.join(curdir, root_building_dir)
            )
        finally:
            os.chdir(curdir)

        self.post_process(root_building_dir, building_names)
        # TODO: Move the files anywhere? Add in the ETS?
        # TODO: Remove building names in children files.
        # TODO: move internal gains to the Resources/Data/Loads/ProjectXXX -- MW either is correct. Library is typically

    def post_process(self, root_building_dir, building_names):
        """
        Cleanup the export of the TEASER files into a format suitable for the district-based analysis. This includes
        the following:

            * Update the partial to inherit from the GeojsonExport class defined in MBL.
            * Rename the files to remove the names of the buildings
            * Move the files to the Loads level and remove the Project folder (default export method from TEASER)
            * Add heat port
            * Add return temperature
            * Remove weaDat and rely on weaBus
        :param building_names: list, names of the buildings that need to be cleaned up after export
        :return:
        """
        file_exts = ['Floor.mo', 'ICT.mo', 'Meeting.mo', 'Office.mo', 'Restrooms.mo', 'Storage.mo']

        # move files to loads level
        for b in building_names:
            shutil.move(
                os.path.join(root_building_dir, f'Project/B{b}/B{b}_Models'), os.path.join(root_building_dir, f'B{b}')
            )

            # process each of the building models
            for file_ext in file_exts:
                filename = os.path.join(root_building_dir, f'B{b}/B{b}{file_ext}')
                new_filename = os.path.join(root_building_dir, f'B{b}/{file_ext}')
                if os.path.exists(os.path.join(root_building_dir, filename)):
                    mofile = InputParser(filename)
                    mofile.save_as(new_filename)
                    # os.remove(filename)


    def to_citygml(self, project, root_directory, filename='citygml.xml'):
        """
        Export a single project Teaser project to citygml. Note that you much pass in a full Teaser project
        to be converted since, at the moment, there is no member variable holding the Teaser project.

        :param project: Teaser Project, project to convert to CityGML.
        :param root_directory: str, root directory where building model will be exported
        :param filename (optional): str, filename to save to
        :return: None
        """
        project.save_citygml(filename, root_directory)
