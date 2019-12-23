import os
import shutil
import json

from jinja2 import FileSystemLoader, Environment

from geojson_modelica_translator.model_connectors.base import Base as model_connector_base
from geojson_modelica_translator.modelica.input_parser import PackageParser
from geojson_modelica_translator.utils import ModelicaPath

class ETS_Template():
    '''This class will template the ETS modelica model.'''
    def __init__(self, thermal_junction_properties_geojson, system_parameters_geojson, ets_from_building_modelica):
        super().__init__()
        '''
        thermal_junction_properties_geojson contains the ETS at brief and at higher level;
        system_parameters_geojson contains the ETS with details                          ;
        ets_from_building_modelica contains the modelica model of ETS                    ;
        '''
        self.thermal_junction_properties_geojson = thermal_junction_properties_geojson
        self.system_parameters_geojson = system_parameters_geojson
        self.ets_from_building_modelica = ets_from_building_modelica

        #print ( "Yanfei-path: ",  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates') )

        self.template_env = Environment(
            loader=FileSystemLoader(searchpath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
        )


        print ("@@@@@@you are good here!!!!", self.template_env)

    def check_ets_thermal_junction(self):
        '''check if ETS info are in thermal-junction-geojson file'''
        with open(self.thermal_junction_properties_geojson,'r') as f:
            data = json.load(f)

        ets_general = False
        for key, value in data.items():
            if key == 'definitions':
                # three levels down to get the ETS signal
                junctions = data["definitions"]["ThermalJunctionType"]["enum"]
                if 'ETS' in junctions:
                    ets_general=True
                    print ("ETS is there!!!")
            else:
                pass

        return ets_general

    def check_system_parameters(self):
        '''check detailed parameters of ETS'''
        with open(self.system_parameters_geojson, 'r') as f:
            data = json.load(f)

        ets_details=False
        for key, value in data.items():
            #print (key, " <==> " ,value)
            # four levels down to get the details
            ets_details = data["definitions"]["building_def"]["properties"]["ets"]
            print (ets_details)
            if ets_details:
                print ("ETS details are here!!!")

        return ets_details

    def check_ets_from_building_modelica(self):
        '''check if ETS-indirectCooling are in modelica building library'''
        ets_modelica_available = os.path.isfile(self.ets_from_building_modelica)
        #print ("ets-available: ", ets_modelica_available)

        return ets_modelica_available

    def to_modelica(self):
        '''convert ETS json to modelica'''
        ets_modelica=""
        if self.check_ets_from_building_modelica():
            with open(self.ets_from_building_modelica) as f:
                ets_modelica = f.read()
                #print ( ets_modelica )
        else:
            pass

        curdir = os.getcwd()
        print("Yanfei-2: ", curdir)
        #loads_root_path = os.path.join(root_building_dir, project_name, 'Loads')
        ets_template = self.template_env.get_template('CoolingIndirect.mot')
        #print ("Yanfei-2: ", curdir)

        building_names = []
        ets_data = {
            "Q_flow_nominal": [8000],
            "eta_efficiency": [0.666],
            "NominalFlow_district": [0.666],
            "NominalFlow_buiding":[0.666],
            "PressureDrop_Valve": [888],
            "PressureDrop_HX_Secondary": [999],
            "PressureDrop_HX_Primary": [999],

        }

        file_data = ets_template.render(
            ets_data=ets_data
        )

        with open(os.path.join(os.path.join(os.getcwd(), 'ets_cooling_indirect.mo')), 'w') as f:
            f.write(file_data)

        return ets_modelica

    def connect(self):
        '''connect ETS-modelica to building-modelica (specifically TEASER modelica)'''
        pass


######################################################################################################################
######                                     For local test only                         ######
######################################################################################################################

thermal_junction_properties_geojson = "/home/Yanfei_Projects/geojson-modelica-translator/geojson_modelica_translator/geojson/data/schemas/thermal_junction_properties.json"
system_parameters_geojson = "/home/Yanfei_Projects/geojson-modelica-translator/geojson_modelica_translator/system_parameters/schema.json"
ets_from_building_modelica = "/home/Yanfei_Projects/geojson-modelica-translator/geojson_modelica_translator/modelica/buildingslibrary/Buildings/Applications/DHC/EnergyTransferStations/CoolingIndirect.mo"
print ( os.getcwd() )
ets = ETS_Template(thermal_junction_properties_geojson, system_parameters_geojson, ets_from_building_modelica )
#ets.check_ets_thermal_junction()
#ets.check_system_parameters()
ets.check_ets_from_building_modelica()
ets.to_modelica()

