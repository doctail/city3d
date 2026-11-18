# New York: METADATA (YouTube), EN only, DRAFT (yb-historian, 18/11/2026)

Chapter times are placeholders `{{t:YEAR}}`: the second at which the counter reaches that year/card in the final render, to be filled from `regia.txt` after the render. The first chapter must be 0:00. No cold open (R14): render times are used as they are.
Status tags: every date in the description comes from `story.json` sources S1-S76 (Wikipedia pages fetched 18/11/2026); [Likely]/[Guessing] items are listed in `NOTE_STORIA.md`.

## Title (<= 100 characters)
EVOLUTION OF NEW YORK | 3D City Timelapse (1609-NOW) | No AI

Check: the first year shown by the video is 1609 (`city.start_year` = `regia.open.rewind_to` = 1609), so the title year is correct. If the owner moves the start to 1624/1625 (see packaging risk below), the title, the thumbnail and `montaggio.title/end/open` change together.

## Description (EN)
New York began as a Lenape island, became the Dutch town of New Amsterdam, then an English port, a capital, a grid, a harbor for millions of immigrants and a forest of towers. Watch 417 years of New York grow, from Henry Hudson's Half Moon in 1609 to the skyline of today.

NO AI imagery. Every frame is rendered from open data. Buildings that stand today appear in the year recorded in the city's building footprint data; the data is incomplete and old buildings cluster on round years, so the years shown before about 1900, and every building that no longer exists (Fort Amsterdam, the first Trinity Church, Penn Station, the Twin Towers), are an approximate reconstruction on the historical footprint, marked on screen as "RECONSTRUCTION · APPROXIMATE". The shoreline before the landfills of the 1700s to 1970s is approximate too. Dates in the captions come from the sources listed below; where a source is thin, the story says so.

Find your building: if a landmark or a block of your neighborhood is missing or wrong, tell me in the comments. Which city should grow next?

CHAPTERS
{{t:start}} New York today
{{t:1609}} I · Mannahatta: Henry Hudson's Half Moon enters the bay (1609)
{{t:1664}} II · The English Port: New Amsterdam becomes New York (1664)
{{t:1776}} III · Revolution and Republic: The Great Fire (1776) and Washington at Federal Hall (1789)
{{t:1811}} IV · The Gridiron City: a grid for the island (1811)
{{t:1855}} V · Immigrant Metropolis: Central Park and the Brooklyn Bridge
{{t:1898}} VI · Five Boroughs, One City (1898)
{{t:1902.75}} VII · The Skyscraper Age: Woolworth, Chrysler, Empire State
{{t:1952}} VIII · Postwar New York: the United Nations, the loss of Penn Station
{{t:1977}} IX · Crisis and Comeback: the Twin Towers (1973)
{{t:2006}} X · The Global City: One World Trade Center (2014)

Data and sources: building footprints, heights and construction years from NYC Open Data; borough boundaries and parks from NYC Open Data; New Jersey land from U.S. Census Bureau TIGER/Line; history from Wikipedia (EN) pages for each event, listed in the video's last card; population from the censuses as compiled on Wikipedia (the city as defined at each date: Manhattan only before 1874, five boroughs from 1898). Music: Unicorn Heads, TrackTribe (YouTube Audio Library). Rendered in Blender.

#NewYork #NYC #Timelapse

## Tags (<= 500 characters)
new york 3d timelapse, evolution of new york, nyc history, new york city history, manhattan history, new amsterdam, new york 1609 to today, how new york grew, manhattan skyline, city timelapse, 3d city timelapse, urban history, history of new york, empire state building history, brooklyn bridge history, year built

## Pinned comment (EN)
New York in 417 years: from the Lenape island of 1609 to today's skyline. Every modern building appears in the year its record says; what no longer stands (Fort Amsterdam, Penn Station, the Twin Towers) is reconstructed and marked on screen. Which building or neighborhood should I check next? Tell me where you live and I will look it up. Which city should grow next?

Pinned comment in the local language: not needed (the local language is English).

## Packaging (R14, series formula)
- Thumbnail: `1609 > NOW`, two full halves, bright, saturated, no flag, no hook event, city name huge at the bottom (`cities/lyon/copertina/lyon_thumb_43bc_now.jpg` as reference). RISK [Likely]: in 1609 there is no city (Dutch settlement from 1624/25): the left half is a forested island. Do the 168 px feed check BEFORE the GO; fallback: start at 1624/1625 and say the new first year in the title.
- No cold open. `thumbnail_hook` in `story.json` (Midtown skyline of 1930-31) is for a Short / community post, not for the thumbnail.

## Not done yet (first line of the delivery will say so)
Chapters in the other 5 languages, Reddit post and first comment, distribution list (candidate communities r/nyc, r/AskNYC, r/newyorkcity, r/MapPorn, r/geography, NYC history Facebook groups, local blogs and outlets: [Guessing], none verified or approached), press note, montage command, covers, cost (NOT measured: the old NYC render of 5:27 is not a basis).
