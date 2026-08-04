<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.mv* downloads and imports [digital terrain model (DTM, in German DGM)](https://www.metaver.de/trefferanzeige?docuuid=2351ABA6-019D-4155-853F-76EEFC26CA52&q=dgm-bremen) for Mecklenburg-Vorpommern (MV) and area of interest.  
The data can be used when referencing the source:  
id: CC-BY 4.0,  
name: Creative Commons Namensnennung 4.0 International,  
url: [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/),  
source: LAiV Mecklenburg-Vorpommern ([LAiV M-V DGM1](https://laiv.geodaten-mv.de/afgvk/Geotopographie/Download?produkt=DGM1))

## EXAMPLE

### Mecklenburg-Vorpommern example

Download and import DTM with native resolution:

```sh
r.dtm.import.mv aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
