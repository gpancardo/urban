# Data-Driven Identification of High-Potential Zones for Urban Mobility Investment in Mexico City

## Abstract

This study demonstrates how open government data can be leveraged to identify high-potential zones for urban mobility investment — offering actionable intelligence for public agencies, private operators, and public-private partnerships. Using only census and transport stop data, we map areas where high population density coincides with poor transport access, providing a transparent, reproducible framework for evidence-based decision-making in dense urban environments.

This project presents a spatial analysis framework to identify high-potential market zones for public transport investment in Mexico City. By integrating census block (AGEB) geometries, population data from the 2020 Mexican Census, and geolocated public transport stops, we quantify spatial mismatches between population density and transit accessibility. The methodology computes population density for each AGEB, measures walking distance to the nearest public transport stop, and flags underserved high-density areas as priority zones for mobility investment. Visualizations and summary statistics highlight the most attractive AGEBs and boroughs for intervention, supporting evidence-based urban planning and policy decisions.

## Data Sources

- **AGEB Geometry:** INEGI, Marco Geoestadístico Nacional 2020  
  [https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=702825296805](https://www.inegi.org.mx/app/biblioteca/ficha.html?upc=702825296805)
- **Population Data:** INEGI, Censo de Población y Vivienda 2020  
  [https://www.inegi.org.mx/programas/ccpv/2020/](https://www.inegi.org.mx/programas/ccpv/2020/)
- **Public Transport Stops:** Gobierno de la Ciudad de México, Datos Abiertos  
  [https://datos.cdmx.gob.mx/](https://datos.cdmx.gob.mx/)

## Usage

1. **Prepare Data:** Place all required shapefiles and census Excel files in the project directory.
2. **Run Scripts:**  
   - `transport.py` combines all public transport stops into a single shapefile.
   - `map.py` performs the spatial analysis, generates figures, and exports results.
3. **Outputs:**  
   - Shapefiles, CSVs, and PNG figures summarizing high-potential zones and their characteristics.

## Requirements

- Python 3.11
- geopandas
- pandas
- matplotlib
- numpy

Install dependencies with:
```bash
pip install geopandas pandas matplotlib numpy
```
