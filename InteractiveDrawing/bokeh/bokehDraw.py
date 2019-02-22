# from bokeh.palettes import *
import re
from itertools import izip
import pyparsing
from bokeh.models import *
from bokeh.models import ColumnDataSource

from bokehTools import *
from ipywidgets import *
from Tools.aliTreePlayer import *
from IPython.display import display


class bokehDraw(object):

    def __init__(self, source, query, varX, varY, varColor, widgetString, p, **options):
        """
        :param source:           input data frame
        :param query:            query string
        :param varX:             X variable name
        :param varY:             : separated list of the Y variables
        :param varXerr:          variable name of the errors on X 
        :param varYerr:          : separated list of the errors on Y variables
        :param varColor:         color map variable name
        :param widgetString:     :  separated string - list of widgets seperated by ','
                                 widget options: dropdown, checkbox, slider
                                     slider:
                                         Requires 4 or 5 numbers as parameters
                                         for single valued sliders: slider.name(min,max,step,initial value)
                                             Ex: slider.commonF(0,15,5,0)
                                         for Ranged sliders:   slider.name(min,max,step,initial start value, initial end value)
                                             Ex: slider.commonF(0,15,5,0,10)
                                     checkbox:
                                         Requires 1 or none parameters. Allowed parameters are: 0,1,True,False
                                         checkbox.name(initial value default=False)
                                             Ex: checkbox.isMax(True)
                                     dropdown menu:
                                         Requires 1 or more parameters.
                                         dropdown.name(option1,option2,....)
                                             Ex: dropdown.MB(0,0.5,1)
                                             
                                 to group widget you can use accordion or tab:
                                     Ex: 
                                         accordion.group1(widget1,widget2...), accordion.group2(widget1,widget2...)
                                         tab.group1(widget1,widget2...), tab.group2(widget1,widget2...)
                                         
        :param p:                template figure
        :param options:          optional drawing parameters
                                 - ncols - number fo columns in drawing
                                 - commonX=?,commonY=? - switch share axis
                                 - size
                                 - errX=?  - query for errors on X-axis 
                                 - errY=?  - array of queries for errors on Y
                                 Tree options:
                                 - variables     - List of variables which will extract from ROOT File 
                                 - nEntries      - number of entries which will extract from ROOT File
                                 - firstEntry    - Starting entry number 
                                 - mask          - mask for variable names
                                 - verbosity     - first bit: verbosity for query for every update
                                                 - second bit: verbosity for source file.
        """
        if isinstance(source, pd.DataFrame):
            if (self.verbosity >> 1) & 1:
                print("Panda Dataframe is parsing...")
            df = source
        else:
            if (self.verbosity >> 1) & 1:
                print('source is not a Panda Dataframe, assuming it is ROOT::TTree')
            if 'variables' in options.keys():
                variableList = options['variables']
            else:
                variableList = str(re.sub(r'\([^)]*\)', '', widgetString) + ":" + varColor + ":" + varX + ":" + varY)
            if 'nEntries' in options.keys():
                nEntries = options['nEntries']
            else:
                nEntries = source.GetEntries()
            if 'firstEntry' in options.keys():
                firstEntry = options['firstEntry']
            else:
                firstEntry = 0
            if 'mask' in options.keys():
                columnMask = options['mask']
            else:
                columnMask = 'default'

            df = tree2Panda(source, variableList, query, nEntries, firstEntry, columnMask)

        self.query = query
        self.dataSource = df.query(query)
        self.sliderWidgets = 0
        self.accordArray = []
        self.tabArray = []
        self.widgetArray = []
        self.all = []
        self.accordion = widgets.Accordion()
        self.tab = widgets.Tab()
        self.Widgets = widgets.VBox()
        self.varX = varX
        self.varY = varY
        self.varColor = varColor
        self.options = options
        self.initWidgets(widgetString)
        self.figure, self.handle, self.bokehSource = drawColzArray(df, query, varX, varY, varColor, p, **options)
        self.updateInteractive("")
        display(self.Widgets)

    def initWidgets(self, widgetString):
        # type: (str) -> None
        """
        parse widgetString string and create widgets
        :param widgetString:   example string - slider.name0(min,max,step,valMin,valMax),tab.tabName(checkbox.name1())
        :return: s sliders
        """
        self.parseWidgetString(widgetString)
        accordBox = []
        tabBox = []
        for acc in self.accordArray:
            newBox = widgets.VBox(acc[1:])
            accordBox.append(newBox)
        for tabs in self.tabArray:
            newBox = widgets.VBox(tabs[1:])
            tabBox.append(newBox)

        self.accordion = widgets.Accordion(children=accordBox)
        for i, wdgt in enumerate(self.accordArray):
            self.accordion.set_title(i, wdgt[0])
        self.tab = widgets.Tab(children=tabBox)
        for i, wdgt in enumerate(self.tabArray):
            self.tab.set_title(i, wdgt[0])
        self.all = []
        if len(self.widgetArray) != 0:
            self.all += self.widgetArray
        if len(self.tabArray) != 0:
            self.all.append(self.tab)
        if len(self.accordArray) != 0:
            self.all.append(self.accordion)

        self.Widgets = widgets.VBox(self.all, layout=Layout(width='66%'))

    def fillArray(self, widget, array):
        """
        Gets create the specified widget and append it into the given widget array.
        :param widget:          is a list with 2 entry: 1.entry is a string: "type.name"
                                                        2.entry is a list of parameters
        :param array:           is the list of widgets to be added
        """
        global title
        title = widget[0].split('.')
        localWidget = 0
        if title[0] == "checkbox":
            if len(widget[1])==0:
                value=False
            else:
                if widget[1][0] in ['True', 'true', '1' ]:
                    value = True
                elif widget[1][0] in ['False', 'false', '0']:
                    value = False
                else:
                    raise ValueError("The parameters for checkbox can only be \"True\", \"False\", \"0\" or \"1\". The parameter for the checkbox {} was:{}".format(title[1],widget[1][0]))
            localWidget = widgets.Checkbox(description=title[1], layout=Layout(width='66%'), value=value, disabled=False)
        elif title[0] == "dropdown":
            values = list(widget[1])
            if len(values)==0:
                raise ValueError("dropdown menu requires at least 1 option. The dropdown menu {} has no options", format(title[1]))
            localWidget = widgets.Dropdown(description=title[1], options=values, layout=Layout(width='66%'), values=values[0])
        elif title[0] == "slider":
            if len(widget[1]) == 4:
                localWidget = widgets.FloatSlider(description=title[1], layout=Layout(width='66%'), min=float(widget[1][0]), max=float(widget[1][1]), step=float(widget[1][2]), value=float(widget[1][3]))
            elif len(widget[1]) == 5:
                localWidget = widgets.FloatRangeSlider(description=title[1], layout=Layout(width='66%'), min=float(widget[1][0]), max=float(widget[1][1]), step=float(widget[1][2]), value=[float(widget[1][3]), float(widget[1][4])])
            else:
                raise SyntaxError("The number of parameters for Sliders can be 4 for Single value sliders and 5 for ranged sliders. Slider {} has {} parameters.".format(title[1],len(widget[1])))
        else:
            if (self.verbosity >> 1) & 1:
                print("type of the widget\""+title[0]+"\" is not specified. Assuming it is a slider.")
            self.fillArray(["slider."+title[0],widget[1]],array)  #For backward compatibility, it can parse sliders defined as: name(min,max,step,value)
        if localWidget != 0:
            localWidget.observe(self.updateInteractive, names='value')
            array.append(localWidget)

    def updateInteractive(self, b):
        sliderQuery = ""
        allWidgets = []
        for widget in [item[1:] for item in self.accordArray] + [item[1:] for item in self.tabArray]: allWidgets += widget
        allWidgets += self.widgetArray
        for widget in allWidgets:
            if isinstance(widget, widgets.FloatRangeSlider):
                sliderQuery += str(str(widget.description) + ">=" + str(widget.value[0]) + "&" + str(widget.description) + "<=" + str(widget.value[1]) + "&")
            else:
                sliderQuery += str(str(widget.description) + "==" + str(widget.value) + "&")
        sliderQuery = sliderQuery[:-1]
        newSource = ColumnDataSource(self.dataSource.query(sliderQuery))
        self.bokehSource.data = newSource.data
        if self.verbosity & 1:
            print(sliderQuery)
        push_notebook(self.handle)

    def parseWidgetString(self, widgetString):
        toParse = "(" + widgetString + ")"
        theContent = pyparsing.Word(pyparsing.alphanums + ".+-") | '#' | pyparsing.Suppress(',') | ':'
        widgetParser = pyparsing.nestedExpr('(', ')', content=theContent)
        widgetList0 = widgetParser.parseString(toParse)[0]
        for title,widget in izip(*[iter(widgetList0)] * 2):
            name = title.split('.')
            if name[0] == 'accordion':
                if findInList(name[1], self.accordArray) == -1:
                    self.accordArray.append([name[1]])
                for name, param in izip(*[iter(widget)] * 2):
                    self.fillArray([name, param], self.accordArray[findInList(name[1], self.accordArray)])
            elif name[0] == 'tab':
                if findInList(name[1], self.tabArray) == -1:
                    self.tabArray.append([name[1]])
                for name, param in izip(*[iter(widget)] * 2):
                    self.fillArray([name, param], self.tabArray[findInList(name[1], self.tabArray)])
            else:
                self.fillArray([title, widget], self.widgetArray)

    verbosity = 0


def findInList(c, classes):
    for i, sublist in enumerate(classes):
        if c in sublist:
            return i
    return -1


def tree2Panda(tree, variables, selection, nEntries, firstEntry, columnMask):
    entries = tree.Draw(str(variables), selection, "goffpara", nEntries, firstEntry)  # query data
    columns = variables.split(":")
    # replace column names
    #    1.) pandas does not allow dots in names
    #    2.) user can specified own mask
    for i, column in enumerate(columns):
        if columnMask == 'default':
            column = column.replace(".fElements", "").replace(".fX$", "X").replace(".fY$", "Y")
        else:
            masks = columnMask.split(":")
            for mask in masks:
                column = column.replace(mask, "")
        columns[i] = column.replace(".", "_")
    #    print(i, column)
    # print(columns)
    ex_dict = {}
    for i, a in enumerate(columns):
        # print(i,a)
        val = tree.GetVal(i)
        ex_dict[a] = np.frombuffer(val, dtype=float, count=entries)
    df = pd.DataFrame(ex_dict, columns=columns)
    return df
