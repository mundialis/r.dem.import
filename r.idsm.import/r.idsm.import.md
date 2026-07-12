## DESCRIPTION

*r.idsm.import* downloads and imports image based digital surface models
(iDSM, in German bDOM) for specified federal state and area of interest.
Implemented federal state options are:

- [Nordrhein-Westfalen (NW)](r.idsm.import.nw.md)

## EXAMPLE

Import iDSM with native resolution:

```sh
r.idsm.import fs=NW aoi=aoi_NW output=idsm_NW -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Lina Krisztian, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
