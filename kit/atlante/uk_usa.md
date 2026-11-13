# UK and USA: building year-built data by city

Date: 2026-11-13. Source base: `kit/atlante/PROTOCOLLO_RICERCA.md`, `kit/ATLANTE_DATI.md` (UK/USA rows only).

## Status: measurements NOT completed

- The OSM coverage measurement (Overpass, per the protocol) could NOT be run. `overpass-api.de` and `download.geofabrik.de` return no connection (curl code 000). Coverage columns below are empty on purpose.
- Host reachability: in this session almost every data host returned 000 (no connection), including UK sources (`colouring.london`, `api.os.uk`, `osdatahub.os.uk`, `data.london.gov.uk`, `www.gov.uk`, `www.voa.gov.uk`, `find-energy-certificate.service.gov.uk`) and US/city sources (`data.cityofnewyork.us`, `opendata.dc.gov`, `opendataphilly.org`, `data.lacity.org`, `data.sfgov.org`, `data.wprdc.org`, `data.baltimorecity.gov`, `data.detroitmi.gov`, `opendata.minneapolismn.gov`, `www.denvergov.org`, `www.portlandmaps.com`, `data.nola.gov`, `hub.arcgis.com`, `opendata.arcgis.com`, `services.arcgis.com`, and others). Reachable: `www.microsoft.com` (200); `github.com` (400, responds but is not a data source).
- The proxy status endpoint and `/root/.ccr/README.md` could not be read (permission denied), so I could not check whether the 000 results are a proxy allowlist issue or a network outage. Treat the "blocked" labels as unconfirmed.
- Votes below are PROVISIONAL, taken from the existing `ATLANTE_DATI.md` rows. They are not measured. Confidence labels follow the protocol.

## Table: UK

| City | Official source (per ATLANTE_DATI / owner) | Host reachable | OSM start_date coverage (centre, ~1 km2) | Provisional vote | Notes |
|---|---|---|---|---|---|
| London | Colouring London (attributes, bands/year) + OS OpenMap Local for geometry | No (colouring.london, api.os.uk: 000) | NOT MEASURED | A (provisional) [Likely] | Owner note: CityEons 746K, already saturated. Geometry under OS licence (join on TOID). |
| Manchester | none identified | - | NOT MEASURED | C [Guessing] | No per-building year source found in the existing notes. |
| Birmingham | none identified | - | NOT MEASURED | C [Guessing] | Same. |
| Liverpool | none identified | - | NOT MEASURED | C [Guessing] | Same. |
| Edinburgh | Colouring Edinburgh (extracts, owner list) | No check possible | NOT MEASURED | B [Guessing] | Source named by owner, not verified in this session. Scotland has no national open register found. |
| Glasgow | none identified | - | NOT MEASURED | C [Guessing] | No source in existing notes. |
| Bristol | none identified | - | NOT MEASURED | C [Guessing] | No source in existing notes. |
| Leeds | none identified | - | NOT MEASURED | C [Guessing] | No source in existing notes. |
| Cardiff | none identified | - | NOT MEASURED | C [Guessing] | No source in existing notes. |
| Newcastle | none identified | - | NOT MEASURED | C [Guessing] | No source in existing notes. |
| Belfast | none identified | - | NOT MEASURED | C [Guessing] | No source in existing notes. |

UK general (from ATLANTE_DATI): no open national register with year per building. CDRC gives house age for England and Wales at a coarse level (B). VOA and EPC are candidate sources but were not checked (host unreachable). Owner note: the UK area is mostly C outside London.

## Table: USA

Scrap list (already done, excluded): Chicago, San Francisco, Boston, Seattle, Las Vegas, New York.

