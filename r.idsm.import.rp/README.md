## DESCRIPTION

*r.idsm.import.rp* downloads and imports [image based digital surface model
(iDSM, in German bDOM)](https://www.geoportal.rlp.de/mapbender/php/mod_iso19139ToHtml.php?url=https%3A%2F%2Fwww.geoportal.rlp.de%2Fmapbender%2Fphp%2Fmod_dataISOMetadata.php%3FoutputFormat%3Diso19139%26id%3D3d2dda7d-b4b5-47d2-b074-dd45edd36738)
for Rheinland-Pfalz (RP) and area of interest.  
The data can be used when referencing the source:  
id: ©GeoBasis-DE / LVermGeoRP , dl-de/by-2-0,
name: Datenlizenz Deutschland -Namensnennung- Version 2.0,  
url: [https://www.govdata.de/dl-de/by-2-0](https://www.govdata.de/dl-de/by-2-0),
source:  	Landesamt für Vermessung und Geobasisinformationen Rheinland-Pfalz ([LVermGeoRP](www.lvermgeo.rlp.de))

## EXAMPLE

### Rheinland-Pfalz example

Download and import iDSM with native resolution:

```sh
r.idsm.import.rp aoi=aoi output=idsm -r
```

## AUTHORS

Kim Kaiser, [mundialis GmbH & Co. KG](https://www.mundialis.de/)  
Lina Krisztian, [mundialis GmbH & Co. KG](https://www.mundialis.de/)


- data can be used by citing "©GeoBasis-DE / LVermGeoRP", [Datenlizenz Deutschland Namensnennung 2.0](https://www.govdata.de/dl-de/by-2-0), [Geoportal RLP](www.lvermgeo.rlp.de)"
