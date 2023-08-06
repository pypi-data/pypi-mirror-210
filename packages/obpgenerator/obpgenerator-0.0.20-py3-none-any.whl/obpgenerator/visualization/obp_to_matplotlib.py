import obplib as obp
from matplotlib.path import Path



def convert_line(element):
    p1 = element.P1
    p2 = element.P2
    start=(p1.get_x()/1000,p1.get_y()/1000)
    end=(p2.get_x()/1000,p2.get_y()/1000)
    line = Path([[start[0],start[1]],[end[0],end[1]]])
    return line

def convert_point(element):
    points = element.points
    circles = []
    for point in points:
        center=(point.get_x()/1000,point.get_y()/1000)
        circle = Path.circle(center=center, radius=0.05)
        circles.append(circle)
    return circles

def convert_arc(element):
    return None

def obp_to_matplotlib(elements):
    mtpl_elements = []
    for element in elements:
        if type(element) is obp.Line:
            mtpl_element = convert_line(element)
            mtpl_elements.append(mtpl_element)
        elif type(element) is obp.TimedPoints:
            mtpl_element = convert_point(element)
            mtpl_elements = mtpl_element + mtpl_element
        elif type(element) is obp.Curve:
            mtpl_element = convert_arc(element)
            mtpl_elements.append(mtpl_element)
    return mtpl_elements