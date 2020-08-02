import os
import glob
import re
from pylab import cm
import matplotlib as mpl
import numpy as np


#Change working directory to script location
print('The current working directory is', os.getcwd())

script_location = glob.glob('C:\\**\\USCovidVisualization\\scripts', recursive=True)[0]
os.chdir(script_location)

print('The current working directory has now moved to this script location at', os.getcwd())


#Add US layer
uscounties = '../data/uscounties_noterritories.geojson'

county_layer = iface.addVectorLayer(uscounties, 'County Layer', 'ogr')

if not county_layer:
    print('There was an error in loading the county layer!')
else:
    print('County layer successfully loaded')


#Add Covid csv    
data_location = glob.glob('../output/Processed*')[0]
csv_layer = iface.addVectorLayer(data_location, 'Covid Data Layer', 'ogr')   

if not csv_layer:
    print('There was an error in loading the csv layer!')
else:
    print('Csv layer successfully loaded')
        

#Join attributes by the GeoJSON FIPS format
geo_field = 'GEO_ID'
csv_field = 'county_fips'

joinObject = QgsVectorLayerJoinInfo()
joinObject.setJoinFieldName(csv_field)
joinObject.setTargetFieldName(geo_field)
joinObject.setJoinLayerId(csv_layer.id())

joinObject.setUsingMemoryCache(True)
joinObject.setJoinLayer(csv_layer)
county_layer.addJoin(joinObject)

if not joinObject:
    print('There was an error in combining the layers!')
else:
    print('Layers were combined successfully')

colour_list = []

#INTERVAL NUMBER (NUMBER OF COLOUR GROUPS) - CHANGE IF DESIRED
interval = 10




#To get real number of spaces
interval+=1

cmap = cm.get_cmap('viridis', interval+1)

#Generate viridis colours
for i in range(cmap.N):
    #Only get rgb of rgba
    rgb = cmap(i)[:3]
    #Convert to hex
    colour_list.append(mpl.colors.rgb2hex(rgb))
    
if not colour_list:
    print('There was an error in generating the colours!')
else:
    print('Colour scale was generated successfully')


#Get field name of Covid cases per 100k
field_names = [field.name() for field in county_layer.fields()]
regex = re.compile(".*cases_per_100k")
re_list = list(filter(regex.match, field_names))
field_name = re_list[0]

#Pre: Colours must be defined, number of colour groups must be specified
#Post: Renderer/gradient applied to Covid layer
def apply_graduation(colour_list, interval):
    range_list = []
    #Generate ranges using linspace
    idx = csv_layer.fields().indexFromName('cases_per_100k')
    interval_list = np.linspace(csv_layer.minimumValue(idx), csv_layer.maximumValue(idx), interval)
    #Create group
    for i in range(interval-1):
        symbol = QgsSymbol.defaultSymbol(county_layer.geometryType())
        symbol.setColor(QColor(colour_list[i]))
        single_range = QgsRendererRange(interval_list[i], interval_list[i+1], symbol, 'Group '+str(i+1))
        range_list.append(single_range)
    
    #Create renderer
    grad_renderer = QgsGraduatedSymbolRenderer(field_name, range_list)
    grad_renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
    
    #Merge renderer to Covid layer
    county_layer.setRenderer(grad_renderer)
    
    print('Choropleth map has been created')
    
apply_graduation(colour_list, interval)

#Get processed name with date
processed_name = (data_location.split('\\')[-1]).split('.')[0]

#Save to shapefile
_writer = QgsVectorFileWriter.writeAsVectorFormat(county_layer, '../output/shapefiles/'+processed_name+'.shp','utf-8', driverName = 'ESRI Shapefile')

if not _writer:
    print('There was an error in saving the shapefile!')
else:
    print('Shapefile successfully saved')