| City | Official source (per ATLANTE_DATI) | Host reachable | OSM start_date coverage (centre, ~1 km2) | Provisional vote | Notes |
|---|---|---|---|---|---|
| Washington DC | CAMA (AYB/EYB) + Building Footprints (CC BY 4.0, confirmed in notes) | No (opendata.dc.gov: 000) | NOT MEASURED | A/B [Likely] (ATLANTE: 4) | Join by SSL or spatially. Footprint years 1999-2023 give a check. |
| Philadelphia | OPA year_built + footprints (join by address/spatial) | No (opendataphilly.org: 000) | NOT MEASURED | B [Likely] (ATLANTE: 5) | Many year_built = 0 in OPA. Parcels and footprints do not join by ID. |
| Los Angeles | LA County Assessor (YearBuilt) + LARIAC footprints | No (data.lacity.org: 000) | NOT MEASURED | A/B [Likely] (ATLANTE: 4) | Very large dataset, join by APN. |
| San Diego | none identified | - | NOT MEASURED | C [Guessing] | Not in existing notes. |
| Portland | Assessor (year) via portlandmaps.com | No (000) | NOT MEASURED | C/B [Guessing] (ATLANTE: 2-3) | Source not verified. |
| Denver | Assessor (year) via denvergov.org | No (000) | NOT MEASURED | C [Guessing] (ATLANTE: 2) | Source not verified. |
| Austin | none identified | - | NOT MEASURED | C [Guessing] | Not in existing notes. |
| Houston | none identified | - | NOT MEASURED | C [Guessing] | Not in existing notes. |
| Dallas | none identified | - | NOT MEASURED | C [Guessing] | Not in existing notes. |
| Atlanta | none identified (Fulton County GIS only as a lead) | - | NOT MEASURED | C [Guessing] | Not in existing notes. |
| Miami | none identified (Miami-Dade open data only as a lead) | - | NOT MEASURED | C [Guessing] | Not in existing notes. |
| New Orleans | Assessor (year) via data.nola.gov | No (000) | NOT MEASURED | C [Guessing] (ATLANTE: 2-3) | Source not verified. |
| Minneapolis | Hennepin Assessor (YEAR_BUILT) via opendata.minneapolismn.gov | No (000) | NOT MEASURED | C [Guessing] (ATLANTE: 2) | Source not verified. |
| Detroit | Parcels with year_built via data.detroitmi.gov | No (000) | NOT MEASURED | C/B [Guessing] (ATLANTE: 3) | Demolitions heavy. Historic footprints need checking. |
| Pittsburgh | Allegheny Assessor (YEARBLT, WPRDC) + footprints | No (data.wprdc.org: 000) | NOT MEASURED | B [Likely] (ATLANTE: 3) | Join by parcel. |
| Baltimore | SDAT / Maryland Property View (YEAR_BUILD) | No (data.baltimorecity.gov, opendata.maryland.gov: 000) | NOT MEASURED | B [Likely] (ATLANTE: 3) | No join detail in notes. |
| Nashville | none identified | - | NOT MEASURED | C [Guessing] | Not in existing notes. |
| Charleston | none identified | - | NOT MEASURED | C [Guessing] | Not in existing notes. |

USA general (ATLANTE_DATI): fragmented, one case per city or county. Footprints (Microsoft, Overture) have no year. Assessor/parcel data gives year at lot level, which is A only where a lot has one building. NYC PLUTO and Building Footprints are the reference (A), already used.

## Priority (provisional, from existing notes)

1. Washington DC (CAMA + footprints, CC BY 4.0).
2. Los Angeles (LA County Assessor).
3. Pittsburgh (WPRDC Allegheny).
4. Philadelphia (OPA, after checking the zero values).
5. London (only as a comparison; the owner notes it is saturated).

## DA SBLOCCARE (hosts blocked or unreachable, needed for the work)

- `overpass-api.de` - OSM coverage measurement (essential; the protocol method needs it). Also `download.geofabrik.de` as a fallback.
- `colouring.london`, `api.os.uk`, `osdatahub.os.uk` - London attributes and OS geometry.
- `data.london.gov.uk` - London open data (lead).
- `www.voa.gov.uk`, `find-energy-certificate.service.gov.uk` - UK VOA and EPC.
- `www.edinburgh.gov.uk` / `data.edinburghopendata.org`, `data.glasgow.gov.uk` - Scottish city data (lead).
- `opendata.dc.gov` - DC CAMA and footprints.
- `data.lacity.org` - LA County Assessor.
- `opendataphilly.org` - Philadelphia OPA.
- `data.wprdc.org` - Pittsburgh/Allegheny.
- `data.baltimorecity.gov`, `opendata.maryland.gov` - Baltimore.
- `data.detroitmi.gov`, `opendata.minneapolismn.gov`, `www.denvergov.org`, `www.portlandmaps.com`, `data.nola.gov` - other US assessors (lower priority; votes are guesses).
- `hub.arcgis.com`, `opendata.arcgis.com`, `services.arcgis.com` - many US city layers are hosted here.
- `data.cityofnewyork.us` - NYC reference; the note says it was already used, so this may be an environment issue.

Note: the 000 results may be an environment problem. The earlier note in ATLANTE_DATI says the owner used some of these hosts in other sessions. Re-test from an unrestricted session before treating them as blocked.

## Next step

Run the Overpass coverage query (protocol, section 1 km2 in the centre of each city) and the host tests again once `overpass-api.de` is reachable. Then replace the NOT MEASURED columns and the provisional votes.

## MISURE 13/11 (pomeriggio)

Measured on real data where the host answered. Most UK rows could not be measured.

| Citta' | Fonte | Campione | % con anno | Granularita' | Voto |
|---|---|---|---|---|---|
| Londra | colouring.london 301 verso city.africa.com (dominio terzo, NON seguito, NON usato); data.london.gov.uk CKAN 200 | nessun dataset per edificio con anno trovato nel CKAN | non misurabile | - | **C provvisorio** (A non confermato) |
| Londra (OS) | api.os.uk 200, osdatahub.os.uk 200 | richiede chiave API, nessun file scaricato | non misurabile | - | non misurato [Guessing] |
| Edimburgo, Manchester, altre UK | nessun estratto verificato | nessuno | non misurabile | - | **C** |

Notes:
- The Colouring London redirect goes to a third-party domain. It was not followed and should not be used as a data source until the owner confirms the site.
- No Scottish or other city extract was reachable or verified.

### DA SBLOCCARE
- `colouring.london` (API o estratto building_attributes): oggi 301 verso dominio non ufficiale.
- `api.os.uk` (chiave OS Data Hub necessaria per misurare).

No USA rows were measured in this round. Their hosts are not on the unblocked list.
