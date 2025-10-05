import ee
import requests
from io import BytesIO
from PIL import Image
import numpy as np

def mask_s2_clouds(image):
  qa = image.select('QA60')

  # Bits 10 and 11 are clouds and cirrus, respectively.
  cloud_bit_mask = 1 << 10
  cirrus_bit_mask = 1 << 11

  # Both flags should be set to zero, indicating clear conditions.
  mask = (
      qa.bitwiseAnd(cloud_bit_mask)
      .eq(0)
      .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
  )

  return image.updateMask(mask).divide(10000)

ee.Authenticate()
ee.Initialize(project='flowers-spaceapps')

lat, lon = 34.738262, -118.388363
center = ee.Geometry.Point(lon, lat)
region = center.buffer(3000).bounds()

dataset_flowers = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate('2019-03-01', '2019-03-31')
    # Pre-filter to get less cloudy granules.
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(mask_s2_clouds)
)
image_flowers = dataset_flowers.mean()

dataset_winter = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterDate('2019-11-01', '2019-11-30')
    # Pre-filter to get less cloudy granules.
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .map(mask_s2_clouds)
)
image_winter = dataset_winter.mean()

thumb_params_RGB = {
    'region': region,
    #'dimensions': 512,
    'format': 'png',
    'min': 0.0,
    'max': 0.3,
    'bands': ['B4', 'B3', 'B2'],
    'crs': 'EPSG:4326',
    'scale': 10
}

url = image_flowers.getThumbURL(thumb_params_RGB)
response = requests.get(url)
response.raise_for_status()