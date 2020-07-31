import os
import glob

print('The current working directory is', os.getcwd())


print(os.path.realpath('USCovidQGIS.py'))

print('The current working directory has now moved to this script location at', os.getcwd())

uscounties = '../data/uscounties_noterr.geojson'

county_layer = iface.addVectorLayer(uscounties, 'County Layer', 'ogr')

if not county_layer:
    print('There was an error in loading the layer!')
    