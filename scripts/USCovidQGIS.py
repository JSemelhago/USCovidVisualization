import os
from qgis.core import QgsVectorLayer

uscounties = 'uscounties_noterritories.geojson'

county_layer = QgsVectorLayer(uscounties, 'County Layer', 'ogr')

if not county_layer.isValid():
    print('Loading the layer failed, please try again!')
else:
    QgsProject.instance().addMapLayer(county_layer)