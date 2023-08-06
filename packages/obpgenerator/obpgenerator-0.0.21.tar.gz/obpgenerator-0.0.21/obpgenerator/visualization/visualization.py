import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
from matplotlib import widgets
import obpgenerator.visualization.obp_to_matplotlib as obp_to_matplotlib

class Vis_layer:
    mpl_elements = []

    def __init__(self, layer):
        obp_elements = []
        for shapes in layer.shapes_to_export:
            obp_elements = obp_elements + shapes.obp_elements
            self.mpl_elements = obp_to_matplotlib.obp_to_matplotlib(obp_elements)


def visualize_part(part):
    vis = Visualization()
    z_pos = 0
    for layer in part.layers:
        contour_paths = []
        for shape in layer.shapes:
            if type(shape.paths) is list:
                contour_paths = contour_paths + shape.paths
            else:
                contour_paths.append(shape.paths)
        vis.add_paths(contour_paths,z_pos)

        vis_layer = Vis_layer(layer)
        ax_vis_layer = []

        for path in vis_layer.mpl_elements:
            ax_element = vis.ax.plot(path.vertices[:, 0], path.vertices[:, 1], len(path.vertices[:, 1])*[z_pos], color='green')
            #ax_element.set_visible(False)
            ax_vis_layer.append(ax_element)
        vis.vis_layers.append(ax_vis_layer)
        z_pos = z_pos + part.layer_height
    vis.show()


class Visualization:
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    contours = []
    vis_layers = []

    def add_paths(self,paths,z_level,color='red'):
        layer = []
        for path in paths:
            layer.append(self.ax.plot(path.vertices[:, 0], path.vertices[:, 1], len(path.vertices[:, 1])*[z_level], color=color))
        self.contours.append(layer)
    def show(self):
        def change_status_of_layer(layer,visability=True):
            for path in layer:
                path[0].set_visible(visability)

        def filter_layers(val):
            for i in range(0,int(val[0])):
                change_status_of_layer(self.contours[i],visability=False)
            for i in range(int(val[0]),int(val[1])+1):
                change_status_of_layer(self.contours[i],visability=True)
            for i in range(int(val[1])+1,len(self.contours)):
                change_status_of_layer(self.contours[i],visability=False)
        
        def update_obp_layer(val):
            for i in range(0,len(self.contours)):
                if i == val:
                    for el in self.vis_layers[i]:
                        el.set_visible(True)
                else:
                    for el in self.vis_layers[i]:
                        el.set_visible(False)
                

        numb_of_layers = len(self.contours)-1
        rax = plt.axes([0.05, 0.2, 0.05, 0.6])
        layer_slider = widgets.RangeSlider(rax,'Layers',0,numb_of_layers,valstep=1,orientation='vertical',valinit=(0,numb_of_layers))
        layer_slider.on_changed(filter_layers)

        rax = plt.axes([0.95, 0.2, 0.05, 0.6])
        obp_slider = widgets.Slider(rax,'Obp layer',0,numb_of_layers,valstep=1,orientation='vertical',valinit=0)
        obp_slider.on_changed(update_obp_layer)
        plt.show()