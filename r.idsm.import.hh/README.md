<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.idsm.import.hh* downloads and imports [image based digital surface model (iDSM, in German bDOM)](https://daten-hamburg.de/geographie_geologie_geobasisdaten/digitales_hoehenmodell_bdom/) for Hamburg (HH) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: (c) Landesbetrieb Geoinformation und Vermessung ([LGV-HH](https://www.hamburg.de/politik-und-verwaltung/behoerden/behoerde-fuer-stadtentwicklung-und-wohnen/aemter-und-landesbetrieb/landesbetrieb-geoinformation-und-vermessung))

## EXAMPLE

### Hamburg example

Download and import iDSM with native resolution:

```sh
r.idsm.import.hh aoi=aoi output=idsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
