<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dsm.import.by* downloads and imports [digital surface model (DSM, in German DOM)](https://geodaten.bayern.de/opengeodata/OpenDataDetail.html?pn=dom20) for Bayern (BY) and area of interest.  
The data can be used when referencing the source:  
id: CC BY 4.0,
name: Namensnennung 4.0 International,  
url: [https://creativecommons.org/licenses/by/4.0/deed.de](https://creativecommons.org/licenses/by/4.0/deed.de),  
source: [Bayerische Vermessungsverwaltung](www.geodaten.bayern.de)

## EXAMPLE

### Bayern example

Download and import DSM with native resolution:

```sh
r.dsm.import.by aoi=aoi output=dsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
