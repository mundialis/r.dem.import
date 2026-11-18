<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.by* downloads and imports [digital terrain model (DTM, in German DGM)](https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=dgm1) for Bayern (BY) and area of interest.  
The data can be used when referencing the source:  
id: CC BY 4.0,
name: Namensnennung 4.0 International,  
url: [https://creativecommons.org/licenses/by/4.0/deed.de](https://creativecommons.org/licenses/by/4.0/deed.de),  
source: [Bayerische Vermessungsverwaltung](www.geodaten.bayern.de)

## EXAMPLE

### Bayern example

Download and import DTM with native resolution:

```sh
r.dtm.import.by aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
