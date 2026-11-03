<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dsm.import.bw* downloads and imports [digital surface model (DSM, in German DOM)](https://www.lgl-bw.de/Produkte/3D-Produkte/Digitale-Oberflaechenmodelle/) for Baden-Württemberg (BW) and area of interest.  
The data can be used when referencing the source:  
id: dl-by-de/2.0,  
name: Datenlizenz Deutschland Namensnennung 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: LGL, [Open GeoData Portal BW](www.lgl-bw.de)

## EXAMPLE

### Baden-Württemberg example

Download and import DSM with native resolution:

```sh
r.dsm.import.bw aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
