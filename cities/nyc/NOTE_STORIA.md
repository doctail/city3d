# New York: story notes (yb-historian, 18/11/2026)

Tags: [Certain] = read in a Wikipedia page opened with the API on 18/11/2026 (sources S1-S70, S74-S76 in `story.json`); [Likely] = from memory or a source not opened; [Guessing] = my estimate. Every conf in `story.json` follows: high = Certain, medium = Certain date with a sketched shape/size, low = Likely/Guessing.

## Counts
45+3 = 48 cards, 20 soste, 17 polity chips (all regimes, 8 of them low-confidence from memory), 76 sources (73 pages + 3 data sources), 25 landmarks, 13 zones, 6 water (landfill) rings, 3 fires, 1 flood, 22 bridge decks, 4 guttings, 3 lost buildings, 1 wall. Population: 29 points (S57).

## Facts [Certain] (page read)
Fort Amsterdam 1625 site / 1626 / completed 1635 / razed 1790; municipal rights 2 Feb 1653; Wall Street wall 1653-1699; English capture Aug-Sept 1664 (arrival 27 Aug, Stuyvesant concedes after 4 Sept: the exact capitulation day was NOT read, chip at 1664.68 = [Likely]); Dutch reconquest Aug 1673 (New Orange), Westminster 9/19 Feb 1674, Andros 10 Nov 1674; Trinity 1698 / burned 1776 / 1790 / 1839-46; Federal Hall 1699-1703, Stamp Act Congress 1765, Congress 1785-90, inauguration 1789, demolished 1812, Custom House 1842; fires 20 Sept 1776 and 16 Dec 1835 (17 blocks, 13 acres, 530-700 buildings); Evacuation Day 25 Nov 1783; Commissioners' Plan 1811; Collect Pond filled 1811; Erie 26 Oct 1825; Croton 1837-42; High Bridge May 1848; Seneca Village 1825-57; Central Park 1857 start, late 1858 first opening, 1876 complete; draft riots 13-16 July 1863; Brooklyn Bridge 24 May 1883; Statue 28 Oct 1886; St. Patrick's 1879/1888; Ellis Island 1892; consolidation 1 Jan 1898; subway 27 Oct 1904; Flatiron 1 Oct 1902; Penn Station 1910 and demolition 1963-66; Triangle fire 25 Mar 1911; Woolworth 24 Apr 1913; Grand Central 1913; Chrysler 27 May 1930 (319 m); Empire State 1 May 1931; Rockefeller 1931/1933/1939; GWB 25 Oct 1931; Cloisters 10 May 1938; UN 1952; WTC groundbreaking 5 Aug 1966, topping out 23 Dec 1970 and 19 Jul 1971, dedicated 4 Apr 1973, destroyed 11 Sept 2001; 1977 blackout 13-14 July; One WTC 2006 / 2013 / 3 Nov 2014; Sandy 29 Oct 2012; 432 Park 2015; Central Park Tower 2020; populations (S57).

## Unverified items (the list the owner asked for)
- Polity chips from memory, NOT fetched: Dominion of New England 1688, Leisler 1689-91, Great Britain 1707, State of New York 9 July 1776, royal colony date 1685.1, Dec 1790 end of the capital; chip colors are illustrative (no Lenape flag).
- Rings and sizes: ALL rings (zones, fires, floods, water, gutting, lost, bridges) are hand sketches, +-150-300 m, not surveyed. Landmark footprints/sizes without `footprint: auto` (Fort, first Trinity, City Hall 1703, Castle Clinton, Penn Station, Twin Towers, Yankee Stadium) are guesses; WTC tower positions +-60 m.
- Heights from memory: Trinity 85 m, Woolworth 241 m, ESB 381 m, 30 Rock 259 m, UN 154 m, Statue 93 m, 432 Park 426 m, Central Park Tower 472 m; start-of-works years for Penn (1904), GCT (1903), Flatiron (1901.6), Cloisters (1935), UN (1949).
- Penn Station demolition start (Oct 1963): only "between 1963 and 1966" was read. Triborough opening (1936) and Washington Bridge (1888): not read. Willis, Madison, Macombs, Henry Hudson bridge months: unknown.
- Landfill dates (Pearl-South Street fill 1686-1830, Greenwich-West Street fill c. 1800, Battery Park City 1970s, Governors Island 1912, Ellis Island 1906): from memory or only the decade given in S31/S60; the single-step approximation is crude. Use the Welikia/Mannahatta 1609 shoreline (not fetched).
- Columbus Park cleared 1892-97, Foley Square void until 1930, Croton Distributing Reservoir 1842-1900: from memory.
- Hudson's arrival month: S10 gives 6 Sept 1609 (a crew death); I wrote only "1609".
- Data, not history: S72/S73 (NYC Open Data, TIGER) were NOT re-opened; `data_reliable_from: 1900` is a guess because the footprint years cluster on 1900 [Likely, from the old note in `metadata_nyc.md`: "buildings before about 1900 are illustrative reconstructions"].

