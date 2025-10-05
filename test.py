import geemap.foliumap as geemap
import ee

ee.Authenticate()
ee.Initialize(project='flowers-spaceapps')

Map = geemap.Map(centre=(-118.3506, 34.7094), zoom=4)
Map