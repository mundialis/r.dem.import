<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.idsm.import* downloads and imports image based digital surface models (iDSM, in German bDOM) for specified federal state and area of interest.  
Implemented federal state options are:

- [Brandenburg (BB)](r.idsm.import.bb.md)
- [Hamburg (HH)](r.idsm.import.hh.md)
- [Mecklenburg-Vorpommern](r.idsm.import.mv.md)
- [Nordrhein-Westfalen (NW)](r.idsm.import.nw.md)
- [Rheinland-Pfalz (RP)](r.idsm.import.rp.md)
- [Schleswig-Holstein (SH)](r.idsm.import.sh.md)

## EXAMPLE

Import iDSM with native resolution:

```sh
r.idsm.import fs=NW aoi=aoi_NW output=idsm_NW -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Lina Krisztian, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