## Risks for yb-modeler / yb-camera / yb-qa (measure BEFORE any GO)
1. Missing years: `fetch_nyc.py` stores `y = 0` when `cnstrct_yr` is missing. With start 1609 these buildings stand from the FIRST FRAME (QA only FAILs y=0 when start_year < 0). Measure the share, infer from neighbors (Lyon recipe), mark them. Also count the 1900 spike.
2. Predecessors vs monuments without a footprint: the zone predecessors of Madison Square Garden (1968) overlap the Penn Station landmark 1910-1963; same for Fort Amsterdam (US Custom House 1907 on the site) and the Twin Towers (gutting "World Trade Center site" is meant to fill the void with Radio Row). Check with the QA corridors/contact sheet.
3. Zones are disjoint on purpose (the kit sorts zones by `born[0]`, oldest first wins, NOT by list order): Manhattan bands are cut with the mid-river line and the infill rings. Brooklyn buildings near the Brooklyn Bridge (river 500 m wide) may still fall in a Manhattan ring: plot zone membership once `buildings.json` exists.
4. Camera: `pitch_max` 38, `alt_max` 600, `d_min` 1400, `lens` 32 are copied from Marseille/the R2 numbers, NOT measured on NYC. Skyscraper heights (400-540 m) and a 22 km N-S box push the cruise altitude; Liberty Island is at the west edge of the data (lon -74.045).
5. Frozen counter (flights >= 12 s under 0.4 years/s), estimated at v_leg 150 m/s: all hops pass except the Woolworth stop (about 0.39, borderline). Expected QA WARN. Soste are clustered by hops that need about 2.7 years per km: geography is therefore limited to Lower Manhattan (13 stops), Central Park, the East River bridges, Midtown (3), plus the harbor; the Bronx, Harlem and Brooklyn appear only as cards with targets.
6. Night: 145K+ buildings (old note): a night pass is a second scene build; R3 says skip the separate preview and check the night in the full render.
7. Central Park (1858-1876) and other parks come from `city.parks`, which the kit writes empty: park polygons and years (`park_years.json` exists at repo root, old NYC) must be supplied or the sosta "Central Park opens (1858)" shows no park.
8. No DEM in the NYC data (`fetch_nyc.py` has none): the Sandy flood ring is draped on the DEM; if flat, drop `floods` and keep the card.

## What the schema/kit could not express
- No suspension-bridge, cantilever or steel-arch preset (Brooklyn, Williamsburg, Manhattan, GWB, Queensboro, Hell Gate show as flat decks; the hero shots use `area:` targets).
- Fort Amsterdam is an earth bastion fort (castle preset used as a stand-in); no Dutch gabled-house or wooden-church presets.
- Population before the first census: no "unknown" value (first point 1609 = 0 means "no count"); the HUD should hide the number before 1655. HUD series changes definition in 1898 (jump to 3.4M); there is no "city definition" note field.
- Water: one step per ring (landfill is gradual over 1700-1830); `water` cannot hold a time ramp. Landfill under existing buildings is expressible only as `water` with `from` = fill year.
- A `thumbnail_hook` with a recommended cover shot is free-form (no schema); `qa.accept` not used.
- Chip colors for a polity that never had a flag (Lenape); chips for contested control (Leisler) are shown as ordinary regimes.
