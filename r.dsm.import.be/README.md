<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dsm.import.be* downloads and imports [digital surface model (DSM, in German DOM)](https://daten.berlin.de/datensaetze/dom-digitales-oberflachenmodell-5f84f650) for Berlin (BE) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: (c) FIS-Broker Berlin ([FIS-Broker Berlin](https://fbinter.stadt-berlin.de/fb/))

## EXAMPLE

### Berlin example

Download and import DSM with native resolution:

```sh
r.dsm.import.be aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
