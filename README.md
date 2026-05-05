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

| Federal state | DSM | DTM | nDSM | iDSM | Tile-Index | Data Download | Resolution | Data Source |
| - | - | - | - | - | - | - | - | - |
| BB | - | ☑ | via iDSM & DTM | ☑ (TODO: rename r.dsm.bb to r.idsm.bb) | DTM <br> iDSM(DSM)| | DTM: 1m <br> iDSM: 0.2m | |
| BE | ☑ | ☑ | via DSM & DTM | - | DSM <br> DTM | | DSM: 1m <br> DTM: 1m  | |
| BW | | | | | | | | [Open GeoData Portal](https://opengeodata.lgl-bw.de/#/) |
| BY | | | | | | | |[Open GeoData](https://geodaten.bayern.de/opengeodata/) |
| HB | | | | | | | | [Geoportal](https://geoportal.bremen.de/geoportal/#) |
| HE | Bug | Bug | | | | | | [Geoportal](/https://www.geoportal.hessen.de/search/) |
| HH | ☑ | ☑ | via DSM & DTM | - | DSM <br> DTM | | DSM: 1m <br> DTM: 1m | [Geoportal](https://geoportal-hamburg.de/) |
| MV | | | | | | | | [Downloadportal](https://laiv.geodaten-mv.de/afgvk/) |
| NI | ☑ | ☑ | via DSM & DTM | - | DSM <br> DTM | | DSM: 1m <br> DTM: 1m | [Open GeoData](https://ni-lgln-opengeodata.hub.arcgis.com/) |
| NW | - | ☑ | ☑ | ☑ | DTM <br> nDSM <br> iDSM | | DTM: 1m <br> nDSM: 0.5m <br> iDSM: 0.5m |
| RP | | | | | | | | [Geoportal](https://www.geoportal.rlp.de/) |
| SH | | | | | | | | [Downloadportal](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/) |
| SL | | | | | | | | [Geoportal](https://geoportal.saarland.de/) |
| SN | ☑ | ☑ | via DSM & DTM | - |DSM <br> DTM | | DSM: 1m <br> DTM: 1m  | |
| ST | | | | | | | | [Geodatenportal](https://www.lvermgeo.sachsen-anhalt.de/de/gdp-open-data.html) |
| TH | ☑ | ☑ |via DSM & DTM | - |DSM <br> DTM | | DSM: 1m <br> DTM: 1m  | |
