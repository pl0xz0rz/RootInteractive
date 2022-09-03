from bokeh.models.scales import ContinuousScale
from bokeh.core.properties import List, Int, Instance
import bokeh

class ToggleableScale(ContinuousScale):
    major, minor, patch = bokeh.__version__.split('.')
    if int(minor) >= 4:
        __implementation__ = "ToggleableScale.ts"
    else:
        __implementation__ = "ToggleableScale_233.ts"
    options = List(Instance(ContinuousScale))
    active = Int(default=0)
