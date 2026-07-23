<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.bb* downloads and imports [digital terrain model (DTM, in German DGM)](https://data.geobasis-bb.de/geobasis/daten/dgm/xyz/) for Brandenburg (BB) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: (c) Landesvermessung und Geobasisinformation Brandenburg ([GeoBasis-DE/LGB](https://geobasis-bb.de/lgb/de/geodaten/))

## EXAMPLE

### Brandenburg example

Download and import DTM with native resolution:

```sh
r.dtm.import.bb aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
