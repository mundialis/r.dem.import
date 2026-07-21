## DESCRIPTION

*r.dsm.import.th* downloads and imports [digital surface model (DSM, in
German
DOM)](https://geoportal.thueringen.de/gdi-th/download-offene-geodaten/download-hoehendaten)
for Thüringen (TH) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: https://www.govdata.de/dl-de/by-2-0,  
source: (c) GDI-Th ([GDI-Th](https://geoportal.thueringen.de/gdi-th))

## EXAMPLE

### Thüringen example

Download and import DSM with native resolution:

```sh
r.dsm.import.th aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
