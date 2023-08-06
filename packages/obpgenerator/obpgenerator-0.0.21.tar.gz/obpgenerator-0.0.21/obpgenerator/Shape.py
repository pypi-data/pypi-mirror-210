import math 
import numpy as np
import obpgenerator.shape_melting as melting
import obplib as obp
import obpgenerator.manufacturing_settings as settings
import obpgenerator.generate_obp as generate_obp

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in degree.
    """
    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def check_points_in_path(matplotpaths, points):
    #points N*2 numpy array
    inside_all = np.full((len(points),), False)

    if type(matplotpaths) is list:
        for path in matplotpaths:
            inside = path.contains_points(points)
            inside_all = np.logical_or(inside_all, inside)
    else:
        inside = matplotpaths.contains_points(points)
        inside_all = np.logical_or(inside_all, inside)
    
    return inside_all

class Shape:
    def __init__(self):
        self.paths = [] #array of matplotlib.path
        self.keep_matrix = None #matrix defining which mesh elements that should be kept
        self.coord_matrix = None #matrix defining the coordinates of the mesh elements
        self.obp_points = [] #array with elements that build your obp file, contains arrays with 1, 2, or 4 obp.Points. 1 Point in array = obplib.TimedPoints, 2 points = obplib.Line, 4 points = obp.Curve
        self.manufacturing_settings = settings.ManufacturingSetting() #Manufacturing settings
        self.obp_elements = [] #array with elements for exports
        self.melt_strategy = "point_random" #melting strategy
        self.melt_settings = dict() #melting settings
        self.nmb_of_scans = 1 #number of times the shape should be scanned

    def generate_matrixes(self, spacing, size=150, angle=0): #spacing and size in mm, angle in degree 
        row_height = math.sqrt(3/4)*spacing
        points_x = math.floor(size/spacing)
        points_y = math.floor(size/row_height)
        self.coord_matrix = np.zeros((points_y, points_x),dtype=np.complex_)
        self.keep_matrix = np.zeros((points_y, points_x))
        
        for i in range(points_x):
            for ii in range(points_y):
                if (ii % 2) == 0:
                    x = i*spacing - size/2
                    y = ii*row_height - size/2
                    if angle != 0:
                        x,y = rotate((0,0),(x,y),angle)
                    self.coord_matrix[ii][i] = complex(x,y)
                else:
                    x = i*spacing - size/2 + spacing/2
                    y = ii*row_height - size/2
                    if angle != 0:
                        x,y = rotate((0,0),(x,y),angle)
                    self.coord_matrix[ii][i] = complex(x,y)
    
    def check_keep_matrix(self):
        if len(self.paths)>0:
            flatten_keep = self.coord_matrix.flatten()
            flatten_2D = np.column_stack((flatten_keep.real,flatten_keep.imag))
            keep_array = check_points_in_path(self.paths,flatten_2D)
            self.keep_matrix = keep_array.reshape(self.keep_matrix.shape)

    def generate_obp_elements(self):
        None
        same_elements = []
        self.obp_elements = []
        for i, element in enumerate(self.obp_points):
            if len(same_elements) == 0 or len(element) == len(same_elements[0]):
                same_elements.append(element)
            if len(element) != len(same_elements[0]) or i == len(self.obp_points)-1:
                if len(same_elements[0]) == 1:
                    self.obp_elements = self.obp_elements + [generate_obp.generate_points(same_elements,self.manufacturing_settings)]
                elif len(same_elements[0]) == 2:
                    self.obp_elements = self.obp_elements + generate_obp.generate_lines(same_elements,self.manufacturing_settings)
                elif len(same_elements[0]) == 4:
                    self.obp_elements = self.obp_elements + generate_obp.generate_curves(same_elements,self.manufacturing_settings)
                same_elements = [element]
            
    def generate_melt_strategy(self,strategy=None,settings=None):
        if strategy is None:
            strategy = self.melt_strategy
        if settings is None:
            settings = self.melt_settings
        points = melting.melt(self.keep_matrix,self.coord_matrix,strategy,settings=settings)
        self.obp_points = self.obp_points + points
