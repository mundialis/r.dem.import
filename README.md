## r.dem.import - Toolset for the import of digital elevation models (DEMs)

It includes import addons for the open geodata elevation models for Germany,
e.g. for the digital terrain models (DTMs), the digital surface models (DSMs),
the image based digital surface models (iDSM) and the normalised DSMs (nDSMs).

The r.dem.import toolset consists of the following modules:

- r.ndsm.import: downloads digital surface models (DSM) and digital
  terrain models (DTM) for specified federal state and area of interest,
  and creates a single file of a normalised DSM (nDSM).
- r.dsm.import: downloads digital surface models (DSM) for specified
  federal state and AOI
- r.idsm.import: downloads image based digital surface models (iDSM) for
  specified federal state and AOI
- r.dtm.import: downloads digital terrain models (DTM) for specified
  federal state and AOI

## Addon coverage for federal states

| Federal state | DTM | DSM | nDSM | iDSM | Tile-Index | Resolution | Data Source |
| - | - | - | - | - | - | - | - |
| BB | ☑| n.a. | via iDSM & DTM | ☑ | DTM <br> iDSM | DTM: 1m <br> iDSM: 0.2m | [Geobasis](https://data.geobasis-bb.de/geobasis/daten/) |
| BE | ☑ | ☑ | via DSM & DTM | | DTM <br> DSM | DTM: 1m <br> DSM: 1m  | [Geoportal](https://gdi.berlin.de/) <br> [iDSM](https://gdi.berlin.de/geonetwork/srv/ger/catalog.search#/metadata/967420e0-3ac3-3caf-8421-bf0a2ecc544d) |
| BW | | | | n.a. | | | [Open GeoData](https://opengeodata.lgl-bw.de/#/) |
| BY | | n.a. | | | | |[Open GeoData](https://geodaten.bayern.de/opengeodata/) <br> [iDSM](https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=dom20) |
| HB | ☑ | ☑ | via DSM & DTM | n.a. | DTM <br> DSM | DTM: 1m <br> DSM: 1m | [Geoportal](https://geoportal.bremen.de/geoportal/#) |
| HE | Bug | Bug | | | | | [Geoportal](/https://www.geoportal.hessen.de/search/) |
| HH | ☑ | n.a. | via iDSM & DTM | ☑  | DTM <br> iDSM | DTM: 1m <br> iDSM: 1m | [Geoportal](https://geoportal-hamburg.de/) |
| MV | | | | | | | [Geoportal](https://laiv.geodaten-mv.de/afgvk/) <br> [iDSM](https://laiv.geodaten-mv.de/afgvk/Geotopographie/Download?produkt=BDOM20) |
| NI | ☑ | ☑ | via DSM & DTM |  | DTM <br> DSM | DTM: 1m <br> DSM: 1m | [Open GeoData](https://ni-lgln-opengeodata.hub.arcgis.com/) <br> [iDSM](https://ni-lgln-opengeodata.hub.arcgis.com/apps/lgln-opengeodata::bildbasiertes-digitales-oberfl%C3%A4chenmodell-bdom20/about) |
| NW | ☑ | n.a. | ☑ | ☑ | DTM <br> nDSM <br> iDSM | DTM: 1m <br> nDSM: 0.5m <br> iDSM: 0.5m | [Open GeoData](https://www.opengeodata.nrw.de/produkte/geobasis/hm/) |
| RP | | n.a. | | | | | [Geoportal](https://www.geoportal.rlp.de/) <br> [iDSM](https://geoshop.rlp.de/opendata-domb.html) |
| SH | | n.a. | | ☑ | | | [Geoportal](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/)|
| SL | | | | n.a. | | | [Geoportal](https://geoportal.saarland.de/) |
| SN | ☑ | ☑ | via DSM & DTM | n.a. | DTM <br> DSM | DTM: 1m <br> DSM: 1m  | [Open Geodata](https://www.geodaten.sachsen.de/downloadbereich-digitale-hoehenmodelle-4851.html) |
| ST | | | | | | | [Geoportal](https://www.lvermgeo.sachsen-anhalt.de/de/gdp-open-data.html) <br> [iDSM](https://www.lvermgeo.sachsen-anhalt.de/de/gdp-bdom20.html) |
| TH | ☑ | ☑ |via DSM & DTM | n.a. |DTM <br> DSM | DTM: 1m <br> DSM: 1m  | [Geoportal](https://geoportal.thueringen.de/gdi-th/download-offene-geodaten/download-hoehendaten)|
