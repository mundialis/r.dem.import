## DESCRIPTION

*r.dtm.import.th* downloads and imports [digital terrain model (DTM, in
German
DGM)](https://geoportal.thueringen.de/gdi-th/download-offene-geodaten/download-hoehendaten)
for Thüringen (TH) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: https://www.govdata.de/dl-de/by-2-0,  
source: (c) GDI-Th ([GDI-Th](https://geoportal.thueringen.de/gdi-th))

## EXAMPLE

### Thüringen example

Download and import DTM with native resolution:

```sh
r.dtm.import.th aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
