from svgpathtools import svg2paths
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.path as mpltPath

def import_svg_layer(file_path):#imports an svg file (path) containing ONE layer
    svg_paths = import_svg(file_path)
    matplotpaths = []
    for path in svg_paths:
        matplotpath = svgpath_to_matplotpath(path)
        matplotpaths.append(matplotpath)
    return matplotpaths

def import_svg(file_path): #imports an svg file (path)
    tree = ET.parse(file_path)
    root = tree.getroot()
    groups = root.findall(r"{http://www.w3.org/2000/svg}g")
    paths, attributes  = svg2paths(file_path)
    svg_layers = []
    i = 0
    for group in groups:
        local_layer = []
        for shapes in group:
            local_layer.append(paths[i])
            i = i + 1
        svg_layers.insert(0,local_layer)
    return svg_layers

def svgpath_to_matplotpath(svg_paths):
    matplotpaths = []
    for path in svg_paths:
        new_path_points = []
        new_path_points.append([path[0].start.real,path[0].start.imag])
        for line in path:
            new_path_points.append([line.end.real,line.end.imag])
        new_path = mpltPath.Path(new_path_points)
        matplotpaths.append(new_path)
    return matplotpaths








