import obpgenerator.melt_strategies.line_melting as line_melting
import obpgenerator.melt_strategies.point_melting as point_melting

def melt(keep_matrix,coord_matrix,strategy,settings=dict()):
    obp_points = []
    if strategy == "point_random":
        obp_points = point_melting.point_random(keep_matrix,coord_matrix)
    elif strategy == "line_snake":
        obp_points = line_melting.line_snake(keep_matrix,coord_matrix)
    elif strategy == "line_left_to_right":
        obp_points = line_melting.line_left_right(keep_matrix,coord_matrix)
    elif strategy == "line_right_to_left":
        obp_points = line_melting.line_right_left(keep_matrix,coord_matrix)
    return obp_points
