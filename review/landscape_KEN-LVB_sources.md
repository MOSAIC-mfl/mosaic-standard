# KEN-LVB explorer: layers to register in the catalogue

The explorer's layers are described in landscapes/KEN-LVB/sources.yaml with the texts of their author. None is a catalogue record yet: ids are assigned by the team. Once a layer is registered, set `record: mosaic:<id>` in sources.yaml (and on the overlay in explorer.yaml) and the website links it.

Licences to confirm before publishing: ICPAC basin boundary (not specified, withheld), DAHITI lake level (non-commercial), HydroSHEDS rivers (display only, no redistribution).

| Layer | Title | Source | Licence |
|---|---|---|---|
| basin | Lake Victoria Basin boundary | ICPAC geoportal (geonode:lv_basin), 2019; lake shoreline from the Copernicus GLO-30 water-body mask (2011-2015), class 2 at native ~30 m, islands as holes | ICPAC: not specified (confirm before public release); WBM: Copernicus, free with attribution |
| flood_hazard | Flood hazard (observed flood frequency) | Copernicus EMS Global Flood Monitoring (Sentinel-1), 20 m, 2016-2025 | Copernicus EMS: free with attribution |
| terrain | Terrain (Copernicus GLO-30) | Copernicus DEM GLO-30 (~30 m), basin extent | Copernicus DEM: free use with attribution |
| precip | Precipitation (CHIRPS v3) | CHIRPS v3.0 daily, 0.05 deg. CHIRPS is a pentad product; daily values are pentad totals disaggregated with ECMWF ERA5 precipitation (the 'rnl' flavour). | CC-BY-4.0 |
| temperature | Temperature (CHIRTS-ERA5) | CHIRTS-ERA5 daily Tmax/Tmin, 0.05 deg; Tmean = (Tmax+Tmin)/2 | CC-BY-4.0 |
| s2_rgb | Satellite imagery (Sentinel-2) | Sentinel-2 L2A median mosaic 2023-2025 (COPERNICUS/S2_SR_HARMONIZED), 30 m | Copernicus Sentinel data: free use with attribution |
| lake_level | Lake water level (satellite altimetry) | DAHITI (DGFI-TUM), multi-mission altimetry | CC BY-NC 4.0 (DAHITI terms of use; non-commercial use only) |
| spi3 | Drought index (SPI-3) | SPI-3 computed from CHIRPS v3.0 monthly totals (gamma fit, Thom 1958; zero-rain mixed distribution), calibration 1991-2020. Daily CHIRPS = ERA5-disaggregated pentads ('rnl'); monthly totals are unaffected by the disaggregation choice. | Derived from CHIRPS v3.0 (CC-BY-4.0) |
| rivers | Rivers (HydroRIVERS) | HydroRIVERS v1.0 (HydroSHEDS), Strahler order >= 4, clipped to the basin | HydroSHEDS v1 licence (WWF; HydroSHEDS Technical Documentation v1.4, Appendix A). Incorporates data from the HydroSHEDS version 1 database, © World Wildlife Fund, Inc. (2006-2022), used under license; full attribution in the data README |
| population | Population (exposure input) | WorldPop constrained individual countries 2020, 100 m (KEN, UGA, TZA, RWA, BDI) | CC-BY-4.0 |
| forest_loss | Tree-cover loss (Hansen GFC) | Hansen Global Forest Change GFC-2025-v1.13; loss where tree cover 2000 >= 30 % | CC-BY-4.0 |
| fire | Active fires (VIIRS) | NASA FIRMS VIIRS 375 m active fires; density: S-NPP only (2012-2025); points: S-NPP + NOAA-20 (NOAA-20 archive from 2020); confidence nominal/high | NASA open data (attribution) |
| burned_area | Burned area (MODIS) | MODIS MCD64A1 v6.1 monthly burned area, annual union per ~500 m cell, via Microsoft Planetary Computer | NASA open data (attribution) |
| landcover | Land cover (Esri/IO annual) | Esri/Impact Observatory annual LULC v2 (10 m; displayed at 30 m, nearest), via Microsoft Planetary Computer (io-lulc-annual-v02) | CC BY 4.0 |
| worldcover | Land cover reference (ESA WorldCover 2021) | ESA WorldCover 10 m 2021 v200 (displayed at 30 m, nearest) | CC BY 4.0 |
| osm_labels | Place names | OpenStreetMap via the Protomaps daily basemap (build 2026-10-22, schema v4, Planetiler 0.10.2) | ODbL 1.0 - © OpenStreetMap contributors |
| admin_boundaries | Admin boundaries | geoBoundaries gbOpen ADM1 + ADM2 (simplified), Kenya, Uganda, Tanzania, Rwanda, Burundi; clipped to the basin | per boundary - see provenance (Public Domain, CC0, CC BY 4.0, CC BY 3.0 IGO, ODbL); geoBoundaries itself CC BY 4.0 |
