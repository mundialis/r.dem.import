<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.idsm.import.sh* downloads and imports [image based digital surface model (iDSM, in German bDOM)](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/dl-bdom.html) for Schleswig-Holstein (SH) and area of interest.  
The data can be used when referencing the source:  
id: CC BY 4.0,  
name: Creative Commons Namensnennung 4.0 International,  
url: https://creativecommons.org/licenses/by/4.0/,  
source: ©GeoBasis-DE/LVermGeo SH ([GDI-SH](https://geodaten.schleswig-holstein.de/gaialight-sh/_apps/dladownload/index.php))

## EXAMPLE

### Import iDSM

Import iDSM with native resolution:

```sh
r.idsm.import.sh aoi=aoi_SH output=idsm_SH -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
