import numpy as np
from bokeh.core.properties import Instance, String, Int, Dict, Any
from bokeh.io import show
from bokeh.models import ColumnDataSource, LayoutDOM
# see options in https://visjs.github.io/vis-graph3d/docs/graph3d/index.html


# This custom extension model will have a DOM view that should layout-able in
# Bokeh layouts, so use ``LayoutDOM`` as the base class. If you wanted to create
# a custom tool, you could inherit from ``Tool``, or from ``Glyph`` if you
# wanted to create a custom glyph, etc.
class Surface3d(LayoutDOM):

    # The special class attribute ``__implementation__`` should contain a string
    # of JavaScript code that implements the browser side of the extension model.
    __implementation__ = "surface3d.ts"

    # Below are all the "properties" for this model. Bokeh properties are
    # class attributes that define the fields (and their types) that can be
    # communicated automatically between Python and the browser. Properties
    # also support type validation. More information about properties in
    # can be found here:
    #
    #    https://docs.bokeh.org/en/latest/docs/reference/core/properties.html#bokeh-core-properties

    # This is a Bokeh ColumnDataSource that can be updated in the Bokeh
    # server by Python code
    data_source = Instance(ColumnDataSource)

    # The vis.js library that we are wrapping expects data for x, y, and z.
    # The data will actually be stored in the ColumnDataSource, but these
    # properties let us specify the *name* of the column that should be
    # used for each field.
    x = String
    y = String
    z = String
    style = String
    myWidth = String("100px")
    legendLabel = String("XXX123")
    xxx = Int
    options3D = Dict(String, Any)
    print("x", __implementation__)
#    width=String(default=10)
