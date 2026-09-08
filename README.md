<!-- markdownlint-disable MD041 -->

[![image-alt](https://github.com/OSGeo/grass/raw/main/man/grass_logo.png)](https://grass.osgeo.org/grass-stable/manuals/index.html)

______________________________________________________________________

## NAME

***r.dem.import*** - Toolset for the import of digital elevation models (DEMs). It includes import addons for the open geodata elevation models for Germany, e.g. for the digital terrain models (DTMs), the digital surface models (DSMs), the image based digital surface models (iDSMs) and the normalised digital surface models (nDSMs).

## KEYWORDS

[raster](https://grass.osgeo.org/grass-stable/manuals/keywords.html#raster), [import](https://grass.osgeo.org/grass-stable/manuals/keywords.html#import), [elevation](https://grass.osgeo.org/grass-stable/manuals/keywords.html#elevation)

## DESCRIPTION

### Modules in this toolset

Examples for the use of this toolset are provided in each module

- [r.dtm.import](r.dtm.import/README.md): downloads digital terrain models (DTM) for specified federal state and area of interest
- [r.dsm.import](r.dsm.import/README.md): downloads digital surface models (DSM) for specified federal state and AOI
- [r.idsm.import](r.idsm.import/README.md): downloads image based digital surface models (iDSM) for specified federal state and AOI
- [r.ndsm.import](r.ndsm.import/README.md): downloads digital surface models (DSM) and digital terrain models (DTM) for specified federal state and AOI, and creates a single file of a normalised DSM (nDSM)

### Overview of the available elevation models

| Federal state | fs | DTM | DSM | iDSM | nDSM | Tile-Index | Resolution | Data Source |
| - | - | - | - | - | - | - | - | - |
| Baden-Württemberg | BW | | | n.a. | | | | [Open GeoData](https://opengeodata.lgl-bw.de/#/) |
| Bayern | BY | | n.a. | | | | | [Open GeoData](https://geodaten.bayern.de/opengeodata/) <br> [iDSM](https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=dom20) |
| Berlin | BE | ☑ | ☑ | | via DSM & DTM | DTM <br> DSM | DTM: 1m <br> DSM: 1m | [Geoportal](https://gdi.berlin.de/) <br> [iDSM](https://gdi.berlin.de/geonetwork/srv/ger/catalog.search#/metadata/967420e0-3ac3-3caf-8421-bf0a2ecc544d) |
| Brandenburg | BB | ☑ | | ☑ | via iDSM & DTM | DTM <br> iDSM | DTM: 1m <br> iDSM: 0.2m | [Geobasis](https://data.geobasis-bb.de/geobasis/daten/) |
| Bremen | HB | ☑ | ☑ | n.a. | via DSM & DTM | DTM <br> DSM | DTM: 1m <br> DSM: 1m | [Geoportal](https://geoportal.bremen.de/geoportal/#) |
| Hamburg | HH | ☑ | n.a. | ☑ | via iDSM & DTM | DTM <br> iDSM | DTM: 1m <br> iDSM: 1m | [Geoportal](https://geoportal-hamburg.de/) |
| Hessen | HE | Bug | Bug | | | | | [Geoportal](/https://www.geoportal.hessen.de/search/) |
| Mecklenburg-Vorpommern | MV | ☑ | | ☑ | | DTM <br> iDSM | DTM: 1m <br> iDSM: 0.2m | [Geoportal](https://laiv.geodaten-mv.de/afgvk/) <br> [iDSM](https://laiv.geodaten-mv.de/afgvk/Geotopographie/Download?produkt=BDOM20) |
| Niedersachsen | NI | ☑ | ☑ | | via DSM & DTM | DTM <br> DSM | DTM: 1m <br> DSM: 1m | [Open GeoData](https://ni-lgln-opengeodata.hub.arcgis.com/) <br> [iDSM](https://ni-lgln-opengeodata.hub.arcgis.com/apps/lgln-opengeodata::bildbasiertes-digitales-oberfl%C3%A4chenmodell-bdom20/about) |
| Nordrhein-Westfalen | NW | ☑ | n.a. | ☑ | ☑ | DTM <br> nDSM <br> iDSM | DTM: 1m <br> nDSM: 0.5m <br> iDSM: 0.5m | [Open GeoData](https://www.opengeodata.nrw.de/produkte/geobasis/hm/) |
| Rheinland-Pfalz | RP | | n.a. | ☑ | | iDSM | iDSM: 0.2m | [Geoportal](https://www.geoportal.rlp.de/) <br> [iDSM](https://geoshop.rlp.de/opendata-domb.html) |
| Saarland | SL | | | n.a. | | | | [Geoportal](https://geoportal.saarland.de/) |
| Sachsen | SN | ☑ | ☑ | n.a. | via DSM & DTM | DTM <br> DSM | DTM: 1m <br> DSM: 1m | [Open Geodata](https://www.geodaten.sachsen.de/downloadbereich-digitale-hoehenmodelle-4851.html) |
| Sachsen-Anhalt | ST | | | | | | | [Geoportal](https://www.lvermgeo.sachsen-anhalt.de/de/gdp-open-data.html) <br> [iDSM](https://www.lvermgeo.sachsen-anhalt.de/de/gdp-bdom20.html) |
| Schleswig-Holstein | SH | ☑ | n.a. | ☑ | via iDSM & DTM | DTM <br> iDSM | DTM: 1m <br> iDSM: 0.2m | [Geoportal](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/) |
| Thüringen | TH | ☑ | ☑ | n.a. | via DSM & DTM | DTM <br> DSM | DTM: 1m <br> DSM: 1m | [Geoportal](https://geoportal.thueringen.de/gdi-th/download-offene-geodaten/download-hoehendaten) |

## REQUIREMENTS

[grass-gis-helpers>=4.0.0](https://pypi.org/project/grass-gis-helpers/)

## SEE ALSO

*[r.dop.import](https://github.com/mundialis/r.dop.import) for import of digital orthophotos*

## AUTHORS

Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
