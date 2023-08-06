import obplib as obp
import obpgenerator.manufacturing_settings as settings

def generate_lines(elements,set):
    lines = []
    for element in elements:
        lines.append(obp.Line(element[0], element[1], int(set.scan_speed.value), set.get_beam_parameters()))
    return lines

def generate_points(elements,set):
    points_to_export = []
    dwell_times = []
    for element in elements:
        points_to_export.append(element[0])
        dwell_times.append(set.dwell_time.value)
    spots = obp.TimedPoints(points_to_export, dwell_times, set.get_beam_parameters())
    return spots

def generate_curves(elements, set):
    curves = []
    for element in elements:
        curves.append(obp.Curve(element[0],element[1],element[3],element[0], int(set.scan_speed.value), set.get_beam_parameters()))
    return curves