## DESCRIPTION

*r.idsm.import.mv* downloads and imports [image based digital surface model
(iDSM, in German bDOM)](https://laiv.geodaten-mv.de/afgvk/Geotopographie/Download?produkt=BDOM20)
for Mecklenburg-Vorpommern (MV) and area of interest.  
The data can be used when referencing the source:  
id: CC-BY 4.0,  
name: Creative Commons Namensnennung 4.0 International,  
url: [https://creativecommons.org/licenses/by/4.0/](https://creativecommons.org/licenses/by/4.0/),
source: LAiV Mecklenburg-Vorpommern ([LAiV M-V BDOM1](https://laiv.geodaten-mv.de/afgvk/Geotopographie/Download?produkt=BDOM20))

## EXAMPLE

### Mecklenburg-Vorpommern example

Download and import iDSM with native resolution:

```sh
r.idsm.import.mv aoi=aoi output=idsm -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
