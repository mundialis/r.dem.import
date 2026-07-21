## DESCRIPTION

*r.dtm.import.ni* downloads and imports [digital terrain model (DTM, in
German
DGM)](https://ni-lgln-opengeodata.hub.arcgis.com/apps/lgln-opengeodata::digitales-gel%C3%A4ndemodell-dgm1/about)
for Niedersachsen (NI) and area of interest.  
The data can be used when referencing the source:  
id: CC-BY 4.0,  
name: Creative Commons Namensnennung 4.0 International,  
url: https://creativecommons.org/licenses/by/4.0/,  
source: (c) Landesamt für Geoinformation und Landesvermessung
Niedersachsen ([LGLN](https://www.lgln.niedersachsen.de/startseite/))

## EXAMPLE

### Niedersachsen example

Download and import DTM with native resolution:

```sh
r.dtm.import.ni aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Johannes Halbauer, [mundialis GmbH & Co.
KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
