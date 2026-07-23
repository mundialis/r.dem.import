<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dsm.import* downloads and imports digital surface models (DSM, in German DOM) for specified federal state and area of interest.  
Alternatively, local data can be imported. Implemented federal state options are:

- Baden-Württemberg (BW): only local data import
- Bayern (BY): only local data import
- [Brandenburg (BB)](r.dsm.import.bb.md)
- [Berlin (BE)](r.dsm.import.be.md)
- [Bremen (HB)](r.dsm.import.hb.md)
- [Hamburg (HH)](r.dsm.import.hh.md)
- [Hessen (HE)](r.dsm.import.he.md)
- [Sachsen (SN)](r.dsm.import.sn.md)
- [Thüringen (TH)](r.dsm.import.th.md)

For local data import the parameter **local_data_dir** has to be given and the folder structure has to be as follows:

```sh
/path/to/DSMs/
├── BW/*.vrt
└── NW/*.tif
└── ...
```

In the federal state folders the addons searches for a `vrt` file or if none is given all `tif`s will be imported. If local data does not overlap with aoi, data will be downloaded from Open Data portals if federal state supports Open Data.

## EXAMPLE

### Use local DSM

Import local DSM with native resolution:

```sh
r.dsm.import fs=BW aoi=aoi_BW output=dsm_BW local_data_dir=/path/to/DSMs/ -r
```

## AUTHORS

Veronica Koess, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Anika Weinmann, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
