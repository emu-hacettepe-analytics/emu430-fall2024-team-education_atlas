import json

# GeoJSON dosyasını yükle
geojson_path = 'data/tr-cities.json'
with open(geojson_path) as f:
    geojson = json.load(f)

# İlk 5 özelliği incele
print(json.dumps(geojson['features']['name'][:5], indent=4))