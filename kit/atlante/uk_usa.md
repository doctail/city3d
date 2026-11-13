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

## MISURE USA 13/11 (pomeriggio)

Metodo: dati reali da API Socrata / ArcGIS REST / CKAN, query di conteggio e distribuzione sull'intera tabella (non campione), dove possibile join testato su campione. Overpass e Geofabrik NON usati (dichiarato morto dal proprietario): copertura OSM non misurata. Non misurato: alcune citta' per host bloccati (vedi DA SBLOCCARE).

| Citta' | Dataset (fonte, host) | Campione | % con anno valido | Geometria | Voto | Evento storico |
|---|---|---|---|---|---|---|
| Pittsburgh | Allegheny County Property Assessments, YEARBLT per parcel, residenziale citta' (data.wprdc.org, CKAN datastore SQL) | 274.197 parcel residenziali, anno 2026, tutti | 87,0% (238.494). Anni validi 1601-2026: 100% dei non nulli. Distribuzione validi: <1800 = 5, 1800s = 10.134 (4,2%), 1900s = 218.349 (91,6%), 2000+ = 10.006 (4,2%). Minimo 1770 | Si': impronte edifici "Allegheny County Building Footprint Locations" (CSV datastore, campo PIN = PARID). Join testato: 220.157 PIN residenziali con impronta; 215.931 parcel con impronta E anno valido (78,8% del totale, 90,6% dei validi) | A [Certain] | 1845 Great Fire (centro): non misurato, anni 1831-1889 non letti |
| Philadelphia | OPA_PROPERTIES_PUBLIC, year_built + flag year_built_estimate (services.arcgis.com, ArcGIS query) | 583.714 parcel, tutti | 92,6% con anno (540.318 validi). MA: 407.753 (70% del totale) hanno year_built_estimate = Y, cioe' stima. Anno NON stimato e valido: 132.303 (22,7% del totale). Zero/vuoto: 984 | Si': building_footprints (545.943 poligoni), join via parcel_id_num = pwd_parcel_id di opa_properties_public_pde. Test su 11.811 ID PWD: 11.806 con match (100%). Footprint sorgente 'LI' e' ~0,6%, non joinata | B [Certain] per i numeri, voto B perche' la misura reale e' 23% | 1793 yellow fever: non misurato. 1700s = 257 record totali (non separato stimato/reale) |
| Baltimora (City) | SDAT Maryland Real Property Assessments, CAMA YEARBLT (opendata.maryland.gov, Socrata) | 241.670 record Baltimore City | 82,0% (198.277). 0000: 43.388 (18%). Ma PICCHI TONDI: 1900 = 18.454, 1910 = 4.217, 1920 = 41.265; vicini 1899 = 20, 1901 = 38, 1909 = 264, 1911 = 318. Round-decade = 63.936 = 32% dei validi. Valido al netto dei picchi: 134.341 (55,6% del totale). Pre-1800: 23 | Parziale: solo punto lat/long per record, nessuna impronta trovata su host sbloccati. Licenza: Public Domain (verificata) | B [Certain] per i conteggi, [Likely] che i picchi siano placeholder/imputazione | 1904 Great Baltimore Fire: 1903 = 202, 1904 = 509, 1905 = 949, 1906 = 607. Nessuna rottura netta a livello citta' [Likely] |
| Portland (citta') | Taxlots regional, YEARBUILT (portlandmaps.com ArcGIS MapServer, Taxlots/0, campo stringa) | 249.430 taxlot con SITECITY = PORTLAND (su 607.091 regionali, COUNTY = M) | 89,7% (223.853). Vuoti/zero: 25.225 (10,1%). Pre-1800: 0. 1800s = 2.813 (1,3%), 1900s = 184.365 (82,4%), 2000+ = 36.675 (16,4%) | Si': poligoni taxlot nello stesso layer (Shape) | A [Certain] | Non misurato |
| Minneapolis | Assessing Department Parcel Data 2025, YEARBUILT (services.arcgis.com, ArcGIS query) | 131.978 parcel, tutti | 88,0% (116.149). Null/0: 15.829 (12%). Pre-1800: 0. 1800s = 1.419 (1,2%), 1900s = 104.500 (90%), 2000+ = 10.230 (8,8%) | No nel layer (tabella, con X/Y e TAX_MAP_UFMT, nessun PID). Poligoni in Assessor_Parcels_2024 (City_Parcels, 128.756, PID) ma join X/Y non testato. Nessuna impronta | B [Likely] (geometria da joinare) | Non misurato |
| Los Angeles | Parcels (data.lacity.org, qyra-qm2s, 883.677 poligoni). Assessor YearBuilt non trovato su host sbloccati | 883.677 parcel (senza anno) | 0% misurato: nessun campo anno nei dataset disponibili su data.lacity.org (Parcels, APN list, Assessor-Parcel-Universe e' di Cook County, non LA: scartato) | Si' (poligoni), senza anno | C [Certain] per quanto misurato | 1933 Long Beach earthquake: non misurato |
| Washington DC | CAMA residenziale (maps2.dcgis.dc.gov) + Building Footprints 2023 (opendata.dc.gov, download via hub.arcgis.com) | non misurato | non misurato | footprint 2023 licenza CC BY 4.0 (verificata nei metadata); item count ~149k al 90% del job | n.m. (provvisorio B) | 1814 incendio di Washington: non misurato |
| Denver | Assessor (denvergov.org reindirizza a opendata-geospatialdenver.hub.arcgis.com) | non misurato | non misurato | n.m. | n.m. (provvisorio C) | non misurato |

Note di qualita':
- Pittsburgh: CSV YEARBLT ha 87% di copertura, valori validi, ma e' PER PARCEL: lotti con piu' edifici hanno un solo anno. Il join PIN a impronte e' il punto forte.
- Philadelphia: l'anno e' in larga parte stimato dall'OPA (75% dei non nulli). Per "anno reale" usare solo il sottoinsieme con flag vuoto (132.303). Il join impronte e' il migliore misurato (100%).
- Baltimora: non usare i picchi 1900/1910/1920 come anno reale senza verifica. Sono 32% dei validi.
- Anni indietro: Pittsburgh arriva al 1770 (5 record pre-1800); Baltimora 23 record pre-1800; Philadelphia ha 257 record nel 1700s (non separati reale/stimato); Minneapolis e Portland non hanno nulla prima del 1800. Nessuna citta' misurata da' stock 1700 significativo tranne Philadelphia (non separato) e Pittsburgh (5).
- Licenze: Maryland Public Domain (verificata). Pittsburgh parcel CC0 (verificata, CKAN). Allegheny footprint: "not specified". DC footprint CC BY 4.0 (verificata). Philadelphia, Minneapolis, Portland, LA: licenza non dichiarata nei metadata letti, da verificare.

Confidenza: [Certain] = numeri misurati da query sull'intera tabella. [Likely] = inferenza forte (placeholder Baltimora, geometria Minneapolis). [Guessing] = eventi storici, non misurati.

DA SBLOCCARE (host bloccati o senza accesso, necessari per completare):
- `maps2.dcgis.dc.gov` - DC CAMA residenziale (il dataset CAMA e' su questo host, non su opendata.dc.gov). Rifiutato dal proxy.
- `hub.arcgis.com` - DC: il download dei footprint (opendata.dc.gov) reindirizza qui. Rifiutato dal proxy.
- `opendata-geospatialdenver.hub.arcgis.com`, `services1.arcgis.com` - Denver: hub e servizi assessor. Rifiutati (000).
- `data.lacounty.gov`, `assessor.lacounty.gov`, `portal.assessor.lacounty.gov` - LA County Assessor YearBuilt / EffectiveYearBuilt. Rifiutati (000).
- `www.arcgis.com` - ricerca globale ArcGIS Online per assessor con anno. Rifiutato (000).
- `overpass-api.de`, `download.geofabrik.de` - ancora morti (copertura OSM non misurata).

## MISURE USA 13/11 (sera)

Metodo: dati reali da ArcGIS REST (FeatureServer/MapServer). Conteggi e distribuzioni sull'intera tabella (query server-side, `returnCountOnly` e paging `resultOffset`/`resultRecordCount`), join testato su campione casuale (seed 7, 199-200 parcel). Overpass e Geofabrik NON usati. Per la sola verifica di LA e' usato `services.arcgis.com` (raggiungibile dal proxy, non nella lista sbloccati: da confermare). Per le citta' con anno non trovato, nessun dato misurato.

| Citta' | Dataset (fonte, host) | Campione | % con anno | Geometria | Piu' vecchio (>100 record) | Voto | Evento storico |
|---|---|---|---|---|---|---|---|
| Washington DC | Residential (CAMA), tabella di DCGIS_APPS/Real_Property_Application (maps2.dcgis.dc.gov); campo AYB | 109.411 record residenziali (intera tabella, 109.300 SSL distinti) | 99,5% (108.892). Null/0: 205. Commerciale (CAMA, 21.086 record): 96,1% | Si': Unique Building Identifier (DCGIS_DATA/Facility_and_Structure layer 17, 185.695 poligoni, SSL). Join SSL: 96,3% dei record residenziali con poligono; 96,1% con poligono E anno valido | 1870 (196 record). Pre-1800: 29 record (1754 primo) | A [Likely] (per SSL/BLDG_NUM, quasi 1 record per SSL). Distribuzione validi: <1800 0,03%, 1800s 3,8%, 1900s 87,8%, 2000+ 8,4%. Picchi a decennio tondo 20,3% dei validi (atteso ~10%): [Likely] imputazione | 1814: incendio di Washington (storia, non legata al dato) |
| Denver | Assessor residenziale ODC_real_property_residential_characteristics, campo CCYRBLT (services1.arcgis.com, tabella 50). Nei nomi del servizio NON esiste YEAR_BUILT ne' RES_ORIG_YR: questi sono i campi trovati | 213.032 parcel residenziali (intera tabella, PARID unico) | 96,7% (206.033). Null/0: 6.999. Commerciale ORIG_YOC (28.215): 55,9% | Si': ODC_PROP_BUILDINGOUTLINES_A (390.104 poligoni, layer 111). Join SCHEDNUM (parcel) = PARID: 199/200 parcel del campione con geometria; 99,0% (197/199) intersecano almeno un poligono edificio | 1884 (206 record). Pre-1800: 0 | B [Likely]: anno per parcel (parcel con piu' edifici = un anno solo), non per edificio. Distribuzione validi: 1800s 4,7%, 1900s 70,9%, 2000+ 24,3% | 1858: fondazione di Denver (storia, non legata al dato) |
| Los Angeles County | Assessor Parcel Data Roll 2026, tabella Parcel_Data_2026 con campo YearBuilt (services.arcgis.com/RmCCgQtiZLDCtblq, host NON nella lista) | 4.856.866 righe, intera tabella. Campione 1.000 righe = 1.000 AIN distinti | 45,4% sul totale (2.205.603). Tra le righe con edifici (totBuildingDataLines > 0, 2.212.990): 99,7% con anno. Il vuoto e' terreno senza edificio | No: tabella senza geometria (ha CENTER_LAT/LON per riga). Poligoni parcel non misurati su host sbloccati (data.lacity.org copre solo LA City) | 1885 (304 record). Scansione 1850-1899: primo anno con >100 = 1885. Record <1800: 0 | B [Likely]: anno per AIN (parcel), non per edificio. 1800s 0,2%, 1900s 90,7%, 2000+ 9,1% dei validi. Picchi 1910 (8.749) e 1920 (11.452): da verificare | 1933: terremoto di Long Beach (storia, non misurata) |
| Richmond (VA) | Year of Construction, polygon layer con Year_Built, PIN (services1.arcgis.com/k3vhq11XkBNeeOfM) | 66.248 poligoni, intero layer | 100% (66.248). Null/0: 0 | Si' poligoni, mediana area ~1.594 (unita' del layer non dichiarata: footprint o parcel non verificato) | 1890 (301). Pre-1800: 24 (min 1720) | B [Likely] per geometria non verificata. Distribuzione: 1800s 2,3%, 1900s 89,9%, 2000+ 7,7% | 1737 fondazione (storia), non misurato |
| Cambridge (MA) | Property Database FY2026, campo Condition_YearBuilt (services1.arcgis.com/WnzC35krSYGuYov4) | 30.156 record (28.850 PID distinti), intero layer | 87,4% (26.358). Null/0: 3.795 | No: tabella senza geometria, solo PID/BldgNum | 1850 (123). Pre-1800: 28 record (min 1700) | B [Likely]: anno per record edificio, geometria da joinare (GISID non testato) | 1630 fondazione (storia), non misurato |
| Minneapolis, Portland, Pittsburgh, Philadelphia, Baltimora | Non rimisurati in questo giro (misure del pomeriggio valide) | n.m. | n.m. | n.m. | n.m. | n.m. | n.m. |
| Detroit | Tentative Assessment Roll 2026 (services2.arcgis.com), SEMCOG footprints (services8.arcgis.com) | n.m. | n.m. | n.m. | n.m. | n.m. (C provvisorio) | 1701 fondazione (storia) |
| New Orleans | Footprint services (services.arcgis.com): NOLA Building Footprints, 159.012 e 162.486 poligoni. Campi: solo date_lastu / F_updated_at (data di modifica, non anno di costruzione). Portale data.nola.gov bloccato | n.m. (anno non trovato) | n.m. | Si' footprint, senza anno | n.m. | C [Certain] per quanto misurato (nessun anno) | 1718 fondazione (storia) |
| Charleston (SC) | build_parcelid (services1, 493.612 poligoni): solo CREATED_DATE / LAST_EDITED_DATE. Portale bloccato | n.m. | n.m. | Si' poligoni, senza anno | n.m. | C [Certain] per quanto misurato | 1670 fondazione (storia) |
| Savannah | Savannah_GA_Buildings (services6), pub.sagis.org, datahub.savannahga.gov: non misurati | n.m. | n.m. | n.m. | n.m. | n.m. (C provvisorio) | 1733 fondazione (storia) |
| Nashville | Building_Footprints_view (services2), Building_Footprint_Richland_Creek (services5): non misurati. data.nashville.gov bloccato | n.m. | n.m. | n.m. | n.m. | n.m. (C provvisorio) | 1779 fondazione (storia) |
| Atlanta | Building Footprints (services3, gis.atlantaga.gov): non misurati. data.atlantaga.gov bloccato | n.m. | n.m. | n.m. | n.m. | n.m. (C provvisorio) | 1837 (Terminus) (storia) |
| Cleveland | Cleveland Building Footprints 2023 (services3): non misurato. data.clevelandohio.gov bloccato | n.m. | n.m. | n.m. | n.m. | n.m. (C provvisorio) | 1796 fondazione (storia) |
| Cincinnati | Buildings (services1, 87.799 poligoni) e Building_Footprints (68.426): solo geometria, nessun campo anno. Portale bloccato | n.m. | n.m. | Si' poligoni, senza anno | n.m. | C [Certain] per quanto misurato | 1788 fondazione (storia) |
| St. Louis | Footprints_StLouis_USA_FEMA_Prj (17.565 poligoni): solo PROD_DATE / IMAGE_DATE (non costruzione). STL_Buildings (stlgis) bloccato | n.m. | n.m. | Si' poligoni, senza anno | n.m. | C [Certain] per quanto misurato | 1764 fondazione (storia) |
| San Antonio | Nessun dataset con anno trovato su host raggiungibili. data.sanantonio.gov bloccato | n.m. | n.m. | n.m. | n.m. | C [Certain] per quanto misurato | 1718 Mission San Antonio de Valero (storia) |

Note di qualita':
- DC: la CAMA residenziale ha anno per SSL-edificio e il join con i poligoni e' alto (96%). Buona base per un timelapse, con il sospetto di imputazione sui decenni tondi.
- Denver: il nome del campo dell'anno non e' YEAR_BUILT ne' RES_ORIG_YR; e' CCYRBLT (residenziale) e ORIG_YOC (commerciale). Il join parcel-poligono funziona (99%), ma l'anno resta per parcel.
- LA: il campo YearBuilt e' pieno dove c'e' un edificio (99,7%). Il 45% sul totale e' terreno vacante, non un buco di dati. La tabella non ha geometria: serve il join con i poligoni parcel (LA County, non misurato).
- Nessuna citta' del secondo elenco ha un anno per edificio su host raggiungibili. Quasi tutti i footprint trovati hanno solo date di modifica o di cattura, che NON sono anni di costruzione.
- Pre-1800 esiste solo come pochi record isolati (DC 29, Richmond 24, Cambridge 28, LA 0, Denver 0). Nessuna citta' misurata ha uno stock 1700 significativo.

Confidenza: [Certain] = numeri misurati da query sull'intera tabella (salvo dove indicato). [Likely] = inferenza forte (granularita' per parcel, geometria non verificata, picchi). [Guessing] = nessuno in questa tabella; gli eventi storici sono riferimenti generali, non legati al dato.

DA SBLOCCARE (host bloccati dal proxy, necessari per completare le citta' non misurate):
- `services2.arcgis.com` - Detroit Tentative Assessment Roll 2026 e Parcels 2021. Rifiutato dal proxy (000).
- `services8.arcgis.com` - Detroit SEMCOG_BuildingFootprints. Rifiutato (000).
- `gis.semcog.org` - Detroit Buildings_2024 (footprint ufficiali SEMCOG). Non testato.
- `data.nola.gov`, `data.nashville.gov`, `data.atlantaga.gov`, `data.clevelandohio.gov`, `data.cincinnati-oh.gov`, `data.detroitmi.gov`, `data.richmondva.gov`, `data.cambridgema.gov`, `data.sanantonio.gov`, `data.charlestoncity.gov`, `datahub.savannahga.gov`, `www.stlouis-mo.gov`: portali aperti delle citta'. Rifiutati (000 / connect_rejected).
- `stlgis.stlouis-mo.gov` (STL_Buildings), `gis.atlantaga.gov` (Atlanta Building Footprints), `pub.sagis.org` (Savannah DPLAT): non raggiungibili. Non testati in dettaglio.
- `services3.arcgis.com`, `services6.arcgis.com`: non testati, ma contengono footprint di Atlanta, Cleveland, Savannah. Da verificare con un test di raggiungibilita'.
- `services.arcgis.com` e' stato usato per LA (Assessor Parcel Data Roll 2026): non nella lista sbloccati, ma raggiungibile. Conferma o rimuovi.
- `overpass-api.de`, `download.geofabrik.de`: non usati (dichiarati morti).
