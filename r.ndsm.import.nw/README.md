<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.ndsm.import.nw* downloads and imports [normalized digital surface model (nDSM, in German nDOM)](https://www.opengeodata.nrw.de/produkte/geobasis/hm/ndom50_tiff/ndom50_tiff/) for Nordrhein-Westfalen (NW) and area of interest.  
The data can be used when referencing the source:  
id: dl-zero-de/2.0,  
name: Datenlizenz Deutschland - Zero - Version 2.0,  
url: [https://www.govdata.de/dl-de/zero-2-0](https://www.govdata.de/dl-de/zero-2-0),  
source: (c) Landesbetrieb Information und Technik Nordrhein-Westfalen ([IT.NRW](https://www.it.nrw/))

## EXAMPLE

### Import nDSM

Import nDSMs with native resolution:

```sh
r.ndsm.import.nw aoi=aoi_NW output=ndsm_NW -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
