<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.ndsm.import* downloads (image based) digital surface models (iDSM/DSM, in German bDOM/DOM) for specified federal state and area of interest, stores it in a local directory, normalizes the DSM files with corresponding digital terrain model files (DTM, in german DGM), and creates a single file of a normalised DSM (nDSM, in German nDOM) in GRASS.  
Implemented federal state options are:

- Berlin
- Brandenburg
- Bremen
- Hamburg
- Hessen
- Niedersachsen
- [Nordrhein-Westfalen (NW)](r.ndsm.import.nw.md)
- Sachsen
- Schleswig-Holstein
- Thüringen

## EXAMPLE

```sh
r.ndsm.import fs=Nordrhein-Westfalen aoi=Polygon_BonnBeuel output=NRW_nDSM_output
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
