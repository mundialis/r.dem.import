<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dsm.import.ni* downloads and imports [digital surface model (DSM, in German DOM)](https://ni-lgln-opengeodata.hub.arcgis.com/apps/lgln-opengeodata::digitales-oberfl%C3%A4chenmodell-dom1/about) for Niedersachsen (NI) and area of interest.  
The data can be used when referencing the source:  
id: CC-BY 4.0,  
name: Creative Commons Namensnennung 4.0 International,  
url: https://creativecommons.org/licenses/by/4.0/,  
source: (c) Landesamt für Geoinformation und Landesvermessung Niedersachsen ([LGLN](https://www.lgln.niedersachsen.de/startseite/))

## EXAMPLE

### Niedersachsen example

Download and import DSM with native resolution:

```sh
r.dsm.import.ni aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Johannes Halbauer, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
