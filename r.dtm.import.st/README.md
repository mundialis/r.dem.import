<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.st* downloads and imports [digital terrain model (DTM, in German DGM)](LINK) for Sachsen-Anhalt (ST) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: SOURCE

## EXAMPLE

### Sachsen-Anhalt example

Download and import DTM with native resolution:

```sh
r.dtm.import.st aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
