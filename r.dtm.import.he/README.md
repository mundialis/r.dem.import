<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.he* downloads and imports [digital terrain model (DTM, in German DGM)](https://www.geoportal.hessen.de/mapbender/php/mod_showMetadata.php?languageCode=de&resource=layer&layout=tabs&id=36995) for Hessen (HE) and area of interest.  
The data can be used when referencing the source:  
id: dl-zero-de/2.0,  
name: Datenlizenz Deutschland - Zero - Version 2.0,  
url: https://www.govdata.de/dl-de/zero-2-0,  
source: (c) Hessische Verwaltung für Bodenmanagement und Geoinformation ([HVBG](https://hvbg.hessen.de/))

## EXAMPLE

### Hessen example

Download and import DTM with native resolution:

```sh
r.dtm.import.he aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
