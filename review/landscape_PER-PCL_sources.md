# PER-PCL explorer: layers to register in the catalogue

The explorer's layers are described in landscapes/PER-PCL/sources.yaml with the texts of their author. None is a catalogue record yet: ids are assigned by the team. Some catalogue records describe products derived from the same sources (last column); they are not the files the explorer shows, so they are not linked. Once a layer is registered, set `record: mosaic:<id>` in sources.yaml (and on the overlay in explorer.yaml) and the website links it.

Licences to confirm before publishing: terrain (DEM provenance open; assumed Copernicus GLO-30, see the data report), GEOBOSQUES forest loss (no licence stated, citation required), SERNANP protected areas (derived maps authorised, no commercial use, original data not redistributed). Not hosted: RAISG Indigenous territories (licence and sensitivity).

| Layer | Title | Licence | Related catalogue records |
|---|---|---|---|
| veg_classes | Vegetation classes (co-produced) | CC0 (as stated on the CaltechDATA record) |  |
| terrain | Terrain | per DEM source (to confirm) |  |
| s2_rgb | Satellite imagery (Sentinel-2) | Copernicus Sentinel data: free use with attribution |  |
| department | Ucayali department | Peruvian government boundary data; the same boundaries on datosabiertos.gob.pe (publisher IGN) carry the Open Data Commons Attribution License (ODC-By) |  |
| admin_boundaries | Provinces & districts | Open Data Commons Attribution License (ODC-By), as stated on the dataset page | MFL-2026-072 (Provinces and Districts, datosabiertos.gob.pe) |
| protected_areas | Protected areas (ANP & ACR) | SERNANP viewer terms: information 'de dominio público'; derived maps authorised with SERNANP cited as source; no commercialisation; redistribution of the original information not authorised (this file is a clipped, simplified derivative; verbatim terms in the data report) | MFL-2026-073 (National Protected Natural Areas), MFL-2026-074 (Regional Conservation Areas) |
| fire | Active fires (VIIRS) | NASA FIRMS data are freely available; cite NASA FIRMS |  |
| canopy | Canopy height (ETH 2020) | CC BY 4.0 (ETH Research Collection record) |  |
| forest_loss | Forest & loss (GEOBOSQUES) | the product metadata's LICENCIA field is '-' (no licence stated); citation required as given by GEOBOSQUES | MFL-2026-079 (GEOBOSQUES forest / loss, aggregated by province and district) |
| precip | Precipitation (CHIRPS v3) | CC-BY-4.0 |  |
| temperature | Temperature (CHIRTS-ERA5) | CC-BY-4.0 |  |
| spi3 | Drought index (SPI-3) | Derived from CHIRPS v3.0 (CC-BY-4.0) |  |
| gedi | GEDI canopy height (RH95) | NASA Earth science data: free and open; cite the product DOI |  |
| landcover | Land cover (MapBiomas) | CC BY 4.0 - 'Los datos de MapBiomas son de uso público, abierto y gratuito, sujetos a citación' (site footer) | MFL-2026-081 (MapBiomas Peru C4, vectorised and aggregated) |
| burned_area | Burned area (MapBiomas) | CC BY 4.0 (MapBiomas: public, open and free use, subject to citation) | MFL-2026-082 (MapBiomas Fuego, cumulative 2013–2024, Collection 1) |
