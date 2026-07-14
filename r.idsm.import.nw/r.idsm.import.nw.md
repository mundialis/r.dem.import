## DESCRIPTION

*r.idsm.import.nw* downloads and imports [image based digital surface
model (iDSM, in German
bDOM)](https://www.opengeodata.nrw.de/produkte/geobasis/hm/bdom50_las/bdom50_las/)
for Nordrhein-Westfalen (NW) and area of interest.  
The data can be used when referencing the source:  
id: dl-zero-de/2.0,  
name: Datenlizenz Deutschland - Zero - Version 2.0,  
url: https://www.govdata.de/dl-de/zero-2-0,  
source: (c) Landesbetrieb Information und Technik Nordrhein-Westfalen
([IT.NRW](https://www.it.nrw/))

## EXAMPLE

### Import iDSM

Import iDSMs with native resolution:

```sh
r.idsm.import.nw aoi=aoi_NW output=idsm_NW -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Lina Krisztian, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
