# ------------------------------------------------------------
# Urban Market Intelligence: Identifying High-Potential Zones 
# for Public Transport Investment in Mexico City
# Journal-ready analysis and visualizations
# ------------------------------------------------------------

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load AGEB geometry (shapefile)
ageb_gdf = gpd.read_file("shape/09a.shp")
ageb_gdf["CVEGEO"] = ageb_gdf["CVEGEO"].astype(str)

# Load AGEB population data (Census 2020)
ageb_df = pd.read_excel("RESAGEBURB_09XLSX20.xlsx")
ageb_df["CVEGEO"] = (
    ageb_df["ENTIDAD"].astype(str).str.zfill(2) +
    ageb_df["MUN"].astype(str).str.zfill(3) +
    ageb_df["LOC"].astype(str).str.zfill(4) +
    ageb_df["AGEB"].astype(str).str.zfill(4)
)
ageb_df = ageb_df[["CVEGEO", "POBTOT"]]

# Merge geometry and population data
ageb = ageb_gdf.merge(ageb_df, on="CVEGEO", how="inner")
ageb = ageb.dropna(subset=["POBTOT"])
ageb["POBTOT"] = ageb["POBTOT"].astype(int)

# Calculate population density (people/km²)
ageb = ageb.to_crs("EPSG:32614")
ageb["area_km2"] = ageb.geometry.area / 1_000_000
ageb["density"] = ageb["POBTOT"] / ageb["area_km2"]
ageb = ageb[ageb["area_km2"] >= 0.01].copy()

# Load public transport stops
transport = gpd.read_file("transporte_union.shp")
transport = transport.to_crs("EPSG:32614")

# Compute minimum distance from AGEB centroid to nearest transport stop
ageb["centroid"] = ageb.geometry.centroid
def min_distance_to_transport(point, gdf):
    return gdf.distance(point).min()
ageb["dist_to_transport_m"] = ageb["centroid"].apply(lambda pt: min_distance_to_transport(pt, transport))

# Identify high-potential market zones
HIGH_DENSITY_THRESHOLD = 8000    # people/km²
LOW_ACCESS_THRESHOLD = 800       # meters
ageb["high_density"] = ageb["density"] > HIGH_DENSITY_THRESHOLD
ageb["low_access"] = ageb["dist_to_transport_m"] > LOW_ACCESS_THRESHOLD
ageb["high_potential_zone"] = ageb["high_density"] & ageb["low_access"]

# Save final AGEB data (without centroid geometry)
ageb_no_centroid = ageb.drop(columns=["centroid"])
ageb_no_centroid.to_file("ageb_final.shp")

# Calculate population in high-potential zones
pop_in_zones = ageb[ageb["high_potential_zone"]]["POBTOT"].sum()
print(f"Population in high-potential zones: {pop_in_zones:,}")

# Save AGEB data for further use
ageb_for_save = ageb.drop(columns=["centroid"])
ageb_for_save.to_file("ageb_final.shp")

# Calculate attractiveness index and export top 10 AGEBs
ageb["attractiveness_index"] = ageb["density"] / (ageb["dist_to_transport_m"] / 1000)
top10 = (
    ageb[ageb["high_potential_zone"]]
    .sort_values("attractiveness_index", ascending=False)
    [["CVEGEO", "POBTOT", "density", "dist_to_transport_m", "attractiveness_index"]]
    .head(10)
)
top10.to_csv("top_10_high_potential_agebs_cdmx.csv", index=False)

# Plot main map: High-potential zones and transport stops
fig, ax = plt.subplots(1, 1, figsize=(12, 10))
ageb.plot(ax=ax, color="#f0f0f0", edgecolor="#ffffff", linewidth=0.2)
high_potential = ageb[ageb["high_potential_zone"]]
high_potential.plot(ax=ax, color="#e31a1c", alpha=0.85, edgecolor="#ffffff", linewidth=0.3, label="High-potential market zones\n(High density + Low access)")
modes = transport["tipo_1"].unique()
colors = plt.cm.tab10(np.linspace(0, 1, len(modes)))
for i, mode in enumerate(modes):
    subset = transport[transport["tipo_1"] == mode]
    subset.plot(ax=ax, color=colors[i], markersize=25, label=mode, marker='o', alpha=0.85)
ax.set_title(
    "High-Density, Low-Access Zones: Untapped Mobility Markets in Mexico City",
    fontsize=14,
    fontweight="bold",
    pad=20
)
ax.axis("off")
legend = ax.legend(
    loc="upper left",
    bbox_to_anchor=(1, 1),
    frameon=True,
    fontsize=10,
    title="Legend",
    title_fontsize=11
)
legend.get_frame().set_facecolor("white")
legend.get_frame().set_alpha(0.95)
caption = (
    "High-potential zones defined as:\n"
    "• Population density > 8,000 people/km²\n"
    "• Walking distance to nearest public transport stop > 800 m\n\n"
    f"Total population in these zones: {pop_in_zones:,}"
)
props = dict(boxstyle="round", facecolor="white", alpha=0.9)
ax.text(0.02, 0.02, caption, transform=ax.transAxes, fontsize=9, verticalalignment="bottom", bbox=props)
plt.tight_layout()
plt.savefig("fig1_high_potential_zones_cdmx.png", dpi=300, bbox_inches="tight")
plt.show()

