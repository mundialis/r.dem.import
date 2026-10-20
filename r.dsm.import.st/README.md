<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dsm.import.st* downloads and imports [digital surface model (DSM, in German DOM)](https://www.lvermgeo.sachsen-anhalt.de/de/gdp-dom-bdom-lsa.html) for Sachsen-Anhalt (ST) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: © GeoBasis-DE / LVermGeo ST [Geodatenportal ST](https://geodatenportal.sachsen-anhalt.de/gfds/)

## EXAMPLE

### Sachsen-Anhalt example

Download and import DSM with native resolution:

```sh
r.dsm.import.st aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
