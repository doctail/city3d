# CTR problem — shared context (14/11/2026). Read-only for the agents.

## The owner's question
"We can make beautiful things but nobody sees them. CTR is the biggest problem of the whole channel. Otherwise it seems we have to open a new channel." No vidIQ calls (credits are spent on other things): work from the data below. YouTube is blocked from this machine (no thumbnail download): only local images.

## Our channel (Year Built, @yearbuiltcities, opened 14/10/2026)
- Subscribers: about 94 (12/11). Long videos so far (views on 11/11): New York 843 (14/10, 5:27) · Madrid 5,771 (18/10, 5:27, pushed by r/Madrid) · Rotterdam 9,765 (21/10) · Copenhagen 33,104 (24/10, 8:32, 174 likes, 51 comments) · Seville 135 (28/10, 5:27) · Paris 5,152 (31/10, 6:31) · Rome 117 (4/11, 4:33). Valencia published 13/11 (8:31).
- Titles used: NYC, Madrid, Rotterdam, Copenhagen: "EVOLUTION OF <CITY> | 3D City Timelapse (<year>–NOW) | No AI". Seville, Paris, Rome: "SEVILLE, Spain - 778 Years in 5 Minutes" style (Rome was switched to the EVOLUTION OF format on 11/11, result unknown). Valencia: "EVOLUTION OF VALENCIA | 3D City Timelapse (1238–NOW) | No AI".
- Early data (REGIA.md, 21 Oct): New York CTR 2.4–2.7%, average view duration 21%, 37% still watching at 0:30. Madrid average view 30%; after the r/Madrid post: Home 17, suggested 21.
- The same channel also hosts battle Shorts (Thermopylae, Constantinople 1453) with a synthetic voice: a different audience on the timelapse channel.
- Copenhagen (the winner) was the first video with: 8:32, full model, thumbnails with the year range and the city name. We have no CTR figure for it in the repo.

## Valencia, first 16 hours (screenshot /root/.claude/uploads/9a70f8cf-3c3e-5618-a9d3-ec6ae55e35ca/68bbe48d-image.png)
- Impressions 823; CTR 1.3%; views 103. The CTR graph: a spike of about 35% in the first hours (a handful of impressions, probably subscribers), then close to 0%. The impressions curve: flat for the first ~6 h, then one jump of ~600 impressions, then flat again.
- 823 x 1.3% = about 11 views from impressions, so about 90 of the 103 views are not from the thumbnail impressions (likely external: Reddit etc.). In other words YouTube barely shows the video: it is an impressions problem and a CTR problem together (a low CTR in the first test stops the expansion).
- Valencia thumbnail: cities/valencia/copertina/valencia_thumb_1238_now.jpg (1238 → NOW diagonal split, big VALENCIA with flag, small "YEAR BUILT" tag, made by thumb_city.py). An earlier variant: valencia_thumb_1960_now.jpg.

## Competitors (CSV: analisi/ctr/concorrenti_titoli.csv, 41 rows: channel, subs, views, date, duration, title)
- Winners with big channels: Latos Charts (118K subs) "PRAGUE - 3D Timelapse" 1.49M, "LISBON - 3D Timelapse" 857K. Cornerstone "EVOLUTION OF NEW YORK | 3D CITY TIMELAPSE (1609–NOW)" 2.2M. Timelapse Studio fixed camera 1.5–2.9M.
- Winners with SMALL channels: Mattia Maps (343 subs): "Valencia: 2,000 Years in 12 Minutes | 3D Timelapse (138 BC–2025)" 135K in 8 days; 2nd video Santiago de Compostela 738 views in 2 days. CityEons (8.9K subs) Rome 1.26M. How Cities Grew (4.6K) Constantinople 1.12M. The City Clock (818 subs) Belgrade 181K. TimeLoop Málaga 203K. nobodycareswhatiswrittenhere: Madrid 228K, Buenos Aires 473K.
- Mattia's thumbnails (screenshot /tmp/claude-0/-home-user/9a70f8cf-3c3e-5618-a9d3-ec6ae55e35ca/images/1.webp, 5 thumbnails): year-range chips on top ("138 BC" / "2025", "1238"), a huge city name, a subtitle chip ("2,000 YEARS IN 3D", "10x BIGGER", "WHY A BAT?", "THE BRIDGE OF SOLIDARITY"). Question or curiosity hooks on his shorts (Why is there a bat on Valencia's coat of arms?, This lake was ten times bigger).
- Analysis of Mattia's Valencia video: analisi/mattia_valencia/FORMULA.md (cards with context, local pride, "No AI", pinned comment asking for the next city).

## Our existing thumbnails (local images)
cities/valencia/copertina/*.jpg · copertine_now/*.jpg (Madrid, NYC, Rotterdam) · copertina_parigi.jpg, copertina_parigi_B.jpg, copertina_rotterdam.jpg, rotterdam_cover_1700.jpg, rotterdam_cover_2026.jpg. Generator: thumb_city.py (usage in its header; fonts in /tmp/claude-0/fonts, otherwise `npm pack @fontsource/anton @fontsource/oswald` and unpack them to /tmp/claude-0/fonts/anton and /oswald). Renders of any year of Valencia: `/home/user/bl/bin/python build_render.py -- data_valencia OUT --frames 1 1 --year Y --cam px py pz tx ty tz --lens 35 --res 1280 720 --samples 16 --denoiser oidn --device CPU --city city_valencia.json` (about 3-5 min each on CPU).

## Constraints
Production pace: 2 long videos per week. Tone of the channel: no voice, "No AI", honest reconstructions. YouTube Studio may offer "Test & compare" for thumbnails (3 variants).
## Output rules
Italian, short tables, tags [Certain]/[Likely]/[Guessing], mention sample sizes, never invent numbers. Final report to me in at most 8 lines.
