# Pittsburgh skyline dataset - sources (2026-11-17)

Reachable and used (all via curl/API, no scraping workarounds):
- S1 https://en.wikipedia.org/wiki/List_of_tallest_buildings_in_Pittsburgh (height m, floors, year, coords; 24 rows used; also tallest-demolished and timeline tables)
- S2 per-building Wikipedia articles (infobox + text): URL for each entry in skyline.json landmarks[].meta.urls
- S3 Wikidata items (QID in meta.qid): P625 coords, P571 inception, P1619 opening, P576. Not independent of Wikipedia (often imported from it); treated as a separate database only.
- S4 OpenStreetMap through Nominatim (nominatim.openstreetmap.org): independent coordinate check (51 entries matched) plus height / building:levels / start_date tags where mapped.
- S5 WPRDC "City Designated Individual Historic Sites" (data.wprdc.org, CKAN datastore, 158 names, no dates): used only for meta.city_designated_historic_site.
- S6 https://en.wikipedia.org/wiki/Pittsburgh_flood_of_1936 (flood extent: Point to Grant Street; crest 46 ft on 1936-03-18).

Definitions
- verified_2_sources = year agrees in >=2 distinct databases (Wikipedia / Wikidata / OSM) AND Wikipedia-vs-OSM coordinates agree (<=70 m buildings, <=200 m bridges). For demolished entries OSM does not exist, so the check is Wikipedia + Wikidata only.
- Heights: "height_m" is the Wikipedia list/infobox value (includes spire where the list does); "height_osm_m" shown when OSM has it. One PPG Place: 193.6 m with glass spires (list) vs 166 m roof (infobox, OSM).

Conflicts kept visible (year in note field): US Steel Tower 1970/1971, BNY Mellon 1983/1984, Fifth Ave Place 1987/1988, Grant Bldg 1929/1930, Bell Telephone 1931/1923, Cathedral of Learning 1936 (list) vs start 1926, Benedum 1927/1928, Birmingham Bridge 1976/1977, 16th St Bridge 1922/1923, Federated Hermes 1986/1982.
Corrections to the brief: Fort Duquesne Bridge opened 1969 (not 1963); Kaufmann's and Union Station (Pennsylvania Station) are NOT demolished in the sources found; Wikipedia pages named "Clark Building" and "Buhl Building" are other cities' buildings and were not used (Buhl dropped).

Blocked hosts (CONNECT 403 from the proxy, not worked around)
- www.phlf.org (Pittsburgh History & Landmarks Foundation): wanted landmark designation dates
- catalog.archives.gov (NARA): 1936 flood photos
- www.emporis.com and www.skyscrapercenter.com (CTBUH): second source for heights/years
- www.loc.gov (HABS/HAER drawings, flood photos), www.nps.gov and npgallery.nps.gov (NRHP forms): designation years
- digital.library.pitt.edu (Pitt flood photo archive): per-building 1936 evidence
- also failed to connect (no HTTP answer, not individually confirmed as 403): www.hmdb.org, pghcitypaper.com, pittsburghpa.gov, preservationpa.org, api.census.gov, historicpittsburgh.org, britannica.com, heinzhistorycenter.org, pittsburghhistory.org, pghbridges.com, buildingsofpa.org, photon.komoot.io; overpass-api.de (connection reset).
- Rate limited, not blocked: commons.wikimedia.org (429), en.wikipedia.org / wikidata.org API (429 after bursts). Wikimedia Commons was therefore not used.

Build scripts (build.py, assemble.py, final.py) are in this folder; raw API caches are in ../w/.
