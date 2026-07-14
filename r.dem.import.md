[![image-alt](grass_logo.png)](https://grass.osgeo.org/grass-stable/manuals/index.html)

------------------------------------------------------------------------

## NAME

***r.dem.import*** - Toolset for the import of digital elevation models
(DEMs). It includes import addons for the open geodata elevation models
for Germany e.g. for the digital terrain models (DTMs), the digital
surface models (DSMs) and the normalised DSMs (nDSMs).

## KEYWORDS

[raster](raster.md), [import](topic_import.md),
[](keywords.html#elevation.md)

## DESCRIPTION

The *r.dem.import* toolset consists of the following modules:

[r.ndsm.import](r.ndsm.import/r.ndsm.import.md)  
downloads digital surface models (DSM) and digital terrain models (DTM)
for specified federal state and area of interest, and creates a single
file of a normalised DSM (nDSM).

[r.dsm.import](r.dsm.import/r.dsm.import.md)  
downloads digital surface models (DSM) for specified federal state and
aoi

[r.dtm.import](r.dtm.import/r.dtm.import.md)  
downloads digital terrain models (DTM) for specified federal state and
aoi

Overview of the available elevation models:

| Federal state | nDSM | DSM | DTM |
|----|----|----|----|
| Baden-Württemberg (BW) | Not available | Not available | Not available |
| Bayern (BY) | Not available | Not available | TODO |
| Berlin (BE) | DSM-DTM | r.dsm.import fs=BE | r.dtm.import fs=BE |
| Brandenburg (BB) | DSM-DTM | r.dsm.import fs=BB | r.dtm.import fs=BB |
| Bremen (HB) | Not available | r.dsm.import fs=HB | r.dtm.import fs=HB |
| Hamburg (HH) | DSM-DTM | r.dsm.import fs=HH | r.dtm.import fs=HH |
| Hessen (HE) | DSM-DTM | r.dsm.import fs=HE | r.dtm.import fs=HE |
| Mecklenburg-Vorpommern (MV) | Not available | Not available | Not available |
| Niedersachsen (NI) | r.dsm.import fs=NI | r.dtm.import fs=NI |  |
| Nordrhein-Westfalen (NW) | r.ndsm.import fs=NW | TODO | TODO |
| Rheinland-Pfalz (RP) | Not available | Not available | TODO |
| Saarland (SL) | Not available | Not available | Not available |
| Sachsen (SN) | DSM-DTM | r.dsm.import fs=SN | r.dtm.import fs=SN |
| Sachsen-Anhalt (ST) | TODO | TODO | TODO |
| Schleswig-Holstein (SH) | TODO | TODO | TODO |
| Thüringen (TH) | DSM-DTM | r.dsm.import fs=TH | r.dtm.import fs=TH |

## REQUIREMENTS

- [grass-gis-helpers\>=0.4.0](https://pypi.org/project/grass-gis-helpers/)

## AUTHOR

Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
