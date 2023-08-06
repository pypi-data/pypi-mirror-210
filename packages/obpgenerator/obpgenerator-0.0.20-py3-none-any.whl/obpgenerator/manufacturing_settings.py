import obplib as obp

class MyVar:
   def __init__(self, num, upper=None, lower=None):
        self.value = num
        if upper == None:
            upper = num
        if lower == None:
            lower = num
        self.upper = upper
        self.lower = lower

class ManufacturingSetting:
    spot_size = MyVar(1) #[µm]
    beam_power = MyVar(1500) #[W]
    scan_speed = MyVar(1) #[micrometers/second] 
    dwell_time = MyVar(1) #[ns]
    def get_beam_parameters(self):
        return obp.Beamparameters(self.spot_size.value, self.beam_power.value)
    def set_spot_size(self,new_value,lower=None,upper=None):
        self.spot_size = MyVar(new_value,lower=lower,upper=upper)
    def set_beam_power(self,new_value,lower=None,upper=None):
        self.beam_power = MyVar(new_value,lower=lower,upper=upper)
    def set_scan_speed(self,new_value,lower=None,upper=None):
        self.scan_speed = MyVar(new_value,lower=lower,upper=upper)
    def set_dwell_time(self,new_value,lower=None,upper=None):
        self.dwell_time = MyVar(new_value,lower=lower,upper=upper)

class ElementSetting:
    #each parameter can go from -1 to 1 where -1 = lower bound of the ManufacturingSetting, 0 = value of ManufacturingSetting, and 1 = upper bound of ManufacturingSetting
    spot_size = 0
    beam_power = 0
    scan_speed = 0
    dwell_time = 0
    def get_beam_parameters(self, manufacturing_setting):
        spot_size = interpret_setting(manufacturing_setting.spot_size, self.spot_size)
        beam_power = interpret_setting(manufacturing_setting.beam_power, self.beam_power)
        return obp.Beamparameters(spot_size,beam_power)
    def get_spot_size(self, manufacturing_setting):
        return interpret_setting(manufacturing_setting.spot_size, self.spot_size)
    def get_beam_power(self, manufacturing_setting):
        return interpret_setting(manufacturing_setting.beam_power, self.beam_power)
    def get_scan_speed(self, manufacturing_setting):
        return interpret_setting(manufacturing_setting.scan_speed, self.scan_speed)
    def get_dwell_time(self, manufacturing_setting):
        return interpret_setting(manufacturing_setting.dwell_time, self.dwell_time)
    def create_manufacturing_setting(self,manufacturing_setting):
        new_manufacturing_setting = ManufacturingSetting()
        new_manufacturing_setting.set_beam_power(interpret_setting(manufacturing_setting.beam_power, self.beam_power))
        new_manufacturing_setting.set_dwell_time(interpret_setting(manufacturing_setting.dwell_time, self.dwell_time))
        new_manufacturing_setting.set_scan_speed(interpret_setting(manufacturing_setting.scan_speed, self.scan_speed))
        new_manufacturing_setting.set_spot_size(interpret_setting(manufacturing_setting.spot_size, self.spot_size))
        return new_manufacturing_setting


def interpret_setting(my_var, parameter):
    output = my_var.value
    if parameter < 0:
        output = my_var.value - (my_var.lower-my_var.value)*parameter
    elif parameter > 0:
        output = my_var.value + (my_var.upper-my_var.value)*parameter
    return output
