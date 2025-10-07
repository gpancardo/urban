import geopandas as gpd
import pandas as pd

# Load each transport layer and keep only point geometries
metro = gpd.read_file("stcmetro_shp/STC_Metro_estaciones_utm14n.shp")
metrobús = gpd.read_file("mb_shp/Metrobus_estaciones.shp")
rtp = gpd.read_file("rtp_shp/RTP_paradas.shp")
trolebus = gpd.read_file("ste_trolebus_shp/STE_Trolebus_Paradas.shp")
tren_ligero = gpd.read_file("ste_tren_ligero_shp/STE_TrenLigero_estaciones_utm14n.shp")
cablebus = gpd.read_file("ste_cablebus_shp/STE_Cablebus_estaciones.shp")

# Filter to keep only point geometries
metro = metro[metro.geometry.type == "Point"]
metrobús = metrobús[metrobús.geometry.type == "Point"]
rtp = rtp[rtp.geometry.type == "Point"]
trolebus = trolebus[trolebus.geometry.type == "Point"]
tren_ligero = tren_ligero[tren_ligero.geometry.type == "Point"]
cablebus = cablebus[cablebus.geometry.type == "Point"]

# Print number of points per mode
print("Points per mode:")
print("Metro:", len(metro))
print("Metrobús:", len(metrobús))
print("RTP:", len(rtp))
print("Trolebús:", len(trolebus))
print("Tren Ligero:", len(tren_ligero))
print("Cablebús:", len(cablebus))

# Set CRS for all layers
crs_target = "EPSG:4326"
metro = metro.to_crs(crs_target)
metrobús = metrobús.to_crs(crs_target)
rtp = rtp.to_crs(crs_target)
trolebus = trolebus.to_crs(crs_target)
tren_ligero = tren_ligero.to_crs(crs_target)
cablebus = cablebus.to_crs(crs_target)

# Add transport mode type column
metro["tipo"] = "Metro"
metrobús["tipo"] = "Metrobus"
rtp["tipo"] = "RTP"
trolebus["tipo"] = "Trolebús"
tren_ligero["tipo"] = "TrenLigero"
cablebus["tipo"] = "Cablebus"

# Combine all transport layers into one GeoDataFrame
transporte_publico = gpd.GeoDataFrame(
    pd.concat([metro, metrobús, rtp, trolebus, tren_ligero, cablebus], ignore_index=True),
    crs=crs_target
)

# Print geometry type counts for verification
print("\nFinal geometry types:")
print(transporte_publico.geometry.type.value_counts())

# Save combined transport stops to shapefile
transporte_publico.to_file("transporte_union.shp")