<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import* downloads and imports digital terrain models (DTM, in German DGM) for specified federal state and area of interest. Alternatively, local data can be imported. Implemented federal state options are:  

- Baden-Württemberg (BW): only local data import
- Bayern (BY): only local data import
- [Brandenburg (BB)](r.dtm.import.bb.md)
- [Berlin (BE)](r.dtm.import.be.md)
- [Hamburg (HH)](r.dtm.import.hh.md)
- [Hessen (HE)](r.dtm.import.he.md)
- [Nordrhein-Westfalen (NW)](r.dtm.import.nw.md)
- [Schleswig-Holstein](r.dtm.import.sh.md)
- [Sachsen (SN)](r.dtm.import.sn.md)
- [Thüringen (TH)](r.dtm.import.th.md)

For local data import the parameter **local_data_dir** has to be given and the folder structure has to be as follows:

```sh
/path/to/DTMs/
├── BW/*.xyz
└── NW/*.xyz
└── ...
```

In the federal state folders the addons searches for `xyz` files. If local data does not overlap with aoi, data will be downloaded from Open Data portals if federal state supports Open Data.

## EXAMPLE

### Use local DTM

Import local DTM with native resolution:

```sh
r.dtm.import fs=BW aoi=aoi_BW output=dtm_BW local_data_dir=/path/to/DTMs/ -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Victoria-Leandra Brunn, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
