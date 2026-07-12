## DESCRIPTION

*r.dtm.import.nw* downloads and imports [digital terrain model (DTM, in
German
DGM)](https://www.opengeodata.nrw.de/produkte/geobasis/hm/dgm1_tiff/dgm1_tiff/)
for Nordrhein-Westfalen (NW) and area of interest.  
The data can be used when referencing the source:  
id: dl-zero-de/2.0,  
name: Datenlizenz Deutschland - Zero - Version 2.0,  
url: https://www.govdata.de/dl-de/zero-2-0,  
source: (c) Landesbetrieb Information und Technik Nordrhein-Westfalen
([IT.NRW](https://www.it.nrw/))

## EXAMPLE

### Import DTM

Import DTM with native resolution:

```sh
r.dtm.import.nw aoi=aoi_NW output=dtm_NW -r
```

## AUTHORS

Victoria-Leandra Brunn, [mundialis GmbH & Co.
KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
