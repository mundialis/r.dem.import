## DESCRIPTION

*r.dtm.import.sn* downloads and imports [digital terrain model (DTM, in
German
DGM)](https://geomis.sachsen.de/geomis-client/?lang=de#/datasets/iso/a3dba5b2-0118-4d76-ab78-ba656a1b489e)
for Sachsen (SN) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: https://www.govdata.de/dl-de/by-2-0,  
source: (c) Landesamt für Geobasisinformation Sachsen (GeoSN)
([GeoSN](https://www.geosn.sachsen.de/))

## EXAMPLE

### Sachsen example

Download and import DTM with native resolution:

```sh
r.dtm.import.sn aoi=aoi output=dtm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
