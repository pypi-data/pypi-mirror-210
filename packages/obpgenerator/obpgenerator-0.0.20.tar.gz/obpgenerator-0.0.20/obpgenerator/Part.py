import obpgenerator.Layer as Layer
import os

class Start_heat:
    def __init__(self):
        self.file = ""
        self.temp_sensor = "Sensor1"
        self.target_temp = 800 #degree celsius
        self.timeout = 3600 #seconds timeout

class Pre_heat:
    def __init__(self):
        self.file = ""
        self.repetitions = 10 #nmb of times the pre-heat is repeated

class Post_heat:
    def __init__(self):
        self.file = ""
        self.repetitions = 0 #nmb of times the pre-heat is repeated

class Layerfeed:
    def __init__(self):
        self.build_piston_distance = -0.1    # mm
        self.powder_piston_distance = 0.2    # mm
        self.recoater_advance_speed = 200.0  # mm/s
        self.recoater_retract_speed = 200.0  # mm/s
        self.recoater_dwell_time = 0         # milliseconds, wait time in fully advanced position
        self.recoater_full_repeats = 0       # Repeats of the full recoater stroke. No extra powder is added, the powder tank will only be raised once.    
        self.recoater_build_repeats = 0      # Repeated recoater passes over the build plane
        self.triggered_start = True # The actual trigger is defined in the `recoaterservice.yaml` config file


class Part:
    def __init__(self):
        self.start_heat = Start_heat()
        self.pre_heat = Pre_heat()
        self.post_heat = Post_heat()
        self.layer_feed = Layerfeed()

        self.layer_height = 0.2 #mm
        
        self.layers = [] #list of Layers

    def create_from_mplt_paths(self, matplot_paths): 
        #matplot_paths should be array on form [[[path1,path2],[path3]],[[path4]],[[path5],[path6]]]
        for path in matplot_paths:
            self.layers.append(Layer.Layer())
            self.layers[-1].create_from_mplt_paths(path)
            
    def set_layers(self, spacing, manufacturing_settings, size=150, angle_between_layers=0, melt_strategy="point_random", nmb_of_scans=1, sorting_strategy="ramp_manufacturing_settings"):
        angle = 0
        for i in range(len(self.layers)):
            self.layers[i].set_shapes(spacing, size=size, angle=angle)
            self.layers[i].set_manufacturing_settings(manufacturing_settings)
            self.layers[i].set_melt_strategies(melt_strategy)
            self.layers[i].set_nmb_of_scans(nmb_of_scans)
            self.layers[i].sorting_strategy = sorting_strategy
            angle = angle + angle_between_layers
    
    def set_settings(self, manufacturing_settings = None, melt_strategies=None, nmb_of_scans=None):
        #Sets settings for each shape in each layer, the settings should be arrays where the first element in the array is assigned to the
        #first shape in each layer, the second element to the second shape in each layer, and so on. If the array is shorter than the number
        #number of shapes in a layer it will loop from the beginning in the array
        if manufacturing_settings != None:
            for layer in self.layers:
                layer_settings = []
                for idx in range(layer.shapes):
                    layer_settings.append(manufacturing_settings[idx % len(manufacturing_settings)])
                layer.set_manufacturing_settings(layer_settings)
        if melt_strategies != None:
            for layer in self.layers:
                layer_settings = []
                for idx in range(layer.shapes):
                    layer_settings.append(melt_strategies[idx % len(melt_strategies)])
                layer.set_melt_strategies(layer_settings)
        if nmb_of_scans != None:
            for layer in self.layers:
                layer_settings = []
                for idx in range(layer.shapes):
                    layer_settings.append(nmb_of_scans[idx % len(nmb_of_scans)])
                layer.set_nmb_of_scans(layer_settings)

    def create_obps(self):
        for i in range(len(self.layers)):
            self.layers[i].create_obp_elements()

    def export_build_file(self, folder_path, file_name="freemelt_run_file.yml", export_shapes_individual=False):
        
        # Create directory to save obp files
        path = os.path.join(folder_path, "obp_files")
        layer_paths = []
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        
        build_file = []
        build_file.append("build:")
        build_file.append("  start_heat:")
        build_file.append("    file: \"" + self.start_heat.file + "\"")
        build_file.append("    temp_sensor: \"" + self.start_heat.temp_sensor + "\"")
        build_file.append("    target_temperatur: " + str(self.start_heat.target_temp))
        build_file.append("    timeout: " + str(self.start_heat.timeout))
        build_file.append("  preheat:")
        build_file.append("    file: \"" + self.pre_heat.file + "\"")
        build_file.append("    repetitions: " + str(self.pre_heat.repetitions))
        build_file.append("  postheat:")
        build_file.append("    file: \"" + self.post_heat.file + "\"")
        build_file.append("    repetitions: " + str(self.post_heat.repetitions))
        build_file.append("  build:")
        build_file.append("    layers: " + str(len(self.layers)))
        build_file.append("    files:")
        for i in range(len(self.layers)):
            file_path = os.path.join(path, "layer"+str(i)+".obp")
            if export_shapes_individual:
                build_file.append("      -")
                self.layers[i].export_shape_obp(file_path)
                for ii in range(len(self.layers[i].shapes)):
                    build_file.append("        - \"" + "/obp_files/layer"+str(i)+"_"+str(ii)+".obp" + "\"")
            else:
                self.layers[i].export_obp(file_path)
                build_file.append("      - \"" + "/obp_files/layer"+str(i)+".obp" + "\"")
        build_file.append("  layerfeed:")
        build_file.append("    build_piston_distance: " + str(self.layer_feed.build_piston_distance))
        build_file.append("    powder_piston_distance: " + str(self.layer_feed.powder_piston_distance))
        build_file.append("    recoater_advance_speed: " + str(self.layer_feed.recoater_advance_speed))
        build_file.append("    recoater_retract_speed: " + str(self.layer_feed.recoater_retract_speed))
        build_file.append("    recoater_dwell_time: " + str(self.layer_feed.recoater_dwell_time))
        build_file.append("    recoater_full_repeats: " + str(self.layer_feed.recoater_full_repeats))
        build_file.append("    recoater_build_repeats: " + str(self.layer_feed.recoater_build_repeats))
        build_file.append("    triggered_start: " + str(self.layer_feed.triggered_start))

        out_path = os.path.join(folder_path, file_name)
        with open(out_path, 'w') as file:
            for line in build_file:
                file.write(line)
                file.write('\n')
        