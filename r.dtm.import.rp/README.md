<!-- markdownlint-disable MD041 -->
## DESCRIPTION

*r.dtm.import.rp* downloads and imports [digital terrain model (DTM, in German DGM)](https://www.geoportal.rlp.de/mapbender/php/mod_iso19139ToHtml.php?url=https%3A%2F%2Fwww.geoportal.rlp.de%2Fmapbender%2Fphp%2Fmod_dataISOMetadata.php%3FoutputFormat%3Diso19139%26id%3Dab69aa3d-e786-41f8-95dc-7b34abb06c41) for Rheinland-Pfalz (RP) and area of interest.  
The data can be used when referencing the source:  
id: ©GeoBasis-DE / LVermGeoRP , dl-de/by-2-0,  
name: Datenlizenz Deutschland -Namensnennung- Version 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),  
source: Landesamt für Vermessung und Geobasisinformationen Rheinland-Pfalz ([LVermGeoRP](www.lvermgeo.rlp.de))

## EXAMPLE

### Rheinland-Pfalz example

Download and import DTM with native resolution:

```sh
r.dtm.import.rp aoi=aoi output=dtm -r
```

## AUTHORS

Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Lina Krisztian, [mundialis GmbH & Co. KG](https://www.mundialis.de/)
