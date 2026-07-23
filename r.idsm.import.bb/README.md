<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.idsm.import.bb* downloads and imports [image based digital surface model (iDSM, in German bDOM)](https://data.geobasis-bb.de/geobasis/daten/bdom/tif/) for Brandenburg (BB) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: https://www.govdata.de/dl-de/by-2-0,  
source: (c) Landesvermessung und Geobasisinformation Brandenburg ([GeoBasis-DE/LGB](https://geobasis-bb.de/lgb/de/geodaten/))

## EXAMPLE

### Import iDSM

Import iDSM with native resolution:

```sh
r.idsm.import.bb aoi=aoi_BB output=idsm_BB -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
