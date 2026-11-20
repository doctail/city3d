# New York: thumbnail (series formula R14, 20/11/2026)

Final: `cities/nyc/delivery/copertina/nyc_thumb_1609_now_1280x720.jpg` (1280x720). Text "1609 > NOW / NEW YORK", no flag, no channel tag, no hook event.
- Rule used (MINIATURE.md rule 4 + owner's style 19/11): one subject per half, strong contrast. Left = `h00_1609` (forest island on teal water, the only 1609 frame; 1609 has no city, it is the Lenape island, true to the video). Right = `h14_2015` (Lower Manhattan towers with One World Trade Center, glass desaturated, vs green forest). Rejected: `n24_2026` (flat top-down grey, no subject), 1931 (beige, similar tone to nothing on the left), 1972 (Twin Towers: not "NOW").
- Frames: from `cities/nyc/qa/fix/frames_final2/` (local CPU render 1920x1080, final colour and limestone/steel towers; not committed, large). The right frame is dated 2015.0; the video's NOW is 2026.
- Command: `python -m kit.thumb_kit cities/nyc/delivery/copertina/nyc_thumb_1609_now_1280x720.jpg --left cities/nyc/qa/fix/frames_final2/h00_1609.jpg --right cities/nyc/qa/fix/frames_final2/h14_2015.jpg --title "NEW YORK" --ly 1609 --ry NOW --lbox 420,0,700 --rbox 400,0,1000`
- 168 px and 120 px check done on this file: "NEW YORK", "1609" and "NOW" read at both sizes.
- Honest limit: the left half has no city (forest) and a lot of teal water at the bottom, it is "island vs towers", not "city vs city". Risk already noted in METADATA (packaging risk). Fallback if the owner prefers: start at 1624/1625 (title, thumbnail and montaggio.title/end/open change together).
- Not checked: the night cover (no night frame requested), post-render frames (covers are re-made from the final render if wanted: `run.sh cover`).
