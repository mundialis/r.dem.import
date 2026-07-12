## DESCRIPTION

*r.dsm.import.hb* downloads and imports [digital surface model (DSM, in
German
DOM)](https://geodienste.bremen.de/wms_dom1?REQUEST=GetCapabilities&SERVICE=WMS&VERSION=1.3.0&)
for Bremen and Bremerhaven (HB) and area of interest.  
The data can be used when referencing the source:  
id: CC-BY 4.0,  
name: Creative Commons Namensnennung 4.0 International,  
url: https://creativecommons.org/licenses/by/4.0/,  
source: (c) Landesamt GeoInformation Bremen ([Geo
Bremen](https://www.geo.bremen.de/))

## EXAMPLE

### Bremen example

Download and import DSM with native resolution:

```sh
r.dsm.import.hb aoi=aoi output=dsm -r
```

## AUTHORS

Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Leon Louwarts, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
