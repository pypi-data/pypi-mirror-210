import copy

def sort(shapes, strategy="shapes_first",settings=dict()):
    if strategy=="shapes_first":
        return shapes_first(shapes)
    elif strategy=="alternate_shapes":
        return alternate_shapes(shapes)
    elif strategy=="ramp_manufacturing_settings":
        return ramp_manufacturing_settings(shapes,settings)
    else:
        return []

def shapes_first(shapes):
    shape_order = []
    for shape in shapes:
        for i in range(shape.nmb_of_scans):
            shape_order.append(shape)
    return shape_order

def alternate_shapes(shapes):
    shape_order = []
    max_scans = 0
    print("The setting alternate shapes is not fully implemented yet")
    for shape in shapes:
        if shape.nmb_of_scans > max_scans:
            max_scans=shape.nmb_of_scans
    for i in range(max_scans):
        for shape in shapes:
            if shape.nmb_of_scans < i:
                shape_order.append(shape)
    return shape_order

def ramp_manufacturing_settings(shapes,settings):
    """
    settings = dictionary with ramp_beam_power, ramp_dwell_time, ramp_scan_speed, ramp_spot_size
    if value is 0 no ramping for parameter, if -1 will ramp setting from upper limit to lower,
    if 1 will ramp parameter from from lower to upper
    """
    def create_ramp_vector(nmb_designs,lower,upper,value,ramp_setting):
        ramped_values = [value] * nmb_designs
        if ramp_setting != 0:
            step = ((upper-lower)/(nmb_designs-1))
            for i in range(nmb_designs):
                ramped_values[i] = lower+i*step
        if ramp_setting<0:
            ramped_values.reverse()
        return ramped_values

    ramp = dict(ramp_beam_power=0,ramp_dwell_time=0,ramp_scan_speed=0,ramp_spot_size=0)
    ramp.update(settings)
    shape_order = []
    for shape in shapes:
        if shape.nmb_of_scans == 1:
            shape_order.append(shape)
        else:
            beam_power = create_ramp_vector(shape.nmb_of_scans,shape.manufacturing_settings.beam_power.lower,shape.manufacturing_settings.beam_power.upper,shape.manufacturing_settings.beam_power.value,ramp["ramp_beam_power"])
            dwell_time = create_ramp_vector(shape.nmb_of_scans,shape.manufacturing_settings.dwell_time.lower,shape.manufacturing_settings.dwell_time.upper,shape.manufacturing_settings.dwell_time.value,ramp["ramp_dwell_time"])
            scan_speed = create_ramp_vector(shape.nmb_of_scans,shape.manufacturing_settings.scan_speed.lower,shape.manufacturing_settings.scan_speed.upper,shape.manufacturing_settings.scan_speed.value,ramp["ramp_scan_speed"])
            spot_size = create_ramp_vector(shape.nmb_of_scans,shape.manufacturing_settings.spot_size.lower,shape.manufacturing_settings.spot_size.upper,shape.manufacturing_settings.spot_size.value,ramp["ramp_spot_size"])
            for i in range(shape.nmb_of_scans):
                new_shape = copy.deepcopy(shape)
                new_shape.manufacturing_settings.beam_power.value = beam_power[i]
                new_shape.manufacturing_settings.dwell_time.value = dwell_time[i]
                new_shape.manufacturing_settings.scan_speed.value = scan_speed[i]
                new_shape.manufacturing_settings.spot_size.value = spot_size[i]
                shape_order.append(new_shape)
    return shape_order