# Chart: Density vs. Distance to Transport
plt.figure(figsize=(10, 7))
plt.scatter(
    ageb["dist_to_transport_m"],
    ageb["density"],
    c="#bdbdbd",
    alpha=0.5,
    s=12,
    label="All AGEBs (n={})".format(len(ageb))
)
high_potential = ageb[ageb["high_potential_zone"]]
plt.scatter(
    high_potential["dist_to_transport_m"],
    high_potential["density"],
    c="#e31a1c",
    s=20,
    label="High-potential zones (n={})".format(len(high_potential)),
    edgecolor="white",
    linewidth=0.2
)
plt.axvline(800, color="#252525", linestyle="--", linewidth=1, alpha=0.7)
plt.axhline(8000, color="#252525", linestyle="--", linewidth=1, alpha=0.7)
plt.xlabel("Walking Distance to Nearest Public Transport Stop (meters)", fontsize=11)
plt.ylabel("Population Density (people per km²)", fontsize=11)
plt.title("Spatial Mismatch: Density vs. Transport Access in Mexico City", fontsize=13, fontweight="bold")
plt.legend(frameon=True, fontsize=10)
plt.grid(alpha=0.3, linestyle="--", linewidth=0.5)
plt.xlim(0, ageb["dist_to_transport_m"].quantile(0.99))
plt.ylim(0, ageb["density"].quantile(0.99))
plt.tight_layout()
plt.savefig("fig2_density_vs_distance_all_agebs.png", dpi=300, bbox_inches="tight")
plt.show()

# Chart: Distribution of distance to transport
plt.figure(figsize=(8, 5))
plt.hist(ageb["dist_to_transport_m"], bins=50, color="#74c476", edgecolor="white", alpha=0.8)
plt.axvline(800, color="#e31a1c", linestyle="--", label="Threshold: 800 m")
plt.xlabel("Distance to Nearest Public Transport Stop (m)")
plt.ylabel("Number of AGEBs")
plt.title("Walking Distance to Public Transport in Mexico City")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig("fig3_distance_distribution.png", dpi=300, bbox_inches="tight")
plt.show()

# Chart: Population in high-potential vs. served zones
pop_served = ageb[~ageb["high_potential_zone"]]["POBTOT"].sum()
labels = ["High-Potential Zones\n(>8k/km² & >800m)", "Served Zones"]
sizes = [pop_in_zones, pop_served]
colors = ["#e31a1c", "#2ca25f"]
plt.figure(figsize=(6, 6))
plt.pie(
    sizes,
    labels=labels,
    colors=colors,
    autopct=lambda pct: f"{pct:.1f}%\n({int(pct/100.*sum(sizes)/1e3):.0f}k)",
    startangle=90,
    textprops={'fontsize': 10}
)
plt.title("Population in High-Potential vs. Served Zones", fontsize=12, pad=20)
plt.tight_layout()
plt.savefig("fig4_population_pie.png", dpi=300, bbox_inches="tight")
plt.show()

# Chart: Top 10 AGEBs by attractiveness index with borough names
alcaldia_map = {
    "002": "Azcapotzalco",
    "003": "Coyoacán",
    "004": "Cuajimalpa",
    "005": "Gustavo A. Madero",
    "006": "Miguel Hidalgo",
    "007": "Milpa Alta",
    "008": "Tláhuac",
    "009": "Tlalpan",
    "010": "Venustiano Carranza",
    "011": "Xochimilco",
    "012": "Benito Juárez",
    "013": "Iztacalco",
    "014": "Iztapalapa",
    "015": "Cuauhtémoc",
    "016": "La Magdalena Contreras",
    "017": "Álvaro Obregón"
}
ageb["MUN"] = ageb["CVEGEO"].str[2:5]
ageb["alcaldia"] = ageb["MUN"].map(alcaldia_map)
top10 = (
    ageb[ageb["high_potential_zone"]]
    .nlargest(10, "attractiveness_index")
    [["CVEGEO", "POBTOT", "density", "dist_to_transport_m", "attractiveness_index", "alcaldia"]]
    .head(10)
)
top10["label"] = top10["alcaldia"] + " (" + top10["CVEGEO"].str[-4:] + ")"
plt.figure(figsize=(9, 6))
bars = plt.barh(
    range(len(top10)),
    top10["attractiveness_index"],
    color="#e31a1c",
    alpha=0.85,
    edgecolor="white",
    linewidth=0.3
)
plt.yticks(range(len(top10)), top10["label"])
plt.xlabel("Attractiveness Index (Density / Distance to Transport)", fontsize=10)
plt.title("Top 10 High-Potential AGEBs for Mobility Investment in Mexico City", fontsize=12, fontweight="bold")
plt.gca().invert_yaxis()
plt.grid(axis="x", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("fig5_top10_agebs.png", dpi=300, bbox_inches="tight")
plt.show()

# Chart: Number of high-potential AGEBs by borough
oportunidad = ageb[ageb["high_potential_zone"]]
agebs_por_alcaldia = oportunidad.groupby("alcaldia").size().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
agebs_por_alcaldia.plot(kind="bar", color="#e31a1c", alpha=0.85)
plt.xlabel("Borough (Alcaldía)")
plt.ylabel("Number of High-Potential AGEBs")
plt.title("High-Potential Mobility Zones by Borough in Mexico City")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("fig6_agebs_por_alcaldia.png", dpi=300, bbox_inches="tight")
plt.show()

# Chart: Population in high-potential zones by borough
pob_por_alcaldia = (
    oportunidad.groupby("alcaldia")["POBTOT"]
    .sum()
    .sort_values(ascending=False)
)
plt.figure(figsize=(10, 6))
pob_por_alcaldia.plot(kind="bar", color="#e31a1c", alpha=0.85)
plt.xlabel("Borough (Alcaldía)")
plt.ylabel("Population in High-Potential Zones")
plt.title("Population in Underserved High-Density Areas by Borough, Mexico City")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("fig6_poblacion_por_alcaldia.png", dpi=300, bbox_inches="tight")
plt.show()

# Print population by borough for reporting
print(pob_por_alcaldia)

print("All figures and data saved!")