import os
import glob
import re
from pylab import cm
import matplotlib as mpl
import numpy as np

print('The current working directory is', os.getcwd())

script_location = glob.glob('C:\\**\\USCovidVisualization\\scripts', recursive=True)[0]
os.chdir(script_location)

print('The current working directory has now moved to this script location at', os.getcwd())

uscounties = '../data/uscounties_noterritories.geojson'

county_layer = iface.addVectorLayer(uscounties, 'County Layer', 'ogr')

if not county_layer:
    print('There was an error in loading the layer!')

data_location = glob.glob('../output/Processed*')[0]
csv_layer = iface.addVectorLayer(data_location, 'Covid Data Layer', 'ogr')   

geo_field = 'GEO_ID'
csv_field = 'county_fips'

joinObject = QgsVectorLayerJoinInfo()
joinObject.setJoinFieldName(csv_field)
joinObject.setTargetFieldName(geo_field)
joinObject.setJoinLayerId(csv_layer.id())

joinObject.setUsingMemoryCache(True)
joinObject.setJoinLayer(csv_layer)
county_layer.addJoin(joinObject)

colour_list = []

#INTERVAL NUMBER
interval = 10




#To get real number of spaces
interval+=1

cmap = cm.get_cmap('viridis', interval)

#Generate Viridis colours
for i in range(cmap.N):
    #Only get rgb of rgba
    rgb = cmap(i)[:3]
    #Convert to hex
    colour_list.append(mpl.colors.rgb2hex(rgb))

field_names = [field.name() for field in county_layer.fields()]
regex = re.compile(".*cases_per_100k")
re_list = list(filter(regex.match, field_names))
field_name = re_list[0]

def apply_graduation(colour_list, interval):
    range_list = []
    idx = csv_layer.fields().indexFromName('cases_per_100k')
    interval_list = np.linspace(csv_layer.minimumValue(idx), csv_layer.maximumValue(idx), interval)
    for i in range(interval-1):
        symbol = QgsSymbol.defaultSymbol(county_layer.geometryType())
        symbol.setColor(QColor(colour_list[i]))
        single_range = QgsRendererRange(interval_list[i], interval_list[i+1], symbol, 'Group '+str(i+1))
        range_list.append(single_range)
    
    grad_renderer = QgsGraduatedSymbolRenderer(field_name, range_list)
    grad_renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
    
    county_layer.setRenderer(grad_renderer)
    
    print('Choropleth map has been created')
    
apply_graduation(colour_list, interval)
