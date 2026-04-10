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


## Addon health

| federal state | DSM | DTM | nDSM | iDSM | testsuit nDSM | data download | resolution |
|---------------|-----|-----|------|------|----------|---------------|------------|
| BB | &#9745; | &#9745; | | | existiert, läuft nicht | | |
| BE | &#9745; | &#9745; | | | läuft | | |
| BW | | | | | | | |
| BY | | | | | | | |
| HB | | | | | | | |
| HE | &#9745; | &#9745; | | | existiert, läuft nicht | | |
| HH | &#9745; | &#9745; | | | läuft | | |
| MV | | | | | | | |
| NI | &#9745; | &#9745; | | | fehlt | | |
| NW | | &#9745; | &#9745; | &#9745; | läuft | | |
| RP | | | | | | | |
| SH | | | | | | | |
| SL | | | | | | | |
| SN | &#9745; | &#9745; | | | existiert, läuft nicht | | |
| ST | | | | | | | |
| TH | &#9745; | &#9745; | | | läuft | | |

&#9745; = Skripte existieren