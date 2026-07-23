<!-- markdownlint-disable MD041 -->

## DESCRIPTION

*r.dtm.import.sh* downloads and imports [digital terrain model (DTM, in German DGM)](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/dl-dgm1.html) for Schleswig-Holstein (SH) and area of interest.  
The data can be used when referencing the source:  
id: CC BY 4.0,  
name: Creative Commons Namensnennung 4.0 International,  
url: [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/),  
source: ©GeoBasis-DE/LVermGeo SH ([GDI-SH](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/index.php))

## EXAMPLE

### Import DTM

Import DTM with native resolution:

```sh
r.dtm.import.sh aoi=aoi_SH output=dtm_SH -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
