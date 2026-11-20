# Instagram — Ledger of Cities / Follower City

Nota: la disponibilita' degli handle NON e' verificabile da qui (nessun accesso a Instagram): controllare nell'app al momento della registrazione.

## Nome e handle
- **Nome visualizzato:** `Ledger of Cities | 1 follower = 1 building` (il nome e' cercabile: tenere le parole chiave qui)
- **Handle, in ordine di preferenza:**
  1. `@ledgerofcities` (coerente col canale YouTube)
  2. `@followercity.ledger`
  3. `@onefollowonebuilding` (alt: `@1follower1building`)
- **Categoria:** Digital Creator (alternativa: Video Creator)

## Bio (146 caratteri)
```
1 follower = 1 building 🏠
A cozy city that grows with you.
Made with Blender · No AI
Urban history on YouTube ↓
```
Se i caratteri sono troppi: tenere le righe 1, 3 e 4. Il rimando YouTube e' nell'ultima riga e nel link.

## Link in bio
`https://www.youtube.com/@ledgerofcities?utm_source=instagram&utm_medium=bio&utm_campaign=follower_city`

## Primo post (immagine fissa `out/post1_1080x1350.png`)
Didascalia:
```
Meet building #1 — the first follower.
Every new follower adds one building to this little city. Follow along and watch it grow, one day at a time.
Built in Blender. No AI. Real stories of real cities live on YouTube: Ledger of Cities (link in bio).
```
Hashtag: `#blender3d #cozycity #lowpoly #3dart #isometric #citybuilder #cozyvibes #urbanhistory #timelapse #satisfying`

Commento fissato: `Day 1 starts now. Follow to add building #2 — and tell me what the city needs next. 🏗️`

## Griglia
Post 1 = immagine fissa. Poi un reel al giorno con cartello `DAY n / n buildings` (Day 1, Day 2, ...). Mockup: `out/mockup_griglia.png` (Day 1/2 sono segnaposto presi dai video di prova).

## Storie in evidenza (copertine `out/story1..5_*.png`)
1. **Day by Day** (calendario con casetta): un frame/clip per ogni giorno, la citta' che cresce; aggiungere ogni reel.
2. **The OGs** (ticket con stella): i primi 100 follower, con screenshot/nome (con permesso) e il loro palazzo "OG ticket".
3. **Requests** (fumetto con cuore): palazzi speciali richiesti nei commenti, "request received" -> "built"; regolamento qui sotto.
4. **Making of** (cubo): sessioni Blender, wireframe, prima/dopo, come nasce un palazzo.
5. **Ledger** (libro mastro con grafico): link ai video del canale YouTube Ledger of Cities, storia vera della citta' che ispira il palazzo del giorno.

## Regolamento commenti e richieste (da mettere in Requests)
- Un palazzo speciale = un follower. Chiedi nei commenti di un reel: tipo di edificio (bar, torre, chiesa, ecc.), un nome, un colore. Una richiesta per persona.
- Il palazzo e' costruito in ordine di arrivo, quando il progetto puo'; non tutte le richieste possono essere accettate e nessuna scadenza e' garantita.
- Niente marchi, loghi, simboli protetti o persone reali; niente contenuti offensivi.
- **OG ticket:** i primi 100 follower ricevono un palazzo con il loro nome su una targa, nella citta' per sempre (serve essere follower al momento della costruzione).
- Se smetti di seguire il palazzo resta, ma la targa viene tolta.

## Immagini (cartella `out/`)
- `profile_1080x1080.png` foto profilo (crop circolare verificato, palazzo e piedistallo dentro il cerchio; sfondo salvia)
- `post1_1080x1350.png` primo post (sfondo blu polvere, golden hour, testo solo "1 follower = 1 building")
- `story1_daybyday`, `story2_ogs`, `story3_requests`, `story4_making`, `story5_ledger` (1080x1920, pastello)
- `mockup_griglia.png`
- Sorgenti: `src/hero.py` (Blender, 56 campioni + denoise), `src/compose.py` (PIL). Es.: `DIST=46 TZ=6.2 DY=-1.5 python src/hero.py profile out/profile_raw.png 56`
