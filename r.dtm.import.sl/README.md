<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.sl* downloads and imports [digital terrain model (DTM, in German DGM)](https://www.shop.lvgl.saarland.de/cloud/index.php/s/NK8ndP55qAqGEZD?dir=/OD_DGM1_2025_tif_LK) for Saarland (SL) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: © GeoBasis DE/LVGL-SL ([GeoPortal Saarland](https://geoportal.saarland.de/))

## EXAMPLE

### Saarland example

Download and import DTM with native resolution:

```sh
r.dtm.import.sl aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
