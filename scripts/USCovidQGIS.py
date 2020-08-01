import os
import glob


print('The current working directory is', os.getcwd())

script_location = glob.glob('C:\\**\\USCovidVisualization\\scripts', recursive=True)[0]
os.chdir(script_location)

print('The current working directory has now moved to this script location at', os.getcwd())

uscounties = '../data/uscounties_noterr.geojson'

county_layer = iface.addVectorLayer(uscounties, 'County Layer', 'ogr')

if not county_layer:
    print('There was an error in loading the layer!')

data_location = glob.glob('../output/Processed*')[0]
csv_layer = iface.addVectorLayer(data_location, 'Covid Data Layer', 'ogr')   

geo_field = 'GEO_ID'
csv_field = 'county_fips'

joinObject.setJoinFieldName(csv_field)
joinObject.setTargetFieldName(geo_field)
joinObject.setJoinLayerId(csv_layer.id())

joinObject.setUsingMemoryCache(True)
joinObject.setJoinLayer(csv_layer)
county_layer.addJoin(joinObject)

