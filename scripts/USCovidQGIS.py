import os
from qgis.core import QgsVectorLayer


uscounties = '../data/uscounties_noterr.geojson'

county_layer = iface.addVectorLayer(uscounties, 'County Layer', 'ogr')

if not county_layer:
    print('There was an error in loading the layer!')
    