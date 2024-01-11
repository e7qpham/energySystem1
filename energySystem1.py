import matplotlib.pyplot as plt
import pandas as pd
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import geopandas as gpd
import networkx as nx


# Read the edges and nodes representing gas transmission pipelines
nodes = gpd.read_file("https://tubcloud.tu-berlin.de/s/8SMwwWQyn6GiPez/download/scigrid-gas-nodes.geojson")
edges = gpd.read_file("https://tubcloud.tu-berlin.de/s/fF6KKpWtJyS3BmD/download/scigrid-gas-pipelines.geojson")


# Plot the transmission network data on a map
## choose figure size
plt.figure(figsize=(15, 10))
## choose a projection
ax = plt.axes(projection=ccrs.PlateCarree())
## add coastlines
ax.add_feature(cfeature.COASTLINE)
## add country borders
ax.add_feature(cfeature.BORDERS, linestyle=":")
## normalize the capacity of the pipelines (for plotting)
capacities = edges["max_cap_M_m3_per_d"]/edges["max_cap_M_m3_per_d"].max()
## normalise the width of the pipelines which is proportional to the rated pipeline pressure
widths = edges["max_pressure_bar"]/edges["max_pressure_bar"].max()
## plot the pipelines
for i, row in edges.iterrows():
    # extract x, y coordinates from geometry column
    x, y = row["geometry"].xy
    # plot the lines
    plt.plot(x,
            y,
            color = plt.cm.viridis(capacities[i]), # line colors indicate their capacities
            linewidth = widths[i], # line widths is scaled by their pressures
            transform = ccrs.PlateCarree()
            )
## add the colorbar, the range is from minimum to maximum of the pipeline capacities
scatter = ax.scatter([], [], c=[],
                    vmin=edges["max_cap_M_m3_per_d"].min(),
                    vmax=edges["max_cap_M_m3_per_d"].max(),
                    cmap=plt.cm.viridis)
plt.colorbar(scatter, label="Pipeline capacity (million cubic meters per day)")
plt.title("European gas transmission network")
plt.show()


# find the pipeline with the highest maximum pressure
max_pressure_pipeline = edges.loc[edges["max_pressure_bar"].idxmax()]
max_pressure_pipeline_info = max_pressure_pipeline[["index", "max_pressure_bar"]]


# find the share of bidirectional pipelines
total_pipelines = len(edges)
bidirectional_pipelines = edges[edges["is_bothDirection"]==1].shape[0]
share = bidirectional_pipelines/total_pipelines *100


# find the cross-border pipelines and this percentage. Then plot this cross-border pipelines on map
all_nodes = nodes[["id", "country_code"]] 
pipeline_country_start = edges.merge(all_nodes, left_on="bus0", right_on="id")
pipeline_country = pipeline_country_start.merge(all_nodes, left_on="bus1", right_on="id", suffixes=("_start", "_end"))
pipeline_country["is_crossborder"] = pipeline_country["country_code_start"] != pipeline_country["country_code_end"]
crossborder_pipelines_number = pipeline_country["is_crossborder"].sum()
crossborder_pipelines_share = crossborder_pipelines_number/len(pipeline_country) *100
## plotting
plt.figure(figsize=(15, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=":")
crossborder_pipelines = pipeline_country[pipeline_country["is_crossborder"]]
for line in crossborder_pipelines["geometry"]:
    x, y = line.xy
    ax.plot(x, y, transform=ccrs.PlateCarree(), color="red")
plt.title("Cross-border pipelines")
plt.show()

