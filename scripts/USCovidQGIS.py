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
    