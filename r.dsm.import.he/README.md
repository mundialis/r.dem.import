<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dsm.import.he* downloads and imports [digital surface model (DSM, in German DOM)](https://hvbg.hessen.de/registry/spatial/dataset/acb6269d-db21-4b6d-8329-de291b6e8180) for Hesse (HE) and area of interest.  
The data can be used when referencing the source:  
id: dl-zero-de/2.0,  
name: Datenlizenz Deutschland - Zero - Version 2.0,  
url: https://www.govdata.de/dl-de/zero-2-0,  
source: (c) Hessische Verwaltung für Bodenmanagement und Geoinformation ([HVBG](https://hvbg.hessen.de/))

## EXAMPLE

### Hessen example

Download and import DSM with native resolution:

```sh
r.dsm.import.he aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
