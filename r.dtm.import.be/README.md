<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.be* downloads and imports [digital terrain model (DTM, in German DGM)](https://daten.berlin.de/datensaetze/atkis-dgm-1m-rasterweite-fa02f9e1) for Berlin (BE) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: https://www.govdata.de/dl-de/by-2-0,  
source: (c) FIS-Broker Berlin ([FIS-Broker Berlin](https://fbinter.stadt-berlin.de/fb/))

## EXAMPLE

### Berlin example

Download and import DTM with native resolution:

```sh
r.dtm.import.be aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
