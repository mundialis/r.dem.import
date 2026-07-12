## DESCRIPTION

*r.dsm.import.sn* downloads and imports [digital surface model (DSM, in
German
DOM)](https://geomis.sachsen.de/geomis-client/?lang=de#/datasets/iso/7efac89b-0798-459d-b06c-c33da86c89a8)
for Sachsen (SN) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: https://www.govdata.de/dl-de/by-2-0,  
source: (c) Landesamt für Geobasisinformation Sachsen (GeoSN)
([GeoSN](https://www.geosn.sachsen.de/))

## EXAMPLE

### Sachsen example

Download and import DSM with native resolution:

```sh
r.dsm.import.sn aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
