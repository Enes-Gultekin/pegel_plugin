#-----------------------------------------------------------
# Copyright (C) 2015 Martin Dobias
#-----------------------------------------------------------
# Licensed under the terms of GNU GPL 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#---------------------------------------------------------------------

from PyQt5.QtWidgets import  QApplication,QWidget,QAction, QMessageBox,QPushButton,QDialog,QVBoxLayout,QGridLayout,QFormLayout,QComboBox,QHBoxLayout
from PyQt5.QtGui import QStandardItem, QStandardItemModel,QIcon
from PyQt5.QtCore import QTextCodec
from qgis.utils import iface
from qgis.core import QgsJsonUtils,QgsVectorLayer,QgsProject,QgsPointXY
from qgis.PyQt.QtWidgets import (QApplication, QWidget,
    QVBoxLayout, QLabel)
from qgis.PyQt.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from .module.fetchPegel import PegelFetch
import json
import os
import matplotlib.pyplot as plt
from .module.past_months_values import monthsData
import datetime #to convert timestamp to standart date


#this to reach path of the current folder. This will be useful to get layers and their styles
current_path = os.path.dirname(__file__)
current_path = current_path.replace("\\", "/")



def classFactory(iface):
    return MinimalPlugin(iface)


class MinimalPlugin:
    def __init__(self, iface):
        self.iface = iface

        ###to reach pegel data
        self.fetchPegel=PegelFetch()
        self.station_names=self.fetchPegel.station_names()
        self.geojson=self.fetchPegel.geojson2list()

    def initGui(self):

        ###custom icon is added
        icon_path =current_path+"/pegel_icon.png"
        icon=QIcon(icon_path)

        self.action = QAction( "pegel online plugin",self.iface.mainWindow())
        self.action.setIcon(icon)
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)


    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        del self.action


    def run(self):

        #pegel station points, germany state and water line-polygon shp files are added
        self.getLayers()

        #create a ui (QDialog lib needed)
        self.dlg=QDialog()
        self.dlg.resize(500,500)
        layout=QVBoxLayout(self.dlg)#QVBoxLayout lib needed
        h_layout=QHBoxLayout()
        #create a button(QPushButton lib needed)
        #add listed style combo-box. To reach the value if combobox
        #self parameter is needed
        self.combo=QComboBox()

        #fetch stations names and add as combo list items
        #station_names=self.fetchPegel.station_names()
        self.combo.insertItem(0, "Select a Station")#add an initial place-holder
        self.combo.addItems(self.station_names)

        #combo values function
        self.combo.currentTextChanged.connect(self.stationValues)

        #add canvas to UI: plotting purpose
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        layout.addWidget(self.combo)
        layout.addLayout(h_layout)

        #add buttons to ui
        graph_button=QPushButton("Graph")
        graph_button.clicked.connect(self.graphWindow)
        graph_button.setFixedSize(100,30)

        inst_button=QPushButton("Instructions")
        inst_button.clicked.connect(self.instWindow)
        inst_button.setFixedSize(100,30)

        close_button=QPushButton("Close")
        close_button.clicked.connect(self.closeWindow)
        close_button.setFixedSize(100,30)

        h_layout.addWidget(graph_button)
        h_layout.addWidget(inst_button)
        h_layout.addWidget(close_button)

        self.dlg.show()
        self.dlg.exec_()

    ###
    def stationValues(self,s):
      #"s" gets combo value
      print("current combo:",s)

      #if the value of combo matches with a station, extend to the point
      for keys in self.geojson["features"]:
        if s==keys["properties"]["longname"]:
          #print(keys["geometry"]["coordinates"])

          longitude = keys["geometry"]["coordinates"][0]
          latitude = keys["geometry"]["coordinates"][1]
          point = QgsPointXY(float(longitude), float(latitude))
          iface.mapCanvas().setCenter(point)
          iface.mapCanvas().zoomScale(1000)
          iface.mapCanvas().refresh()

    ###to add layers and pegel points
    def getLayers(self):

        # Check if the layers already exist in the project. If so, dont add more
        project = QgsProject.instance()
        if project.mapLayersByName("states") and project.mapLayersByName("water_polygon") and project.mapLayersByName("water_lines") and project.mapLayersByName("PegelPoints"):
            return

        #add water package which has Germany's waters sources data
        path_water_line=current_path+"/module/waters.gpkg|layername=water_l"
        path_water_poly=current_path+"/module/waters.gpkg|layername=water_f"
        path_states = current_path+"/module/states/B-2022-AI-N-04--AI0215--2024-02-03.shp"


        ###add germany states polygon layer and style
        layer_state=iface.addVectorLayer(path_states,"states","ogr")
        style_path_state=current_path+"/module/style/state_style.qml"
        layer_state.loadNamedStyle(style_path_state)
        layer_state.triggerRepaint()
        QgsProject.instance().addMapLayer(layer_state)

        ###add water polygon layer and style
        layer_water_polygon=iface.addVectorLayer(path_water_poly,"water_polygon","ogr")
        style_path_waterpolygon=current_path+"/module/style/waterpolygon_style.qml"
        layer_water_polygon.loadNamedStyle(style_path_waterpolygon)
        layer_water_polygon.triggerRepaint()
        QgsProject.instance().addMapLayer(layer_water_polygon)


        ###add water line layer and style
        layer_water_line=iface.addVectorLayer(path_water_line,"water_lines","ogr")
        style_path_waterline=current_path+"module/style/waterline_style.qml"
        layer_water_line.loadNamedStyle(style_path_waterline)
        layer_water_line.triggerRepaint()
        QgsProject.instance().addMapLayer(layer_water_line)







        ###add pegel points as geojson to qgis as a layer###

        #add points as a layer
        fcString = json.dumps(self.geojson)

        codec = QTextCodec.codecForName("UTF-8")
        fields = QgsJsonUtils.stringToFields(fcString, codec)
        feats = QgsJsonUtils.stringToFeatureList(fcString, fields, codec)

        vl= QgsVectorLayer('Point', "PegelPoints", "memory")
        dp = vl.dataProvider()
        dp.addAttributes(fields)
        vl.updateFields()

        dp.addFeatures(feats)
        vl.updateExtents()

        #adjust pegel point style
        style_path_pegel_points=f"{current_path}/module/style/pegelpoints_style.qml"

        vl.loadNamedStyle(style_path_pegel_points)
        vl.triggerRepaint()

        ###--------###

        return QgsProject.instance().addMapLayer(vl)


    ###draws graph of given station on the canvas
    def drawGraph(self,y_axis,x_axis,station_name):
            self.figure.clear()
            plt.close()


            dates=[]
            for item in x_axis:
                date=datetime.datetime.fromisoformat(item)
                date=date.strftime("%d %b %Y")
                dates.append(date)

            #print(dates)


            first=dates[0]
            #print(first)
            last=dates[-1]
            #print(last)
            mid=dates[len(x_axis)//2]
            #print(mid)

            #to be able to display plot on canvas
            ax = self.figure.add_subplot(111)
            ax.plot(dates,y_axis)
            ax.set_ylabel("Water Level (mm)")
            ax.set_xlabel("Date")

            ax.set_xticks([first,mid,last])
            self.canvas.draw()

    #to display graph after clicking "Graph button"
    def graphWindow(self):


        combo_station_name=self.combo.currentText()
        #print(self.combo.currentText())


        for keys in self.geojson["features"]:
            if combo_station_name==keys["properties"]["longname"]:
                values,date=monthsData(keys["properties"]["uuid"])
                self.drawGraph(values,date,combo_station_name)



    ###instruction window
    def instWindow(self):
        dlg=QDialog()
        dlg.resize(200,250)


        layout=QFormLayout(dlg)

        msg=QLabel("This plugin designed to display the water level measurements across Germany.")
        msg2=QLabel("The data is provided from Pegel Online")
        msg3=QLabel(" ")
        msg4=QLabel("How to Use:")
        msg5=QLabel("- On the plugin UI, there is a list menu at the bottom. This list has")
        msg6=QLabel("names of Stations of Pegel. When a station is selected and after clicking ")
        msg7=QLabel("the  'Graph' button brings a plot to the window and the map is extended to ")
        msg8=QLabel("this point. This plot illustrates the water level trends at the respective")
        msg9=QLabel("station over the past 30 days.")
        msg10=QLabel("- Additionally, when hovering over any points, details can be viewed such")
        msg11=QLabel("as the station name, the latest measurement, and its corresponding date.")
        layout.addWidget(msg)
        layout.addWidget(msg2)
        layout.addWidget(msg3)
        layout.addWidget(msg4)
        layout.addWidget(msg5)
        layout.addWidget(msg6)
        layout.addWidget(msg7)
        layout.addWidget(msg8)
        layout.addWidget(msg9)
        layout.addWidget(msg10)
        layout.addWidget(msg11)
        dlg.show()
        dlg.exec_()




    #to close dialog window
    def closeWindow(self):
        self.dlg.close()






