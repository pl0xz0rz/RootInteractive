from bokeh.io.showing import show
from bokeh.models.callbacks import CustomJS
from RootInteractive.InteractiveDrawing.bokeh.CDSAlias import CDSAlias
from RootInteractive.InteractiveDrawing.bokeh.CustomJSNAryFunction import CustomJSNAryFunction
from RootInteractive.InteractiveDrawing.bokeh.DownsamplerCDS import DownsamplerCDS

from RootInteractive.InteractiveDrawing.bokeh.bokehDrawSA import bokehDrawSA

from bokeh.models.sources import ColumnDataSource
from bokeh.models.widgets import Slider
from bokeh.models.layouts import Column

from bokeh.plotting import Figure, output_file

import pandas as pd
import numpy as np

df = pd.DataFrame(np.random.random_sample(size=(200000, 6)), columns=list('ABCDEF'))

parameterArray = [
    {"name": "colorZ", "value":"A", "options":["A", "B"]},
    {"name": "size", "value":7, "range":[0, 30]},
    {"name": "legendFontSize", "value":"13px", "options":["9px", "11px", "13px", "15px"]},
    {"name": "paramX", "value":10, "range": [-20, 20]},
    {"name": "C_cut", "value": 1, "range": [0, 1]}
]

# This interface with two arrays is only for the case when functions are reused with different columns as target
jsFunctionArray = [
    {
        "name": "saxpy",
        "parameters": ["paramX"],
        "fields": ["x", "y"],
        "func": "return paramX*x+y"
    }
]

#This array shows the two options in action
aliasArray = [
    {
        "name": "A_mul_paramX_plus_B",
        "variables": ["A", "B"],
        "transform": "saxpy" 
    },
    {
        "name": "C_cut",
        "variables": ["C"],
        "parameters": ["C_cut"],
        "func": "return C < C_cut"
    }
]

figureArray = [
    [['A'], ['B', '4*A+B', 'A_mul_paramX_plus_B'], {"size":"size"}],
    [['B'], ['C+B', 'C-B'], { "size":"size", "colorZvar": "colorZ", "rescaleColorMapper": True }],
    [['D'], ['(A+B+C)*D'], {"colorZvar": "colorZ", "size": 10}],
    # This interface is not implemented yet
    # [['bin_center_0'], ['entries', 'entries_C_cut'], {"context":"histoA"}],
    [['histoA.bin_center'], ['histoA.bin_count'], {"context":"histoA"}]
]

histoArray = [
    {
        "name": "histoA", "variables": ["A"], "histograms": {
            "entries": None,
            "entries_C_cut": {
                "weights": "C_cut"
            }
        },
        "weights": "C_cut"
    }
]

widgetParams=[
    ['range', ['A']],
    ['range', ['B', 0, 1, 0.1, 0, 1]],

    ['range', ['C'], {'type': 'minmax'}],
    ['range', ['D'], {'type': 'sigma', 'bins': 10, 'sigma': 3}],
    ['range', ['E'], {'type': 'sigmaMed', 'bins': 10, 'sigma': 3}],
    #['slider','F', ['@min()','@max()','@med','@min()','@median()+3*#tlm()']], # to be implmneted
    ['select',["colorZ"], {"callback": "parameter", "default": 0}],
    ['slider',["size"], {"callback": "parameter"}],
    ['select',["legendFontSize"], {"callback": "parameter", "default": 2}],
    ['slider',["C_cut"], {"callback": "parameter"}],
    ['slider',["paramX"], {"callback": "parameter"}],
]

widgetLayoutDesc={
    "Selection": [[0, 1, 2], [3, 4], {'sizing_mode': 'scale_width'}],
    "Graphics": [[5, 6, 7], {'sizing_mode': 'scale_width'}],
    "CustomJS functions": [[8, 9]]
    }

figureLayoutDesc=[
        [0, 1, {'commonX': 1, 'y_visible': 1, 'x_visible':1, 'plot_height': 300}],
        [2, 3, {'plot_height': 200, 'sizing_mode': 'scale_width', 'y_visible' : 2}]
        ]

tooltips = [("VarA", "(@A)"), ("VarB", "(@B)"), ("VarC", "(@C)"), ("VarD", "(@D)")]

def test_customJsFunction():
    jsFunction = "return a*x+y"

    sliderWidget = Slider(title='X', start=-20, end=20, step=1, value=10)

    jsMapper = CustomJSNAryFunction(parameters={"a": sliderWidget.value}, fields=["x", "y"], func=jsFunction)

    cdsOrig = ColumnDataSource(df)
    cdsAlias = CDSAlias(source=cdsOrig, mapping={"a":"A", "b":"B", "a*x+b": {"fields":["A", "B"], "transform": jsMapper}})
    cdsDownsampled = DownsamplerCDS(source = cdsAlias, selectedColumns=["a", "b", "a*x+b"])

    sliderWidget.js_on_change("value", CustomJS(args = {"jsMapper": jsMapper, "cdsAlias": cdsAlias}, code="""
        jsMapper.parameters = {x: this.value}
        jsMapper.update_args()
        cdsAlias.compute_functions()
    """))

    output_file("test_Alias.html")
    fig = Figure()
    fig.scatter(x="a", y="b", source=cdsDownsampled)
    fig.scatter(x="a", y="a*x+b", source=cdsDownsampled)
    show(Column(fig, sliderWidget))

def test_customJsFunctionBokehDrawArray():
    jsFunctionArray = [
        {
            "name": "saxpy",
            "parameters": ["paramX"],
            "fields": ["x", "y"],
            "func": "return paramX*x+y"
        }
    ]
    output_file("test_AliasBokehDraw.html")
    bokehDrawSA.fromArray(df, None, figureArray, widgetParams, layout=figureLayoutDesc, tooltips=tooltips, parameterArray=parameterArray,
                          widgetLayout=widgetLayoutDesc, sizing_mode="scale_width", nPointRender=300, jsFunctionArray=jsFunctionArray,
                           aliasArray=aliasArray, histogramArray=histoArray)

def test_customJsFunctionBokehDrawArray_v():
    jsFunctionArray = [
        {
            "name": "saxpy",
            "parameters": ["paramX"],
            "fields": ["a", "b"],
            "v_func": "return a.map((el, idx) => paramX*a[idx]+b[idx])"
        }
    ]
    output_file("test_AliasBokehDraw_v.html")
    bokehDrawSA.fromArray(df, None, figureArray, widgetParams, layout=figureLayoutDesc, tooltips=tooltips, parameterArray=parameterArray,
                          widgetLayout=widgetLayoutDesc, sizing_mode="scale_width", nPointRender=300, jsFunctionArray=jsFunctionArray,
                           aliasArray=aliasArray, histogramArray=histoArray)

test_customJsFunctionBokehDrawArray_v()